# Reproduce v0.12.0

Pinned environment:
- Lean 4.34.0-rc2
- Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

Run:

```bash
bash VERIFY_V0120.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier checks the immutable v0.11 hashes, rebuilds the required dependency spine
into a clean output directory with `-DwarningAsError=true`, compiles the v0.12
scalar-extension and axiom-audit modules, and rejects source-level `sorry`, `admit`, or
custom `axiom` declarations.
