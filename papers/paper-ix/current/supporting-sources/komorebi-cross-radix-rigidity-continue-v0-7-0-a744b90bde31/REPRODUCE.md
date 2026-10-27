# Reproduction — v0.7.0

Pinned toolchain:

- Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict flag `-DwarningAsError=true`

Run:

```bash
bash VERIFY_V070.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier checks all v0.6 source hashes, rebuilds the dependency chain into a fresh custom-module output directory, compiles `CrossRadixBellCommonHull.lean` and `CrossRadixV07AxiomAudit.lean` with warnings as errors, and scans the complete source tree for placeholders/custom axioms.

The literature dependency is not executable proof evidence. See `BELL_EXTERNAL_INTERFACE.md` for the source-level boundary.
