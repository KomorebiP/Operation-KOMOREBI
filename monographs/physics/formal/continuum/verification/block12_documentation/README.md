# Komorebi Physics Lean v0.12.0 — Block 12

Cumulative formalization of the 550-page *Projector-Refinement Physics: Complete Unified Theory* by Komorebi P.

**Production audit: PASS.** The completed `verification/final/report.json` is authoritative. The finished archive is also reverified from a fresh extraction; that external receipt is delivered alongside the ZIP.

Inventory: **1,083 theorem declarations, 1,296 inventoried names, 65 mathematical modules and 87 invalid controls**. Block 12 adds 106 theorems and 18 other declarations. All 58 prior mathematical modules are preserved. Counts include support lemmas and examples, not independent discoveries or a completion percentage.

This block constructs infinite-cell coarse projectors, proves energy regrouping, derives domain preservation from closedness and graph compatibility, and proves justified iterated current identities. Joint-product sums retain explicit joint summability. Arbitrary spectral masks and a non-spectral infinite parity example use the actual unbounded model and constructed normalized global solution. A repeated-cycle array disproves generic rowwise/iterated-to-joint summability shortcuts.

Read `docs/BLOCK_12_PROOF_GUIDE.md`, `docs/BLOCK_12_DECLARATION_INDEX.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and `CONTINUE_HERE.md`.

## Reproduce

The exact Linux/WSL portable runtime is external. Restore it using `runtime_restore_support/` or reuse the pinned kit.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

All local mathematical modules are freshly compiled, with one worker and warnings as errors. All names are axiom-audited and each invalid control requires its own designated proof diagnostic. All source preservation layers and nine clean dependency pins are checked. Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 remain pinned. Imported caches are reused, not rebuilt wholesale.

```bash
python3 scripts/package_release.py --out ../Komorebi_Physics_Lean_v0.12.0_Checked_Block_12.zip
python3 scripts/recheck_archive.py --archive ../Komorebi_Physics_Lean_v0.12.0_Checked_Block_12.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /new/extraction --out /external/evidence
```

Packaging refuses a non-PASS report or changed proof inputs. The archive recheck validates every checksum and reruns the complete audit from a new extraction. Runtime bytes are not bundled.

## Boundary

Strong sums do not automatically preserve an arbitrary unbounded domain. The sufficient closed/graph assumptions and the alternative coarse-preservation interface are explicit. Iterated sums are not a license to flatten a nonsummable double array. Section 6.6 residue/ladder routing, form domains, general Stone/spectral representation, differential-oscillator equivalence, nonlinear/dissipative existence and later gravity/cosmology remain separate. No empirical validation follows from formal model theorems.
