import os
import pandas as pd

ROOT_DIR = r"D:\Machine learning\Atefeh\NCAD_Conference\Development-and-Computational-Validation-of-the-Normative-Cognitive-Assessment"
DATA_PATH = os.path.join(ROOT_DIR, "dataset", "NCAD_Iranian_Dataset.xlsx")
TABLES_DIR = os.path.join(ROOT_DIR, "results", "tables")
os.makedirs(TABLES_DIR, exist_ok=True)

print(f"Loading dataset from: {DATA_PATH}")
df = pd.read_excel(DATA_PATH, sheet_name="Simulated Data", skiprows=1)
print(f"Total benchmark records: {len(df)}")

strat_summary = df.groupby(["age", "sex"]).agg(
    Sample_Size=("participant_id", "count"),
    Public_Schools=("school_type", lambda x: (x == "public").sum()),
    Private_Schools=("school_type", lambda x: (x == "private").sum()),
    Razavi=("province", lambda x: (x == "Khorasan Razavi").sum()),
    South_Khorasan=("province", lambda x: (x == "South Khorasan").sum()),
    North_Khorasan=("province", lambda x: (x == "North Khorasan").sum())
).reset_index()

out_path = os.path.join(TABLES_DIR, "Table1_Demographic_Stratification.csv")
strat_summary.to_csv(out_path, index=False)
print(f"[SUCCESS] Table 1 generated at: {out_path}")
print(strat_summary.head(6))
