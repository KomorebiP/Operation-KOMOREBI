# Komorebi H12 — Fourier flattening and conjugation criterion v0.11.0

The original gamma/class-field comparison remains open. This checkpoint gives
an explicit Fourier-orbit test for flattening a holomorphic scalar unit
multiplier, constructs the removing gauge, and proves a weaker conjugation-only
criterion sufficient for a conductor-three phase bound after the actual scalar
comparison and modulus hypotheses are supplied.

Start with PROOF.md and FORMALIZATION_SCOPE.md. SOURCE_CHECK.md distinguishes
classical input from the self-contained argument. REVIEW.md records the
adversarial self-check and the exact research boundary.

Reproduce from this directory:

```sh
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean
```

Python 3.13.5 and SymPy 1.14.0 were used. The Lean runtime is the user's pinned
4.34.0-rc2 portable compiler; it is not included. No Mathlib download or rebuild
is required. Run the manifest check BEFORE regenerating logs: reruns update
runtimes and thus change recorded file hashes.

The source/evidence snapshot of v0.10.0 is under prior/, unmodified. The actual
new checks do not depend on importing its formal files. No gamma numerical
comparison or new interval arithmetic is run here.
