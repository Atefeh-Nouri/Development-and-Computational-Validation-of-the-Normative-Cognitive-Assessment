import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncad_core as C

def main():
    df = C.load()
    t1 = C.table1_grid(df)
    out = C.tables_dir()/"Table1_Demographic_Stratification.csv"
    t1.to_csv(out, index=False)
    print(f"[01] Table 1 (full cross-tab from data) -> {out}")
    print(t1.to_string(index=False))

if __name__ == "__main__":
    main()
