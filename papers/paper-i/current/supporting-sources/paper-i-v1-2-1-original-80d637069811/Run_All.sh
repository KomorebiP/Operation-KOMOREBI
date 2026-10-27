#!/usr/bin/env sh
set -eu

SOURCE_ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH:-1788393600}
export SOURCE_DATE_EPOCH
export MPLBACKEND=Agg
export PYTHONDONTWRITEBYTECODE=1
SCRATCH_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/paper1_verify.XXXXXX")
WORK_ROOT="$SCRATCH_ROOT/$(basename "$SOURCE_ROOT")"

cleanup() {
  rm -rf -- "$SCRATCH_ROOT"
}
trap cleanup EXIT HUP INT TERM

command -v python3 >/dev/null 2>&1 || { echo "python3 is required" >&2; exit 1; }
command -v lake >/dev/null 2>&1 || { echo "lake is required" >&2; exit 1; }
command -v latexmk >/dev/null 2>&1 || { echo "latexmk is required" >&2; exit 1; }

cp -a -- "$SOURCE_ROOT" "$WORK_ROOT"
rm -rf -- "$WORK_ROOT/formalization/lean/.lake" "$WORK_ROOT/.verification-venv"

VERIFY_ENV="$WORK_ROOT/.verification-venv"
PYTHON_ROOT="$WORK_ROOT/code/python"
LEAN_ROOT="$WORK_ROOT/formalization/lean"
PAPER_ROOT="$WORK_ROOT/paper"
WHEEL_ROOT="$PYTHON_ROOT/dist"
WHEEL_PATH="$WHEEL_ROOT/projector_seed_calculus-1.1.1-py3-none-any.whl"
THEOREM_MAP="$LEAN_ROOT/LEAN_THEOREM_MAP_v1.0.1.md"

[ -f "$THEOREM_MAP" ] || { echo "missing theorem map: $THEOREM_MAP" >&2; exit 1; }

python3 -m venv "$VERIFY_ENV"
"$VERIFY_ENV/bin/python" -m pip install --disable-pip-version-check \
  --requirement "$PYTHON_ROOT/requirements.lock.txt"

"$VERIFY_ENV/bin/python" "$PYTHON_ROOT/run_all.py"
rm -rf -- "$WHEEL_ROOT"
mkdir -p -- "$WHEEL_ROOT"
"$VERIFY_ENV/bin/python" -m pip wheel "$PYTHON_ROOT" --no-deps \
  --no-build-isolation --wheel-dir "$WHEEL_ROOT"
[ -f "$WHEEL_PATH" ] || { echo "missing built wheel: $WHEEL_PATH" >&2; exit 1; }
"$VERIFY_ENV/bin/python" -m pip install --force-reinstall --no-deps "$WHEEL_PATH"
"$VERIFY_ENV/bin/python" -c \
  "import seed_calculus; assert seed_calculus.__version__ == '1.1.1'"
(
  cd "$SCRATCH_ROOT"
  "$VERIFY_ENV/bin/python" -m pytest -q -W error -p no:cacheprovider \
    --import-mode=importlib "$PYTHON_ROOT/tests"
)
"$VERIFY_ENV/bin/python" -m pip check

(
  cd "$LEAN_ROOT"
  lake --wfail build
  "$VERIFY_ENV/bin/python" scripts/verify_theorem_map.py
  lake env lean -E warning KomorebiVerification/KernelAudit.lean
)

(
  cd "$PAPER_ROOT"
  latexmk -C Projector_Resolved_Seed_Calculus_I.tex
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    Projector_Resolved_Seed_Calculus_I.tex
)

echo "Paper I verification completed successfully in an isolated copy."
