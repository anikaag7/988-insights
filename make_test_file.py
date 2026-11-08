"""Make a 'next quarter' test file from the real survey: renames 2 columns and adds a new answer label.

Usage: python pipeline/make_test_file.py data/survey.xlsx data/test_next_quarter.xlsx
"""
import sys
import pandas as pd

src, dst = sys.argv[1], sys.argv[2]
raw = pd.read_excel(src)
cols = list(raw.columns)
rec = next(c for c in cols if "recommend" in c.lower())
cty = next(c for c in cols if "county" in c.lower())
item = next(c for c in cols if "can identify" in c.lower())
raw = raw.rename(columns={rec: "Would you recommend this training to others? (0-10)", cty: "County"})
raw.loc[:11, item] = "Totally agree"
raw.to_excel(dst, index=False)
print(f"Wrote {dst}: 2 columns renamed, 12 answers set to 'Totally agree'")
