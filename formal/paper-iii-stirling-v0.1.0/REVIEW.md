# Focused Paper III proofreading and counting review

Reviewed source revision: `f49e00d6088bbc8dca4f8a3a70b232db1eea085b`.
The exact manuscript, original statement-register row and their identities are
retained in [CLAIM_MAP.json](CLAIM_MAP.json). This is self-review by the same
assistant that wrote the new formalization; it is not independent peer review.

## Proofreading

Scope: `manuscript/chapters/03_nonlinear_coordinates.tex`, from the block-jet
notation preceding the packet Faà di Bruno theorem through the remark on jet
coordinate dependence. This includes the composition formula and proof,
Proposition 17.6 and proof, structural pruning, and the second-order example.

- Routine edits: none. No objective grammar, typography or LaTeX correction
  was required in this scope.
- Mathematical-token changes: none.
- Local checks: input slots and intermediate labels agree with the displayed
  block notation; referenced theorem labels resolve uniquely; displays and
  theorem/proof environments are balanced in the selected excerpt.
- Ordering: the manuscript chooses increasing least elements for blocks; the
  existing Lean composition theorem chooses increasing greatest elements.
  Each is one representative ordering per set partition. This does not
  multiply the term count by the number of block permutations.
- Unresolved proofreading findings: none in this scope. The broader chapter
  and manuscript have not been proofread by this pass.
- Validation: source identity and selected LaTeX structure were checked. No TeX
  build or PDF rendering was needed because the manuscript was not edited.

## Claim and verdict

**Claim:** For every integer `n > 0` and every finite packet-label type `J`, the
number of pairs consisting of a partition of `Fin n` and one label from `J`
for each block is `∑ k ∈ Icc 1 n, Nat.stirlingSecond n k * |J|^k`.

**Verdict: proved as written**, for Proposition 17.6's count of syntactic
terms. Acceptance is bound to the exact new Lean source and execution receipt.
The result is independent of the vector-space coefficients, projector norms
and differentiability assumptions because it counts the summation index,
before evaluating its summands.

## Dependencies and obligations

| Implication | Evidence | Result |
|---|---|---|
| Canonical partitions extend by a new singleton or membership in one existing block | Pinned Mathlib `OrderedFinpartition.extendEquiv`, `extendLeft_length`, `extendMiddle_length` | Passed |
| Weighted partition-length sums obey the corresponding extension recurrence | New `sum_partitions_succ` | Passed |
| Stirling-weighted sums obey the same recurrence | New `sum_stirling_succ` | Passed |
| The two weighted sums agree for all orders and weight functions | New `sum_partitions_eq_stirling`, with the unique order-zero partition | Passed |
| A partition with `k` blocks has `|J|^k` label functions | Mathlib finite sigma/function cardinalities applied to the actual index type | Passed |
| Removing the zero-block term gives the manuscript formula when `n > 0` | New `card_decoratedPartition_pos` | Passed |
| Nonzero jet values or distinct resulting maps have this cardinality | Not asserted; cancellation and zero constituents may reduce them | Out of scope |
| Full derivative composition, Taylor remainder, or the expanded monograph is newly certified | Not asserted by this companion | Out of scope |

The exact Mathlib source is the pinned
`Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean`, together with
`Mathlib/Combinatorics/Enumerative/Stirling.lean`. No unverified literature
input or finite experiment is used as a proof leaf in the new count.

## Decisive checks and remaining work

The compiler checks the general quantified statements. Kernel replay checks
the new compiled modules against their pinned imported environments. Positive
controls cover the empty order with no labels, first/second/third order with
two labels, and positive order with no labels. Negative controls assert the
wrong factorial-weighted second-order count, omit one partition shape, give
the wrong empty-order count, and attempt an admitted proof. Each must fail for
its declared reason.

The strongest new coverage is the complete counting proposition, including
boundary cases beyond the manuscript's positive-order statement. The packet
Taylor integral remainder and estimate, separate norm corollaries, and later
expanded sections remain open formalization targets. The next appropriate
step is to choose and map one of those exact statements separately.
