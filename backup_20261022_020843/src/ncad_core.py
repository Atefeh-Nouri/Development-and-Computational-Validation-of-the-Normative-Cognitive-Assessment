"""NCAD core aligned to the manuscript Table 3 Note:
Outcome ~ Age(centered at 15) + Sex(0=Female,1=Male) + (1|school_type).
No Age x Sex interaction in the reported Table 3 model.
Python engine uses Wald analytic CIs; R/lmerTest supplies Satterthwaite df
and non-parametric bootstrap CIs for the publication run.
"""
from __future__ import annotations

import json
import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT_DEFAULT = Path(
    r"D:\Machine learning\Atefeh\NCAD_Conference\"
    r"Development-and-Computational-Validation-of-the-Normative-Cognitive-Assessment"
)


def root() -> Path:
    return Path(os.environ.get("NCAD_ROOT", ROOT_DEFAULT))


def data_path() -> Path:
    return root() / "dataset" / "NCAD_Iranian_Dataset.xlsx"


def tables_dir() -> Path:
    p = root() / "results" / "tables"
    p.mkdir(parents=True, exist_ok=True)
    return p


def figs_dir() -> Path:
    p = root() / "results" / "figures"
    p.mkdir(parents=True, exist_ok=True)
    return p


def manifest_path() -> Path:
    return root() / "results" / "truth_manifest.json"


AGES = [12, 13, 14, 15, 16, 17, 18]

OUTCOME_ALIASES = {
    "corsi_forward_span":        ["corsi_forward_span", "corsi_span"],
    "corsi_backward_span":       ["corsi_backward_span", "backward_span"],
    "corsi_cumulative_errors":   ["corsi_cumulative_errors", "corsi_errors", "corsi_total_errors"],
    "srt_mean_latency":          ["srt_mean_latency", "srt_mean_ms", "srt_mean"],
    "srt_response_time_cv":      ["srt_response_time_cv", "srt_cv", "srt_rt_cv"],
    "crt_mean_latency":          ["crt_mean_latency", "crt_mean_ms", "crt_mean"],
    "crt_response_time_cv":      ["crt_response_time_cv", "crt_cv", "crt_rt_cv"],
    "stop_signal_rt":            ["stop_signal_rt", "ssrt_ms", "ssrt"],
    "rvp_sensitivity_dprime":    ["rvp_sensitivity_dprime", "sdt_dprime", "rvp_dprime", "dprime"],
    "rvp_decision_criterion_c":  ["rvp_decision_criterion_c", "rvp_criterion", "rvp_c", "criterion_c"],
    "processing_speed_index":    ["processing_speed_index", "processing_speed", "psi"],
}

CORE6 = [
    "corsi_forward_span",
    "srt_mean_latency",
    "crt_mean_latency",
    "stop_signal_rt",
    "rvp_sensitivity_dprime",
    "processing_speed_index",
]


def load() -> pd.DataFrame:
    df = pd.read_excel(data_path(), sheet_name="Simulated Data", skiprows=1)
    df["age_band"] = np.floor(df["age"].astype(float)).astype(int)
    return df


def detect_outcomes(df: pd.DataFrame) -> dict:
    cols = set(map(str, df.columns))
    found = {}
    for label, cands in OUTCOME_ALIASES.items():
        for c in cands:
            if c in cols:
                found[label] = c
                break

    missing_core = [lbl for lbl in CORE6 if lbl not in found]
    if missing_core:
        raise RuntimeError(
            f"Core outcomes absent from .xlsx: {missing_core}. "
            f"Columns present: {sorted(cols)}"
        )
    return found


def cluster_column(df: pd.DataFrame) -> str | None:
    """
    The manuscript Table 3 Note explicitly uses (1|school_type).
    Therefore the canonical Python grouping is school_type, not school_id.
    """
    if "school_type" in df.columns:
        return "school_type"

    for c in ("school_id", "school", "cluster", "school_cluster", "site_id"):
        if c in df.columns and df[c].nunique() >= 2:
            return c

    return None


def fmt(v) -> str:
    return f"{float(v):.2f}"


def cell(m, s) -> str:
    return f"{fmt(m)} ± {fmt(s)}"


def table1_grid(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    for a in AGES:
        d = df[df.age_band == a]
        sx = d.sex.str.lower().value_counts()
        st = d.school_type.str.lower().value_counts()
        pv = d.province.value_counts()

        rows.append(
            dict(
                age_cohort=f"{a}.0-{a}.9",
                total=len(d),
                female=int(sx.get("female", 0)),
                male=int(sx.get("male", 0)),
                public=int(st.get("public", 0)),
                private=int(st.get("private", 0)),
                razavi=int(pv.get("Khorasan Razavi", 0)),
                south_khorasan=int(pv.get("South Khorasan", 0)),
                north_khorasan=int(pv.get("North Khorasan", 0)),
            )
        )

    tot = df.sex.str.lower().value_counts()
    stt = df.school_type.str.lower().value_counts()
    pvt = df.province.value_counts()

    rows.append(
        dict(
            age_cohort="TOTAL",
            total=len(df),
            female=int(tot.get("female", 0)),
            male=int(tot.get("male", 0)),
            public=int(stt.get("public", 0)),
            private=int(stt.get("private", 0)),
            razavi=int(pvt.get("Khorasan Razavi", 0)),
            south_khorasan=int(pvt.get("South Khorasan", 0)),
            north_khorasan=int(pvt.get("North Khorasan", 0)),
        )
    )

    return pd.DataFrame(rows)


def table2_grid(df: pd.DataFrame, outcomes: dict) -> tuple[pd.DataFrame, dict]:
    raw = {}

    for label, col in outcomes.items():
        g = df.groupby("age_band")[col]
        means = g.mean().reindex(AGES).values
        sds = g.std().reindex(AGES).values
        raw[label] = (means.tolist(), sds.tolist())

    out = pd.DataFrame(
        [
            {
                "age_cohort": f"{a}.0-{a}.9",
                **{lbl: cell(raw[lbl][0][i], raw[lbl][1][i]) for lbl in outcomes},
            }
            for i, a in enumerate(AGES)
        ]
    )

    return out, raw


def _var_parts(res, metric_col: str, df: pd.DataFrame) -> dict:
    try:
        X = res.model.exog
        names = list(res.model.exog_names)
        beta = res.params.reindex(names).values
        var_fixed = float(np.var(X @ beta))
    except Exception:
        var_fixed = float("nan")

    try:
        su = float(np.asarray(res.cov_re).ravel()[0])
    except Exception:
        su = float("nan")

    se = float(getattr(res, "scale", float("nan")))
    den = su + se

    icc = su / den if den and den > 0 else float("nan")
    tot = var_fixed + su + se
    r2m = var_fixed / tot if tot and tot > 0 else float("nan")
    r2c = (var_fixed + su) / tot if tot and tot > 0 else float("nan")

    return dict(
        sigma2_school=su,
        sigma2_resid=se,
        icc=icc,
        r2_marginal=r2m,
        r2_conditional=r2c,
        var_fixed=var_fixed,
    )


def fit_lmm(df: pd.DataFrame, col: str, gcol: str):
    """
    Canonical manuscript model:
      Outcome ~ Age_c + Sex_male + (1 | school_type)

    Sex_male:
      0 = Female
      1 = Male
    matching the Table 3 Note: dummy-coded (0=Female, 1=Male).
    """
    w = df.copy()
    w["age_c"] = w["age"].astype(float) - 15.0
    w["sex_male"] = (
        w["sex"].astype(str).str.strip().str.lower().eq("male").astype(float)
    )

    f = f"{col} ~ age_c + sex_male"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = smf.mixedlm(f, data=w, groups=w[gcol]).fit()

    p = res.params
    pv = res.pvalues

    d = dict(
        intercept=float(p.get("Intercept", np.nan)),
        age_beta=float(p.get("age_c", np.nan)),
        age_p=float(pv.get("age_c", np.nan)),
        sex_beta=float(p.get("sex_male", np.nan)),
        sex_p=float(pv.get("sex_male", np.nan)),
        ix_beta=float("nan"),
        ix_p=float("nan"),
    )

    d.update(_var_parts(res, col, w))
    d["converged"] = bool(getattr(res, "converged", True))

    return d, res


def bootstrap_ci(df: pd.DataFrame, col: str, gcol: str, B: int = 0) -> dict:
    """
    Python-side CI is analytic Wald. The manuscript's promised non-parametric
    bootstrap CIs and Satterthwaite df are produced by src/analysis_pipeline.R.
    This function intentionally does not fake 1,000 bootstrap iterations.
    """
    d, res = fit_lmm(df, col, gcol)

    try:
        se_age = float(res.bse.get("age_c", np.nan))
    except Exception:
        se_age = float("nan")

    if np.isfinite(se_age):
        low = d["age_beta"] - 1.96 * se_age
        high = d["age_beta"] + 1.96 * se_age
    else:
        low = high = float("nan")

    return {
        "age_beta_low": low,
        "age_beta_high": high,
        "ci_method": "wald_analytic_python",
        "bootstrap_iterations": 0,
    }


def build_table3(df: pd.DataFrame, outcomes: dict, gcol: str, B: int = 0) -> pd.DataFrame:
    rows = []

    for label, col in outcomes.items():
        d, _ = fit_lmm(df, col, gcol)
        ci = bootstrap_ci(df, col, gcol, B=B)

        rows.append(
            {
                "Cognitive_Domain": label,
                "Intercept_Beta0": round(d["intercept"], 3),
                "Age_Beta": round(d["age_beta"], 3),
                "Age_P_Value": d["age_p"],
                "Sex_Beta": round(d["sex_beta"], 3),
                "Sex_P_Value": d["sex_p"],
                "AgeXSex_Beta": np.nan,
                "AgeXSex_P_Value": np.nan,
                "Sigma2_School": round(d["sigma2_school"], 4),
                "Sigma2_Resid": round(d["sigma2_resid"], 4),
                "ICC": round(d["icc"], 4),
                "R2_Marginal": round(d["r2_marginal"], 4),
                "R2_Conditional": round(d["r2_conditional"], 4),
                "CI_Low": round(ci["age_beta_low"], 3),
                "CI_High": round(ci["age_beta_high"], 3),
            }
        )

    return pd.DataFrame(rows)


def write_manifest(
    df: pd.DataFrame,
    outcomes: dict,
    gcol: str,
    t1: pd.DataFrame,
    t2raw: dict,
    t3: pd.DataFrame,
    B: int,
) -> dict:
    clus = cluster_column(df)

    man = {
        "engine": "python/statsmodels (Wald analytic CIs; Satterthwaite/bootstrap via R script)",
        "p_method": "wald_normal_approx",
        "ci_method": "wald_analytic_python",
        "satterthwaite_available": False,
        "grouping_column": gcol,
        "grouping_levels": int(df[gcol].nunique()),
        "cluster_supported": clus is not None and df[clus].nunique() >= 5,
        "cluster_column": clus,
        "centered_age_at": 15.0,
        "sex_reference": "female",
        "sex_coding": "0=Female,1=Male",
        "interaction_included": False,
        "modeled_outcomes": sorted(outcomes.keys()),
        "data_outcome_columns": {k: outcomes[k] for k in outcomes},
        "table1_per_age": {
            int(r["age_cohort"].split(".")[0]): int(r["total"])
            for _, r in t1.iterrows()
            if r["age_cohort"] != "TOTAL"
        },
        "table2_raw": t2raw,
        "table3": t3.to_dict(orient="records"),
        "interaction_any_significant": False,
        "bootstrap_iterations": 0,
    }

    manifest_path().write_text(
        json.dumps(man, indent=2, default=str),
        encoding="utf-8",
    )

    return man
