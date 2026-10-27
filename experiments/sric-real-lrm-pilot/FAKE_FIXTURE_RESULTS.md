# Engineered Adapter Fixture Results

## Boundary

This is a deterministic positive control for the audit pipeline. It is not a trained language model and is not evidence about the external Coconut checkpoint.

## Result

- Tasks: 48
- Status: **`PROCEDURE_SPECIFIC`**
- Maximum replay logit error: 0
- Maximum semantic-twin effect magnitude: 0
- Result receipt: `220324ce30387de4fb0216f315192551cffe51491e457ad15acd7533a1697fd4`

| Effect | Mean | Grouped 95% interval | Positive fraction |
|---|---:|---:|---:|
| Latent necessity | 0.149230 | [0.146630, 0.151482] | 1.000 |
| Step order | 0.237738 | [0.231035, 0.244419] | 1.000 |
| Norm-matched structure | 0.346394 | [0.334891, 0.357867] | 1.000 |
| Same-answer far-proof transplant | 0.219653 | [0.216013, 0.223558] | 1.000 |
| Semantic-twin transplant | 0.000000 | [0.000000, 0.000000] | 0.000 |

## Interpretation

The fixture was constructed so that its recurrent state is invariant to premise reordering, contains the final answer, and also contains step-indexed proof-procedure information. The audit correctly distinguishes a same-answer far-proof donor from a surface-only twin and returns `PROCEDURE_SPECIFIC`.

This validates the decision logic and intervention plumbing. It does not validate any empirical claim about a third-party checkpoint.
