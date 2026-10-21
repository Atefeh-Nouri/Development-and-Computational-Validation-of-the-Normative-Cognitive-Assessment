import os
import warnings
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

ROOT_DIR = r"D:\Machine learning\Atefeh\NCAD_Conference\Development-and-Computational-Validation-of-the-Normative-Cognitive-Assessment"
DATA_PATH = os.path.join(ROOT_DIR, "dataset", "NCAD_Iranian_Dataset.xlsx")
TABLES_DIR = os.path.join(ROOT_DIR, "results", "tables")
FIG_DIR = os.path.join(ROOT_DIR, "results", "figures")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_excel(DATA_PATH, sheet_name="Simulated Data", skiprows=1)

metrics = [
    "corsi_span",
    "srt_mean_ms",
    "crt_mean_ms",
    "ssrt_ms",
    "sdt_dprime",
    "processing_speed"
]

# 1. Generate Table 2: Descriptive Statistics
means = df.groupby("age")[metrics].mean().round(2)
sds = df.groupby("age")[metrics].std().round(2)

table2 = pd.DataFrame()
for col in metrics:
    table2[f"{col}_Mean_SD"] = means[col].astype(str) + " ± " + sds[col].astype(str)

table2.reset_index(inplace=True)
table2_path = os.path.join(TABLES_DIR, "Table2_Descriptive_Psychometrics.csv")
table2.to_csv(table2_path, index=False)
print(f"[SUCCESS] Table 2 saved to: {table2_path}")

# 2. Fit Linear Mixed-Effects Models (LMM)
print("\nFitting Linear Mixed-Effects Models (Outcome ~ Age + Sex + (1|school_type))...")
lmm_results = []
for m in metrics:
    model = smf.mixedlm(f"{m} ~ age + C(sex)", data=df, groups=df["school_type"])
    res = model.fit()
    lmm_results.append({
        "Cognitive_Domain": m,
        "Age_Beta": round(res.params["age"], 3),
        "Age_P_Value": "< 0.001" if res.pvalues["age"] < 0.001 else round(res.pvalues["age"], 4),
        "Sex_Male_Beta": round(res.params["C(sex)[T.male]"], 3),
        "Sex_P_Value": round(res.pvalues["C(sex)[T.male]"], 4)
    })

lmm_df = pd.DataFrame(lmm_results)
lmm_path = os.path.join(TABLES_DIR, "LMM_Fixed_Effects_Summary.csv")
lmm_df.to_csv(lmm_path, index=False)
print(f"[SUCCESS] LMM fixed effects summary saved to: {lmm_path}")
print(lmm_df)

# 3. Plot Developmental Trajectories
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
axes = axes.flatten()

titles = [
    "Corsi Span Capacity", "Simple Reaction Time (ms)", "Choice Reaction Time (ms)",
    "Stop-Signal Reaction Time (ms)", "Signal Detection d' (Sensitivity)", "Processing Speed Score"
]

for i, m in enumerate(metrics):
    sns.lineplot(
        data=df, x="age", y=m, hue="sex", marker="o", ax=axes[i],
        palette={"female": "#2b5c8f", "male": "#d95f02"}
    )
    axes[i].set_title(titles[i], fontsize=12, fontweight="bold")
    axes[i].set_xlabel("Age (Years)")
    axes[i].set_ylabel("Score / Latency")

plt.tight_layout()
fig_path = os.path.join(FIG_DIR, "Developmental_Trajectories.png")
plt.savefig(fig_path, dpi=300)
print(f"[SUCCESS] High-resolution trajectory plot saved to: {fig_path}")
