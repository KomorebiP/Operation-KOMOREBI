# Audit Report
## Komorebi Information Realization · v0.2.0

**Audit date:** 15 October 2026  
**Outcome:** the supplied finite mathematical claims survived review and expanded testing under their stated assumptions. Three implementation issues were found and corrected. Additional theorems, exact certificates, and seven worked examples were added. All seven final test suites passed in both normal and optimized Python execution.

## 1. Baseline reproduced

The supplied v0.1 probe was executed unchanged. It reproduced its advertised 199,017 finite-map composition checks, 2,000 seeded probabilistic checks, and all six rows of the original three-bit example. Its unchanged source and note are retained in `baseline/`, and the replay output is `reports/baseline_replay.txt`.

This establishes reproducibility of those particular results. It does not validate untested edge cases. In particular, the old randomized generator used strictly positive weights and therefore could not expose failures caused by null observation cells.

## 2. Issues found and fixed

| ID | What failed | Exact reproduction | Correction |
|---|---|---|---|
| BUG-01 | Both scalar MSE and projection-increment functions indexed a conditional-mean entry for a null observation cell. | Two states with probabilities `(1,0)` and distinct observations produce `KeyError: 1`. | Skip null mass in expectations and use a documented arbitrary conditional-mean version on null cells. |
| BUG-02 | The probability interface checked normalization but not nonnegativity. | Probabilities `(2,-1)` passed the normalization assertion and returned optimal error `-1`. | Validate exact nonnegative probabilities/weights with explicit exceptions. |
| BUG-03 | `ceil(log2(k))` is unsafe for a large exact integer alphabet. | For `k=2**53+1`, floating-point logarithms return 53 bits, while 54 are required. | Use `(k-1).bit_length()`. Check boundaries around powers of two through exponent 1024. |

BUG-03 is a latent integer-arithmetic weakness, not a failure reached by the tiny v0.1 map enumeration. BUG-02 concerns invalid input outside the mathematical probability assumptions. None of these three findings disproves the correctly scoped theorems.

Validation and test conditions in v0.2 use explicit checks rather than Python `assert`, so they remain active under `python -O`.

## 3. Expanded checks actually executed

| Test layer | Exact coverage/count | Result |
|---|---|---|
| Structural composition | 521,196 observation/task/coarsening configurations on 1–6 states, up to alphabet relabeling | PASS |
| Constructive minimal repair | 44,168 realization/task pairs, with a decoded reconstruction checked on every state | PASS |
| Weighted finite models | 18,684 models on 1–4 states, all nonzero weight vectors in `{0,1,2}^n` | PASS |
| Independent decoder search | 266,034 explicitly enumerated deterministic decoders across the weighted models | PASS |
| Independent encoder search | 273,316 code partitions evaluated, covering 74,016 message-budget instances | PASS |
| Probability transport | 73,610 deterministic coarsenings checked for exact entropy, risk, and scalar/categorical projector laws | PASS |
| Stochastic extension | All 3,125 binary Markov chains on the specified quarter-probability grid | PASS |
| Linear obstruction bridge | 10,657 exhaustive GF(2)/GF(3) matrix pairs plus 300 seeded GF(5)^4 cases | PASS |
| Predictive refinement | 3,984 exhaustive single-action systems plus 1,000 seeded multiple-action systems | PASS |
| Metamorphic invariances | 1,000 seeded models, tested under relabeling, state permutation, weight scaling, and latent-state splitting | PASS |
| Boundary and adverse tests | 9 invalid generalizations refuted, 3,072 integer bit-boundary checks, 11 invalid-input cases rejected | PASS |
| Worked examples | Seven checked examples, including all 625 signal states and all 60 CRT states | PASS |
| Optimized interpreter replay | All seven suites rerun with `python -O` | PASS |

These counts describe different, sometimes overlapping test populations. They should **not** be summed into a fictitious number of independent experiments or converted into a statistical confidence that a universal claim is true.

Among the exhaustive weighted models, 14,866 contain at least one zero-weight state. Among the Markov models, 2,882 do. This directly addresses the coverage gap in v0.1.

## 4. Why the verification is stronger

The cardinality tests now cover all observation/task partitions on up to six states, rather than only maps into a fixed three-symbol target alphabet. Alphabet relabelings are removed from the partition enumeration. Each state-aware minimal repair is actually constructed and decoded.

The Bayes error formula is compared with explicit decoder enumeration. The optimal repair tradeoff is compared with an exhaustive search over all possible code partitions on the small state spaces. These searches include alternative encoders rather than merely evaluating a chosen construction.

Shannon entropy inequalities are no longer checked using a floating-point tolerance. For integer weights totaling W, the suite computes the exact rational certificate

`2**(W*H(F|R)) = product(W_r**W_r) / product(W_rf**W_rf)`.

Comparing entropies becomes exact rational comparison. Displayed decimal values remain approximations, and 1,341 channel-grid display values were independently cross-checked at 60-digit precision.

Linear tests use three separately expressed views: enumeration of observation fibers, enumeration of the image of the observation kernel, and modular row reduction. The resulting repair rows are then used to reconstruct every task value in the enumerated state space.

Dynamic tests compare iterative partition refinement with product-state reachability. On up to four states they also check minimality against every candidate stable partition.

## 5. Important mathematical additions

The note now proves the full optimal success curve for a state-aware m-symbol repair, not just the alphabet required for exact recovery.

It gives an explicit information valuation of the linear obstruction `F(ker R)`. Its dimension d yields `K=q**d`, and under a uniform finite-field source yields `H=d*log2(q)` and `E=V=1-q**(-d)`.

It replaces arbitrary numerical label encodings with a categorical one-hot projector residual when task labels have no natural metric. The scalar MSE remains available for tasks with a declared numerical geometry.

It proves the scalar and categorical loss identities for finite stochastic channels under a Markov condition, using conditional independence rather than incorrectly assuming nested observation spaces.

It distinguishes unrestricted state-aware repair from restricted encoder access. A five-cycle example requires two state-aware symbols but three target-only symbols. The general access-restricted problem is described through obstruction witnesses and confusability graphs. Only the worked five-cycle access example is exhaustively coded in this release; the graph theorem has a written proof, not a separate exhaustive graph suite.

## 6. Negative controls and boundaries

The package explicitly rejects these false extensions:

1. Zero expected deficit implies pointwise recovery without full support.
2. The projector loss identity holds for arbitrary, nonnested, non-Markov observations.
3. Task information is additive across packets or always has diminishing marginal returns.
4. The minimal alphabet is independent of the encoder's access to information.
5. A sum/difference repair works unchanged in characteristic two.
6. Pairwise satisfiability guarantees global assembly.
7. Tiny Bayes error means no exact obstruction remains.
8. Scalar MSE is independent of numerical task encoding.
9. Injectivity by itself guarantees noise-robust recovery.

All nine are refuted by explicit finite or rational witnesses. A negative control passes when the forbidden generalization fails in the intended example.

## 7. Execution failures and recovery

A combined command replaying the normal and optimized suites exceeded its command time limit during the optimized probability suite. Its partial log is preserved as `reports/optimized_combined_attempt_TIMEOUT.txt`. The normal full replay had completed. The optimized probability suite and remaining suites were then rerun in separate bounded calls and completed successfully. A partial timed-out run is not counted as a completed verification.

The first chart export raised `PermissionError` because the plotting process could not write to the container-created figures directory. The output-directory permissions were corrected, the chart script was rerun, and the resulting three PNG/SVG pairs were inspected. This was an artifact-export failure, not a mathematical test failure.

No theorem-checking assertion failed in the expanded final suites. The baseline input bugs and deliberately false generalizations are recorded explicitly rather than hidden behind that statement.

## 8. Proof and integration status

The general proofs are written in `THEORY.md`. Finite computation corroborates those proofs within declared domains, but it is not a proof for all finite sizes.

Neither `lean` nor `lake` was found on the checked runtime PATH. No Lean compilation was performed, and no uncompiled Lean placeholder is included.

This release does not test the existing production Komorebi signal, arithmetic, or machine libraries directly. The examples are standalone finite realizations. It does not establish novelty or universality. The practical advance is a precisely scoped, executable information layer with quantitative predictions, constructive repairs, and counterexamples that reveal its assumptions.
