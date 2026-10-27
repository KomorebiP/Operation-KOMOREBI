# Projective Terminal-Only Training Result

**Developmental gate status:** `PASS`  
**Training:** lengths 1–4, terminal answer loss only, no named relations, no intermediate targets, no anchor compiler.
**Checkpoint training source:** `a5f2db2864b664837cf9bde4e44b9ef36efe296026af952f0b097c6c6b80c9ac`  
**Current evaluation source:** `cb5d6b1eccb7b9e05cbbe16637dac90cc1334a469fb9add6472238affa61210e`  
The bundled completion time is checkpoint re-evaluation time; original per-seed training durations remain in `RESULTS.json`.

## D4 comparison

| Arm | L4 | L12 | L64 | L128 | L256 |
|---|---:|---:|---:|---:|---:|
| Raw v0.1 parent | 0.9990 | 0.8403 | 0.3867 | 0.2869 | 0.0000 |
| Projective terminal-only | 1.0000 | 1.0000 | 1.0000 | 0.9924 | 0.8477 |

The only architectural change is positive-ray normalization after each recurrent operator application. The operator encoder remains learned from terminal supervision. This prevents scale from serving as an optimization shortcut and forces composition to be represented directionally.

At depth 128, before the raw float32 arm overflows, the projective advantage is `0.7056`. The preregistered depth-256 advantage includes raw overflow and should not be read as a purely semantic margin.

## Held-out operator families

| Family | L64 | L128 | L256 |
|---|---:|---:|---:|
| D4 | 1.0000 | 0.9924 | 0.8477 |
| C8 | 1.0000 | 0.9917 | 0.7351 |
| Mixed cycle | 1.0000 | 0.9956 | 0.8665 |
| Arbitrary random permutations | 0.2629 | 0.2485 | 0.2480 |

C8 and mixed-cycle transfer remained strong despite being absent from training. Arbitrary independent permutation pairs did not: their long-depth score settled near 0.25. The result is therefore broad within structured permutation families, not universal over arbitrary operators.

## Closure and holonomy audit

All evaluated hidden states remained finite. Table-verified null cycles preserved the correct answer down to `0.9941`, but the largest median ray angle relative to the no-cycle trajectory reached `0.4712` radians. The learned computation is behaviorally closed over the tested loops before it is geometrically flat.

The ambient learned matrices had mean median spectral radius `0.1978`, mean scale-quotiented anchor defect `0.7480`, and mean conformal-metric defect `0.9409`. Because per-step normalization removes matrix scale, spectral radius is not a stability criterion for this arm. The nonzero scale-free defects show that the encoder did not learn an exact ambient group representation; its successful semantics live on reachable projective trajectories.

## Gates

| Gate | Observed | Criterion | Result |
|---|---:|---|---|
| `projective_train_range` | 1 | `>= 0.98 per seed` | PASS |
| `projective_d4_depth64` | 1 | `>= 0.98 per seed` | PASS |
| `projective_d4_depth128` | 0.987793 | `>= 0.95 per seed` | PASS |
| `projective_d4_depth256_mean` | 0.847656 | `>= 0.80` | PASS |
| `projective_d4_depth256_seed_floor` | 0.809082 | `>= 0.75` | PASS |
| `projective_depth256_advantage` | 0.847656 | `>= 0.50 over matched raw parent` | PASS |
| `projective_all_depth_finite` | 1 | `== 1.0` | PASS |
| `projective_deep_state_patch` | 1 | `>= 0.90` | PASS |
| `projective_deep_operator_patch` | 1 | `>= 0.90` | PASS |
| `projective_random_state_control` | 0.078125 | `<= 0.40` | PASS |
| `projective_random_operator_control` | 0.0654297 | `<= 0.40` | PASS |
| `projective_null_cycle_accuracy` | 0.994141 | `>= 0.90` | PASS |
| `projective_cross_seed_transport` | 1 | `>= 0.70` | PASS |
| `projective_transport_random_control` | 0.00390625 | `<= 0.40` | PASS |

## Claim boundary

This is a two-seed developmental result whose long-depth gates were informed by an initial exploratory run. It shows that projective gauge fixing is sufficient to induce substantially more stable terminal-only operator learning in this finite table task. It does not establish spontaneous Neuralese in an unconstrained model, exact group representation, universal arbitrary-permutation generalization, asymptotically unbounded recurrence, or architecture-independent emergence.

## Cross-seed transport

Aligned continuation accuracy: `1.0000`. Random-map control: `0.0039`.

The same D4-fitted map achieved C8 `1.0000`, mixed-cycle `1.0000`, and arbitrary-random `0.5869` continuation accuracy. The target model's native arbitrary-random score was `0.5879`, so transport preserved its limitation rather than concealing it.

## Strongest supported claim

> In this randomly re-coordinatized finite operator task, positive-ray gauge fixing during terminal-only training produced a compact recurrent state with stable finite norms, causal state and operator semantics, long-depth structured-family generalization, and behavior-preserving cross-seed transport. Residual projective holonomy and arbitrary-operator failure remain.
