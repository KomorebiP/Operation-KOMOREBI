# Komorebi Physics Lean v0.15.0 — Block 15

Cumulative formalization of the 550-page *Projector-Refinement Physics: Complete Unified Theory* by Komorebi P.

**Production audit: PASS.** The completed `verification/final/report.json` is authoritative. The final ZIP is separately reverified from a fresh extraction. Its external receipt is delivered beside the ZIP.

Inventory: **1,371 theorem declarations, 1,626 inventoried names and 86 mathematical modules**. Block 15 adds 111 theorem declarations and 13 definitions. All 78 parent mathematical modules are byte-identical. Counts include support lemmas and examples, not independent physical discoveries or a full-edition completion percentage.

Section 6.8 now has actual strong reconstruction for bounded operators, operator-norm reconstruction for compact operators, basis-independent Hilbert–Schmidt reconstruction and domain-correct graph-compatible generator reconstruction. Actual finite-subset cutoff operators supply the needed contraction and self-adjointness. A compact rank-one counterexample rejects reliance on arbitrary strong convergence alone. An exact infinite-tail example has squared HS error (4/3)4^(-M) and operator-norm error 2^(-M).

Read `docs/BLOCK_15_PROOF_GUIDE.md`, `docs/BLOCK_15_DECLARATION_INDEX.md`, `docs/BLOCK_15_FAILURES.md`, `docs/SOURCE_MAP.md`, `docs/CLAIM_LEDGER.json` and `CONTINUE_HERE.md`.

## Reproduce

Restore or reuse the exact Linux/WSL runtime. Its multi-gigabyte bytes are external; SHA-256-verified seven-part assembly support is included.

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

The verifier freshly compiles all mathematical modules and the aggregate with one worker and warnings as errors, audits every inventoried declaration and proof-bearing definition, requires each invalid control's designated diagnostic, and checks all source-preservation layers. Lean is 4.34.0-rc2. Mathlib is aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Nine clean dependency revisions are checked. Imported caches are reused, not independently rebuilt wholesale.

```bash
python3 scripts/package_release.py --out ../Komorebi_Physics_Lean_v0.15.0_Checked_Block_15.zip
python3 scripts/recheck_archive.py --archive ../Komorebi_Physics_Lean_v0.15.0_Checked_Block_15.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /new/extraction --out /external/evidence
```

Packaging refuses an incomplete/non-PASS report or modified proof inputs. A full fresh-extraction verification, not just a ZIP checksum, is required.

## Boundary

The reconstructed topology is explicit. Strong convergence on fixed states is not operator-norm convergence. The compact/HS theorems use self-adjoint contractive cutoffs as a sufficient contract; arbitrary strong convergence alone is not enough. The HS scalar formula is a norm only on the proved square-summable class. Graph reconstruction retains action convergence and domain-valued inputs; it does not assert graph-norm convergence of the generator images.

General spectral/Stone theory, differential-oscillator equivalence, harmonic half-power hierarchy, ladder-product commutators, companion coherent-state weights, nonlinear/dissipative existence, density positivity, entropy endpoints and later gravity/cosmology remain separate. Chapter 3 is not fully inventoried. Section 6.9 historical numerical residuals were not rerun. Formal model results do not establish empirical validity.

Next literal source: Chapter 7 finite pointwise derivation no-go, then matrix corner derivations and exact trace integration by parts.
