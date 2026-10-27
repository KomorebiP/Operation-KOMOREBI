# Unified Inference Lean status — v0.4.0

## Checked major theorem families

| Manuscript family | Status |
|---|---|
| Bayesian packet factorization | Strong finite realization checked |
| Sequential evidence composition | Checked |
| Linear stochastic packet moment algebra | Checked conditional on base moment equations; Itô derivation open |
| Direct-sum Kalman algebra | Checked, including mean and Joseph covariance |
| Gaussian packet independence from block covariance | Checked |
| Gaussian Bayes = Kalman conditioning | Open |
| Strong Markov lumpability/intertwining | Finite iff checked |
| Markov exponential intertwining | Checked in bounded-operator form |
| Approximate lumping | Exact discrete defect propagation checked; continuous Duhamel norm bound open |
| Constant-projector Caputo commutation | Checked under explicit analytic hypotheses |
| Volterra packet reconstruction | Checked |
| Volterra packet-path convolution | Checked |
| Scalar resolvent convergence | Checked |
| Operator-valued resolvent convergence | **Checked in v0.4** |
| Finite Markovian memory lift | Output + differential law checked |
| Explicit augmented drift | **Checked in v0.4** |
| Recursive augmented-memory Kalman block closure | **Checked in v0.4** |

## Current counts

- theorem declarations: 81
- definitions/abbreviations: 50
- structures: 1
- `sorry`: 0
- `admit`: 0
- custom axioms: 0
