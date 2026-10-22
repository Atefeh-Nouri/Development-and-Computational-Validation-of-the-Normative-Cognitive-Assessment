"""Regenerate data-derived truth and manuscript edit checklist."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ncad_core as C
import manuscript_claims as K


def _row(*cells) -> str:
    return "| " + " | ".join(f"`{c}`" for c in cells) + " |"


def write_checklist(man: dict) -> None:
    L = []
    L.append("# Manuscript Edit Checklist (auto-generated from the shipped dataset)")
    L.append("")
    L.append("Replace LEFT (current `.docx`) with RIGHT (data-derived truth).")
    L.append("")

    L.append("## 1. Table 1 per-cohort N")
    L.append("| Age | Paper | Data |")
    L.append("|---|---|---|")
    for a in C.AGES:
        paper = getattr(K, "TABLE1_PER_AGE", {}).get(a, "SKIP")
        data = man.get("table1_per_age", {}).get(a, man.get("table1_per_age", {}).get(str(a)))
        L.append(_row(a, paper, data))

    L.append("")
    L.append("## 2. Table 2 core means")
    L.append("| Outcome | Paper @12->@18 | Data @12->@18 |")
    L.append("|---|---|---|")
    for lbl in C.CORE6:
        paper = getattr(K, "TABLE2", {}).get(lbl, "SKIP")
        data = [round(x, 2) for x in man.get("table2_raw", {}).get(lbl, [[], []])[0]]
        L.append(_row(lbl, paper, data))

    L.append("")
    L.append("## 3. Table 3 core LMM fields")
    L.append("| Outcome | Field | Paper | Data |")
    L.append("|---|---|---|---|")
    t3d = {r["Cognitive_Domain"]: r for r in man.get("table3", [])}
    t3p = getattr(K, "TABLE3_PRINTED", {})
    for lbl in C.CORE6:
        if lbl not in t3d:
            continue
        pk = t3p.get(lbl, {})
        for field, pkey in [
            ("Intercept_Beta0", None),
            ("Age_Beta", "age_beta"),
            ("Sex_Beta", "sex_beta"),
            ("Sex_P_Value", "sex_p"),
        ]:
            pv = "SKIP" if pkey is None or pk.get(pkey) is None else pk.get(pkey)
            L.append(_row(lbl, field, pv, t3d[lbl].get(field)))

    L.append("")
    L.append("## 4. Remaining method/clause checks")
    L.append("- See `results/doc_punchlist.md` and the pytest `doc_audit` output.")
    L.append("- `d09` remains red until `src/analysis_pipeline.R` is run and registered.")

    out = C.root() / "results" / "manuscript_edit_checklist.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"[00] checklist -> {out}")


def main() -> None:
    args = sys.argv[1:]

    if "--checklist-only" in args:
        p = C.manifest_path()
        if not p.exists():
            sys.exit("[00] --checklist-only: no manifest on disk; run full mode first.")
        man = json.loads(p.read_text(encoding="utf-8"))
        if "table1_per_age" in man:
            man["table1_per_age"] = {int(k): int(v) for k, v in man["table1_per_age"].items()}
        write_checklist(man)
        return

    df = C.load()
    outcomes = C.detect_outcomes(df)
    gcol = C.cluster_column(df) or "school_type"

    t1 = C.table1_grid(df)
    t2, t2raw = C.table2_grid(df, outcomes)
    t3 = C.build_table3(df, outcomes, gcol, B=0)

    t1.to_csv(C.tables_dir() / "table1_truth.csv", index=False)
    t2.to_csv(C.tables_dir() / "table2_truth.csv", index=False)
    t3.to_csv(C.tables_dir() / "table3_truth.csv", index=False)

    man = C.write_manifest(df, outcomes, gcol, t1, t2raw, t3, B=0)
    write_checklist(man)

    print(
        f"[00] truth written. grouping='{gcol}' "
        f"levels={man['grouping_levels']} "
        f"modeled={len(outcomes)}"
    )
    print(f"[00] manifest -> {C.manifest_path()}")


if __name__ == "__main__":
    main()
