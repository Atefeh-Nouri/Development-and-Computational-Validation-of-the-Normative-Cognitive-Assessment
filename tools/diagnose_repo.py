"""Report every path the README promises and whether it actually exists."""
from pathlib import Path
import sys, shutil, subprocess
ROOT = Path(__file__).resolve().parent.parent

CHECKS = [
    ("dataset/NCAD_Iranian_Dataset.xlsx",         "file", "src/generate_synthetic_data.py"),
    ("src/ncad_core.py",                           "file", "manual"),
    ("src/generate_synthetic_data.py",             "file", "manual"),
    ("src/write_codebook_sheet.py",                "file", "manual (Block 1)"),
    ("src/00_regenerate_truth.py",                 "file", "manual"),
    ("src/01_data_validation.py",                  "file", "manual"),
    ("src/02_lmm_modeling.py",                     "file", "manual"),
    ("src/03_render_infographic.py",               "file", "manual"),
    ("src/04_register_r_engine.py",                "file", "manual"),
    ("src/05_manuscript_number_sheet.py",          "file", "manual"),
    ("src/analysis_pipeline.R",                    "file", "manual"),
    ("src/install_R_packages.R",                   "file", "manual"),
    ("src/dump_R_env.R",                           "file", "manual (Block 1)"),
    ("src/sdt_correct.py",                         "file", "manual (Block 1)"),
    ("run_pipeline.sh",                            "file", "manual (Block 1)"),
    ("requirements.txt",                           "file", "manual"),
    ("requirements.lock.txt",                      "file", "manual (optional)"),
    ("LICENSE",                                    "file", "manual (Block 1)"),
    ("README.md",                                  "file", "manual (Block 1)"),
    (".gitignore",                                 "file", "manual (Block 1)"),
    (".github/workflows/ci.yml",                   "file", "manual (Block 1)"),
    ("results/tables",                             "dir",  "01_data_validation.py + 02_lmm_modeling.py"),
    ("results/tables/*_R_*.csv",                   "glob", "src/analysis_pipeline.R (NEEDS R)"),
    ("results/figures",                            "dir",  "02_lmm_modeling.py + 03_render_infographic.py"),
    ("results/figures/Developmental_Trajectories.png", "file", "02_lmm_modeling.py"),
    ("results/figures/GitHub_Hero.png",            "file", "03_render_infographic.py"),
    ("docs",                                       "dir",  "write_codebook_sheet.py + dump_R_env.R"),
    ("docs/CODEBOOK.md",                           "file", "write_codebook_sheet.py"),
    ("docs/data_dictionary.csv",                   "file", "write_codebook_sheet.py"),
    ("docs/R_sessionInfo.txt",                     "file", "dump_R_env.R (NEEDS R)"),
    ("docs/R_packages.txt",                        "file", "dump_R_env.R (NEEDS R)"),
    ("tests/test_code_audit.py",                   "file", "manual"),
    ("tests/test_doc_audit.py",                    "file", "manual"),
]

missing = []
for path, kind, gen in CHECKS:
    p = ROOT / path
    if kind == "file":
        ok = p.is_file()
    elif kind == "dir":
        ok = p.is_dir()
    elif kind == "glob":
        ok = bool(list(ROOT.glob(path)))
    if not ok:
        missing.append((path, gen))

# Sheet-2 check
sheet2_ok, sheet2_msg = False, ""
try:
    from pandas import ExcelFile
    xl = ROOT / "dataset/NCAD_Iranian_Dataset.xlsx"
    if xl.exists():
        names = ExcelFile(xl).sheet_names
        sheet2_ok = len(names) >= 2
        sheet2_msg = f"sheets={names}"
    else:
        sheet2_msg = ".xlsx missing"
except Exception as e:
    sheet2_msg = f"error: {e}"

print("=" * 78)
print(f"MISSING ({len(missing)} of {len(CHECKS)}):")
for path, gen in missing:
    print(f"  ✗ {path}\n      → generate with: {gen}")
if not missing:
    print("  ✓ nothing missing")
print(f"\nSheet-2 Codebook in .xlsx: {'✓' if sheet2_ok else '✗'}  ({sheet2_msg})")

# R availability
print("\nR environment:")
rscript = shutil.which("Rscript")
if rscript:
    try:
        v = subprocess.run([rscript, "--version"], capture_output=True, text=True, timeout=5)
        print(f"  ✓ Rscript = {rscript}\n      {v.stdout.splitlines()[0] if v.stdout else v.stderr.strip()}")
    except Exception as e:
        print(f"  ✗ Rscript broken: {e}")
else:
    print("  ✗ Rscript NOT on PATH")
    # search common install roots
    for root in ["/c/Program Files/R", "/d/prerequisite/R", "/d/prerequisite/R-env"]:
        if Path(root).exists():
            hits = list(Path(root).rglob("Rscript.exe"))
            if hits:
                print(f"      found candidates: {[str(h) for h in hits[:3]]}")
print("=" * 78)
sys.exit(1 if (missing or not sheet2_ok) else 0)
