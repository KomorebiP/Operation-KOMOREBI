# Komorebi H12 — Gerbe Descent v0.8.0

Start with PROOF.md and FORMALIZATION_SCOPE.md. The main gamma-arithmetic
comparison remains open. This block proves the twisted compact Hodge
obstruction, classifies its finite topologically trivial class group,
constructs the intermediate Stein-cover correspondence, and recovers the
oriented Gauss additive phase through a specified elliptic pairing.

## Reproduce

Use Python 3.13 with SymPy 1.14.0 (the recorded run versions are authoritative):

```sh
python checks/validate_manifest.py MANIFEST.json --root .
python checks/exact_checks.py
python checks/verify_lean.py --lean /absolute/path/to/toolchain/bin/lean
```

The pinned compiler is Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d. Only its bundled Std is needed;
Mathlib is not imported in the new modules. The runtime is not shipped.

Run the manifest check first: verification rewrites its own evidence files
with new runtimes. A rerun authenticates the new computations; it does not
preserve the shipped run's evidence hashes. The isolated build is placed in
`.lean-check/`. Timeouts are explicit failures, not successful checks.

All 51 new Lean theorems and the 58 exact assertions have been replayed from a
fresh archive extraction. The previous v0.7.0 ZIP is preserved byte-for-byte.
No fresh cumulative build of all inherited theorems is claimed.

The 252 fixed classes are not 252 possible values of U_Gamma. No finite class
count, coboundary cancellation, or pairing identity supplies the missing
normalized scalar comparison.
