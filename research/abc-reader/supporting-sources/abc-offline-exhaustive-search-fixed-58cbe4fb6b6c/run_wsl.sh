#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
find_python() {
  local candidate
  if [[ -n "${ABC_PYTHON:-}" ]]; then
    if "$ABC_PYTHON" -c 'import sympy,mpmath' >/dev/null 2>&1; then
      printf '%s\n' "$ABC_PYTHON"
      return 0
    fi
  fi
  for candidate in python3 python "$HOME"/miniconda3/envs/*/bin/python "$HOME"/anaconda3/envs/*/bin/python "$HOME"/.conda/envs/*/bin/python; do
    [[ -x "$(command -v "$candidate" 2>/dev/null || true)" || -x "$candidate" ]] || continue
    if "$candidate" -c 'import sympy,mpmath' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}
PYTHON="$(find_python || true)"
if [[ -z "$PYTHON" ]]; then
  echo 'No offline Python environment with sympy and mpmath was found.' >&2
  echo 'Activate your existing WSL conda environment, or set ABC_PYTHON to its python executable.' >&2
  exit 2
fi
exec "$PYTHON" "$ROOT/abc_offline_exhaustive.py" "$@"
