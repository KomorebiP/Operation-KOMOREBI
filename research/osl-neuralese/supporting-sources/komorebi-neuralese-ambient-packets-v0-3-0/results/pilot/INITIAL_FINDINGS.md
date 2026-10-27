# Initial findings

## Retained developmental pilot

The hardened v0.1.1 pilot completed six arms across two deterministic seeds. All fourteen frozen developmental gates passed. This remains a developmental result because the thresholds and hardening changes were informed by the earlier v0.1.0 scaffold.

### Main positive result

The 4,224-parameter linear latent-operator recurrence learned from terminal answers alone and achieved:

- 0.9998 mean exact accuracy on D4 lengths 1 through 4
- 0.8988 mean exact accuracy on held-out D4 lengths 8, 10, and 12
- 0.9972 mean exact accuracy on held-out C8 lengths 1 through 4
- 0.9509 causal donor-state continuation accuracy versus 0.0742 for a norm-matched random displacement
- 0.9561 causal operator-replacement accuracy versus 0.0605 for a norm-matched random operator displacement

The unconstrained 19,304-parameter GRU reached 0.4585 on the same held-out D4 long split. Explicit intermediate supervision did not repair the GRU, which reached 0.4312.

### Relation pressure

Adding D4 relation and hidden-return pressure raised held-out D4 long accuracy to 0.9980 and held-out C8 length-12 accuracy to 0.9792. It also increased arbitrary-random-permutation length-12 accuracy from 0.3296 to 0.4888.

This is not an exact latent group representation. Ambient matrix and hidden-return residuals remain nonzero. The posthoc stability audit shows that relation pressure acts primarily as a dynamical regularizer: it lowers spectral expansion, contracts path-conditioned state clouds, and delays depth failure.

### Coordinate transport

An affine map fitted only on D4 trajectories of lengths 1 through 4 was applied without refitting to new length-8 episodes. Aligned continuation accuracy was:

| Family | Target native | Aligned source state | Random-map control |
|---|---:|---:|---:|
| D4 | 0.9473 | 0.7979 | 0.0635 |
| C8 | 0.8721 | 0.7490 | 0.0688 |
| Mixed cycle | 0.7959 | 0.7378 | 0.0776 |
| Independent random permutations | 0.5029 | 0.4951 | 0.0991 |

Behavioral transport is substantially stronger than raw hidden-state matching. On D4, hidden-state R² was only 0.4033 while transported continuation accuracy was 0.7979. This is consistent with transport of task-relevant equivalence classes rather than literal pointwise identity.

## Failure mode discovered

Terminal-only latent matrices are dynamically unstable. In the posthoc depth audit, median D4 hidden norm grew from roughly 182 at depth 8 to approximately 5.3×10^17 at depth 64. The relation-pressure sweep reduced the median learned spectral radius and improved depth-64 exact accuracy:

| Relation weight | D4 depth 64 | Median spectral radius | Median hidden norm at depth 64 |
|---:|---:|---:|---:|
| 0.00 | 0.3994 | 1.9173 | 8.66×10^17 |
| 0.15 | 0.5679 | 1.2647 | 1.52×10^6 |
| 0.30 | 0.6782 | 1.2097 | 1.03×10^5 |
| 0.60 | 0.7241 | 1.2254 | 1.38×10^5 |

The immediate next mechanism to test is a coordinate-free stability constraint, such as a learned invariant metric satisfying approximately

\[
M_g^\top G M_g \approx G,
\]

combined with generic composition consistency rather than only named D4 relations.

## Claim boundary

These experiments establish a controlled positive-bias mechanism for recurrent latent operator execution, causal editing, and coordinate transport in an exact finite task. They do not establish spontaneous Neuralese, open-ended operator discovery, large-language-model internals, or consciousness.
