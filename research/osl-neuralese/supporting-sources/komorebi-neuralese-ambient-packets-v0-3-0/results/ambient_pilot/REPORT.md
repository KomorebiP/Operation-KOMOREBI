# Ambient packet frozen-checkpoint diagnostics

- Profile: `pilot`
- Status: `developmental_posthoc_frozen_checkpoint_diagnostics`
- Assay: `PASS`
- Mechanism reference: `FAIL`
- Capability reference: `FAIL`
- Full developmental claim: `NOT_CLAIMED_POSTHOC`

This is a diagnostics-only, developmental posthoc evaluation of frozen, retrospectively selected projective checkpoints. Scientific gate failure is retained as a result and does not make the run incomplete.

## Assay gates

| Gate | Status | Criterion |
|---|---|---|
| `A01_checkpoint_integrity` | PASS | >= 1 SHA/config-validated frozen checkpoint |
| `A02_episode_and_slot_contract` | PASS | all exact |
| `A03_exact_global_gauge_control` | PASS | <= 1e-12 |
| `A04_statewise_gauge_control` | PASS | statewise <= 1e-12 and global >= 0.10 |
| `A05_negative_and_leakage_controls` | PASS | negative detected, leakage > 1e-3, reconstruction <= 1e-12 |
| `A06_exact_chart_packet_control` | PASS | == 1.0 at every audited prefix |
| `A07_exact_chart_switched_control` | PASS | accuracy == 1 and gains within 1e-10 of 1 |
| `A08_nonnormal_control` | PASS | flagged with individual radii < 1 and projective gain > 30 |

## Learned mechanism reference gates

| Gate | Status | Criterion |
|---|---|---|
| `M01_statewise_gauge_advantage` | PASS | >= 0.50 of operators per family |
| `M02_full_per_episode_observability` | PASS | rank == 8 |
| `M03_exhaustive_d4_packet_membership` | FAIL | >= 0.90 at every audited prefix |
| `M04_null_loop_packet_retention` | FAIL | >= 0.90 for every tested relation/repeat |
| `M05_projective_domain_safety` | PASS | minimum > 1e-8 and no undefined switched applications |

## Capability reference gates

| Gate | Status | Criterion |
|---|---|---|
| `C01_structured_long_depth_accuracy` | FAIL | >= 0.70 per seed/family at final profile depth |
| `C02_random_family_reported_not_required` | OBSERVED | descriptive only; no success threshold |

## Interpretation boundary

A pass describes finite, task-relative packet behavior in this explicit permutation-table model. It does not establish an infinite quotient, spontaneous Neuralese, architecture-independent emergence, or awareness. A failure localizes the corresponding gauge, packet, null-loop, switched-dynamics, or capability hypothesis without erasing earlier causal execution results.
