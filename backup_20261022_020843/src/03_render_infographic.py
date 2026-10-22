"""Render results/figures/GitHub_Hero.png from results/tables/table3_truth.csv and
sync src/manuscript_claims.py INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION to the single
canonical SSRT age-beta the image displays. Closes d08 by construction (image =
tables = code), not by editing a number to match a stale picture."""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncad_core as C
import pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, seaborn as sns

t3 = pd.read_csv(C.tables_dir()/"table3_truth.csv").set_index("Cognitive_Domain")
s  = round(float(t3.loc["stop_signal_rt","Age_Beta"]), 3)          # canonical SSRT beta

# ---- hero figure: 6 core trajectories (sex-stratified) + canonical-slope banner ----
df = C.load(); outs = C.detect_outcomes(df)
core = ["corsi_forward_span","srt_mean_latency","crt_mean_latency",
        "stop_signal_rt","rvp_sensitivity_dprime","processing_speed_index"]
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(15, 8))
for ax, lbl in zip(axes.ravel(), core):
    sns.lineplot(data=df, x="age_band", y=outs[lbl], hue="sex", marker="o", ax=ax,
                 palette={"female":"#2b5c8f","male":"#d95f02"})
    ax.set_title(lbl.replace("_"," ").title(), fontweight="bold")
    ax.set_xlabel("Age (Years)"); ax.set_ylabel("Score / Latency (ms)")
banner = "  |  ".join(f"{l.split('_')[0].upper()} β_age={round(float(t3.loc[l,'Age_Beta']),3):+}"
                      for l in core)
fig.suptitle(f"NCAD developmental trajectories  ·  SSRT age-β = {s:+} (single canonical value)\n{banner}",
             fontsize=10, y=1.0)
plt.tight_layout()
fp = C.figs_dir()/"GitHub_Hero.png"; plt.savefig(fp, dpi=300, bbox_inches="tight")
print(f"[03] hero image -> {fp}   (SSRT beta embedded = {s:+})")

# ---- sync the manuscript mirror to what the regenerated image now shows ----
mp = Path(__file__).resolve().parent/"manuscript_claims.py"
txt = mp.read_text(encoding="utf-8")
pat = r"INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION\s*=\s*\([^)]*\)[^\n]*"
new, n = re.subn(pat, f"INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION = ({s}, {s})  # regenerated from table3_truth.csv", txt)
assert n == 1, f"[03] ABORT: mirror INFOGRAPHIC anchor matched {n}x"
mp.write_text(new, encoding="utf-8")
print(f"[03] mirror INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION synced to ({s}, {s})")
