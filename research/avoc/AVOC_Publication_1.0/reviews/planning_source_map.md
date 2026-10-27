# Planning chapter source map

Publication input: `manuscripts/planning_chapters.tex`.
Authoritative source root: `source/AVOC_Formal_v0.41.0`.
Read the current `FORMAL_THEORY.md`, `PROOF_BOUNDARY.md`, and `GAP_LEDGER.md`
before authoring. No Lean source was changed and no new Lean theorem was added.

## Claim-to-source mapping

| Publication claim | Source module / declarations | Status and exact boundary |
|---|---|---|
| State-dependent Bellman recursion and optimal complete adaptive tree | `AVOC/GuardedControl.lean`: `value`, `qValue`, `planValue_le_value`, `optimalPlan_value`, `safe_optimal_plan_exists` | Prose reconstruction of archived formal statements. Finite feasible sets and finite observations, state space can be infinite. Every branch legal, including zero-probability branches. |
| Lazy warm inspection/cold generation | `AVOC/LazyStagedControl.lean`: `actionList`, `probability`, `step`, `reward`, `evaluated_value_exact` | Acquisition charges on both success and rejection; deployment requires ready state. h continuation steps means h+1 total at first choice. |
| Artifact-backed 133/196 vs 15000 | `AVOC/RobustQuoteExamples.lean`: `exactModel`, `exactRealization`, `exact_recovers_v037`, `artifact_refines_deterministic_fields` | Source gross for 1000 calls, symbolic model rather than measured savings. Scores 14867/14804 are prose arithmetic from exact model at two total actions. |
| Executable workflow correspondence | `AVOC/WorkflowPlanner.lean`: `model_realizes`, `model_branch_bound`, `executable_policy_source_safe`, `executable_policy_regret` | Same information regime; work counter abstract evaluator nodes, not wall-clock/rational bit complexity. |
| Protected quote identities, bands, conservative nominal realization | `AVOC/QuoteAuthority.lean`: `Identity`, `RawQuote`, `validate`, `nominalQuote`; `AVOC/RobustQuotePlanning.lean`: `trueSystem` | Exact evidence equality; true system keeps nominal guards and upper-setup reservations. |
| Primitive radius, expectation transport, value/Q enclosure | `AVOC/RobustQuotePlanning.lean`: `reward_close`, `probability_l1_le`, `expectation_transport`, `value_error`, `local_q_error`, `value_between`, `q_between` | Prose reconstructions. Epsilon sums setup/gross widths; delta twice sum probability widths; M sum upper setup/gross. |
| Distinct competitor dominance | `AVOC/CalibrationBridge.lean`: `competitor_dominance_sound`, `self_comparison_forces_zero_radius` | Distinct competitors only. Old self-comparison is sound but forces chosen radius0. |
| Lower-Q selection and whole-policy regret | `AVOC/RobustQuotePlanning.lean`: `robustChoice_lower_max`, `robust_action_gap`, `robust_policy_regret`; `AVOC/GuardedPolicyRegret.lean`: `plan_regret_le` | Expected frozen-policy regret against same conservative guarded true system. Surrogate optimization, not exact minimax. |
| Closed polynomial form of regret | Source finite sums above | Prose algebra: epsilon H(H+1) + delta M H(H−1)(H+1)/3; no new Lean declaration. |
| Abstract warm120±208/cold60 example | `AVOC/RobustQuoteExamples.lean`: `uncertainWarmRaw`, `uncertainColdRaw`, `uncertainModel`, `uncertain_warm_local_radius`, `uncertain_cold_local_radius`, `uncertainty_changes_numerical_order` | Initial both untried, zero setup, h1 continuation. Quote fixture cannot produce artifact gross200/60 at calls1 for dense cost36. Exact Q range120–200 shows conservative lower-Q choice is not exact maximin. First-action choice reconstructed, not presented as a separate source selector theorem. |
| Exact finite-grid interval | `AVOC/FiniteCalibration.lean`: `mass`, `envelope`, `retained`, `lower`, `upper`, `grid_covers`, `mass_le_envelope`, `excluded_mass_le`, `missMass_le` | Rational p need not be grid point; m positive; alpha nonnegative. Cell-envelope method, not binomial-tail inversion. |
| n=m10 alpha1/10 exact endpoints and empirical singleton failure | Same: `ten_successes_retained`, `ten_successes_lower`, `ten_successes_upper`, `ten_failures_retained`, `ten_failures_lower`, `ten_failures_upper`, `empirical_singleton_counterexample` | Source theorem examples. |
| Predetermined schedule / outcome-dependent selection | `AVOC/CalibrationSchedule.lean`: `finite_union_le`, `scheduled_binomial_failure_le`, `selected_binomial_failure_le`, `fairBool_adaptive_exceeds_single_budget` | No cross-checkpoint independence needed; schedule total allowance retained; not unrestricted anytime validity. |
| Primitive law→product→count→prefix | `AVOC/ObservationStream.lean`: `ConditionalLaw`, `conditional_implies_product`, `count_fiber_eq_binomial`, `prefix_count_fiber_eq_binomial`, `correlatedPair_not_product` | Conditional fresh law explicit. Equal marginals insufficient. |
| Recorder lifecycle invariant | `AVOC/ObservationRecorder.lean`: `step`, `run_wellFormed`, `runFrom_log_prefix`, `accepted_terminal_retained_once`, `inherited_unfinished_terminal_conflict` | Pure finite snapshots. Global IDs span identities and pending/terminal states. Fault no binary sample. |
| Whole-run source refinement | `AVOC/RecorderReveal.lean`: `step`, `run_refines`, `run_samples_eq_take`, `replay_fault_exhaustion_example`, `exhausted_fresh_report_rejected` | Generated reports construct source bit; arbitrary physical raw labels require coupling. ID7/8/9 trace is new illustrative transition walkthrough, no new Lean claim. |
| Full gated observed sample→policy composition | `AVOC/RecorderPolicy.lean`: `gatedCounts_faithful`, `rejected_run_no_plan`, `pending_run_no_plan`, `recorder_episode_coverage`, `recorder_issued_failure_le`; `AVOC/CalibratedPolicy.lean`: `EpisodeCertified` | Unconditional original outcome space. Rejection, any pending ID, insufficient selected samples suppress issue. No issuance/liveness/collection cost claim. |
| Completion-conditioning obstruction | `AVOC/ObservationCensoring.lean`: `deadline_second_retention_predictable`, `deadline_conditioned_first_success`, `deadline_conditioned_count_not_binomial`, `conditioned_completed_bad_bound` | Kernel-checked two-fair-bit example. Ten-bit issue-only-on-all-success is separate elementary illustration combining archived interval endpoints, not a new Lean theorem. |
| Completion-order obstruction | `results/v0.41.0/review_completion_order.py`, `.json` | Exact finite executable evidence: two fair attempts first completed success3/4; twenty success-first attempts gives at-least-ten mass308333/524288. No missing observation, no fault, all intents resolved. Explicitly not new Lean theorem. |
| Checked acknowledgment/recovery | `AVOC/RobustQuoteRecovery.lean`: `prepare`, `acknowledge_fresh_contract`, `acknowledge_safe`, `acknowledge_idempotent`, `quote_mutation_rejected`; `AVOC/CalibrationBridge.lean`: `new_bands_obstruct_old_acknowledgement` | Fresh confirms successor; duplicate branch acknowledges already accepted commit without revalidating arbitrary new Outcome argument. prepare provenance supplied if needed. |
| Durable upgrade accounting/restore | `AVOC/DurableUpgrade.lean`: `begin`, `finish`, `abandon`, `begin_keeps_active`, `finish_evaluation_unchanged`, `abandon_keeps_current`; `AVOC/DurableUpgradeLaws.lean`: `paid_trace_exact_accounting`, `paid_trace_no_overspend`, `replay_utility_nondecreasing`, `restored_certificate`, `restored_is_actual` | Begin prepaid evaluation, abandon retains charge, replay same keys unchanged. Model accounting not physical exactly-once or physical origin authentication. |

## Authorial checks

- The long-form proof paragraphs reconstruct existing arguments and do not
  silently claim newly compiled publication prose.
- Statistical error is an outer failure probability, not automatically added
  to reward/regret and not a posterior interpretation of an observed band.
- The physical attempt/report-order coupling, universal parser/host/storage
  refinement, and multi-episode learning/accounting remain open.
- The recovery/recorder machines are separate and should not be described as
  a single newly proved integrated external transaction service.
- The final independent review qualified the synthesis by the simultaneous
  coverage event and made explicit the initial-contract premise for restored
  safety plus authority checker/utility soundness obligations for upgrades.
- Examples distinguish actual artifact-backed rank-one data from abstract
  quote fixtures and new elementary worked illustrations.

## Conservative mathematical proofreading

Proofread: full authored planning fragment, including local definitions,
index conventions, displayed equations, theorem/proof environment structure,
and source references.
- Routine edits: none required.
- Mathematical-token changes: none.
- Independent substantive review clarifications: coverage qualification and
  restore/authority premises, recorded above.
- Unresolved issues: none within this authored scope.
- Validation: 5338-word pre-clarification fragment had balanced environments,
  unique labels, all 17 file references resolved, and every simple formal
  declaration name found in authoritative Lean text. Full PDF compile and
  visual QA delegated to parent.
