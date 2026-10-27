# Reproducing Block 33

## Pins and prerequisites
Lean4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06, with all other exact dependency
revisions recorded in lake-manifest.json. Python 3.13.5 and SymPy 1.14.0 were used
for the recorded finite audit. Source is in lean/KomorebiPadic/.

The runtime and dependency caches are not embedded in this release. The retained
portable archive fingerprint is
f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7.
Only use a runtime with the exact toolchain and revision checks below.

## Evidence-only replay (no runtime needed)

    PYTHONDONTWRITEBYTECODE=1 python verify_release.py
    python validate_manifest.py COMPUTATION_MANIFEST.json --root .

The first command validates records, source hashes, expected exits/negative
diagnostics, axiom inventories, predecessor source/archive identity and compiled
artifact presence. CHECKSUMS.json additionally authenticates packaged files against
this release's ledger. A matching hash is integrity evidence, not external authorship.
The second command uses the retained project-local schema1 manifest validator.

## Fresh execution with the known portable layout
Do this in a disposable extracted copy: the runner deletes only .lake/build and
replaces results/ receipts. That intentionally makes the original archive ledger
stale in the copy; preserve the published archive before rerunning.

    export RUNTIME=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
    export PATH="$RUNTIME/toolchain/bin:$PATH"
    python verification/prepare_offline.py "$RUNTIME"
    lean --version
    lake --version
    PYTHONDONTWRITEBYTECODE=1 python verification/run_final.py

prepare_offline.py checks the exact runtime identity and all cached dependency git
revisions before attaching symlinks. It refuses to replace a real dependency
directory. A standard online Lean/mathlib setup must match lake-manifest.json;
no stable4.34.0 compatibility is inferred.

The runner executes a clean root build, declared and environment axiom inventories,
new and predecessor examples, positive and four negative controls, leanchecker,
and the exact integer audit. Each subprocess has a 600-second timeout. The four
negative controls are expected nonzero exits with required diagnostics. Every phase
requires identical before/after hashes of all registered execution inputs.

To run only the numerical experiment:

    PYTHONDONTWRITEBYTECODE=1 python verification/audit_observable.py

This writes results/audit_observable.json and may change runtime/version fields.
It does not execute or prove Lean statements. Source theorem counts come from
verification/theorem_inventory.json; environment audit includes generated constants
and must not be reported as the number of separate mathematical discoveries.
