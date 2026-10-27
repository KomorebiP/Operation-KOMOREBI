# Core chapter source map and self-review

Authored fragment: `manuscripts/core_chapters.tex` (7 sections, approximately 5,200 words including mathematical source tokens).

All paths below are relative to `source/AVOC_Formal_v0.41.0`. The formal archive is used read-only. The fragment presents selected existing statements and proofs in mathematical prose. It does not add Lean declarations, assert independent novelty, or expand the AVOC acronym.

## Source mapping

| Manuscript block | Formal source and selected declarations | Exact scope |
|---|---|---|
| Deterministic refinement, sufficiency, minimality | `AVOC/Core.lean`: `Refines`, `EncodingEquiv`, `TaskSufficient`, `refines_trans`, `taskMinimal_iff_encodingEquiv`, `target_is_coarsest_sufficient` | Arbitrary types; no cost or efficiency conclusion |
| Exact fiber criterion and collision | `AVOC/Core.lean`: `sufficient_iff_fiber_refinement`, `collision_obstructs_sufficiency` | Nonempty target codomain for total decoder on unreachable states; classical representative choice |
| Reached-state cardinality | `AVOC/Core.lean`: `reachableCard_mono_of_refines` | Finite sample cardinality, while sufficiency itself is universal |
| Joint target | `AVOC/Core.lean`: `sufficient_joint_iff_each`, `joint_target_is_coarsest_sufficient` | Simultaneous decoder choice may be classical; future query family must be declared |
| Deterministic decision value | `AVOC/Blackwell.lean`: `deterministic_policy_lift_value_eq`, `deterministic_blackwell_monotonicity`, `deterministic_blackwell_cost_dominance` | Finite observation/action types; nonempty actions; structural result does not require normalized prior |
| Rational stochastic channels | `AVOC/StochasticBlackwell.lean`: `RationalChannel`, `composeChannel`, `signalActionScore_compose`, `stochastic_blackwell_policy_dominance`, `stochastic_blackwell_monotonicity` | Finite rational channels, normalized/nonnegative channel rows, deterministic action policies |
| Rational Bayes normalization and total update | `AVOC/Bayesian.lean`: `RationalBelief`, `predictiveProb_sum_one`, `bayesUpdate`, `bayesUpdateTotal`, `bayesNumerator_eq_zero_of_predictive_eq_zero`, `bayesianPolicyValue_eq_stochasticDecisionValue` | Positive evidence for ordinary division; total fallback is prior on impossible signals |
| Sequential likelihood identities | `AVOC/BayesianEvidence.lean`: `conditionByWeight_compose`, `evidenceMass_condition_compose`, `conditionByWeight_commute` | Nonnegative likelihood weights and positive stated normalizers; algebraic multiplication needs appropriate joint observation law for physical interpretation |
| Compression/conditioning square | `AVOC/BayesianCompression.lean`: `condition_pushforward_commutes`, `likelihood_factors_iff_fiber_constant`, `likelihood_collision_obstructs_factorization` | Finite raw/quotient spaces and fiber-constant likelihood |
| Rare-evidence posterior flip | `AVOC/BayesianInstability.lean`: `rareLikelihood_pointwise_close`, `rare_evidence_maximal_posterior_flip`, posterior coordinate lemmas | Rational epsilon > 0; uniform binary prior; full L1 convention |
| Deterministic control sufficient fibers | `AVOC/ControlSufficiency.lean`: `ControlSufficient`, `horizonValue_eq_of_controlSufficient`, `qValue_eq_of_controlSufficient`, `bellmanOptimalAt_iff_of_controlSufficient`, `controlSufficient_of_refines_and_transitionClosed` | One global finite action set; dynamic closure needed for refinement |
| Failure of refinement monotonicity | `AVOC/ControlSufficiencyExamples.lean`: `controlSufficiency_not_monotone_under_refinement` | Exact three-state zero-reward example, one action |
| Projected stochastic sufficiency | `AVOC/ProjectedStochasticSufficiency.lean`: `ProjectedStochasticControlSufficient`, `projectedTransitionEquivalent_iff_fiberMassEqual`, `stochasticHorizonValue_eq_of_projectedSuff` | Equality of projected expectations, not necessarily pointwise raw transition rows |
| Exact stochastic quotient | `AVOC/StochasticQuotient.lean`: `quotientStochasticControlSystem_horizonValue_eq`, `quotientStochastic_reward_eq`, `grouped_expectation_eq_raw` | Finite raw and quotient spaces; surjective representation; representative independence asserted only for admissible actions |
| Data-only proof checker | `AVOC/CertificateLogic.lean`: `infer_sound`, `check_sound` | Defined intuitionistic propositional derivation syntax, arbitrary proposition valuation |
| Full identity and once-consumed receipt | `AVOC/ArtifactBinding.lean`: `validate_iff`, `validated_sound`, `generation_mismatch_rejected`, `proof_bytes_mismatch_rejected`, `successful_receipt_not_replayable`, `old_pending_rejected_after_register` | Exact byte snapshots in strings; no hash-injectivity axiom; no arbitrary Lean-proof ingestion or external exactly-once execution |
| Boolean tree semantics and eager cost | `AVOC/BooleanProgram.lean`: `runCount_value`, `runCount_visits`, `check_iff`, `programs_length`, `programs_nodes_bound`, `bounded_grammar_complete` | Three Boolean inputs and given tree grammar; eight input values are exhaustive |
| Budgeted bounded synthesis | `AVOC/BoundedSynthesis.lean`: `search_budget`, `synthesis_sound`, `synthesis_work_nondegrading`, `synthesis_optimal_bounded_grammar`, `insufficient_generation_no_search` | Declared generation and test meters; optimality over examined prefix, or height bound when whole layer fits |
| Six-node to three-node example | `AVOC/SynthesisExamples.lean`: `pair_strictly_smaller`, `pair_generated_replacement`, `pair_search_charge` | Archived exact depth-one search with 85 candidates, budget 10000, charge 6890 |
| Signature compaction | `AVOC/SemanticIndex.lean`: `signature_eq_iff`, `compact_covers`, `compact_origin`, `compact_at_most_256` | Complete truth signature and retained no-larger representative |
| Recursive representatives preserve optimum | `AVOC/RecursiveSynthesis.lean`: `recursive_coverage`, `representative_in_frozen`, `same_optimum_as_frozen` | Depth-specific full grammar coverage and reference fallback; cost optimum preserved, not necessarily identical chosen bytes |
| Instrumented semantic indexing | `AVOC/SemanticSynthesisWork.lean`: `indexed_refines`, `indexed_charge_bound`, `learnedBuild_optimum`, `learnedBuild_capacity` | Emitted entries/node mass/index probes; allocation and wall time outside tariff |
| Global constructor lower certificate | `AVOC/SemanticCostCertificate.lean`: `lower_bound`, `witness_global_minimum`, `cost_is_attained_minimum`, `exact_cost_unique` | Every finite expression in the fixed grammar, no syntax-height restriction |
| Complete checked Boolean closure bank | `AVOC/BooleanCostClosure.lean`: `check_bank_parts`, `query_equivalent`, `query_globally_minimum`, `query_cost_fixed` | Exactly 256 signature rows, exact node witness, unary/binary closure inequalities |
| Affine coefficients and complete probes | `AVOC/AffineSignature.lean`: `eq_iff_zero_basis`, `eq_iff_eval`, `mismatch_witness`, `checkProbes_iff`, `probe_count` | Ring coefficients, affine language only; dimensions fixed; coefficient equality decidable for executable checker |
| Typed affine normalization and replacement | `AVOC/TypedAffineProgram.lean`: `normalize_correct`, `normalized_iff_equivalent`, `context_congr`, `context_cost_mono` | Matching typed dimensions and declared additive tariff |
| Dense fusion and campaign threshold | `AVOC/AffineFusion.lean`: `fuse_correct`, `chooseNoSlower_cost`, `bottleneck_fusion_cost_increases`, `beneficial_fusion_break_even`, `beneficial_fusion_strict_gain` | Dense scalar tariff; normalization excluded from per-call selector but included in campaign comparison |
| Certified rank factorization | `AVOC/AffineFactorization.lean`: `valid_rank_exact`, `width_minimal`, `two_stage_cost_minimal`, `checked_optimal` | Field coefficients; exact affine offsets; rank witness LAH=I; minimum among exact two-dense-stage affine factorizations |
| Rank-one finite field example | `AVOC/AffineFactorExamples.lean`: `rankOne_check`, `rankOne_execution_costs`, `rankOne_checker_charge`, `rankOne_amortization` | F5 example, 4x4 all-ones linear matrix, width 1, costs 36/21, check charge 105 |
| Cost menu and exploration accounting | `AVOC/AffineFactorChoice.lean`: `choose_le_any_two_stage`, `choose_menu_member`, `amortization_iff`; `AVOC/AffineReuse.lean`: `choose_cost_exact` | Current/fused/factored menu and all exact two dense stages, not arbitrary sparse/shared or hardware programs |
| Offset-retargeted imported reuse | `AVOC/AffineReuse.lean`: `retarget_valid`, `retarget_overwrite`, `importFor_iff`, `import_invalid_rejected`, `import_wrong_linear_rejected`, `reused_choice_correct` | Revalidate stored certificate; exact current linear matrix equality; retain first offset and compensate second offset |

## Expository examples

Three small examples are elementary worked applications, not additional Lean theorems: Boolean task collisions for AND versus XOR, binary prediction with alternative acquisition prices, and scalar affine zero-probe omission (`f(x)=x`, `g(x)=2x-1`). Their complete derivations are written in the manuscript. All larger numerical claims above directly match named archived declarations.

## Proof and interpretation boundaries checked

- The fiber criterion's nonempty target hypothesis and classical choice are explicit.
- A coarsest sufficient target is an information-order statement, with no implied shortest file or efficient decoder.
- The stochastic information-value theorem is a garbling domination direction only. No converse classification theorem is claimed.
- Bayesian weight products are algebraic likelihood operations, not an unqualified independence assertion about reports.
- Control sufficiency uses common action feasibility; dynamic refinement counterexample is preserved.
- Stochastic quotient equality is finite-horizon expected value in the declared model.
- Receipt byte identity does not authenticate external facts or establish a parsed-source-to-formula correspondence.
- Boolean global minimum belongs to the three-input AST language and node tariff; bounded synthesis and global closure certification are distinguished.
- Exact affine zero/basis probes are valid only in the affine language over the stated ring.
- Rank width is minimum among affine bottlenecks. Two-stage dense tariff optimality is not universal affine circuit optimality.
- Retargeting preserves the first-stage offset and subtracts `V*u0` from the new second-stage bias.
- Source files were not changed, and no fresh Lean compilation is claimed.

## Conservative mathematical proofreading

Mode: self-review of the full newly authored fragment under `mathbox:proofread-math`.

- Routine edits: checked grammar, theorem/premise scope, math punctuation, indexing conventions, and separation of expected model quantities from physical outcomes.
- Mathematical-token changes: none after drafting.
- Unresolved issues: root integration must supply theorem environments and the promised macros `R`, `Q`, and `N`; these are preamble obligations, not additional mathematics. No external citations were introduced.
- Validation: structural source check PASS for balanced braces, all 42 paired mathematical environments, 10 unique labels, and all local references. Exact tariff arithmetic for the fusion and rank-one break-even examples also PASS. Compilation intentionally left to the root's shared publication build.
- Coverage: all of `core_chapters.tex`; formal Lean source was read for provenance, not freshly recompiled.
