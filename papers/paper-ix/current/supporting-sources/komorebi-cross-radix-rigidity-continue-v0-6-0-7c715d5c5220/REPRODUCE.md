# Reproduction — v0.6.0

## Pinned toolchain

- Lean `4.34.0-rc2`
- Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict flag `-DwarningAsError=true`

The v0.6 development run used the compact portable runtime assembled with SHA-256

`f7548038f94ea30789ce28fc2ff769c40e9c37d8879ea133e9bea821056342c7`.

The proof-system commits match the v0.5 pinned environment.

## Strict clean check

```bash
bash VERIFY_V060.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The verifier checks all v0.5 source hashes, creates a fresh temporary custom-module output directory, recompiles the exact v0.6 dependency chain there with warnings as errors, compiles the new rank/nullity and axiom-audit modules, and scans all saved Lean sources for `sorry`, `admit`, or custom `axiom` declarations.

## Development incidents

The initial portable runtime extraction exceeded one command's execution ceiling and was resumed by extracting the pinned package cache explicitly. An early project invocation attempted a network dependency fetch because the offline cache was not attached. After attaching the exact local package cache, compilation proceeded offline. One clean dependency batch later hit the execution ceiling while entering `CrossRadixAffineDecoder`; that incomplete batch was not counted. The affected modules were rerun individually and passed. These are environment incidents, not theorem checks.
