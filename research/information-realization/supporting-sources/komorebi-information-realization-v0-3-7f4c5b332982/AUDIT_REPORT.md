# Audit and verification report
## Information Realization and Obstruction · v0.3.0

**Date:** 15 October 2026  
**Result:** all five new suites passed in normal and optimized Python. All seven original v0.2 suites were replayed successfully in normal Python. New worked examples passed in both modes.

## 1. What changed

The release adds an exact single-encoder linear repair construction with explicit access constraints, graph-based access verification, transfer leakage calculations, predictive closure certificates, and an adapter to the actual Komorebi Math Haar packet implementation. The preceding code, documentation, and evidence are retained under `prior_v0_2/`.

The principal theorem is that, on a full finite-field vector space with linear task, observation, and encoder access, exact repair is feasible iff ker R intersect ker U is contained in ker F. When feasible, d independent linear message coordinates attain the q^d alphabet lower bound, with d = rank[R;F] - rank R. An impossibility witness is returned otherwise.

## 2. Completed new checks

| Layer | Coverage | Outcome |
|---|---|---|
| General access graphs | All 144,117 observation/task/access partition triples on 1–5 states | PASS |
| Independent graph optimality oracle | 3,509 instances on up to 4 states, evaluating 13,813 encoder partitions | PASS |
| Linear restricted repair | All 26,918 row-space triples in the declared small-field/dimension families | PASS |
| State-by-state constructive repair | 419,851 decoded source-state checks in feasible exhaustive cases | PASS |
| Nonlinear comparison oracle | 1,132 encoder partitions for small helper alphabets | PASS |
| Redundant linear maps | 1,200 seeded cases, 19,780 decoded-state checks in feasible cases | PASS |
| Transfer composition | All 6,817 ordered pairs of 2-by-2 matrices over F_2 and F_3 | PASS |
| Predictive closure | 8,758 exhaustive single-action systems | PASS |
| Closure minimality | 134,388 candidate-subspace comparisons | PASS |
| Closed-state transition oracle | 70,230 exhaustive state-transition checks | PASS |
| Multiple actions | 400 seeded two-action systems, 40,000 trajectory steps | PASS |
| Native Haar export | 51 complete-pruning matrices, 391 native impulse columns | PASS |
| Native synthesis | 255 pruned reconstructions | PASS |
| Native/modular integration | 7,060 native analyses, 45,184 observation/task/state cases | PASS |
| Boundary tests | Access impossibility, partial-budget penalty, energy/information separation, invalid inputs, mutated certificate, bad field, unsupported pruning, precision guards | PASS |
| Worked shift example | All 625 F_5^4 sources and 7,500 trajectory steps | PASS |
| Optimized execution | All five new suites and new worked examples rerun with python -O | PASS |

These populations overlap and should not be summed as independent experiments. Exhaustive claims always refer to the explicit bounded family, not every possible dimension or graph.

The row-space families are F_2 in dimensions 0–3, F_3 in dimensions 1–3, and F_5 in dimension 2. Arbitrary redundant-row seeded cases cover fields 2,3,5,7 and dimensions 0–7. The exhaustive linear cases include 17,634 feasible and 9,284 inaccessible instances. Direct observation/task fibers independently determine feasibility and alphabet sizes.

The graph suite validates feasibility and constructive decoding for every case through five states. Its independent search over **all encoder partitions** is limited to cases through four states. It would be inaccurate to describe the larger population as independently exhaustive chromatic-minimality verification.

The native/modular state tests use all 81 F_3^4 states and all 625 F_5^4 states, all 16 retained-coordinate subsets, and all four cyclic shifts. The decoder receives only the retained tuple and the permitted code. Full tree objects and source states are kept in the test harness, not passed to the decoder.

## 3. Replaying the preceding release

All seven v0.2 suites were called from the unchanged original source: structural, probability, Markov, linear, dynamics, metamorphic, and negative controls. New replay outputs are `reports/v02_replay_*.json`; original reports remain under `prior_v0_2/reports/`.

The replay reproduces the original finite-map counts, rational probability checks, Markov boundaries, linear examples, predictive partitions, and metamorphic controls. This continuation does not claim a fresh optimized replay of v0.2: optimized execution was newly run for the five v0.3 suites and the new worked examples. The original v0.2 optimized logs are retained as prior evidence, not counted as new executions.

## 4. What the integration actually validates

The unchanged wheel is `komorebi_math-1.0.0b4-4b21-py3-none-any.whl`, SHA-256:

`a7b41efe91524ad1e6e641b0567b571a04247c0b17994c1d019e7d6ac2c4e52d`

Its `wavelets.py` Git blob is:

`db646e04f6d3d67ecf22a4eee7376647e7ae598f`

That blob matches the file returned by the connected GitHub read during this continuation. The adapter verifies the whole wheel digest and the selected source hashes. It imports the real module from that wheel without installation or modification. A different preimported library instance is rejected.

This is not a latest-repository-wide audit. The entire repository, all dependencies, other public APIs, and every release claim were not tested. The adapter's tested route is the Haar packet construction and its finite linear export.

Native code uses floating arrays even in unnormalized mode. Exact arithmetic is supplied by a separate prime-field implementation, not retroactively attributed to the native library. Native impulse outputs are compared with an independent integer recurrence. Actual input checks are bounded so every relevant integer sum is exactly representable, and outputs are checked before modular reduction. The adapter rejects noninteger and overly large data instead of silently converting rounded results to exact integers.

A complete packet pruning is not erasure. The native tree retains the source and all nodes, so using it as a decoder input would leak unavailable information. This release explicitly separates packet extraction, allowed encoder input, and decoder input.

## 5. Mathematical boundary results

The general-access theorem has constructive graph checks, while the linear specialization has exact algebraic certificates and fiber-based verification. A mutated encoder certificate is rejected.

The Haar shift example needs one coded field coordinate from two hidden detail coordinates. Selecting raw detail coordinates requires both. At the native API level those two coordinates inhabit one detail leaf, so the result is not reported as a reduction from two native leaf packets to one.

Two individually nonzero transfer leakage blocks can cancel in a composite: 1,004 exhaustive transfer pairs exhibit this. Endpoint deficits are not monotone across different target horizons. Entire-trajectory deficits remain nondecreasing. The theory and examples distinguish these different tasks.

The full-support GF(3)^2 example has no exact-alphabet access penalty, but a two-symbol partial-recovery penalty of 1/15. This rejects an unsupported extension of the exact theorem to every probabilistic budget.

The energy examples preserve two noiseless missing task bits while detail energy falls by many orders of magnitude. They separate task distinguishability from energy, but do not assert robustness against physical noise or finite measurement precision.

## 6. Failures, corrections, and recovered execution

No final mathematical test condition failed in the completed new suites. The following operational and development failures did occur:

1. A direct container Git read failed because the host could not be resolved. The connected GitHub file read succeeded, and the executable source was obtained from a visible Library wheel.
2. A direct raw-file download was rejected by the download tool's URL validation. That route produced no usable source. The Library materialization route supplied the pinned wheel instead.
3. The first authoring-time syntax check found an unmatched parenthesis in the new test file. The expression was rewritten using a separate helper binding before the suites were run. This was a test-code syntax defect, not a mathematical counterexample.
4. One combined command containing prior replays, native tests, and an optimized replay exceeded its 60-second command limit during the optimized transfer/closure suite. The completed reports were inspected, the partial log was preserved in `reports/v03_combined_attempt_TIMEOUT.txt`, and unfinished optimized suites were rerun separately. Final complete normal and optimized v0.3 runs also succeeded. The partial run is not counted as a complete verification.

The complete successful final logs are `reports/v03_final_normal_execution.txt` and `reports/v03_final_optimized_execution.txt`. The old logs and intermediate successful runs are retained for traceability.

## 7. Environment and proof status

The executed environment is recorded in `VERIFICATION_SUMMARY.json`: Python 3.13.5, NumPy 2.3.5, Linux. This is not a Windows execution certificate. The Python sources are portable, but this block did not validate a Windows installation.

Neither `lean` nor `lake` was found on the checked PATH. No Lean compiler was run. No uncompiled Lean placeholder is included. General mathematical proofs appear in `THEORY.md`; finite computations corroborate those proofs in the stated domains and validate concrete certificate production.

The remaining obligations are formal proof compilation, numerical stability and noisy real-signal models, and separately justified extensions beyond one encoder/one decoder. The present integration supplies a reproducible finite information-theoretic interpretation of an actual packet construction, not a completed universal theory of information.
