# Komorebi Euler Cubic Unit v26

This cumulative project continues v25 with a scale-sensitive cubic jet obstruction.
Read PROOF_AND_STATUS.md for the exact quantifiers, formulas and remaining gaps.

The mathematical Lean files are under Euler/. This release adds:

- ThirdOrderRemainder.lean
- CubicUnitObstruction.lean
- CubicUnitCertificates.lean
- ScaledCubicUnitObstruction.lean
- EulerCubicUnitBridge.lean
- CubicUnitSharpControls.lean

The prior 104 modules are unchanged. A project replay checks all 950 named
lemmas/theorems and their transitive axioms. This count includes helper results.

## Lean replay

Use the same pinned portable runtime as the incoming project:
Lean 4.34.0-rc2, mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
The runtime is not duplicated in this source archive.

```bash
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --evidence /path/to/NEW_evidence_directory --build-dir /path/to/NEW_build_directory
```

Replays refuse existing output paths. Compiler/dependency caches are reused,
not independently bootstrapped from source. No credentials or full process
environment are written into the archive.

## Exact/modular corroboration

```bash
python3 checks/check_cubic_unit.py --generic --output /path/to/new_generic.json
python3 checks/check_cubic_unit.py --actual 3 --precision 256 --output /path/to/new_B3.json
python3 checks/check_cubic_unit.py --actual 3 --alternate --precision 288 --output /path/to/new_B3_alt.json
```

The declared fixed actual inputs are B=3,7,11,15. They are not a universal
multiplier-family certificate. Finite residues never stand for exact dyadic
critical points. See the output records for shared-component limitations.

SHA256_MANIFEST.json tracks release bytes other than itself. RELEASE_STATUS.json
summarizes fresh execution. Historical evidence retains its original provenance.
