# Reproduction — v0.5.0

## Pinned toolchain

- Lean `4.34.0-rc2`
- Lean commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- strict flag `-DwarningAsError=true`
- assembled offline runtime archive SHA-256: `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`

The user's existing Library runtime consists of `Lean_Offline_01.zip` through `Lean_Offline_07.zip`. It is not duplicated into this small checkpoint.

## Clean strict check

From a Lake root with the pinned `lake-manifest.json` and package cache available, compile with `src` on `LEAN_PATH`. The saved verification script does this for the v0.5 load-bearing modules:

```bash
bash VERIFY_V050.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The script recompiles the four baseline dependencies used by the new layer, all six substantive v0.5 modules, and the v0.5 axiom-audit module with warnings as errors. It then scans all source files for `sorry`, `admit`, and custom `axiom` declarations.

## Environment incidents during development

Development encountered four non-mathematical issues, all preserved in `logs/ENVIRONMENT_NOTES.md`: one full-runtime verifier timeout after successful preflight stages; one module-path wiring issue; one Lake root-containment issue; and two clean batch compile invocations that reached the execution ceiling before individual strict retries passed. None is treated as a theorem refutation or as a passing theorem check.
