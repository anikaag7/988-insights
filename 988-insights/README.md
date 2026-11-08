# 988 Training Insights

A tool for EveryMind staff to turn 988 training survey exports into checked, comparable results.

All the code is in the [`988-insights/`](988-insights/) folder. Paths below are relative to that folder.

It has two parts:

| Part | What it is | What you need |
|---|---|---|
| **Website** (`web/index.html`) | Upload a survey export, review the data check, explore data visualizations, download results | Any modern web browser |
| **Python pipeline** (`pipeline/`) | The reference analysis: data check report and charts (PNG) | Python 3.10 or newer |

**Your survey file never leaves your computer.** The website processes everything in the browser,
and the pipeline runs locally. Nothing is uploaded or stored.

---

## 1. Use the website

### Option A: hosted link
Open the hosted link (added before submission). Nothing to install.

### Option B: open the file directly
1. Download this repository (green **Code** button → **Download ZIP**, then unzip), or
   `git clone` it.
2. Double-click `988-insights/web/index.html`. It opens in your default browser.

The page loads two pinned libraries (SheetJS and Chart.js) from cdnjs, so it needs an internet
connection the first time it loads.

### Option C: local web server
If your browser blocks local files, serve the folder instead (requires Python). Run this from the
inner `988-insights` folder:

```bash
python3 -m http.server 8000 --directory web
```

Then go to <http://localhost:8000>. Press `Ctrl+C` in the terminal to stop it.

### Using it
1. **Upload**: drag in the survey export (`.xlsx` or `.csv`), or click **Try synthetic demo data**.
2. **Data check**: review possible issues. These are *possible* issues only; no responses are
   removed or changed. Choose how to treat any unrecognized answer labels.
3. **Data visualizations**: use the top filters for date, county and group. The group selection applies throughout the visualizations: Everyone (students + adults), Students only, Adults only, or Compare students and adults. Explore specific, approximate themes in training-improvement comments, ranked by mention count; comments themselves are never displayed.
4. **Export**: download the cleaned CSV, the possible-issues CSV, or print a one-page summary.

Columns are matched by their wording, not their position, so renamed or reordered columns in a
future export still work.

---

## 2. Run the Python pipeline

### Step 1: install Python
Check whether you already have it:

```bash
python3 --version     # macOS / Linux
py --version          # Windows
```

If it's missing or older than 3.10, install it from <https://www.python.org/downloads/>.
On Windows, tick **"Add Python to PATH"** during setup.

### Step 2: get the code
```bash
git clone https://github.com/shauna1-stack/988-insights.git
cd 988-insights/988-insights
```
(Or download the ZIP from GitHub, unzip it, and open a terminal in the inner `988-insights`
folder, the one that contains `pipeline/` and `web/`.)

### Step 3: create a virtual environment and install packages

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If PowerShell refuses to run the activate script, run
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once, then try again.
In Command Prompt, use `.venv\Scripts\activate.bat` instead.

After activation, `python` refers to the environment's Python on every system.

### Step 4: add your survey file
The survey data is **not** in this repository (it contains personal responses). Put your export at
`data/survey.xlsx`, or use any path you like in the commands below.

### Step 5: run it
Run these from the inner `988-insights` folder (the one with `pipeline/` and `web/`):

```bash
# Possible data issues: prints a report and saves it to a text file
python pipeline/checks.py data/survey.xlsx outputs/data_check.txt

# Cleaned data as CSV
python pipeline/clean.py data/survey.xlsx outputs/clean.csv

# Reference charts (PNG files)
python pipeline/charts.py data/survey.xlsx outputs/charts
python pipeline/charts_story.py data/survey.xlsx outputs/charts
```

Results appear in `outputs/`, which is created automatically.

### Optional: test with a "next quarter" file
This builds a copy of the survey with two columns renamed and 12 answers changed to an unfamiliar
label, to show that the tool still works on a changed export:

```bash
python pipeline/make_test_file.py data/survey.xlsx data/test_next_quarter.xlsx
python pipeline/checks.py data/test_next_quarter.xlsx
```
The report should include `Unrecognized answer "Totally agree": 12`.

When you're done, run `deactivate` to leave the virtual environment.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `python: command not found` | Use `python3` (macOS/Linux) or `py` (Windows), or activate the virtual environment first |
| `ModuleNotFoundError: No module named 'pandas'` | Activate the virtual environment (Step 3), then `pip install -r requirements.txt` |
| `FileNotFoundError` for the survey | Check the path; run the commands from the inner `988-insights` folder |
| Website shows a blank page or no charts | Check your internet connection (the libraries load from cdnjs), or try Option C |
| `.csv` export shows odd characters | Save the CSV as UTF-8, or upload the original `.xlsx` |

---

## Who runs it and how often
A program coordinator, after each quarterly batch of trainings, in about 5 minutes.
