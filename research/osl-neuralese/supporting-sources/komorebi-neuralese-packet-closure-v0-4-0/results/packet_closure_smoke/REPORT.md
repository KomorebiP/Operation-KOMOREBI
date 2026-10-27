# Packet-closure training block

- Author: `Komorebi P.`
- Profile: `smoke`
- Study: `engineering_smoke`
- Execution: `PASS`
- Assay: `PASS`
- Mechanism: `NOT_EVALUATED`
- Primary D4 capability: `NOT_EVALUATED`
- Causal attribution: `NOT_EVALUATED`
- Secondary cross-family transfer: `NOT_EVALUATED`
- Descriptive ambient-Q attribution: `NOT_EVALUATED`
- Descriptive hard-polar-stratum CR-objective effect: `NOT_EVALUATED`
- Full developmental claim: `NOT_EVALUATED`

Scientific failures are retained. The clean paired 2x2 crosses raw Euclidean-normalized operators with hard O(12)-polar operators and matched supervised versus demonstration-aligned composition plus finite-path complement-return (CR) objectives. All cells share initialization and both accepted and proposal episode streams.

## Arm outcomes

Packet membership, continuation margin, and null closure are worst-cell estimands over every registered prefix, relation group, null relation, and repeat through 2; deep metrics use depth 64.
Causal patch/control entries are conditional transition accuracies among same-bank cases with a correct native answer and a distinct counterfactual target. Relative-conjugacy control is inapplicable to raw arms and is shown as unavailable.

| Arm | Packet | Margin p10 | D4 deep | Xfer min | Null closure | Switch gain/acc | Hard defect | Raw smin | State patch / angle / reachable | Operator patch / conjugacy / cross-context |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `euclidean_supervised` | 0 | -0.8894 | 0.1562 | 0.09375 | 0 | 7.312/0.1875 | — | — | 0/0/0 | 0/—/1 |
| `euclidean_cr` | 0 | -0.8581 | 0.25 | 0.03125 | 0 | 10.99/0.125 | — | — | 0.25/0/0 | 0/—/0 |
| `polar_supervised` | 0 | -0.8465 | 0.125 | 0.09375 | 0 | 1/0.125 | 3.844e-06 | 0.001207 | 0/0.1667/0.1667 | 0.3333/0.1667/0.1667 |
| `polar_cr` | 0 | -0.8326 | 0.1875 | 0.0625 | 0 | 1/0.2188 | 3.402e-06 | 0.0004793 | 0/0.3333/0 | 0/0/0 |

## Paired 2x2 contrasts

Positive values mean the named first condition has the larger metric; desirability depends on the metric. The interaction is the difference in the CR effect between polar and raw architectures.

| Metric | Polar main | CR main | CR given raw | CR given polar | Polar given supervised | Interaction |
|---|---:|---:|---:|---:|---:|---:|
| `packet_membership` | 0 | 0 | 0 | 0 | 0 | 0 |
| `packet_margin_p10` | 0.03417 | 0.02257 | 0.03124 | 0.01389 | 0.04284 | -0.01734 |
| `d4_accuracy` | -0.04688 | 0.07812 | 0.09375 | 0.0625 | -0.03125 | -0.03125 |
| `cross_family_minimum_accuracy` | 0.01562 | -0.04688 | -0.0625 | -0.03125 | 0 | 0.03125 |
| `structured_minimum_accuracy` | 0.01562 | -0.04688 | -0.0625 | -0.03125 | 0 | 0.03125 |
| `null_closure` | 0 | 0 | 0 | 0 | 0 | 0 |
| `switched_max_gain` | -8.149 | 1.837 | 3.675 | -5.862e-07 | -6.312 | -3.675 |
| `switched_word_accuracy` | 0.01562 | 0.01562 | -0.0625 | 0.09375 | -0.0625 | 0.1562 |
| `feshbach_return_fraction` | 0.03457 | -0.006358 | -0.008085 | -0.004632 | 0.03284 | 0.003453 |
| `ambient_q_ablation_drop` | -0.03125 | 0.04167 | 0 | 0.08333 | -0.07292 | 0.08333 |
| `ambient_q_specific_excess_drop` | -0.01042 | 0.04167 | 0.02083 | 0.0625 | -0.03125 | 0.04167 |

## Execution gates

| Gate | Status | Criterion |
|---|---|---|
| `E01_preregistration_profile_match` | PASS | contract schema, version, author, status, source digest, all profiles, selected profile, and registered design exactly match the implementation |
| `E02_all_training_runs_completed` | PASS | == 4 |
| `E03_all_evaluations_completed` | PASS | == 4 |
| `E04_checkpoint_seal_complete` | PASS | == 4 checkpoint receipts |
| `E05_frozen_checkpoint_reload` | PASS | == 4 hash-verified disk reloads |
| `E06_source_and_contract_immutable` | PASS | source-tree and preregistration-contract hashes equal their startup values before checkpoint sealing and after evaluation |

## Assay gates

| Gate | Status | Criterion |
|---|---|---|
| `A01_paired_initialization_and_stream` | PASS | identical full/shared initialization, accepted episode-stream, and terminal-proposal-stream digests within every seed |
| `A02_construction_bank_shared` | PASS | every checkpoint and the seal match the exact canonical 20-word nonempty horizon-4 construction set, whose induced actions exclude identity and r2 |
| `A03_checkpoint_audit_firewall` | PASS | no heldout/evaluation bank content in any checkpoint |
| `A04_reserved_terminal_action_holdout` | PASS | 171 exhaustive horizon-8 continuations (including empty) in two reserved terminal-action groups; endpoint split verified |
| `A05_checkpoint_before_evaluation_bank` | PASS | checkpoint seal timestamp precedes evaluation-bank materialization |
| `A06_exact_episode_contracts` | PASS | every registered bank has the exact family, contexts, depth, tensor geometry, one-hot maps, canonical conjugated action, targets, intermediates, and slot mapping |
| `A07_nonvacuous_exact_feshbach_split` | PASS | retained rank == 8 and nuisance rank == 4 for every evaluated checkpoint |
| `A08_switched_bank_contract` | PASS | exactly all 256 length-8 words for pilot; declared deterministic bank with configured contexts otherwise |
| `A09_terminal_endpoint_group_firewall` | PASS | every run uses the frozen identity/r2 endpoint-rejection policy; accepted count equals steps*batch and proposal/rejection counts close exactly |
| `A10_hard_polar_isometry` | PASS | both polar arms pass exact O(12) matrix and finite-bank projective-gain implementation checks for every seed |
| `A11_raw_prepolar_singular_diagnostic` | PASS | raw pre-polar relative singular values are recorded for both polar arms; conditioning below 1e-4 is a warning, not a closure failure |
| `A12_ambient_control_geometry` | PASS | all ambient assays have ideal rank-8/4 construction within 1e-8; the float32-cast P/Q and random controls retain ranks 8/4 and match the actually removed Q energy within 1e-6 |
| `A13_complete_primary_closure_grid` | PASS | every seed x arm evaluation contains exactly all registered packet prefixes, both reserved relation groups, every D4 null relation x repeat cell, and the complete depth x family grid with registered example counts |
| `A14_cross_context_operator_control_bank` | PASS | independent operator-control slots are balanced by frozen row and flipped only to exclude exact collisions with either the original or alternate visible table; both selected collision counts are zero |
| `A15_packet_result_contract` | PASS | every seed x arm packet result binds the exact held-out bank, registered context count, zero boundary, canonical 86/85 relation-group cardinalities, fraction denominators, and complete numeric summaries |
| `A16_deep_result_contract` | PASS | every seed x arm depth x family result has registered counts, fractions in [0,1], accuracy no greater than finite fraction, and exact pooled, macro, and minimum arithmetic |
| `A17_ambient_result_contract` | PASS | every seed x arm ambient result has the exact family/condition schema, registered geometry and thresholds, bounded count-derived fractions, recomputed performance drops, and coherent attribution status |
| `A18_causal_result_contract` | PASS | every seed x arm causal result has registered banks and intervention positions, bounded count-derived fractions, valid eligible denominators, coherent conditional transitions, and architecture-appropriate controls |
| `A19_switched_result_contract` | PASS | every seed x arm switched result binds the exact word bank and fingerprint, registered contexts, defined denominator, behavioral accuracy, numeric summaries, and gain/log-gain extrema |
| `A20_null_result_contract` | PASS | every seed x arm null-loop result binds the exact packet bank and repeat grid, with valid baseline, conditional denominators, retained intersection bounds, margin summaries, and first-crossing arithmetic |
| `A21_feshbach_result_contract` | PASS | every seed x arm exact Feshbach result has the full rank, metric, generator-block, and delayed-return schemas with registered counts, finite nonnegative summaries, and coherent spectral diagnostics |
| `A22_hard_polar_result_contract` | PASS | every seed x arm hard-polar result has its architecture-appropriate exact schema; polar arms reconcile family and pooled geometry, use family-specific switched banks, and derive every pass flag |

## Mechanism gates

| Gate | Status | Criterion |
|---|---|---|
| `M01_heldout_packet_membership` | NOT_EVALUABLE | >= 0.90 at every audited prefix and in both reserved groups per polar_cr pilot seed |
| `M02_heldout_margin_p10` | NOT_EVALUABLE | > 0 at every audited prefix and in both reserved groups per polar_cr pilot seed |
| `M03_null_loop_packet_retention` | NOT_EVALUABLE | >= 0.90 for null-bank baseline membership, conditional retention, and post-loop membership for every relation and repeat through 32 per polar_cr pilot seed |
| `M04_switched_projective_gain` | NOT_EVALUABLE | hard-polar exhaustive length-8 maximum gain lies in [0.999, 1.001] per pilot seed |
| `M05_switched_domain_defined` | NOT_EVALUABLE | defined fraction == 1 per polar_cr pilot seed |
| `M06_switched_word_accuracy` | NOT_EVALUABLE | exhaustive length-8 switched-word behavioral accuracy >= 0.95 per polar_cr pilot seed |

## Primary D4 capability gates

| Gate | Status | Criterion |
|---|---|---|
| `C01_primary_d4_depth_curve` | NOT_EVALUABLE | polar_cr per-seed D4 outputs are fully finite and accuracy >= 0.98@128, 0.90@256, 0.75@512 |

## Causal attribution gates

| Gate | Status | Criterion |
|---|---|---|
| `T01_complete_paired_2x2` | PASS | all four paired raw/polar x supervised/CR cells available |
| `T02_causal_state_patch_specificity` | NOT_EVALUABLE | on natively correct cases with distinct targets, polar_cr state patch >= 0.90; native accuracy and eligibility >= 0.90; all relevant outputs finite; angle-matched and reachable-wrong controls <= 0.40; geometry receipts valid per pilot seed |
| `T03_causal_operator_patch_specificity` | NOT_EVALUABLE | on natively correct cases with distinct targets, polar_cr operator patch >= 0.90; native accuracy and eligibility >= 0.90; all relevant outputs finite; operator-geometry and cross-context controls <= 0.40; geometry receipts valid per pilot seed |

## Secondary cross-family transfer gates

| Gate | Status | Criterion |
|---|---|---|
| `S01_zero_shot_cross_family_depth_curve` | NOT_EVALUABLE | descriptive secondary: polar_cr per-seed C8 and mixed-cycle outputs are fully finite and accuracy >= 0.98@128, 0.90@256, 0.75@512 |

## Descriptive ambient-Q attribution gates

| Gate | Status | Criterion |
|---|---|---|
| `D01_specific_ambient_complement_use` | NOT_EVALUABLE | descriptive only: every polar_cr family has fully finite/defined causal rollouts, native accuracy >= 0.75, Q drop >= 0.05, and Q-specific excess over the energy/rank-matched random control >= 0.05; failure does not invalidate closure |

## Descriptive hard-polar-stratum CR-objective effect gates

| Gate | Status | Criterion |
|---|---|---|
| `O01_cr_grid_margin_benefit` | NOT_EVALUABLE | paired polar_cr minus polar_supervised grid-min margin has positive mean and is positive in at least two of three pilot seeds |
| `O02_cr_grid_membership_nonnegative_direction` | NOT_EVALUABLE | mean paired polar_cr minus polar_supervised grid-min packet-membership difference is nonnegative |
| `O03_cr_null_closure_nonnegative_direction` | NOT_EVALUABLE | developmental direction check: mean paired polar_cr minus polar_supervised difference in worst baseline/conditional/post-loop null closure is nonnegative |

## Audit boundary

The terminal sampler rejects every loss-bearing D4 word whose complete induced action is identity or r². The horizon-8 evaluation bank was materialized only after all available checkpoints were serialized and hashed. It contains the empty continuation plus all 170 nonempty words through length eight in those two reserved endpoint-action groups. The empty continuation makes current-prefix decoding part of packet membership. Checkpoints contain only the horizon-4 construction words plus aggregate terminal-firewall counts and digests, never rejected or evaluation words.

The Feshbach and causal ambient audits use an ideal rank-eight anchor plane and rank-four complement, then separately audit the float32 projectors actually applied. Q energy alone is not evidence of use: the descriptive attribution requires finite, defined rollouts and a performance loss under Q ablation beyond a rank- and removed-energy-matched random control within the registered applied tolerance. A negative ambient-Q result does not invalidate packet closure.

Hard polar isometry is an architectural implementation assay, not evidence that stability was learned. Raw pre-polar singular conditioning is retained as a warning diagnostic and is not a closure gate.

## Claim boundary

A successful primary pilot would establish finite-depth packet preservation, tolerance-bounded hard-polar switched control on the registered finite bank, D4 depth extrapolation, and causal state/operator execution in this explicit table-conditioned architecture. Cross-family zero-shot transfer and ambient-Q use are reported separately and cannot be hidden inside the primary closure claim. The experiment would not establish spontaneous Neuralese, an infinite quotient, universal stability, architecture-independent emergence, awareness, or consciousness.
