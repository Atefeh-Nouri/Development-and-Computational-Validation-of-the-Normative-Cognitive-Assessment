#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"

# ---------------------------------------------------------------
# 1) Activate Python venv
# ---------------------------------------------------------------
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

# ---------------------------------------------------------------
# 2) Python syntax gate
# ---------------------------------------------------------------
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
  || { echo "[gate] Python syntax error"; exit 2; }

echo "[gate] Python syntax OK"

# ---------------------------------------------------------------
# 3) Find a WORKING Rscript, not the broken conda one
# ---------------------------------------------------------------
RSCRIPT_BIN=""

for root in \
  "/c/Program Files/R" \
  "/c/Program Files (x86)/R" \
  "/d/prerequisite/R" \
  "/d/prerequisite/R-env"
do
  [ -d "$root" ] || continue

  while IFS= read -r cand; do
    [ -z "$cand" ] && continue
    dir="$(dirname "$cand")"

    if PATH="$dir:$PATH" Rscript --version >/dev/null 2>&1; then
      RSCRIPT_BIN="$cand"
      break 2
    fi
  done < <(find "$root" -type f -iname 'Rscript.exe' 2>/dev/null | grep -v 'conda_pkgs')
done

# Last resort: test every Rscript under D:/prerequisite, including conda,
# but only accept it if --version actually works.
if [ -z "$RSCRIPT_BIN" ] && [ -d "/d/prerequisite" ]; then
  while IFS= read -r cand; do
    [ -z "$cand" ] && continue
    dir="$(dirname "$cand")"

    if PATH="$dir:$PATH" Rscript --version >/dev/null 2>&1; then
      RSCRIPT_BIN="$cand"
      break
    fi
  done < <(find "/d/prerequisite" -type f -iname 'Rscript.exe' 2>/dev/null)
fi

if [ -z "$RSCRIPT_BIN" ]; then
  echo "=========================================================================="
  echo "ERROR: no working Rscript.exe found."
  echo ""
  echo "Install standalone CRAN R first:"
  echo "  https://cloud.r-project.org/bin/windows/base/"
  echo ""
  echo "Do not use the broken conda_pkgs R extract."
  echo "=========================================================================="
  exit 3
fi

R_DIR="$(dirname "$RSCRIPT_BIN")"
export PATH="$R_DIR:$PATH"

echo "[R] using Rscript: $RSCRIPT_BIN"
Rscript --version

# ---------------------------------------------------------------
# 4) R library location
#    Use Windows-style forward-slash paths for R.
# ---------------------------------------------------------------
NCAD_R_LIB_UNIX="${NCAD_R_LIB_UNIX:-/d/prerequisite/R-library}"
NCAD_R_PKG_DIR_UNIX="${NCAD_R_PKG_DIR_UNIX:-/d/prerequisite/R-packages}"

mkdir -p "$NCAD_R_LIB_UNIX"

NCAD_R_LIB="$(cygpath -w "$NCAD_R_LIB_UNIX")"
NCAD_R_LIB="${NCAD_R_LIB//\\//}"
export NCAD_R_LIB
export R_LIBS_USER="$NCAD_R_LIB"

echo "[R] NCAD_R_LIB = $NCAD_R_LIB"

if [ -d "$NCAD_R_PKG_DIR_UNIX" ]; then
  NCAD_R_PKG_DIR="$(cygpath -w "$NCAD_R_PKG_DIR_UNIX")"
  NCAD_R_PKG_DIR="${NCAD_R_PKG_DIR//\\//}"
  export NCAD_R_PKG_DIR
  echo "[R] NCAD_R_PKG_DIR = $NCAD_R_PKG_DIR"
else
  echo "[R] optional offline package dir not found: $NCAD_R_PKG_DIR_UNIX"
fi

# ---------------------------------------------------------------
# 5) Helper: run Rscript, with PowerShell fallback if Git Bash crashes
# ---------------------------------------------------------------
run_rscript_with_fallback() {
  local script="$1"
  shift

  echo "[R] trying direct Rscript: $script $*"
  if Rscript "$script" "$@"; then
    return 0
  fi

  echo "[R] direct Rscript failed or crashed; trying PowerShell wrapper..."

  local win_repo win_rscript win_script args_ps a
  win_repo="$(cygpath -w "$PWD")"
  win_rscript="$(cygpath -w "$RSCRIPT_BIN")"
  win_script="$win_repo\\${script//\//\\}"

  args_ps=""
  for a in "$@"; do
    args_ps="$args_ps '$a'"
  done

  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '$win_rscript' '$win_script'$args_ps"
}

# ---------------------------------------------------------------
# 6) Install/check R packages
# ---------------------------------------------------------------
echo "================= Installing/checking required R packages ================="

if ! run_rscript_with_fallback src/install_R_packages.R; then
  echo "=========================================================================="
  echo "ERROR: R package installation/check failed."
  echo ""
  echo "Open Windows PowerShell and run this manually:"
  echo ""
  echo "  \$Rscript = '$(cygpath -w "$RSCRIPT_BIN")'"
  echo "  \$Repo    = '$(cygpath -w "$PWD")'"
  echo "  \$Lib     = '$NCAD_R_LIB'"
  echo ""
  echo "  New-Item -ItemType Directory -Force -Path \$Lib | Out-Null"
  echo "  \$env:NCAD_R_LIB = \$Lib"
  echo "  & \$Rscript '\$Repo\\src\\install_R_packages.R'"
  echo ""
  echo "If PowerShell also crashes, open R GUI and run:"
  echo ""
  echo "  lib <- '$NCAD_R_LIB'"
  echo "  dir.create(lib, recursive = TRUE, showWarnings = FALSE)"
  echo "  .libPaths(c(lib, .libPaths()))"
  echo "  install.packages(c('readxl','lme4','lmerTest','dplyr','tibble'),"
  echo "                   lib = lib,"
  echo "                   repos = 'https://cloud.r-project.org',"
  echo "                   dependencies = TRUE)"
  echo "=========================================================================="
  exit 4
fi

echo "[R] required packages are available"

# ---------------------------------------------------------------
# 7) Python pipeline
# ---------------------------------------------------------------
echo "================= Generating calibrated synthetic benchmark ================="
python src/generate_synthetic_data.py || exit 5

echo "================= Regenerating truth manifest ================="
python src/00_regenerate_truth.py || exit 6

echo "================= Table 1 validation ================="
python src/01_data_validation.py || echo "[warn] 01_data_validation.py failed, continuing"

echo "================= LMM tables and trajectories ================="
python src/02_lmm_modeling.py || exit 7

echo "================= Hero infographic ================="
python src/03_render_infographic.py || exit 8

# ---------------------------------------------------------------
# 8) Run R engine
# ---------------------------------------------------------------
NSIM="${NSIM:-1000}"

echo "================= Running R/lmerTest engine with NSIM=$NSIM ================="
if ! run_rscript_with_fallback src/analysis_pipeline.R . "$NSIM"; then
  echo "ERROR: analysis_pipeline.R failed."
  exit 9
fi

echo "================= Registering R engine in truth manifest ================="
python src/04_register_r_engine.py "$NSIM" || exit 10

# ---------------------------------------------------------------
# 9) Final audits
# ---------------------------------------------------------------
echo "================= code_audit ================="
python -m pytest tests/ -m code_audit -q

echo "================= doc_audit ================="
python -m pytest tests/ -m doc_audit -v -rs
