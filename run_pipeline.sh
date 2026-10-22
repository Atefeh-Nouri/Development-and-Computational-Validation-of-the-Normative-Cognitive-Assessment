#!/usr/bin/env bash
# NCAD end-to-end reproduction entry point.
#   data -> Python LMM -> Sheet-2 Codebook -> R/lmerTest Satterthwaite+bootstrap -> audits
set -uo pipefail
cd "$(dirname "$0")"

if [ -f venv/Scripts/activate ]; then source venv/Scripts/activate
elif [ -f .venv/Scripts/activate ]; then source .venv/Scripts/activate
else echo "ERROR: no venv found."; exit 1; fi
echo "[env] python = $(which python)"; python --version

python -m py_compile \
  src/ncad_core.py src/generate_synthetic_data.py src/00_regenerate_truth.py \
  src/01_data_validation.py src/02_lmm_modeling.py src/03_render_infographic.py \
  src/04_register_r_engine.py src/05_manuscript_number_sheet.py \
  src/write_codebook_sheet.py src/sdt_correct.py src/manuscript_claims.py \
  tests/test_code_audit.py tests/test_doc_audit.py \
  || { echo "[gate] Python syntax error"; exit 2; }
echo "[gate] Python syntax OK"

# ---- locate a WORKING Rscript (skip broken conda_pkgs extracts) ----
RSCRIPT_BIN=""
for root in "/c/Program Files/R" "/c/Program Files (x86)/R" "/d/prerequisite/R" "/d/prerequisite/R-env"; do
  [ -d "$root" ] || continue
  while IFS= read -r cand; do
    [ -z "$cand" ] && continue
    dir="$(dirname "$cand")"
    if PATH="$dir:$PATH" Rscript --version >/dev/null 2>&1; then RSCRIPT_BIN="$cand"; break 2; fi
  done < <(find "$root" -type f -iname 'Rscript.exe' 2>/dev/null | grep -v 'conda_pkgs')
done
if [ -z "$RSCRIPT_BIN" ] && [ -d "/d/prerequisite" ]; then
  while IFS= read -r cand; do
    [ -z "$cand" ] && continue
    dir="$(dirname "$cand")"
    if PATH="$dir:$PATH" Rscript --version >/dev/null 2>&1; then RSCRIPT_BIN="$cand"; break; fi
  done < <(find "/d/prerequisite" -type f -iname 'Rscript.exe' 2>/dev/null)
fi
if [ -z "$RSCRIPT_BIN" ]; then
  echo "ERROR: no working Rscript.exe found. Install standalone CRAN R (https://cloud.r-project.org/bin/windows/base/)."; exit 3
fi
export PATH="$(dirname "$RSCRIPT_BIN"):$PATH"
echo "[R] using Rscript: $RSCRIPT_BIN"; Rscript --version

export NCAD_R_LIB="D:/prerequisite/R-library"
export R_LIBS_USER="$NCAD_R_LIB"
mkdir -p "$NCAD_R_LIB"

run_rscript_with_fallback() {
  local script="$1"; shift
  if Rscript "$script" "$@"; then return 0; fi
  echo "[R] direct Rscript failed; trying PowerShell wrapper..."
  local win_rscript win_script args_ps a
  win_rscript="$(cygpath -w "$RSCRIPT_BIN")"; win_script="$(cygpath -w "$script")"
  args_ps=""; for a in "$@"; do args_ps="$args_ps '$a'"; done
  powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "& '$win_rscript' '$win_script'$args_ps"
}

echo "================= R packages ================="
run_rscript_with_fallback src/install_R_packages.R || { echo "ERROR: R packages unavailable."; exit 4; }

echo "================= Generating benchmark ================="
python src/generate_synthetic_data.py || exit 5
python src/write_codebook_sheet.py || exit 6          # re-embed Sheet 2 after every regen

echo "================= Truth manifest ================="
python src/00_regenerate_truth.py || exit 7
python src/01_data_validation.py || echo "[warn] 01 failed, continuing"
python src/02_lmm_modeling.py || exit 8
python src/03_render_infographic.py || exit 9

NSIM="${NSIM:-1000}"
echo "================= R/lmerTest engine (NSIM=$NSIM) ================="
run_rscript_with_fallback src/analysis_pipeline.R . "$NSIM" || exit 10
python src/04_register_r_engine.py "$NSIM" || exit 11

echo "================= code_audit ================="
python -m pytest tests/ -m code_audit -q
echo "================= doc_audit ================="
python -m pytest tests/ -m doc_audit -v -rs
