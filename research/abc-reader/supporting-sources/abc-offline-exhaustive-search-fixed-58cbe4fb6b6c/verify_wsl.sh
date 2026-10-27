#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
find_python() {
  local candidate
  if [[ -n "${ABC_PYTHON:-}" ]] && "$ABC_PYTHON" -c 'import sympy,mpmath,pandas' >/dev/null 2>&1; then
    printf '%s\n' "$ABC_PYTHON"
    return 0
  fi
  for candidate in python3 python "$HOME"/miniconda3/envs/*/bin/python "$HOME"/anaconda3/envs/*/bin/python "$HOME"/.conda/envs/*/bin/python; do
    [[ -x "$(command -v "$candidate" 2>/dev/null || true)" || -x "$candidate" ]] || continue
    if "$candidate" -c 'import sympy,mpmath,pandas' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}
PYTHON="$(find_python || true)"
if [[ -z "$PYTHON" ]]; then
  echo 'No Python environment with sympy, mpmath, and pandas was found.' >&2
  exit 2
fi
exec "$PYTHON" "$ROOT/verify_suite.py"
