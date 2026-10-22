"""Regenerate the data-derived TRUTH and write the manuscript edit checklist.
Run FIRST. Makes code_audit green; produces the exact numbers doc_audit needs."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ncad_core as C
import manuscript_claims as K

def main(B=200):
    df = C.load(); outcomes = C.detect_outcomes(df); gcol = C.cluster_column(df) or "school_type"
    t1 = C.table1_grid(df)
    t2, t2raw = C.table2_grid(df, outcomes)
    t3 = C.build_table3(df, outcomes, gcol, B=B)
    t1.to_csv(C.tables_dir()/"table1_truth.csv", index=False)
    t2.to_csv(C.tables_dir()/"table2_truth.csv", index=False)
    t3.to_csv(C.tables_dir()/"table3_truth.csv", index=False)
    man = C.write_manifest(df, outcomes, gcol, t1, t2raw, t3, B)
    write_checklist(man, t3)
    print(f"[00] truth written. grouping='{gcol}' levels={man['grouping_levels']} "
          f"cluster_supported={man['cluster_supported']} modeled={len(outcomes)} outcomes boot B={B}")
    print(f"[00] manifest -> {C.manifest_path()}")
    print(f"[00] checklist -> {C.root()/'results'/'manuscript_edit_checklist.md'}")

def _row(head, *rest): return f"| {head} | " + " | ".join(f"`{r}`" for r in rest) + " |"

def write_checklist(man, t3):
    L = ["# Manuscript Edit Checklist (auto-generated from the shipped dataset)",
         "",
         "Replace the LEFT value (current `.docx`) with the RIGHT value (data-derived truth).",
         "After editing, `doc_audit` turns green. Point estimates are engine-independent;",
         "p-values here are Wald/normal-approx (statsmodels) — see item 9 for Satterthwaite.", ""]
    # 1 Table 1
    L += ["## 1. Table 1 — per-cohort N (and replace the whole grid with `results/tables/table1_truth.csv`)",
          "| Age | Paper | Data |", "|---|---|---|"]
    for a in C.AGES:
        L.append(_row(str(a), K.TABLE1_PER_AGE[a], man["table1_per_age"][a]))
    # 2 Table 2
    L += ["", "## 2. Table 2 — descriptive means (replace with `table2_truth.csv`, 2-decimal APA)",
          "| Outcome | Paper @12→@18 | Data @12→@18 |", "|---|---|---|"]
    for lbl in C.CORE6:
        if lbl in man["table2_raw"]:
            new = [round(x,2) for x in man["table2_raw"][lbl][0]]
            L.append(_row(lbl, K.TABLE2.get(lbl), new))
    # 3 Table 3
    L += ["", "## 3. Table 3 — LMM estimates (replace with `table3_truth.csv`)",
          "| Outcome | Field | Paper | Data |", "|---|---|---|---|"]
    t3d = {r["Cognitive_Domain"]: r for r in man["table3"]}
    fields = [("Intercept_Beta0",0),("Age_Beta",1),("Sex_Beta",2),("AgeXSex_Beta",3),
              ("Sigma2_School",4),("Sigma2_Resid",5),("ICC",6),("R2_Marginal",7),("R2_Conditional",8)]
    for lbl in C.CORE6:
        if lbl in t3d:
            for fn, idx in fields:
                L.append(_row(lbl, fn, f"{K.TABLE3[lbl][idx]}", f"{t3d[lbl][fn]}"))
    # 4-9 narrative / structural
    c12 = round(man["table2_raw"]["corsi_forward_span"][0][0],2)
    c18 = round(man["table2_raw"]["corsi_forward_span"][0][-1],2)
    ssrt_slope = round(t3d["stop_signal_rt"]["Age_Beta"],3) if "stop_signal_rt" in t3d else "n/a"
    ix_sig = man["interaction_any_significant"]
    L += ["", "## 4. §7.1 narrative", _row("Corsi@12", K.SEC71_CORSI_12, c12),
          _row("Corsi@18", K.SEC71_CORSI_18, c18),
          "", "## 5. Abstract — Age×Sex interaction",
          f"- Paper asserts **significant**; data gives **{'significant' if ix_sig else 'NON-significant'}**.",
          f"- Reword the Abstract to: *'…marked by {'significant' if ix_sig else 'non-significant (parallel)'} "
          f"age-by-sex effects…'* to match §6.4.2 and Table 3.",
          "", "## 6. 40-school-cluster / ICC / conditional-R² claims",
          f"- Data grouping = `{man['grouping_column']}` ({man['grouping_levels']} levels); "
          f"`cluster_supported={man['cluster_supported']}`.",
          "- EITHER regenerate the `.xlsx` with a real 40-level `school_id` column, "
          "OR qualify §5.1/§6.4.3 to *'school_type as a 2-level institutional proxy; "
          "full 40-cluster ICC deferred to the live cohort'*.",
          "", "## 7. Battery scope",
          f"- Paper models {K.CLAIMS_BATTERY_N} outcomes; data contains columns for "
          f"{len(man['modeled_outcomes'])}: {man['modeled_outcomes']}.",
          "- Trim §5.2/§6.2 to the outcomes actually present, OR add the missing columns to the generator.",
          "", "## 8. Infographic SSRT slope (single value)",
          _row("SSRT age β", f"text {K.INFOGRAPHIC_SSRT_TEXT} / bar {K.INFOGRAPHIC_SSRT_BAR}", ssrt_slope),
          "", "## 9. Inference method (Satterthwaite / REML / lme4)",
          f"- Python engine p-method = `{man['p_method']}` (no Satterthwaite).",
          "- To honour §5.3 verbatim, generate Table 3 from the promised R/`lme4`+`lmerTest` script "
          "on this same `.xlsx` (point estimates will match; only df/p differ), "
          "OR reword §5.3 to *'Wald z-tests via statsmodels; Satterthwaite df in the R replication script'*.",
          ""]
    (C.root()/"results"/"manuscript_edit_checklist.md").write_text("\n".join(L), encoding="utf-8")

if __name__ == "__main__":
    B = int(sys.argv[sys.argv.index("--boot")+1]) if "--boot" in sys.argv else 200
    main(B=B)
