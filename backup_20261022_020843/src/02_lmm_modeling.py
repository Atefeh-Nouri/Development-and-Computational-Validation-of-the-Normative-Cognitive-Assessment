"""Build Table 2, Table 3, and developmental trajectory figure."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ncad_core as C

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns


def main() -> None:
    df = C.load()
    outcomes = C.detect_outcomes(df)
    gcol = C.cluster_column(df) or "school_type"

    t2, _ = C.table2_grid(df, outcomes)
    t3 = C.build_table3(df, outcomes, gcol, B=0)

    t2.to_csv(C.tables_dir() / "table2_truth.csv", index=False)
    t2.to_csv(C.tables_dir() / "Table2_Descriptive_Psychometrics.csv", index=False)

    t3.to_csv(C.tables_dir() / "table3_truth.csv", index=False)
    t3.to_csv(C.tables_dir() / "LMM_Fixed_Effects_Summary.csv", index=False)

    print(f"[02] grouping='{gcol}' levels={df[gcol].nunique()}")
    print(
        t3[
            [
                "Cognitive_Domain",
                "Intercept_Beta0",
                "Age_Beta",
                "Sex_Beta",
                "ICC",
                "R2_Conditional",
            ]
        ].to_string(index=False)
    )

    # Figure: sex-stratified trajectories for the six core outcomes.
    core = C.CORE6
    n = len(core)
    nrow = 2
    ncol = 3

    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(nrow, ncol, figsize=(15, 8))

    for i, lbl in enumerate(core):
        ax = axes[i // ncol][i % ncol]
        col = outcomes[lbl]

        sns.lineplot(
            data=df,
            x="age_band",
            y=col,
            hue="sex",
            marker="o",
            ax=ax,
            palette={"female": "#2b5c8f", "male": "#d95f02"},
        )

        ax.set_title(lbl.replace("_", " ").title(), fontweight="bold")
        ax.set_xlabel("Age (Years)")
        ax.set_ylabel("Score / Latency")

    for j in range(n, nrow * ncol):
        axes[j // ncol][j % ncol].axis("off")

    plt.tight_layout()
    fp = C.figs_dir() / "Developmental_Trajectories.png"
    plt.savefig(fp, dpi=300)
    print(f"[02] figure -> {fp}")


if __name__ == "__main__":
    main()
