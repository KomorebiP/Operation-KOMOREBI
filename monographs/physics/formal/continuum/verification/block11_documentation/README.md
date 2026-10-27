# Komorebi Physics Lean v0.11.0 — Block 11

Cumulative formalization of the 550-page *Projector-Refinement Physics: Complete Unified Theory* by Komorebi P.

**Production audit: PASS.** The authoritative result is `verification/final/report.json`; only a completed PASS is a checked release.

Inventory: **977 theorem declarations, 1,172 inventoried names, 58 mathematical modules and 81 invalid controls**. Block 11 adds 81 theorems and seven definitions. All 52 prior mathematical modules are preserved. Counts include support lemmas and examples, not independent discoveries or a completion percentage.

This block proves strong time continuity, preservation of the actual maximal domain, and the actual l2 Schrödinger derivative of the constructed diagonal phase group. It proves global domain-solution existence/uniqueness and the converse differentiability-domain characterization. The countable current laws now consume a constructed solution. Exact rough-state and operator-norm counterexamples preserve the topology boundary; an actual normalized global solution has nonzero coherent-observable evolution.

Read `docs/BLOCK_11_PROOF_GUIDE.md`, `docs/BLOCK_11_DECLARATION_INDEX.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and `CONTINUE_HERE.md`.

## Reproduce

The exact Linux/WSL portable runtime is external. Restore it using `runtime_restore_support/` or reuse the pinned kit.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

Every local mathematical module is freshly compiled with one worker and warnings as errors. All inventoried names are axiom-audited and each invalid control requires its own intended diagnostic. All preservation layers and nine dependency pins are checked. Lean 4.34.0-rc2 and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06 are pinned. Imported caches are reused, not rebuilt wholesale.

## Package and recheck

```bash
python3 scripts/package_release.py --out ../Komorebi_Physics_Lean_v0.11.0_Checked_Block_11.zip
python3 scripts/recheck_archive.py --archive ../Komorebi_Physics_Lean_v0.11.0_Checked_Block_11.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /new/extraction --out /external/evidence
```

Packaging refuses a non-PASS report or changed verified proof inputs. The recheck uses a new extraction, verifies all checksums and repeats the complete Lean audit. Runtime bytes are not bundled.

## Boundary

This constructs dynamics for arbitrary real diagonal spectra on l2, not general non-diagonal Hamiltonians or the differential oscillator without an equivalence proof. All states have continuous orbits, but ambient differentiability holds exactly on the maximal domain. Uniform time cutoff estimates concern a fixed state, not the whole unit ball. The general Stone theorem, form-domain hierarchy, infinite coarse-cell domain/current regrouping, nonlinear/dissipative existence, continuum/gravity/cosmology and empirical adequacy remain separate.
