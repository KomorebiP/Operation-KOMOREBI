# Block 04 — assumption and source review

**Source:** Reviewed Core 0.2, Proposition 3.8 (printed pages 13–14, physical pages 17–18) and Proposition 5.6 (printed page 22, physical page 26).

## Core 3.8

- The fine and coarse distributions live on explicit finite types. The state map is supplied. The new bound does not require it to be surjective; the book's surjective case is covered by specialization.
- `Instrument.Law` supplies nonnegativity and full report/successor normalization. No separate report and transition marginals are substituted.
- At every time, all relevant action/fine-state rows satisfy the stated complete joint-row bound. The code states the stronger all-represented-row premise, not a sample-based estimate.
- The fine and coarse policy is the same `Instrument.Policy`, using only previously observed action/report pairs. Coarse-state coordinates inside a mathematical path do not become policy inputs.
- The actual fine state evolves first; projection occurs on its constructed complete path. No lumpability or Markov assumption is silently imposed on the projected fine process.
- Initial law discrepancy is separately included. Equality of final-state marginals does not imply equality of full paths.
- Both distributions at every horizon are normalized by a proof. Positivity of the final error allowance follows from the TV bound; it is not assumed to fix an inconsistent negative allowance.
- The conditioning event is the same event on the common coarse path space. Both masses must be positive. Projection after conditioning supplies the final-state result. The theorem in fact allows any common finite event, including the observed-history events in the source.
- The denominator is `max(P(E),Q(E))`, with coefficient one. The complement contribution, rather than an unsharp free triangle estimate, proves it.
- Inferred counterpart positivity requires strict inequality. Zero-event algebra is never described as a posterior.

## Core 5.6

- Policies belong to the same finite catalogue in both models. Catalogue membership represents the externally specified admissibility requirement; the approximation theorem does not infer permissions.
- Every individual policy uses the same loss function across its two models, on the same common path space. Distinct policies may have distinct functions. Losses must be bounded between zero and B with B nonnegative.
- The comparison is uniform on that entire catalogue. Checking one baseline is not enough to protect a newly selected policy.
- The selected policy minimizes approximate risk on the common catalogue. The existence theorem constructs actual finite minimizers, with classical choice; it is not an efficient optimizer.
- Each fixed policy is compared with itself before its optimality inequality is used. `history_selected_policy_regret` obtains the uniform law premise from the actual whole-history construction.
- A finite stopping-tree class may be represented by its actual common stopped/padded path distributions and complete losses. This block proves the source implication for such distributions and directly for observed-history policies. It does not export a universal host-tree-to-absorbing-process compiler. Any padding must preserve the chosen policy's loss and law.
- Bounds on expectations do not certify a hard resource cap, zero-probability safety, or fairness. A report probability zero under one model may become small but positive under the other.

## Source and code alignment

No mathematical statement in the source book was changed. All fourteen prior substantive modules and the inherited API check retain their Block03 hashes. The new API check restates the source-facing bounds independently of their implementations. The two source promotions are exact and the other sixteen unformalized result records are retained.

The four new modules contain 85 authored theorem declarations: supporting finite-sum lemmas, general source-facing results, and exact examples. This is not 85 new manuscript results. Their transitive axiom dependencies are checked for all elaborated project theorem constants, including generated auxiliaries.

## Proof review route

Read `Variation.push_kernel_step`, `restricted_discrepancy`, `normalize_bound`, `condition_bound`, and `expectation_bound`; then `ApproximateHistory.law_succ`, `stepRow_error`, `pathKernel_error`, `whole_history_bound`, and `conditional_final_bound`; finally `ApproximateDecision.uniform_policy_regret`, `minimizing_policies_exist`, and `history_selected_policy_regret`. The exact examples and negative fixtures address the omitted-premise alternatives.

The new statements received internal proof and interface review. The retained modules received exact preservation and fresh kernel checks, not a new independent semantic review of every old interpretation. There is no independent proof-kernel implementation or external peer-review claim.
