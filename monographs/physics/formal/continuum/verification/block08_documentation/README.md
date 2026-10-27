# Komorebi Physics Lean v0.8.0 — Checked Block 08

Cumulative formalization of the 550-page *Projector-Refinement Physics: Complete Unified Theory* by Komorebi P.

**Completed cumulative audit: PASS.** The release contains 670 theorem declarations, 808 inventoried named declarations, 40 mathematical modules and 59 deliberately invalid controls. Block 08 adds 98 theorem declarations. All 34 mathematical modules from Block 07 are unchanged and freshly recompiled. Counts include support lemmas and exact examples, not independent discoveries or a full-edition completion percentage.

## This block

Chapter 5.4's actual bounded Parseval-channel analysis/synthesis, channel-norm probabilities, full cross-channel operator reconstruction, finite Hilbert-sum sharp projectors, isometry and effect compression are checked. An additional universal construction starts with arbitrary finite positive effects and uses their actual positive square roots to build the dilation; no dilation or channel-factorization hypothesis is supplied to that theorem.

The range projection Q=VV* is kept distinct from V*V=I. Exact formulas characterize the failure of arbitrary compression to preserve multiplication, and express effect unsharpness as a squared norm outside the analysis image. Actual skew-flow derivatives and currents carry into the enlarged sharp atlas. Chapter 5.5's zero-divergence cycle freedom is also checked, including a nonzero three-cycle and coarse/subsystem invariance.

The output spaces can be different complete complex Hilbert spaces, with a finite label type. The universal construction uses finitely many copies of H. H need not be finite-dimensional. All maps are bounded and everywhere defined. Imported Mathlib square-root/functional-calculus results are reused, not claimed as new mathematical discoveries.

Read `docs/BLOCK_08_PROOF_GUIDE.md`, `docs/BLOCK_08_DECLARATION_INDEX.md`, `docs/SOURCE_MAP.md` and `docs/CLAIM_LEDGER.json`. `STATUS.md` gives counts and boundaries. `CONTINUE_HERE.md` provides the next-block protocol.

## Reproduce

Restore the exact portable Linux/WSL kit using the checksum-verified seven-part assembly instructions in `runtime_restore_support/`, or use an existing matching kit. The multi-gigabyte runtime is intentionally not bundled. Lean is 4.34.0-rc2; Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

The verifier uses one worker and warnings as errors; removes local compiled outputs; rebuilds all active mathematical modules and the aggregate; audits every inventoried name including proof-bearing constructors; checks designated diagnostics for every negative control; verifies all source-preservation layers; and checks nine clean pinned dependency repositories. The imported dependency cache is reused, not rebuilt wholesale. Only `propext`, `Classical.choice` and `Quot.sound` are allowed axiom dependencies.

`verification/final/report.json` is the completed current cumulative report. `verification/block07_baseline/report.json` records the fresh starting audit. Development failures and source snapshots are retained under `verification/development/block08`. The `docs/BLOCK_08_FAILURES.md` record distinguishes failed development from successful checking. Negative controls are intentionally false and are not active mathematical modules.

## Package and extracted-package verification

```bash
python3 scripts/package_release.py --out ../Komorebi_Physics_Lean_v0.8.0_Checked_Block_08.zip
python3 scripts/recheck_archive.py --archive ../Komorebi_Physics_Lean_v0.8.0_Checked_Block_08.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /new/extraction/directory --out /external/evidence/directory
```

The second command requires a new extraction directory and runs the entire verifier again, not just ZIP checksums. Its external report can hash the unchanged delivered ZIP without making a circular self-certification claim.

## Boundary

This is not a proof of the entire 550-page edition. No countable/unbounded dilation, minimality/uniqueness, instrument-update theorem, time-dependent-channel derivative, ODE existence, completely positive dynamical semigroup, entropy-boundary extension, continuum gravity/cosmology completion, or empirical validation is claimed. Historical numerical residuals in Chapter 5.6 are not rerun. Next: Chapter 6 graph-compatible countable atlases and unbounded-generator packet continuity, with domains and convergence explicitly represented.
