# 988 Training Insights: project context for Claude Code

Competition entry for **UMD BuildFest 2026 (Nonprofit Data Challenge)**: analyze EveryMind's
988 awareness-training survey and build a tool staff can rerun on future surveys.
**Deadline: Sunday, Nov 8, 2026, 9:00 AM ET. Submit Saturday night.** Late entries are rejected.

## What we are building
1. **`web/index.html`: a static website (the technical artifact).** One self-contained page hosted on
   GitHub Pages. The user uploads the survey .xlsx/.csv; **all processing happens in the browser**,
   so the file never leaves their computer. No server, no build step, no API keys.
2. **`pipeline/*.py`: the Python reference pipeline.** It is the reproducible analysis and the
   source of truth for numbers. The website must match it (see "Parity targets").

## Hard rules
- **Never commit survey data.** The repo is public. `data/`, `*.xlsx`, `*.csv` are gitignored.
  The real dataset contains comments from real people, many probably minors. Demo data on the site
  must be **synthetic**, generated in code and labeled "Synthetic demo data".
- **Client-side only.** No fetch/upload of user data anywhere. Show "Your file never leaves your browser."
- **Anonymous judging.** No team member names, emails, or university IDs in code, comments, page text,
  file metadata, or commit history. Commit from the neutral GitHub account only.
- **Pin library versions** from cdnjs (e.g. SheetJS `xlsx` 0.18.5, Chart.js 4.4.1). No unpinned URLs.
- **Never remove or silently change responses.** Problems are reported as *possible* issues; results include all rows.
- **Use the shared definitions below everywhere**, so the site, the Python, the memo, and the charts agree.
- Plain language for a nontechnical program coordinator. Show **n** next to every number.

## The data (`data/survey.xlsx`, 1,299 rows × 20 columns, one sheet "Survey Data")
Columns are found **by keywords, not position or exact header** (see `FIELDS` in `pipeline/clean.py`;
mirror it in JS). Fields: id, start, end, language, role, train_date, county,
post_identify / post_describe / post_when ("I can…" after training),
pre_identify / pre_describe / pre_when ("Now think back to before…"),
q_engaged / q_knew / q_organized (presenter/training quality), recommend (0–10),
call988 (0–10, "How likely are you to call 988"), valuable, improve (free-text comments).

Quirks the cleaner must handle:
- Invisible characters: `‎` after language names, `\xa0` in headers and in "Strongly agree\xa0", trailing spaces.
- "Neither agree **or** disagree" (quality items) = "Neither agree **nor** disagree" (knowledge items).
- **"Very agree" (37 answers) and "Satisfied" (31)** appear only in quality items, April–May 2026
  (likely a translated form). Treat as **missing** and warn; do not guess.
- Role is multi-select, separated by `;` (e.g. "Caregiver/parent;Student").
- County spellings vary ("Montgomery County ", "Fairfax county ") → strip "County…" suffix and whitespace.
- `call988` exists only on some survey versions: 293 of 1,299 answered.
- Quality items are blank for ~150 rows (another survey version).

## Shared definitions
- Likert: Strongly disagree 1, Disagree 2, Neither 3, Agree 4, Strongly agree 5. **Agree = 4 or 5.**
- **Promoter** = recommend 9–10; **detractor** = 0–6; NPS = %promoters − %detractors.
- **Student** = role is only "Student". Everyone else (incl. "Multiple") is an **adult** (`group`).
- **Session** = training date + county (no session ID exists; this is an approximation).
- **Too few** = fewer than 10 people → grey out / suppress, say "Too few responses to compare".
- Knowledge gain = mean(post items) − mean(pre items). "Before" was rated **after** the training
  (retrospective), so always caveat that gains may be overstated.

## Possible-issue warnings (`pipeline/checks.py`; counts on the real data)
| Warning | Rule | Count |
|---|---|---|
| Unrecognized answer label | not in Likert map | "Very agree" 37, "Satisfied" 31 |
| Question blank for many | ≥20% blank | Likely to call 988: 1,006 (77.4%) |
| Low confidence + strong recommend | mean(post) ≤ 2 and recommend ≥ 9 | 21 |
| Very fast | duration < 20 s | 16 |
| Possible duplicates | same session+role, identical answers incl. comments and quality text, AND (non-empty comment OR < 10 min apart) | 5 |
| Date problem | train date missing, survey before training, or > 30 days after | 18 (3 / 1 / 14) |
| Outside service area | county not in {Anne Arundel, Prince George's, Montgomery, Queen Anne's} | 7 (Fairfax 6, Harris 1) |
Header text: "These are POSSIBLE issues, not confirmed errors. No responses were removed or changed."

## Parity targets: the website must reproduce these on `data/survey.xlsx`
| Metric | Value |
|---|---|
| Responses / students / adults / sessions | 1,299 / 1,076 / 223 / 55 |
| % agree before → after: identify | 72.2 → 89.9 |
| % agree before → after: describe 988 | 46.5 → 90.5 |
| % agree before → after: know when | 55.7 → 92.3 |
| NPS overall (n = 1,266) | +12.0 |
| Students: NPS / mean recommend / % 9–10 | −2.2 / 7.21 / 32.3% |
| Adults: NPS / mean recommend / % 9–10 | +79.9 / 9.39 / 82.2% |
| Students % agree after (identify, describe, when) | 89.6, 90.3, 92.2 |
| Adults % agree after (identify, describe, when) | 91.5, 91.0, 92.8 |
| Presenter items % agree, students (engaged, knew, organized) | 86.3, 88.7, 90.7 |
| Presenter items % agree, adults | 95.1, 96.6, 95.6 |
| Likely to call 988, mean (n): students / adults | 7.37 (253) / 9.50 (40) |
| Intent gap (of those agreeing they know when to use 988, % rating call ≤ 6): students / adults | 29.0% (n=231) / 2.6% (n=39) |
| Students by county | Anne Arundel 887, Prince George's 180, Queen Anne's 6, Montgomery 3 |
| Student recommend mean / % 9–10: Anne Arundel vs Prince George's | 7.02 / 28.5% vs 8.25 / 52.7% |
Verify with `python pipeline/checks.py data/survey.xlsx` and by adding a parity test in JS
(e.g. a hidden "self-test" that logs these values to the console).

## The story the site should support
**"Students learn as much as adults, but they don't feel the same."**
- Knowledge rises for everyone; after training both groups are at 90–93% agree.
- Students are less positive about delivery (86–91% vs 95–97%), much less likely to recommend
  (32% vs 82% giving 9–10), and less likely to call 988 (29% intent gap vs 3%).
- Among students, Anne Arundel recommends less than Prince George's (borderline at session level, p≈0.08).
- Caveats to show in the UI: students and adults almost never attended the same session (only 2 sessions,
  8 students, truly together); student surveys appear typed in later (one at a time, ~1 week after);
  intent question on only 23% of forms; no demographic questions, so equity analysis is limited.
- Do NOT claim "students feel the same as adults" or that any group "proves" causation.

## Website spec (`web/index.html`)
Screens (single page, tabs or steps):
1. **Upload**: drag-and-drop .xlsx/.csv, "Try synthetic demo data" button, privacy line.
2. **Data check**: summary ("1,299 responses, 55 sessions, Oct 2025 – Oct 2026"), auto-fixes applied,
   the warnings table above, and for unrecognized labels a dropdown per label (Exclude [default] /
   Strongly agree / Agree / …) that recomputes results.
3. **Dashboard** with filters (date range, county, group): Overview tiles; Knowledge before/after;
   Students vs adults ("same learning, different feelings"); Intent gap; Students by county
   (suppress n < 10); Survey coverage by month (which questions were on the form).
4. **Export**: cleaned CSV, warnings CSV, and a printable one-page summary (window.print with print CSS).
Design: light and dark themes, students orange `#eb6834`, adults blue `#2a78d6`, n on every chart,
plain-English "What this means" line under each chart. Must work at phone width without horizontal scroll.

## Repo layout
```
CLAUDE.md               this file
../README.md            how to run / access (judges read this; at repo root)
docs/plan.md            schedule, video outline, office-hours questions, submit checklist
docs/app-architecture.png
docs/sessions_reference.csv   per-session summary (no personal data)
pipeline/clean.py       load + clean; load_and_clean(path) -> (df, notes)
pipeline/checks.py      warnings only; run_checks(df, notes)
pipeline/charts.py, charts_story.py   reference charts (PNG) for memo/deck
pipeline/make_test_file.py            builds data/test_next_quarter.xlsx
web/index.html          the website (to build)
data/                   real data, gitignored
outputs/                generated files, gitignored
```

## Commands
```bash
pip install pandas openpyxl matplotlib scipy
python pipeline/checks.py data/survey.xlsx outputs/data_check.txt
python pipeline/charts.py data/survey.xlsx outputs/charts
python pipeline/charts_story.py data/survey.xlsx outputs/charts
python pipeline/make_test_file.py data/survey.xlsx data/test_next_quarter.xlsx
python -m http.server 8000 --directory web    # preview the site at http://localhost:8000
```

## Data-update test (shown in the video)
`data/test_next_quarter.xlsx` = real data with the recommend and county columns renamed and 12 answers
set to "Totally agree". The site and `checks.py` must still run, match the renamed columns, and warn
`Unrecognized answer "Totally agree": 12`.

## Status
- Done: clean.py, checks.py, reference charts, architecture diagram, plan.
- To do: web/index.html (priority), README.md, optional pipeline/metrics.py and comments.py
  (comment themes with a 100-comment hand-coded validation sample for the AI appendix).

## Lessons already learned (do not repeat)
- "Session = date + county" can merge different trainings: "Apr 15, Prince George's" contains adults
  surveyed Apr 17 and students surveyed May 8, so it is NOT a mixed session. Check timestamps before
  claiming students and adults shared a session.
- Matching numeric answers alone is not evidence of a duplicate (198 people share answer patterns);
  require identical comments or submissions minutes apart, and call them "possible".
- Matplotlib rounding: describe-988 before is 46.5% (46.47), shown as 46% in charts; use one decimal in tables.
