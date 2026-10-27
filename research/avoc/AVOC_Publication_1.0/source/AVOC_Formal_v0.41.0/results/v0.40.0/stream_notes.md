# Observation-stream derivation

`AVOC/ObservationStream.lean` contains 24 proved theorems. It derives the binomial success-count law from a primitive outcome process, then supplies ordered-list and shared-source prefix interfaces for the reveal/calibration composition.

The primitive `ConditionalLaw` is a division-free conditional independence contract: after every finite revealed pattern, a fresh coordinate has success event mass p times the history event mass. This explicitly includes zero-probability histories. It is an assumption on the source law, not something established by logging or marginal success frequencies. `conditional_pattern_mass` proves all pattern probabilities by finite-set induction, and `conditional_implies_product` obtains exact vector-product probabilities. `vectorMass_card_sum` derives the binomial coefficient by counting success-position subsets. `count_fiber_eq_binomial` and `conditional_count_fiber_eq_binomial` then obtain the count-law premise needed by v0.39 calibration.

`bernoulliLaw` supplies an explicit normalized rational product model for every n and p in [0,1]; `bernoulliLaw_product` proves its full-vector contract. `fairOne_conditional` gives a concrete nontrivial n=1 model of the conditional contract. The general converse ProductLaw -> ConditionalLaw was not added; it is not required by the integrated direction.

`sampleList` is the ordered Boolean-list representation, with exact length and success-count identities. `truncateSample`, `conditional_truncate`, `sampleList_truncate`, and the two prefix count-law theorems let multiple predetermined sample sizes share one per-identity latent source. Checkpoints can be dependent; independent checkpoint counts are not asserted.

`correlatedPair_marginal` proves each of two perfectly correlated bits is fair. `correlatedPair_one_success_mass` gives count-one mass 0, whereas the binomial mass would be 1/2. `correlatedPair_not_product` therefore rejects replacing the conditional/joint contract with marginal frequencies alone. The negative test `FalseEqualMarginalsIndependent.lean` deliberately attempts the impossible binomial count-one equality and must fail mathematically.

## Limits

No sampling independence, stationarity, fault neutrality, or historical precommitment is inferred from actual logs. Every result is on a finite rational probability space. The prefix results require a predetermined n <= N. Conditioning on run completion is not justified by these theorems. Operational censoring/fault rules and safe gating are separate composition obligations.

## Validation and development record

Final positive compile: `stream_12.log` / matching JSON, warnings as errors, pinned Lean 4.34.0-rc2, no timeout. Exact source SHA-256: `956cc267a0e3173537ea1870e73c1fc7f14649302c881503e9b7844404a9b096`.

Retained failed attempts: stream_01 (cardinality simplification and consequent downstream elaboration failure), stream_03 (function-composition simplification), stream_04 (complement-cardinality lemma plus deprecated tactic lemma names), stream_07 (dependent tuple-prefix elaboration), stream_10 (tactic tried a closed goal), stream_11 (unused simp argument warning). Successful intermediate revisions: stream_02, 05, 06, 08, 09, 12. No false mathematical conjecture was used in a positive theorem. No project axioms, admitted proofs, native_decide, or unsafe declarations were introduced.
