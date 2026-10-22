"""Register R/lmerTest output in the truth manifest."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ncad_core as C
import pandas as pd


def main(nsim: int = 1000) -> None:
    rp = C.tables_dir() / "table3_R_satterthwaite.csv"
    if not rp.exists():
        sys.exit("[04] table3_R_satterthwaite.csv missing - run analysis_pipeline.R first")

    rt = pd.read_csv(rp).set_index("outcome")
    py = pd.read_csv(C.tables_dir() / "table3_truth.csv").set_index("Cognitive_Domain")

    common = [x for x in rt.index if x in py.index]
    worst = max(
        abs(float(rt.loc[x, "age_beta"]) - float(py.loc[x, "Age_Beta"]))
        for x in common
    )

    mp = C.manifest_path()
    man = json.loads(mp.read_text(encoding="utf-8"))

    if "table1_per_age" in man:
        man["table1_per_age"] = {int(k): int(v) for k, v in man["table1_per_age"].items()}

    man["satterthwaite_available"] = True
    man["p_method"] = "satterthwaite_R_lmerTest"
    man["ci_method"] = "nonparametric_bootstrap_R_bootMer"
    man["bootstrap_iterations"] = int(nsim)
    man["r_engine"] = {
        "script": "src/analysis_pipeline.R",
        "packages": ["readxl", "lme4", "lmerTest", "dplyr", "tibble", "MuMIn"],
        "model": "Outcome ~ Age_c + Sex_male + (1|school_type)",
        "bootstrap_iterations": int(nsim),
        "max_abs_age_beta_parity_vs_python": round(float(worst), 6),
    }

    mp.write_text(json.dumps(man, indent=2, default=str), encoding="utf-8")

    print(f"[04] R engine registered; cross-language age-beta parity max|diff| = {worst:.6f}")


if __name__ == "__main__":
    nsim = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    main(nsim=nsim)
