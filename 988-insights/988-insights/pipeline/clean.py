"""Load and clean the EveryMind 988 training survey export.

Usage:  python clean.py <survey.xlsx|csv> [output.csv]
As a module:  from clean import load_and_clean; df, notes = load_and_clean(path)
"""
import re
import sys

import numpy as np
import pandas as pd

# Each field is found by keywords in the column header, so renamed columns still match.
# A column matches when ALL keywords in one of its keyword lists appear (case-insensitive).
FIELDS = {
    "id": [["id"]],
    "start": [["start time"]],
    "end": [["completion time"]],
    "language": [["language"]],
    "role": [["are you a"]],
    "train_date": [["date", "training"]],
    "county": [["county"]],
    "post_identify": [["can identify"]],
    "post_describe": [["can describe"]],
    "post_when": [["know when"]],
    "pre_identify": [["think back", "identify"], ["could identify"]],
    "pre_describe": [["think back", "describe"], ["could describe"]],
    "pre_when": [["think back", "knew when"], ["knew when"]],
    "q_engaged": [["engaged"]],
    "q_knew": [["knew the subject"], ["subject matter"]],
    "q_organized": [["organized"]],
    "recommend": [["recommend"]],
    "call988": [["likely", "call 988"]],
    "valuable": [["most valuable"]],
    "improve": [["improve"]],
}

LIKERT = {
    "strongly disagree": 1, "disagree": 2,
    "neither agree nor disagree": 3, "neither agree or disagree": 3,
    "agree": 4, "strongly agree": 5,
}
ITEMS = ["identify", "describe", "when"]
QUALITY = ["q_engaged", "q_knew", "q_organized"]
ROLES = {"student": "Student", "staff": "School staff", "parent": "Caregiver", "other": "Other"}


def norm_text(v):
    """Remove invisible characters and extra spaces; keep missing values missing."""
    if pd.isna(v):
        return np.nan
    v = re.sub(r"[‎‏\xa0]", " ", str(v))
    v = re.sub(r"\s+", " ", v).strip()
    return v or np.nan


def match_columns(columns):
    """Return {field: column name} and a list of fields that could not be found."""
    lowered = {c: norm_text(c).lower() for c in columns}
    found, missing = {}, []
    for field, options in FIELDS.items():
        hit = None
        for keywords in options:
            for col, low in lowered.items():
                if col in found.values():
                    continue
                if field == "id" and low != "id":
                    continue
                if all(k in low for k in keywords):
                    hit = col
                    break
            if hit:
                break
        if hit:
            found[field] = hit
        else:
            missing.append(field)
    return found, missing


def code_likert(series, unknown):
    """Map agree/disagree text to 1-5. Unrecognized labels become missing and are counted."""
    text = series.map(norm_text)
    coded = text.str.lower().map(LIKERT)
    for label, n in text[text.notna() & coded.isna()].value_counts().items():
        unknown[label] = unknown.get(label, 0) + int(n)
    return coded, text


def load_and_clean(path):
    raw = pd.read_excel(path) if str(path).lower().endswith((".xlsx", ".xls")) else pd.read_csv(path)
    cols, missing = match_columns(raw.columns)
    notes = {"rows": len(raw), "missing_fields": missing, "unknown_labels": {}}
    get = lambda f: raw[cols[f]] if f in cols else pd.Series(np.nan, index=raw.index)

    df = pd.DataFrame(index=raw.index)
    df["id"] = get("id")
    df["start"] = pd.to_datetime(get("start"), errors="coerce")
    df["end"] = pd.to_datetime(get("end"), errors="coerce")
    df["duration_s"] = (df.end - df.start).dt.total_seconds()
    df["language"] = get("language").map(norm_text).map(
        lambda v: "Spanish" if isinstance(v, str) and v.lower().startswith("esp") else "English")

    roles = get("role").map(norm_text).fillna("")
    for key, label in ROLES.items():
        df["role_" + key] = roles.str.contains(label, case=False)
    n_roles = df[[f"role_{k}" for k in ROLES]].sum(axis=1)
    df["role"] = np.select(
        [n_roles > 1, df.role_student, df.role_staff, df.role_parent, df.role_other],
        ["Multiple", "Student", "School staff", "Caregiver/parent", "Other/community"], "Missing")
    df["group"] = np.where(df.role == "Student", "Students", "Adults")

    df["train_date"] = pd.to_datetime(get("train_date"), errors="coerce")
    df["county"] = (get("county").map(norm_text)
                    .str.replace(r"(?i)\s*county.*$", "", regex=True).str.strip())
    df["session"] = df.train_date.dt.strftime("%Y-%m-%d").fillna("no date") + " | " + df.county.fillna("no county")

    unknown = notes["unknown_labels"]
    for item in ITEMS:
        df["post_" + item], _ = code_likert(get("post_" + item), unknown)
        df["pre_" + item], _ = code_likert(get("pre_" + item), unknown)
        df["gain_" + item] = df["post_" + item] - df["pre_" + item]
    for q in QUALITY:
        df[q], df[q + "_text"] = code_likert(get(q), unknown)

    df["post_mean"] = df[[f"post_{i}" for i in ITEMS]].mean(axis=1)
    df["pre_mean"] = df[[f"pre_{i}" for i in ITEMS]].mean(axis=1)
    df["gain_mean"] = df.post_mean - df.pre_mean
    df["recommend"] = pd.to_numeric(get("recommend"), errors="coerce")
    df["call988"] = pd.to_numeric(get("call988"), errors="coerce")
    df["valuable"] = get("valuable").map(norm_text)
    df["improve"] = get("improve").map(norm_text)
    return df, notes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python clean.py <survey.xlsx|csv> [output.csv]")
    out = sys.argv[2] if len(sys.argv) > 2 else "clean.csv"
    data, info = load_and_clean(sys.argv[1])
    data.to_csv(out, index=False)
    print(f"Cleaned {info['rows']} responses -> {out}")
    if info["missing_fields"]:
        print("Columns not found:", ", ".join(info["missing_fields"]))
