# Computability route return

Base: checked Realization Boundaries Lean v0.6.0. Target contracts: monograph 3.3–3.4 and 8.1–8.4. Parent source and publication were read before development. This route owns `ComputablePresentations.lean` and `ComputableQuotientCodes.lean` only.

## Exact new evidence

`ComputablePresentations.lean` proves native Mathlib oracle-recursion closure under total composition, pairing, primitive recursion and terminating minimization. `selectorOracle`, `OracleComputable` and `SelectorReducible` use Mathlib's actual `Nat.RecursiveIn` and `TuringReducible`, rather than a computability label on a classical definition.

`OracleGroupCopy` has bijective Nat names and oracle-computable addition. Equality is literal Nat equality. Repeated addition is proved oracle computable by native primitive recursion. The candidate root test computes the actual production nth prime using `computable_primeAt_value`, supplied independently in `PrimeComputability.lean`.

The actual root candidate test is combined into two complementary positive searches. Their totality is proved from the existing exact prime-root theorems. `oracle_marked_copy_reduces` proves the uniform marked lower bound in 8.2. `oracle_unmarked_copy_reduces` and `oracle_copy_exists_implies_selector_reducible` prove the forward implication of 8.3 for a genuine computable Nat copy. The abstract copy isomorphism nonuniformly supplies the natural name of the distinguished element; that finite natural is hard-coded into the oracle program. There is no uniform marker-finding claim. A separate native finite-table/tail-recovery theorem is also proved.

Relative enumerable sets are actual domains of native partial oracle-recursive functions. `oracle_copy_primeSpectrum_enumerable` semidecides the existence of nonzero prime torsion by candidate tests and minimization. `oracle_spectrum_copy_implies_enumerable` proves the forward 3.3 implication for Nat-domain copies of the actual `spectrumSubgroup B`. Finite groups require a finite-domain convention separately.

`ComputableQuotientCodes.lean` removes the need for canonical raw encodings. `OracleRawGroupCodes` requires a surjective Nat enumeration, zero/addition code operations, and an oracle-computable equality test whose zero value is proved equivalent to equality of the actual meanings. For an infinite group, the file proves `toOracleGroupCopy` and `oracleGroupCopy_of_rawCodes`. Native finite products test least representatives, native finite counts and terminating minimization compute their increasing enumeration, and a further terminating search gives each raw code its unique canonical Nat name. The resulting addition respects actual group addition and is native oracle computable.

## Coverage boundary

- 8.2: full marked decoding contract checked.
- 8.3: forward implication checked. Reverse construction is owned by `ComputableNormalCodes.lean`; this return does not claim it complete.
- 8.1 and 8.4: not closed by this route alone.
- 3.3: forward semidecision checked for infinite Nat copies. Enumerable-selector construction and finite-domain convention are outside this return.
- 3.4: owned separately by `SpectrumComputability.lean`.

## Verification

Final production compile receipts:

- `verification/development/ComputablePresentations_016.json`: exit 0, warning-as-error, automatic implicit parameters disabled.
- `verification/development/ComputableQuotientCodes_010.json`: exit 0, warning-as-error, automatic implicit parameters disabled.

The coordinator's immutable full audit remains authoritative for release. Earlier failed development compilations are retained as development evidence and are not represented as accepted proof results.

## Exact source hashes

- `RealizationBoundaries/ComputablePresentations.lean`: `f51b96aa3871c4dde05879d132c861f7d8382f82fdcbcb53e7f2276cbb742219`
- `RealizationBoundaries/ComputableQuotientCodes.lean`: `1e476f875f0917cdcaf3292c399ddbb83b3dacca080c7cbd2c2faec57da32757`
- `RealizationBoundaries/PrimeComputability.lean`: `55bc437c950eafb805b8ad812d00250f268d3f95ad3d42336b30f430ff379511`
- `RealizationBoundaries/SubgroupSpectrum.lean`: `cc4356c4a4f9b8ed1054e39b72fb62c822c6602c4703e3444c4dd4649ca53f69`

## Next dependency

Concrete raw normal-form arithmetic and equality must instantiate `OracleRawGroupCodes` using a proved native algorithm. Once that is checked, `toOracleGroupCopy` and `oracle_unmarked_copy_reduces` give the exact upper/lower oracle equivalence without any change to the copy semantics.

## Subsequent closure: the native enumeration normal form

`OracleEnumerationNormalForm.lean` now proves `recursiveIn_has_graphSearch` and `oracleEnumerable_has_total_search` for the actual native `Nat.RecursiveIn` domain definition. The former is an induction over every native oracle-recursion constructor. It builds total oracle-computable natural certificate verifiers for graphs, including primitive recursion and minimization. Primitive recursion checks a finite list of intermediate states and child certificates. Minimization checks every earlier defined nonzero output and the final zero. No behavior after the successful bound is required. All finite loops are certified by native primitive recursion.

The pure semantic trace lemmas are supplied independently in `OraclePartialRecursionTraces.lean` and `OraclePartialMinimizationTraces.lean`. The final result converts relative partial-recursive domains into genuine total stage-search tests. Together with `SearchEnumerableSpectrum.lean` and `ListingSearchEquivalence.lean`, it connects the native-domain, positive-search, and literal finite-listing conventions; the latter modules own the resulting exact 3.3 theorem.

Final compile: `verification/development/OracleEnumerationNormalForm_009.json`, exit 0, 2.70 seconds. Earlier failed elaborations are development records. The final proof uses default heartbeat bounds; explicit intermediate types removed the development-time elaboration bottleneck.

- `RealizationBoundaries/OracleEnumerationNormalForm.lean`: `1f271d55166e8766314516e4e8aede4b7b852d646a57d5c50b6b50cb94d90d09`
- `RealizationBoundaries/OraclePartialRecursionTraces.lean`: `172328b148f24cca56ba2f2fc51925aa489336e715b3f3a0957a5cb8fc20ac83`
- `RealizationBoundaries/OraclePartialMinimizationTraces.lean`: `0166b56a8768bb2539e97eb03f16e9b4f48748229f84e6ac04b33666000a168d`

## Exact operation graph degree

`AdditionGraphDegree.lean` supplies the ordinary graph-oracle convention for total functions. The graph computes the unique output by a native terminating minimization; a computed function computes its graph by a finite equality test. `operationGraph_reducible_iff` proves equivalence of these conventions. With the independently supplied `CanonicalOperationDegree.lean`, `canonicalPairedAddition_graph_equivalent` identifies the actual canonical addition graph's native Turing degree with the selector oracle. This checks the exact-operation part of 8.1 separately from abstract least presentation degree.

Final compile: `verification/development/AdditionGraphDegree_002.json`, exit 0, 2.51 seconds.

- `RealizationBoundaries/AdditionGraphDegree.lean`: `659c840acde911418032e38ac599d9f40f7fcf5c9c208ad04e7c642a5362c5f9`
- `RealizationBoundaries/CanonicalOperationDegree.lean`: `eadfa32bff8aebc76a5a051be569d3adda06df81728cb26418e0af3024d37c75`
