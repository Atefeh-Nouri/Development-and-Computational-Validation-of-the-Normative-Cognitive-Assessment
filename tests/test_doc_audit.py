"""Document audit: manuscript mirror vs data-derived truth."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

try:
    import numpy as np
    import pandas as pd
except Exception:
    pd = None
    np = None

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ncad_core as C
import manuscript_claims as K


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


@pytest.fixture(scope="session")
def man():
    p = C.manifest_path()
    if not p.exists():
        pytest.fail("truth manifest missing -> run: python src/00_regenerate_truth.py")

    m = json.loads(p.read_text(encoding="utf-8"))

    if "table1_per_age" in m:
        m["table1_per_age"] = {int(k): int(v) for k, v in m["table1_per_age"].items()}

    return m


@pytest.fixture(scope="session")
def oracle():
    """Python no-interaction oracle matching Table 3 Note."""
    df = C.load()
    outs = C.detect_outcomes(df)
    gcol = C.cluster_column(df) or "school_type"

    return {
        lbl: C.fit_lmm(df, col, gcol)[0]
        for lbl, col in outs.items()
    }


@pytest.fixture(scope="session")
def r_table():
    p = C.tables_dir() / "table3_R_satterthwaite.csv"
    if not p.exists():
        return None
    return pd.read_csv(p).set_index("outcome")


@pytest.mark.doc_audit
def test_d01_table1_per_age(man):
    data = man["table1_per_age"]
    fails = []

    for a, kb in K.TABLE1_PER_AGE.items():
        if kb is None:
            continue
        if int(data.get(a, -1)) != int(kb):
            fails.append(f"age {a}: paper {kb} vs data {data.get(a)}")

    assert not fails, (
        "Table 1 per-cohort N mismatch: " + "; ".join(fails) +
        " -> replace Table 1 with results/tables/table1_truth.csv"
    )


@pytest.mark.doc_audit
def test_d02_table2_grid(man):
    if not K.TABLE2_GRID_AVAILABLE:
        pytest.skip("Table 2 numeric grid unavailable")

    tol = 0.02
    fails = []

    for lbl in C.CORE6:
        data = [round(x, 2) for x in man["table2_raw"][lbl][0]]
        for i, (d, pv) in enumerate(zip(data, K.TABLE2[lbl])):
            if abs(d - pv) > tol:
                fails.append(f"{lbl}@{C.AGES[i]}: paper {pv} vs data {d}")

    assert not fails, "Table 2 mismatch: " + "; ".join(fails)


@pytest.mark.doc_audit
@pytest.mark.parametrize("o", C.CORE6)
def test_d03_table3_printed_fields(o, man, oracle, r_table):
    kb = K.TABLE3_PRINTED.get(o)
    if kb is None:
        pytest.skip(f"{o} row not printed in manuscript mirror")

    fails = []

    if r_table is not None and o in r_table.index:
        row = r_table.loc[o]
        age_beta = _num(row["age_beta"])
        sex_beta = _num(row["sex_beta"])
        sex_p = _num(row["sex_p"])
        age_p = _num(row["age_p"])
        source = "R/lmerTest"
    else:
        row = oracle[o]
        age_beta = _num(row["age_beta"])
        sex_beta = _num(row["sex_beta"])
        sex_p = _num(row["sex_p"])
        age_p = _num(row["age_p"])
        source = "Python/Wald"

    paper_age = _num(kb["age_beta"])
    paper_sex = _num(kb["sex_beta"])
    paper_sex_p = _num(kb.get("sex_p"))

    if paper_age is not None and age_beta is not None:
        tol_age = max(0.10, 0.01 * abs(paper_age))
        if abs(paper_age - age_beta) > tol_age:
            fails.append(
                f"Age_Beta paper {paper_age} vs {source} {round(age_beta, 3)}"
            )

    if paper_sex is not None and sex_beta is not None:
        tol_sex = max(0.10, 0.05 * abs(paper_sex))
        if abs(abs(paper_sex) - abs(sex_beta)) > tol_sex:
            fails.append(
                f"Sex_Beta magnitude paper {abs(paper_sex)} vs {source} {abs(round(sex_beta, 3))}"
            )

    # p-values are engine-dependent. Compare them only when R output exists.
    if r_table is not None:
        if paper_sex_p is not None and sex_p is not None:
            if abs(paper_sex_p - sex_p) > 0.25:
                fails.append(
                    f"Sex_P paper {paper_sex_p} vs R {round(sex_p, 4)}"
                )

        if kb.get("age_p") == "<0.001":
            if age_p is None or age_p >= 0.001:
                fails.append(
                    f"Age_P not <0.001 in R output (got {age_p})"
                )

    assert not fails, f"Table 3 '{o}' mismatch: " + " | ".join(fails)

@pytest.mark.doc_audit
def test_d04_sec71_corsi_range(man):
    raw = man["table2_raw"]["corsi_forward_span"][0]
    c12 = round(raw[0], 2)
    c18 = round(raw[-1], 2)

    rng = K.SEC71_CORSI_RANGES_IN_DOC
    match = [r for r in rng if abs(r[0] - c12) <= 0.02 and abs(r[1] - c18) <= 0.02]
    stale = [r for r in rng if r not in match]

    assert match, f"no §7.1 Corsi range {rng} matches data {c12}->{c18}"
    assert not stale, (
        f"§7.1 contains conflicting Corsi ranges {rng}; data supports only {match}. "
        f"Delete/rewrite stale sentence(s) {stale} in the .docx."
    )


@pytest.mark.doc_audit
def test_d05_interaction_prose_vs_table(man):
    note_has_interaction = bool(K.TABLE3_NOTE.get("interaction_term_present"))
    prose_has_interaction = bool(K.PROSE_DISCUSSES_AGE_BY_SEX_INTERACTION)

    if (not note_has_interaction) and prose_has_interaction:
        pytest.fail(
            "Internal inconsistency: prose discusses Age x Sex interaction, "
            "but Table 3 Note specifies no interaction. Either add the interaction "
            "to Table 3 and regenerate, or remove interaction claims from prose."
        )

    assert True


@pytest.mark.doc_audit
def test_d06_clusters_and_variance(man):
    probs = []

    if K.CLAIMS_40_SCHOOL_CLUSTERS and not man.get("cluster_supported", False):
        probs.append(
            f"Manuscript claims 40-school clustering, but shipped data grouping is "
            f"'{man.get('grouping_column')}' with {man.get('grouping_levels')} levels."
        )

    promised_var = bool(
        K.PROSE_CLAIMS_R2_M
        or K.PROSE_CLAIMS_R2_C
        or K.PROSE_CLAIMS_SCHOOL_RANDOM_INTERCEPTS
    )

    if promised_var and not K.TABLE3_PRINTS_VARIANCE_COMPONENTS:
        probs.append(
            "Prose promises ICC / sigma2 / R2 diagnostics, but Table 3 mirror says "
            "variance components are not printed."
        )

    r2c = [_num(r.get("R2_Conditional")) for r in man.get("table3", [])]
    r2c = [v for v in r2c if v is not None]

    lo, hi = K.PROSE_CLAIMS_R2_C
    tol = 0.005  # tight: the prose band must equal the realized data span

    if r2c:
        dlo, dhi = min(r2c), max(r2c)
        if dlo < lo - tol or dhi > hi + tol or dlo > lo + tol or dhi < hi - tol:
            probs.append(
                f"TWO-SIDED Conditional R2 mismatch: prose {K.PROSE_CLAIMS_R2_C} "
                f"vs realized [{dlo:.3f}, {dhi:.3f}] (tol {tol}). "
                f"Edit the .docx sentence to the realized span, then sync the mirror."
            )

    # Marginal R2 was never numerically checked; check it two-sided too.
    r2m = [_num(r.get("R2_Marginal")) for r in man.get("table3", [])]
    r2m = [v for v in r2m if v is not None]
    if r2m and getattr(K, "PROSE_CLAIMS_R2_M", None):
        mlo, mhi = K.PROSE_CLAIMS_R2_M
        dmlo, dmhi = min(r2m), max(r2m)
        if dmlo < mlo - tol or dmhi > mhi + tol or dmlo > mlo + tol or dmhi < mhi - tol:
            probs.append(
                f"TWO-SIDED Marginal R2 mismatch: prose {K.PROSE_CLAIMS_R2_M} "
                f"vs realized [{dmlo:.3f}, {dmhi:.3f}] (tol {tol})."
            )

    assert not probs, "Variance / clustering mismatch:\n - " + "\n - ".join(probs)


@pytest.mark.doc_audit
def test_d07_named_battery(man):
    present = set(man.get("modeled_outcomes", []))
    missing = sorted(K.NAMED_BATTERY_OUTCOMES - present)

    assert not missing, (
        f"manuscript names outcomes absent from shipped data: {missing}. "
        f"Data has {len(present)} columns: {sorted(present)}."
    )


@pytest.mark.doc_audit
def test_d08_infographic_ssrt(man):
    t3 = {r["Cognitive_Domain"]: r for r in man.get("table3", [])}
    s = round(float(t3["stop_signal_rt"]["Age_Beta"]), 3)

    a, b = K.INFOGRAPHIC_SSRT_VALUES_IN_CIRCULATION

    assert abs(a - s) <= 0.05 and abs(b - s) <= 0.05, (
        f"Infographic SSRT beta is {a}/{b}; data beta is {s}. "
        f"Re-render GitHub_Hero.png from table3_truth.csv and use {s} everywhere."
    )


@pytest.mark.doc_audit
def test_d09_method_parity(man, r_table):
    probs = []

    if K.METHOD_SATTERTHWAITE_PROMISED and not man.get("satterthwaite_available", False):
        probs.append(
            f"Manuscript promises Satterthwaite df via {K.METHOD_ENGINE_PROMISED}, "
            f"but Python manifest uses {man.get('p_method')}. "
            "Run: Rscript src/analysis_pipeline.R . 1000 "
            "then python src/04_register_r_engine.py 1000."
        )

    if K.METHOD_BOOTSTRAP_1000_PROMISED and int(man.get("bootstrap_iterations", 0)) < 1000:
        probs.append(
            f"Manuscript promises 1,000-iteration bootstrap CIs, but manifest has "
            f"B={man.get('bootstrap_iterations')}. Run the R script with nsim=1000."
        )

    if r_table is None and K.METHOD_SATTERTHWAITE_PROMISED:
        probs.append("R output table3_R_satterthwaite.csv not found.")

    assert not probs, "Method-claim mismatch:\n - " + "\n - ".join(probs)
