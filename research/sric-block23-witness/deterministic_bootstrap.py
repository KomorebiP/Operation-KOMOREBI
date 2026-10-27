"""Process bootstrap for deterministic, bounded BLAS execution.

The hosted validation runtime may import NumPy before user code. Setting thread
variables inside a package is then too late. Entry-point scripts call ``ensure``
before importing Block 23; the first invocation re-executes Python with the
thread budget fixed in the process environment.
"""
from __future__ import annotations

import os
import sys

_MARKER = "SRIC_BLOCK23_BOOTSTRAPPED"
_THREAD_VARS = (
    "OMP_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
)


def ensure() -> None:
    """Re-execute the current Python command once with deterministic defaults."""
    if os.environ.get(_MARKER) == "1":
        return
    env = os.environ.copy()
    for name in _THREAD_VARS:
        env[name] = env.get(f"SRIC_{name}", "1")
    env.setdefault("PYTHONHASHSEED", "0")
    env[_MARKER] = "1"
    os.execve(sys.executable, [sys.executable, *sys.argv], env)
