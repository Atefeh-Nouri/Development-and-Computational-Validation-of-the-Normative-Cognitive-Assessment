"""Dump every data-dependent number the manuscript must contain, in paste-ready form,
straight from the R (Satterthwaite) output + the truth tables. Closes the document<->data
loop WITHOUT tolerances: paste these into Word, then re-transcribe manuscript_claims.py
from the updated Word, then re-run the audit."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncad_core as C
import pandas as pd, numpy as np

r = pd.read_csv(C.tables_dir()/"table3_R_satterthwaite.csv").set_index("outcome")
t2 = pd.read_csv(C.tables_dir()/"table2_truth.csv").set_index("age_cohort")
t1 = pd.read_csv(C.tables_dir()/"table1_truth.csv")
core = C.CORE6

print("="*78); print("TABLE 1  (paste into Word Table 1)"); print("="*78)
print(t1.to_string(index=False))

print("\n"+"="*78); print("TABLE 2  M ± SD  (paste into Word Table 2)"); print("="*78)
print(t2[core].to_string())

print("\n"+"="*78); print("TABLE 3  R/lmerTest Satterthwaite (paste into Word Table 3)"); print("="*78)
cols = ["intercept","age_beta","age_df","age_p","sex_beta","sex_df","sex_p",
        "s2_school","s2_resid","icc","r2_marginal","r2_conditional","ci_low","ci_high"]
print(r.loc[core, cols].round(4).to_string())

print("\n"+"="*78); print("PROSE VALUES TO SYNC INTO THE .docx"); print("="*78)
rc = r.loc[core,"r2_conditional"]; rm = r.loc[core,"r2_marginal"]
print(f"Conditional R2 realized band : {rc.min():.3f} to {rc.max():.3f}   (was 0.328-0.448 in prose)")
print(f"Marginal    R2 realized band : {rm.min():.3f} to {rm.max():.3f}")
print(f"ICC realized band (core6)    : {r.loc[core,'icc'].min():.4f} to {r.loc[core,'icc'].max():.4f}")
ssrt = float(r.loc['stop_signal_rt','age_beta'])
print(f"Infographic / Abstract SSRT age-beta : {ssrt:+.3f}   (single canonical value)")
c12 = float(t2.loc['12.0-12.9','corsi_forward_span'].split('±')[0])
c18 = float(t2.loc['18.0-18.9','corsi_forward_span'].split('±')[0])
print(f"Sec 7.1 Corsi endpoints      : {c12:.2f} -> {c18:.2f}")
print("\nNOTE: the 3 supplementary outcomes (corsi_backward_span, crt_response_time_cv,")
print("rvp_decision_criterion_c) fit singular (ICC=0). They are NOT in Table 3's core six;")
print("if any prose quotes their ICC/R2 it must read ~0 / 'no detectable school-type clustering'.")
