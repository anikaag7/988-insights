"""Warn about POSSIBLE data issues in the survey. Nothing is removed or changed.

Usage:  python checks.py <survey.xlsx|csv> [data_check.txt]
As a module:  from checks import run_checks; warnings = run_checks(df, notes)
"""
import os
import sys

import pandas as pd

from clean import load_and_clean, ITEMS, QUALITY

SERVICE_AREA = {"Anne Arundel", "Prince George's", "Montgomery", "Queen Anne's"}
FAST_SECONDS = 20
LATE_DAYS = 30
DUP_WINDOW_MIN = 10
MISSING_WARN_PCT = 20


def _pct(n, total):
    return f"{n / total * 100:.1f}%" if total else "0%"


def run_checks(df, notes):
    """Return a list of (title, count, explanation) for each possible issue found."""
    total = len(df)
    out = []

    # 1. Columns or answer labels the cleaner did not recognize
    if notes["missing_fields"]:
        out.append(("Questions not found in this file", len(notes["missing_fields"]),
                    "Not found: " + ", ".join(notes["missing_fields"])
                    + ". Results that need them are skipped."))
    for label, n in notes["unknown_labels"].items():
        out.append((f'Unrecognized answer "{label}"', n,
                    "Not on the agree/disagree scale, so these answers are treated as missing. "
                    "Ask EveryMind what this label meant on the form."))

    # 2. Questions that many responses skipped (often a sign of different survey versions)
    for col, name in [("call988", "Likely to call 988"), ("recommend", "Would recommend"),
                      ("q_engaged", "Presenter engaged participants")]:
        blank = int(df[col].isna().sum())
        if blank / total * 100 >= MISSING_WARN_PCT:
            out.append((f'"{name}" is blank for many responses', blank,
                        f"{_pct(blank, total)} blank. It may not have been on every version of the form, "
                        "so results for this question may not represent everyone."))

    # 3. Low confidence after training but a 9-10 recommendation
    low_high = df[(df.post_mean <= 2) & (df.recommend >= 9)]
    if len(low_high):
        out.append(("Low confidence after training but would strongly recommend", len(low_high),
                    "Could be real low confidence, or the person may have misread the scale. Kept in results."))

    # 4. Very fast completions
    fast = df[df.duration_s < FAST_SECONDS]
    if len(fast):
        out.append((f"Completed in under {FAST_SECONDS} seconds", len(fast),
                    "Possibly rushed. If surveys were typed in from paper, this reflects typing speed instead."))

    # 5. Possible duplicate submissions
    key = ["session", "role", *[f"post_{i}" for i in ITEMS], *[f"pre_{i}" for i in ITEMS],
           *[q + "_text" for q in QUALITY], "recommend", "call988", "valuable", "improve"]
    keyed = df.assign(_k=df[key].apply(lambda r: "|".join(map(str, r.values)), axis=1)).sort_values("start")
    pairs = 0
    for _, g in keyed[keyed.duplicated("_k", keep=False)].groupby("_k"):
        has_comment = g.valuable.notna().any() or g.improve.notna().any()
        gap_min = (g.start.iloc[-1] - g.start.iloc[0]).total_seconds() / 60
        if has_comment or gap_min < DUP_WINDOW_MIN:
            pairs += len(g) - 1
    if pairs:
        out.append(("Possible duplicate submissions", pairs,
                    "Identical answers in the same session, minutes apart or with identical comments. "
                    "The survey is anonymous, so these can't be confirmed. Kept in results."))

    # 6. Date problems
    days = (df.start.dt.normalize() - df.train_date).dt.days
    no_date = int(df.train_date.isna().sum())
    before = int((days < 0).sum())
    late = int((days > LATE_DAYS).sum())
    if no_date + before + late:
        out.append(("Training date looks wrong or is missing", no_date + before + late,
                    f"{no_date} missing, {before} surveyed before the training date, "
                    f"{late} surveyed more than {LATE_DAYS} days after."))

    # 7. Counties outside the service area
    outside = df[df.county.notna() & ~df.county.isin(SERVICE_AREA)]
    if len(outside):
        counts = ", ".join(f"{c} {n}" for c, n in outside.county.value_counts().items())
        out.append(("County outside the service area", len(outside),
                    f"{counts}. Could be typos, out-of-area attendees, or test entries."))
    return out


def format_report(df, warnings):
    lines = [f"DATA CHECK: {len(df):,} responses, {df.session.nunique()} sessions",
             "These are POSSIBLE issues, not confirmed errors. No responses were removed or changed.", ""]
    if not warnings:
        lines.append("No issues found.")
    for title, n, why in warnings:
        lines.append(f"[!] {title}: {n:,}")
        lines.append(f"    {why}")
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python checks.py <survey.xlsx|csv> [data_check.txt]")
    data, info = load_and_clean(sys.argv[1])
    report = format_report(data, run_checks(data, info))
    print(report)
    if len(sys.argv) > 2:
        os.makedirs(os.path.dirname(os.path.abspath(sys.argv[2])), exist_ok=True)
        with open(sys.argv[2], "w", encoding="utf-8") as f:
            f.write(report + "\n")
