# H12: based holonomy and the corrected descent criterion — v0.10.0

Read PROOF.md for the mathematical results and exact unresolved target.
Read FORMALIZATION_SCOPE.md before interpreting theorem counts.

## Reproduction

Use Python with SymPy installed, and the pinned portable Lean 4.34.0-rc2 compiler.
The runtime is not included in this source handoff. Its original archive hash
and the executed compiler version are recorded under evidence/.

First authenticate the shipped evidence:

    python checks/validate_manifest.py MANIFEST.json --root .

Then run, in the package directory:

    python checks/exact_checks.py
    python checks/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean

These two commands overwrite result records and therefore change their runtime
hashes. The manifest authenticates the shipped run; regenerate it after a rerun:

    python checks/make_manifest.py
    python checks/validate_manifest.py MANIFEST.json --root .

The included validator is the predecessor's openly labeled adapted version-one
Mathbox validation path. It validates structure and hashes, not mathematical truth.

The main gamma equality remains unproved. No new gamma numerical test is used.
