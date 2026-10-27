# Komorebi p-adic program — Block 33 checked release

Start with REPORT.md and PROOF_BOUNDARY.md. RESULTS.json records the final build,
axiom inventories, concrete examples and exact finite audit. MATHEMATICS.md is a
self-contained derivation. CONTINUE_HERE.md identifies the next proof obligation.

New mathematical modules are LinearObservability, ObservableQuotient,
ObservableMaskAutomaton, and ObservabilityExamples. All other mathematical
modules are preserved from the checked Block 32 archive.

## Read-only evidence replay

    PYTHONDONTWRITEBYTECODE=1 python verify_release.py
    python validate_manifest.py COMPUTATION_MANIFEST.json --root .

These commands inspect retained records and hashes; they do not rerun Lean.
For a fresh build, see REPRODUCE.md. The archive includes project .olean/.ilean
artifacts separately under compiled/, not runtime binaries or dependency caches.

The predecessor archive is retained byte-for-byte under predecessor/Block32_Checked.zip.
The evidence guarantees observability and fixed-source quotient minimality, not a
minimum deterministic automaton or comparison with all other linear realizations.
