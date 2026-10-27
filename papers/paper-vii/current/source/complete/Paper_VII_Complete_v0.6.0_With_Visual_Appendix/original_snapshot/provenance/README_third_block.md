# Projector-Resolved Seed Calculus VII
## Checked third block · v0.3.0

**Author: Komorebi P.**

This cumulative release adds five checked finite manuscript items. **All 12 active modules passed a fresh Lean run**, with **146 theorem declarations audited**. This is not a claim that the entire original manuscript or its continuum conjectures is verified.

| Measure | First block | Second block | Third block, cumulative |
|---|---:|---:|---:|
| Named finite items checked | 6 of 19 | 11 of 19 | **16 of 19** |
| Named finite items remaining | 13 | 8 | **3** |
| Lean theorem declarations | 32 | 82 | **146** |
| Active Lean modules | 4 | 9 | **12** |
| Continuum conjectures proved | 0 of 5 | 0 of 5 | **0 of 5** |

Declaration counts include supporting lemmas and concrete specializations. They are not counts of separate manuscript theorems or a difficulty-weighted completion percentage.

## New checked results

| Item | Result | Module | New declarations |
|---|---|---|---:|
| 2.1 | Actual matrix orbit dimension and cyclicity | `SeedOrbit.lean` | 8 |
| 2.2 | Sharp minimum seed count in a finite direct sum | `SeedOrbit.lean` | 13 |
| 2.3 | Local tensor orbit, Schmidt rank, and reduced support | `SeedOrbit.lean` | 13 |
| 3.1 | Finite-order complex character projectors | `CyclicProjectors.lean` | 18 |
| 10.1 | Actual Euclidean matrix exponential | `EuclideanTransfer.lean` | 12 |
| | **Total added** | **3 modules** | **64** |

The declaration grouping within `SeedOrbit.lean` is bookkeeping. Its results reuse one another.

### Orbit and seed rank

The one-seed orbit is defined using actual products `A * C`. An explicit linear equivalence with independently chosen rows proves its dimension is `d * rank(C)`. The source proves that k seeds generate exactly when their stacked coefficient matrix has full column rank, constructs generating seeds whenever `m <= k*d`, and proves the sharp finite direct-sum minimum as an `IsLeast` statement. All algebra block dimensions must be positive. Empty block families have minimum seed count zero.

### Schmidt rank and reduced support

The coefficient equivalence is connected to the actual Kronecker action `(A tensor I) psi`. Schmidt rank is independently defined as the minimum number of product-vector summands, not defined to equal matrix rank. A factorization lower bound and row-space-basis construction establish equality with rank(C). The reduced B matrix is defined by the actual partial-trace sum. For these coefficient conventions it equals `transpose(C) * adjoint(transpose(C))`, not `adjoint(C) * C`. Its rank and full support yield the local-orbit criterion. An orthonormal Schmidt decomposition is not separately constructed in this release.

### Cyclic packets

The standard primitive additive character and the actual powers `S^val(r)` produce the Fourier projectors. The source proves the exact exponential-root coefficient formula, finite character sum, product law, completeness, eigenaction, and self-adjointness for unitary S. A concrete complex-matrix theorem collects these properties. The proofs cover every positive N, including N=1.

### Euclidean transfer

The transfer operator uses the actual power-series exponential. Its equality with continuous functional calculus is proved before using spectral mapping. The ground energy is the actual minimum of a nonempty finite eigenvalue set. Positive definiteness, semigroup composition, and both real and complex spectrum containment in (0,1] are checked. Nonnegative time is needed for the upper spectral bound; semigroup composition holds for all real times.

## Fresh cumulative verification

Runtime: **Lean 4.34.0-rc2**. Pinned Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Every active module returned exit code **0** with warnings treated as errors. All 146 theorem declarations have matching `#print axioms` output. No declaration depended on an axiom outside `propext`, `Classical.choice`, and `Quot.sound`.

The active sources have no admitted proofs, new `axiom` declarations, `unsafe`, or `native_decide` tokens after comments and strings are stripped. Both deliberately invalid controls were rejected: the false equality and the admitted-proof placeholder. Negative controls and unsuccessful development drafts are not active proof modules.

The current run is `verification/third_block_release_run/SUMMARY.json`. It contains exact commands, source and log hashes, compiler exit codes, per-module timings, and every declaration's axiom dependencies. The nine upstream modules and original manuscript are byte-preserved, as recorded in `verification/UPSTREAM_PRESERVATION.json`.

The restored portable runtime's archive and part checks are recorded in `verification/third_block_runtime_restore.log`. Imported dependencies were reused. They were not independently rebuilt or rechecked from scratch.

## Reproduce

Use the previously delivered portable Linux kit. From this extracted release folder:

```bash
python scripts/verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_rerun
```

For a host with a short command limit, repeat this checkpointed command until `COMPLETE PASS`:

```bash
python scripts/verify.py --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/local_rerun --max-checks 3 --resume
```

Exit code 2 is a deliberate incomplete checkpoint, not PASS. Exit code 1 is failure. Exit code 0 means the complete run passed. Resume checks source, log, runner, runtime and theorem inventory consistency. Use a fresh output directory and omit `--resume` to request an entirely fresh run.

The low-memory launcher captures Lake's environment before starting Lean and uses one Lean worker. Module imports reduce unnecessary imported information. These settings do not change kernel proof rules and do not themselves impose a RAM cap.

## Manuscript, provenance and development failures

`manuscript/Paper_VII_Third_Lean_Block_Supplement.pdf` explains all five new results, explicit assumptions, the trust boundary, and the remaining work. The original PDF and TeX are unchanged. The first and second supplements remain included. The cumulative ledger is `THEOREM_LEDGER.json` and `.md`.

Initial drafts failed on imports, elaboration, finite-sum rewriting, complex conjugation and warning diagnostics. Captured source snapshots, failed logs and successful development checks are preserved in `verification/third_block_development/`. The final cumulative run is separate. Current development notes are in `verification/DEVELOPMENT_HISTORY.md`. Historical second-block front matter and metadata are in `provenance/`, clearly named as historical.

## Still unchecked

**Three named finite items remain:** 5.2 quantitative commutator leakage, 6.4 manifold projected connection and curvature, and 8.1 the finite Knill–Laflamme necessary-and-sufficient criterion. These are substantive unfinished results, not automatically covered by exact symmetry, finite projector derivatives, or complete positivity.

**Conjectures 12.1–12.5 remain unproved.** The original numerical suite was not rerun, and Papers I–VI were not rebuilt. Kernel checking of the exact propositions is not a guarantee that every sentence, numerical certificate, figure or physical interpretation in the unchanged manuscript has been validated.
