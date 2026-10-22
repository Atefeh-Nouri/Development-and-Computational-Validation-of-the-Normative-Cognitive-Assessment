#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"

# Activate venv.
if [ -f venv/Scripts/activate ]; then
  source venv/Scripts/activate
elif [ -f .venv/Scripts/activate ]; then
  source .venv/Scripts/activate
else
  echo "ERROR: no venv found."
  exit 1
fi

echo "[env] python = $(which python)"
python --version

# ------------------------------------------------------------------
# Locate Rscript.exe from D:\prerequisite first, then common R dirs.
# ------------------------------------------------------------------
PREREQ="/d/prerequisite"
export R_LIBS_USER="$PREREQ/R-library"
mkdir -p "$R_LIBS_USER"

RSCRIPT_BIN=""
# Prefer standalone CRAN R (complete DLLs) over conda partial extracts.
for search_root in "/c/Program Files/R" "/c/Program Files (x86)/R" "$PREREQ/R-env" "$PREREQ"; do
  if [ -d "$search_root" ]; then
    # Skip conda_pkgs partial extracts (they lack Rblas/R LAPACK DLLs)
    cand="$(find "$search_root" -type f -iname 'Rscript.exe' 2>/dev/null | grep -v 'conda_pkgs' | head -n 1)"
    if [ -z "$cand" ]; then
      # Fallback: include conda if nothing else found
      cand="$(find "$search_root" -type f -iname 'Rscript.exe' 2>/dev/null | head -n 1)"
    fi
    if [ -n "$cand" ]; then
      RSCRIPT_BIN="$cand"
      break
    fi
  fi
done

if [ -n "$RSCRIPT_BIN" ]; then
  R_DIR="$(dirname "$RSCRIPT_BIN")"
  export PATH="$R_DIR:$PATH"
  echo "[R] found Rscript: $RSCRIPT_BIN"
  Rscript --version || true
else
  echo "[R] Rscript.exe NOT found under $PREREQ or common R directories."
  echo "[R] Searching for R installers in $PREREQ ..."
  find "$PREREQ" -type f \( -iname 'R-*.exe' -o -iname 'R-*.msi' \) 2>/dev/null || true
  echo "[R] Install R first, then rerun this script."
fi

# ------------------------------------------------------------------
# Syntax gate.
# ------------------------------------------------------------------
python -m py_compile \
  src/ncad_core.py \
  src/generate_synthetic_data.py \
  src/00_regenerate_truth.py \
  src/01_data_validation.py \
  src/02_lmm_modeling.py \
  src/03_render_infographic.py \
  src/04_register_r_engine.py \
  src/manuscript_claims.py \
  tests/test_code_audit.py \
  tests/test_doc_audit.py \
  || { echo "[gate] Python syntax error"; exit 1; }

echo "[gate] Python syntax OK"

# ------------------------------------------------------------------
# Python pipeline.
# ------------------------------------------------------------------
echo "================= Generating calibrated synthetic benchmark ================="
python src/generate_synthetic_data.py

echo "================= Regenerating truth manifest ================="
python src/00_regenerate_truth.py

echo "================= Table 1 validation ================="
python src/01_data_validation.py || echo "[warn] 01_data_validation.py failed, continuing"

echo "================= LMM tables and trajectories ================="
python src/02_lmm_modeling.py

echo "================= Hero infographic ================="
python src/03_render_infographic.py

# ------------------------------------------------------------------
# R pipeline, if available.
# ------------------------------------------------------------------
if command -v Rscript >/dev/null 2>&1; then
  echo "================= Checking/installing required R packages ================="
  Rscript -e 'lib <- Sys.getenv("R_LIBS_USER"); dir.create(lib, recursive=TRUE, showWarnings=FALSE); .libPaths(c(lib, .libPaths())); need <- c("readxl","lme4","lmerTest","dplyr","tibble"); have <- rownames(installed.packages(lib.loc=lib)); miss <- setdiff(need, have); if (length(miss)) { cat("Installing R packages:", paste(miss, collapse=", "), "\n"); install.packages(miss, lib=lib, repos="https://cloud.r-project.org", dependencies=TRUE) } else { cat("Required R packages already installed.\n") }' \
    || echo "[R] package installation/check failed; trying to run engine anyway"

  NSIM="${NSIM:-20}"
  echo "================= Running R/lmerTest engine with NSIM=$NSIM ================="
  if Rscript src/analysis_pipeline.R . "$NSIM"; then
    python src/04_register_r_engine.py "$NSIM"
  else
    echo "[R] analysis_pipeline.R failed"
  fi
else
  echo "================= R engine skipped ================="
  echo "[R] Rscript not available. d09_method_parity will remain red until R is installed/run."
fi

# ------------------------------------------------------------------
# Audit.
# ------------------------------------------------------------------
echo "================= code_audit ================="
python -m pytest tests/ -m code_audit -q

echo "================= doc_audit ================="
python -m pytest tests/ -m doc_audit -v -rs
