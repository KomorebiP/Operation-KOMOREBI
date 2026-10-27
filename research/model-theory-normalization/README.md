# Komorebi Model-Theory Normalization v0.10

**Verified scalar binary backend; end-to-end discovery bit-cost lowering remains open.**

Start with NORMALIZED_CORE.md and FORMALIZATION_COVERAGE.md. The new implementation
contains ripple addition/subtraction, shift-and-add multiplication, restoring
positive-divisor division, signed Euclidean adjustment and modular reduction.
Its actual evaluators have proved operand-length-dependent gate/cell counters.

Nine Lean modules and 27 concrete examples pass a fresh cold build. The independent
Python port reproduces all 203 predecessor discovery outputs and their canonical
bases, while retaining 295,173 original arithmetic events. Those complete port
runs are finite tests, not a universal Lean lowering theorem.

## Reproduce

First verify distribution bytes:

    python tools/verify_integrity.py
    python tools/validate_manifest.py LEAN_MANIFEST.json --root .
    python tools/validate_manifest.py PYTHON_MANIFEST.json --root .

Then use a fresh working directory and the exact pinned runtime root:

    python checks/run_audit.py lean-init --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work /tmp/komorebi-bits-check
    python checks/run_audit.py lean-step --work /tmp/komorebi-bits-check --limit 5

Repeat lean-step until all 17 tasks complete. It refuses changed inputs and writes
PASS only after every planned expected outcome succeeds. The upstream Mathlib
cache is reused, not rebuilt. Runtime/cache files are not bundled.

    python checks/run_audit.py python

The last commands intentionally rewrite current execution records. Run integrity
checks BEFORE them in a fresh copy. The Python audit requires only the Python
standard library and the included unchanged baseline modules.

The predecessor ZIP is preserved verbatim under history/. Selected baseline data
are duplicated only to make the current audit self-contained. No fonts are bundled.
