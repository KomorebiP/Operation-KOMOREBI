#!/usr/bin/env sh
set -eu

RELEASE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-1788393600}
export SOURCE_DATE_EPOCH
export MPLBACKEND=Agg
export PYTHONDONTWRITEBYTECODE=1

WHEEL_NAME="projector_seed_refinement-1.2.1-py3-none-any.whl"
FROZEN_WHEEL="$RELEASE_ROOT/code/python/dist/$WHEEL_NAME"
CHECKSUM_FILE="$RELEASE_ROOT/SHA256SUMS.txt"

command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }
command -v lake >/dev/null 2>&1 || { echo "lake is required" >&2; exit 1; }
command -v latexmk >/dev/null 2>&1 || { echo "latexmk is required" >&2; exit 1; }
command -v sha256sum >/dev/null 2>&1 || { echo "sha256sum is required" >&2; exit 1; }
[ -f "$CHECKSUM_FILE" ] || { echo "missing checksum manifest: $CHECKSUM_FILE" >&2; exit 1; }
[ -f "$FROZEN_WHEEL" ] || { echo "missing frozen wheel: $FROZEN_WHEEL" >&2; exit 1; }

verify_release_checksums() {
  (cd "$RELEASE_ROOT" && sha256sum --check --quiet SHA256SUMS.txt)
}

verify_release_checksums
CHECKSUM_MANIFEST_HASH=$(sha256sum "$CHECKSUM_FILE" | awk '{print $1}')

WORK_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/projector-seed-II.XXXXXX")
cleanup() {
  case "$WORK_ROOT" in
    "${TMPDIR:-/tmp}"/projector-seed-II.*)
      rm -rf -- "$WORK_ROOT"
      ;;
    *)
      echo "refusing to remove unexpected temporary path: $WORK_ROOT" >&2
      ;;
  esac
}
trap cleanup EXIT HUP INT TERM

VERIFY_ENV="$WORK_ROOT/verification-venv"
PYTHON="$VERIFY_ENV/bin/python"
GENERATED_ROOT="$WORK_ROOT/generated"
FRESH_WHEEL="$WORK_ROOT/dist/$WHEEL_NAME"
PYTHON_SOURCE="$WORK_ROOT/python-source"

python3 -m venv "$VERIFY_ENV"
"$PYTHON" -m pip install --disable-pip-version-check \
  --requirement "$RELEASE_ROOT/code/python/requirements.lock"

"$PYTHON" "$RELEASE_ROOT/code/python/run_all.py" \
  --output-root "$GENERATED_ROOT" \
  --compare-release-root "$RELEASE_ROOT"

cp -R "$RELEASE_ROOT/code/python" "$PYTHON_SOURCE"
"$PYTHON" -m build --wheel --no-isolation \
  --outdir "$WORK_ROOT/dist" "$PYTHON_SOURCE"
[ -f "$FRESH_WHEEL" ] || { echo "missing temporary wheel: $FRESH_WHEEL" >&2; exit 1; }
"$PYTHON" -m pip install --force-reinstall --no-deps "$FRESH_WHEEL"

(
  cd "$WORK_ROOT"
  "$PYTHON" -m pytest -q -W error -p no:cacheprovider \
    --import-mode=importlib "$RELEASE_ROOT/code/python/tests"
  "$PYTHON" -m pip check
  "$PYTHON" -c 'import seed_refinement; assert seed_refinement.__version__ == "1.2.1"; print("WHEEL_IMPORT_PASS version=1.2.1")'
  "$PYTHON" -m seed_refinement.release_validation \
    compare-wheels "$FRESH_WHEEL" "$FROZEN_WHEEL"
)

LEAN_WORK="$WORK_ROOT/lean"
cp -R "$RELEASE_ROOT/formalization/lean" "$LEAN_WORK"
if [ -d "$LEAN_WORK/.lake/build" ]; then
  rm -rf -- "$LEAN_WORK/.lake/build"
fi
(
  cd "$LEAN_WORK"
  lake --wfail build
  "$PYTHON" scripts/verify_theorem_map.py
  lake env lean -E warning KomorebiVerification/PaperII/KernelAudit.lean
)

PAPER_WORK="$WORK_ROOT/paper"
cp -R "$RELEASE_ROOT/paper" "$PAPER_WORK"
cp "$GENERATED_ROOT/paper/figures/"*.png "$PAPER_WORK/figures/"
cp "$GENERATED_ROOT/paper/figures/"*.pdf "$PAPER_WORK/figures/"
(
  cd "$PAPER_WORK"
  latexmk -C Projector_Resolved_Seed_Calculus_II.tex
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    Projector_Resolved_Seed_Calculus_II.tex
)
[ -f "$PAPER_WORK/Projector_Resolved_Seed_Calculus_II.pdf" ] || {
  echo "temporary LaTeX build did not produce the paper PDF" >&2
  exit 1
}

verify_release_checksums
FINAL_MANIFEST_HASH=$(sha256sum "$CHECKSUM_FILE" | awk '{print $1}')
[ "$CHECKSUM_MANIFEST_HASH" = "$FINAL_MANIFEST_HASH" ] || {
  echo "SHA256SUMS.txt changed during verification" >&2
  exit 1
}

echo "Paper II verification completed successfully without modifying the frozen release."
