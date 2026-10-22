"""Code audit: pipeline must reproduce the data-derived truth manifest."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

try:
    import numpy as np
    import pandas as pd
    OK = True
except Exception:
    OK = False

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import ncad_core as C


@pytest.fixture(scope="session")
def man():
    p = C.manifest_path()
    if not p.exists():
        pytest.fail("truth manifest missing -> run: python src/00_regenerate_truth.py")

    m = json.loads(p.read_text(encoding="utf-8"))

    # JSON stringifies integer keys; coerce back to int.
    if "table1_per_age" in m:
        m["table1_per_age"] = {int(k): int(v) for k, v in m["table1_per_age"].items()}

    return m


@pytest.fixture(scope="session")
def df():
    return C.load()


@pytest.mark.code_audit
def test_c01_env():
    assert OK, "pandas/numpy missing in venv"


@pytest.mark.code_audit
def test_c02_header_offset():
    d0 = pd.read_excel(C.data_path(), sheet_name="Simulated Data", skiprows=0)
    d1 = pd.read_excel(C.data_path(), sheet_name="Simulated Data", skiprows=1)

    assert "age" in map(str, d1.columns), "skiprows=1 lost the header"
    assert not all(re.fullmatch(r"\d+", str(c)) for c in d1.columns)


@pytest.mark.code_audit
def test_c03_schema_and_core6(df):
    outs = C.detect_outcomes(df)
    assert set(C.CORE6) <= set(outs)


@pytest.mark.code_audit
def test_c04_table1_pipeline_equals_truth(df, man):
    t1 = pd.read_csv(C.tables_dir() / "table1_truth.csv")
    recomp = C.table1_grid(df)

    pa = {
        int(r.age_cohort.split(".")[0]): int(r.total)
        for _, r in recomp.iterrows()
        if r.age_cohort != "TOTAL"
    }

    assert pa == man["table1_per_age"], f"per-age mismatch {pa} vs {man['table1_per_age']}"
    assert len(t1) == 8  # 7 cohorts + TOTAL


@pytest.mark.code_audit
@pytest.mark.parametrize("lbl", C.CORE6)
def test_c05_table2_pipeline_equals_truth(lbl, man):
    t2 = pd.read_csv(C.tables_dir() / "table2_truth.csv").set_index("age_cohort")
    raw = man["table2_raw"][lbl]

    for i, a in enumerate(C.AGES):
        m, s = [float(x) for x in t2.loc[f"{a}.0-{a}.9", lbl].split("±")]
        assert abs(m - raw[0][i]) <= 0.01
        assert abs(s - raw[1][i]) <= 0.01


@pytest.mark.code_audit
def test_c06_modeled_equals_detected(man):
    assert set(man["modeled_outcomes"]) == set(man["data_outcome_columns"].keys())


@pytest.mark.code_audit
def test_c07_spec_implements_table3_note(man):
    assert man["centered_age_at"] == 15.0
    assert man["sex_reference"] == "female"
    assert man["sex_coding"] == "0=Female,1=Male"
    assert man["interaction_included"] is False
    assert man["grouping_column"] == "school_type"
    assert man["grouping_levels"] >= 2


@pytest.mark.code_audit
@pytest.mark.parametrize("lbl", C.CORE6)
def test_c08_table3_pipeline_equals_truth(lbl, man):
    t3 = pd.read_csv(C.tables_dir() / "LMM_Fixed_Effects_Summary.csv").set_index("Cognitive_Domain")
    ref = {r["Cognitive_Domain"]: r for r in man["table3"]}[lbl]

    for f in ["Intercept_Beta0", "Age_Beta", "Sex_Beta"]:
        assert abs(float(t3.loc[lbl, f]) - float(ref[f])) <= 0.01, f

    # No interaction is reported in Table 3 Note.
    assert np.isnan(float(t3.loc[lbl, "AgeXSex_Beta"]))


@pytest.mark.code_audit
def test_c09_table3_has_all_columns():
    cols = set(pd.read_csv(C.tables_dir() / "LMM_Fixed_Effects_Summary.csv").columns)

    req = {
        "Cognitive_Domain",
        "Intercept_Beta0",
        "Age_Beta",
        "Age_P_Value",
        "Sex_Beta",
        "Sex_P_Value",
        "AgeXSex_Beta",
        "AgeXSex_P_Value",
        "Sigma2_School",
        "Sigma2_Resid",
        "ICC",
        "R2_Marginal",
        "R2_Conditional",
        "CI_Low",
        "CI_High",
    }

    assert not (req - cols), f"missing {sorted(req - cols)}"


@pytest.mark.code_audit
def test_c10_apa_two_decimals():
    pat = re.compile(r"^\d+\.\d{2} ± \d+\.\d{2}$")
    t2 = pd.read_csv(C.tables_dir() / "table2_truth.csv")

    bad = [
        (c, v)
        for c in t2.columns
        if c != "age_cohort"
        for v in t2[c]
        if not pat.match(str(v))
    ]

    assert not bad, f"non-2dp cells: {bad[:5]}"
