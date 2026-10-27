# Reproduction — v0.8.0

Pinned toolchain:

- Lean `4.34.0-rc2`, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict flag `-DwarningAsError=true`

Run:

```bash
bash VERIFY_V080.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier first checks every v0.7 source hash, attaches the pinned local package cache, rebuilds the required v0.7 dependencies and spectral shell layer into a fresh output directory, then compiles the v0.8 orbit-hull, active shell/jet, invariant shell/jet, refined sequence-hull, and axiom-audit modules with warnings as errors. Finally it scans the complete source tree for `sorry`, `admit`, and custom `axiom` declarations.

Bell and the rational-generating-function/quasi-polynomial normalization remain external source dependencies rather than executable proof evidence. See `BELL_EXTERNAL_INTERFACE.md`.
