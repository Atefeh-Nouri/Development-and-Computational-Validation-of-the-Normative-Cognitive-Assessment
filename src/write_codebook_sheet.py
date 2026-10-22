"""Embed the standardized Data Dictionary (Codebook) as Sheet 2 of the dataset .xlsx,
fulfilling the Open Data Badge sentence, and mirror it to docs/. Idempotent."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncad_core as C
import pandas as pd, numpy as np

XL = C.data_path()
df = pd.read_excel(XL, sheet_name="Simulated Data", skiprows=1)
title = ("NCAD Iranian Synthetic Benchmark Dataset - calibrated to manuscript Tables 1-3 "
         "(src/generate_synthetic_data.py, SEED=20261015)")

UNIT = {"srt_mean_latency":"ms","crt_mean_latency":"ms","stop_signal_rt":"ms",
        "srt_response_time_cv":"ratio (SD/mean)","crt_response_time_cv":"ratio (SD/mean)",
        "rvp_sensitivity_dprime":"d-prime (unitless)","rvp_decision_criterion_c":"c (unitless)",
        "processing_speed_index":"index points"}
NOTE = {
 "sex":"dummy-coded in models: 0=Female, 1=Male",
 "school_type":"institutional clustering variable; random intercept (1|school_type); 2 levels (Public/Private)",
 "rvp_sensitivity_dprime":"log-linear SDT correction applied upstream (Hautus 1995; Stanislaw & Todorov 1999): +0.5 hits/FA, +1.0 trials",
 "rvp_decision_criterion_c":"log-linear SDT correction applied upstream",
}
rows=[]
for c in df.columns:
    if c in ("participant_id","first_name","last_name"):
        lab,unit,note = c.replace("_"," ").title(), "identifier", "pseudonymous / decorative"
    elif c=="age": lab,unit,note = "Age","years","12-18"
    elif c=="age_band": lab,unit,note = "Age band","years (floor)","derived = floor(age)"
    elif c=="grade": lab,unit,note = "School grade","grade","age-5 capped at 12"
    elif c=="province": lab,unit,note = "Province","category","Khorasan Razavi / South / North"
    else:
        lab = c.replace("_"," ").title(); unit = UNIT.get(c,"score"); note = NOTE.get(c,"outcome")
    lo,hi = (np.nan,np.nan)
    if pd.api.types.is_numeric_dtype(df[c]) and c not in ("age","age_band","grade"):
        lo,hi = round(float(df[c].min()),3), round(float(df[c].max()),3)
    rows.append(dict(Variable=c, Label=lab, Unit=unit,
                     Valid_Range=("" if np.isnan(lo) else f"{lo} to {hi}"),
                     Description=note))
cb = pd.DataFrame(rows)
cb.to_csv("docs/data_dictionary.csv", index=False)
Path("docs/CODEBOOK.md").write_text(
 "# NCAD Codebook / Data Dictionary (Sheet 2 of dataset/NCAD_Iranian_Dataset.xlsx)\n\n"
 "**Synthetic, empirically calibrated benchmark (N=2,000); disclosed as synthetic in Sec 6.1.**\n\n"
 + cb.to_markdown(index=False) + "\n", encoding="utf-8")

with pd.ExcelWriter(XL, engine="openpyxl") as xw:
    df.to_excel(xw, sheet_name="Simulated Data", index=False, startrow=1)
    xw.sheets["Simulated Data"]["A1"] = title
    cb.to_excel(xw, sheet_name="Codebook", index=False)
print(f"[codebook] Sheet 2 'Codebook' embedded in {XL.name}; docs/ written ({len(cb)} vars)")
