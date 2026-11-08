# Technical Artifact Plan: 988 Training Insights

**Deadline: Sunday, Nov 8, 2026, 9:00 AM ET.** Submit Saturday night. Late entries are not accepted.

## Goal
A pipeline that turns any EveryMind survey export into checked, comparable results:
**upload → clean → warn about possible issues → calculate → charts → download**.

It must (from the rubric):
- Run without errors on the provided dataset
- Produce clear, usable outputs
- Handle reasonable data updates (renamed columns, new answer labels)
- Include instructions for running it
- Be shown in a video of 2 minutes or less

## Folder layout
```
pipeline/
  clean.py          # load + clean (done)
  checks.py         # warn about possible issues, never removes data (done)
  metrics.py        # every number in the memo (to do)
  comments.py       # remove names, tag themes, sample 100 for hand coding (to do)
  charts.py         # charts from metrics (exists; switch input to metrics output)
  run_all.py        # one command runs everything (to do)
  ../web/index.html # static website, the main artifact (to do)
  sample_data/      # provided dataset + test_next_quarter.xlsx
  outputs/          # clean.csv, data_check.txt, summary_tables.xlsx, charts/
  README.md         # install + run instructions
```

## Scripts
| Script | Status | Input | Output |
|---|---|---|---|
| `clean.py` | ✅ Done | .xlsx or .csv | `clean.csv` |
| `checks.py` | ✅ Done | .xlsx or .csv | `data_check.txt` (warnings only) |
| `metrics.py` | ⬜ To do | `clean.csv` | `summary_tables.xlsx` |
| `comments.py` | ⬜ To do | `clean.csv` | `themes.csv`, `hand_code_sample.csv` |
| `charts.py` | 🟨 Adapt | `summary_tables.xlsx` | `charts/*.png` |
| `run_all.py` | ⬜ To do | .xlsx or .csv | all of the above |
| `web/index.html` | ⬜ Priority | upload in browser | static website on GitHub Pages |

### `checks.py`: possible issues it warns about
Nothing is removed or changed. Each warning says "possible."
| Warning | Count in provided data |
|---|---|
| Unrecognized answer "Very agree" | 37 |
| Unrecognized answer "Satisfied" | 31 |
| "Likely to call 988" blank (not on every form version) | 1,006 (77%) |
| Low confidence after training but recommends 9–10 | 21 |
| Completed in under 20 seconds | 16 |
| Possible duplicate submissions | 5 |
| Training date missing or wrong | 18 |
| County outside the service area | 7 |

### `metrics.py`: what to calculate
1. Knowledge before vs. after: % agree on each of the 3 items, plus average gain
2. Students vs. adults: knowledge after, 3 presenter ratings, recommend (mean and % 9–10), likely to call 988
3. Students by county: Anne Arundel vs. Prince George's; mark others "too few"
4. Intent gap: of those who know when to use 988, % rating calling at 6 or below, by group
5. Survey coverage: responses per question, by month
6. Sample size (n) next to every number; suppress groups under 10

## Definitions (use everywhere so numbers match the charts)
- **Agree** = 4 or 5 (Strongly disagree = 1 … Strongly agree = 5)
- **"Very agree" / "Satisfied"** = missing until EveryMind confirms their meaning
- **Promoter** = 9–10 on recommend; **detractor** = 0–6
- **Student** = checked only "Student"; everyone else is an adult
- **Session** = training date + county
- **Too few** = fewer than 10 people

## Run instructions (for the README)
```bash
pip install pandas openpyxl matplotlib scipy
python run_all.py sample_data/BuildFest_EveryMind_Survey_Data_FULL.xlsx
# individual steps
python clean.py  <file.xlsx> outputs/clean.csv
python checks.py <file.xlsx> outputs/data_check.txt
```

## Data-update test (show this in the video)
`sample_data/test_next_quarter.xlsx` is the real data with two changes:
- 2 columns renamed (recommend question, county)
- 12 answers changed to "Totally agree"

Result: the pipeline still runs, matches the renamed columns, and warns:
`Unrecognized answer "Totally agree": 12`

## Schedule
| Day | Artifact work |
|---|---|
| **Wed (today)** | ✅ `clean.py`, `checks.py`. Write `metrics.py`. |
| **Thu** | `comments.py`, `run_all.py`, charts connected. **6 PM office hours.** |
| **Fri** | README, finish website, host on GitHub Pages. Someone outside the team runs it from the README alone. |
| **Sat** | Record video (aim for ~110 s), anonymity check, submit as `Team#_TechnicalArtifact` |

## Video outline (≤ 120 s)
1. 0:00–0:15 The problem: survey versions don't match, so results can't be compared
2. 0:15–0:40 Run on the real data; show the data-check warnings
3. 0:40–1:20 Results: knowledge gains; students learn the same but don't feel the same
4. 1:20–1:45 Run on `test_next_quarter.xlsx`; it still works and flags "Totally agree"
5. 1:45–2:00 Who runs it (program coordinator), how often (each quarter), what they need (a laptop with Python, or a browser if the app is hosted)

## Questions for office hours (Thu 6 PM)
- What did "Very agree" and "Satisfied" mean on the April 2026 form?
- Were student surveys done on paper and typed in later?
- Why is "likely to call 988" only on some versions of the form?
- What software do staff use: Excel, Google Sheets, or something else?

## Before submitting
- [ ] Runs from a fresh copy using only the README
- [ ] No names in code, file metadata, GitHub account, or commit history
- [ ] Links set to "anyone with the link can view"
- [ ] File named `Team#_TechnicalArtifact` with your team number
