# Komorebi Physics — Lean Formalization
## Full edition, checked Blocks 01–03 · v0.3.0

**PASS: 210 theorem declarations, 263 audited named declarations, 15 mathematical modules, 15/15 negative controls.** Block 03 adds **83** theorem declarations. All ten Block 02 mathematical source files remain byte-identical and were freshly recompiled. The total consists of 171 declarations authored in this full-edition program and 39 recovered Paper VII declarations.

The source is the included **550-page Projector-Refinement Physics: Complete Unified Theory**, not the shorter Physics Guide. This release covers Chapter 2 and the selected Chapter 4 extensions under the explicit finite-atlas/bounded-operator and finite-matrix assumptions in the source map. It is not a formalization of all 550 pages.

## Block 03 additions

| Module | New theorem declarations | Content |
|---|---:|---|
| `NonlinearFlow` | 9 | Actual packet-energy derivatives and norm conservation for state/time-dependent skew flows |
| `RefinementTower` | 20 | Associative address maps, incidence matrices and actual coarse projectors, corners, energies and currents |
| `MixedTransfer` | 31 | Actual matrix-trace derivatives, current antisymmetry, positive normalized packet probabilities, pure-state reduction and coarsening |
| `UniversalBalance` | 7 | Actual subsystem/coarse derivatives for source-driven antisymmetric balance |
| `ExtensionExamples` | 16 | Exact mixed density, nonzero currents, derivative witness and hypothesis sensitivity |

The mixed-state continuity equation is derived from the derivative of the original density-matrix curve. It is not a structure field assumed to hold. Probability reality, nonnegativity and normalization are separately proved. Binary weights alone are not treated as a partition, and source terms are not silently cancelled.

Read `docs/BLOCK_03_PROOF_GUIDE.md` for the mathematics, `docs/SOURCE_MAP.md` for equation-to-declaration mapping, `STATUS.md` for exact scope, and `CONTINUE_HERE.md` before continuing.

## Verify locally

Use Linux x86-64 or WSL with the restored exact-pin portable kit:

```bash
bash run_checks.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Equivalent command with an explicit evidence location:

```bash
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_run
```

Lean is **4.34.0-rc2** and Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The verifier checks all nine dependency pins and their tracked clean state, deletes the local build outputs, recompiles all 15 mathematical modules plus the aggregate with one worker and warnings as errors, audits all 263 names in bounded module batches, and checks every invalid control against its intended failure diagnostic. The default command limit is 240 seconds; this release's production run used 120 seconds per command. Timeouts and import failures never count as proofs or successful negative controls.

All active theorem/definition axiom dependencies are restricted to `propext`, `Classical.choice` and `Quot.sound`. There are no active admissions, custom axioms or native-evaluation proof escapes. Structures and proof-bearing definitions are included in the named audit. The imported Lean/Mathlib cache was used, not rebuilt wholesale.

`verification/final/report.json` is the fresh cumulative result. Earlier successful reports, the interrupted baseline attempt, its successful retry, failed development snapshots and corrected successful builds are retained in separate directories. `docs/BLOCK_03_FAILURES.md` explains the distinction.

The multi-gigabyte compiler/dependency runtime is **not** duplicated in this ZIP. Its seven-part assembler and exact checksums are under `runtime_restore_support/`. All seven archived parts were successfully restored in the production session. Their archive availability is not implied by the source-only ZIP itself.

## Recheck a packaged release

```bash
python3 scripts/recheck_archive.py --archive /path/to/Komorebi_Physics_Lean_v0.3.0_Checked_Block_03.zip --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --destination /path/to/new-empty-parent --out /path/to/recheck-evidence
```

The destination must not exist. The script checks ZIP integrity, extracts safely, verifies manifest hashes, invokes the extracted cumulative verifier, then checks hashes again and compares proof-input hashes, counts and axiom dependencies with the packaged final report. The supplied kit is reused only for pinned imported dependencies; local proof outputs are rebuilt.

## Limits and next target

No flow existence/uniqueness, positivity preservation from initial data, infinite-dimensional trace-class extension, unbounded-generator domain theorem, countable-atlas limit, gravity/cosmology proof or observational confirmation is claimed. The affine mixed-state example satisfies the differential equation at one time; it is not presented as a global solution.

Next: Chapter 4.4 tensor-product mixed-state atlases and marginals, followed by actual entropy/moment/Rényi derivatives and Lindblad packet reduction. Chapter 3's independent unit, variational and asymptotic claims still need their own inventory. There is no justified full-edition completion percentage.
