# Metric dictionary

| Metric | Meaning |
|---|---|
| `task_accuracy` | Fraction of terminal decisions matching the evaluator target |
| `continuous_task_accuracy` | Task accuracy accumulated by one persistent continuous controller |
| `workspace_decodability` | Ability to recover task-relevant state from the workspace or packet field |
| `formation_accuracy` / `formation_balanced_accuracy` | Balanced workspace-need accuracy; equal weight is given to workspace and no-workspace cases |
| `formation_raw_accuracy` | Unbalanced workspace-need accuracy, retained so class prevalence is visible |
| `packet_birth_accuracy` | Correct active-packet count relative to task demand |
| `packet_death_accuracy` | Correct packet teardown when demand decreases |
| `workspace_dissolution_accuracy` | Correct return to no-workspace processing |
| `change_detection_accuracy` | Detection of unannounced non-memory changes at event boundaries |
| `self_world_attribution_accuracy` | Correct self-side versus world-side attribution after a detected change |
| `repair_accuracy` | Restoration of the hidden synthetic model after the chosen repair |
| `adaptive_probe_accuracy` | Presence of the configured bounded probing mechanism; use probe count and attribution accuracy for effect |
| `probe_count` | Total bounded diagnostic samples requested |
| `ownership_accuracy` / `provenance_accuracy` | Correct autobiographical write, quarantine, or rejection action |
| `false_autobiographical_write_rate` | Foreign or corrupted content incorrectly stored as owned history |
| `continuity_accuracy` | Correct continuity treatment under self, partner, and memory events |
| `relation_accuracy` | Exact continuation/fork/copy/replacement/unresolved classification in identity tasks |
| `recurrence_reopen_rate` | Fraction of relevant events that increase later evidence acquisition |
| `alignment_r2` | Cross-agent shared-coordinate alignment |
| `private_leakage_accuracy` | Private information decodable from the shared state; lower may be better |
| `structural_closure` | Indicator of bidirectionality, memory, planner binding, and recurrence |
| `synergy_information_bits` | Exact information available only from the joint state in the configured task |
| `causal_patch_effect` | Fraction of patches producing the predicted downstream change |
| `ablation_drop` | Intact performance minus performance after a declared cut |
| `route_accuracy` | Selection of the minimal sufficient workspace route |
| `mean_excess_cost` | Selected workspace cost above the minimal sufficient cost |
| `membership_entropy` | Degree of fuzzy overlap in coalition membership |
| `idempotence_defect` | Distance from a crisp projector-like packet |
| `transport_defect` | Misalignment between current packet geometry and the estimated coordinate transport |
| `mean_active_packets` | Mean number of active shared packets |
| `causal_membership_calibration` | Correlation between fuzzy membership strength and ablation effect |
| `jspace_jacobian_energy_capture` | Fraction of the averaged terminal-Jacobian energy contained in the selected projector |
| `jspace_activation_variance_fraction` | Activation covariance retained by the selected J-space projector |
| `jspace_projector_idempotence_defect` | Frobenius defect of the selected projector; zero is exactly idempotent |
| `jspace_task_score` | Exponentiated negative held-out loss from the sparse Jacobian code |
| `pca_matched_task_score` / `random_matched_task_score` | Same-rank, same-active-count control scores |
| `jspace_minus_pca` / `jspace_minus_random` | J-space score advantage over the matched controls; positive favors the Jacobian frame |
| `jspace_ablation_drop` | Intact score minus score after removing the J-space code |
| `broadcast_ablation_drop` | Intact score minus score after blocking delivery while retaining upstream J code |
| `code_preservation_under_broadcast_cut` | Explicit equality score for upstream J code under a downstream broadcast cut |
| `provenance_plan_drop` | Intact score minus score when provenance is replaced by the declared cut value |
| `planner_cut_drop` | Intact score minus score after the committed plan output is cut |
| `recurrence_false_reopen_rate` | Reopening rate after matched null event boundaries |
| `recurrence_recovery_gain` | Later plan-loss improvement attributable to retained feedback |
| `longest_supported_prefix` | Longest consecutive serial-link sequence passing smoke diagnostic gates; not a frozen inferential claim |
| `emergence_rate` | Joint task/probe/patch/cut criterion in emergence families |
| `trajectory_digest` | Digest of the semantic continuous trajectory used to test exact resume equivalence |
| `functional_closure_score` | Experiment-local engineered composite; not a consciousness probability |
| `functional_closure_composite` | Cross-family engineering profile composite; not an awareness probability |
| `wall_time_seconds` | Measured run duration |
| `peak_python_memory_mb` | Python-tracked peak allocation; not total process or GPU memory |
