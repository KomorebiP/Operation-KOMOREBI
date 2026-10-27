# Unified Inference / Memory Lean v0.3.0 — Status

## Verification

- Final warning-as-error compile: **PASS (RC = 0)**
- Representative `#print axioms` audit: **PASS (RC = 0)**
- theorem declarations: **72**
- definitions: **42**
- structures: **1**
- `sorry`: **0**
- `admit`: **0**
- custom `axiom` declarations: **0**

Representative central theorems report only ordinary Lean/Mathlib foundations
(`propext`, `Classical.choice`, `Quot.sound`).

## Manuscript theorem-family crosswalk

| Family | v0.3 Lean state |
|---|---|
| Bayesian packet factorization | Strong finite exact realization, including fine-state conditional packet posterior |
| Sequential evidence composition | Checked |
| Stochastic packet moments | Packet/Lyapunov algebra checked; derivation from Itô calculus remains open |
| Direct-sum Kalman | Prediction, innovation, derived inverse block closure, gain, packetwise mean, simplified and Joseph covariance closure checked |
| Gaussian packet semantics | Joint Gaussian + zero cross-packet covariance / block covariance implies packet independence checked |
| Gaussian Bayes = Kalman conditioning | Open; no ready conditioning theorem in pinned Mathlib |
| Strong Markov lumpability | Finite row-cell definition iff intertwiner checked; powers/polynomials/coarse propagation checked |
| Markov semigroup exponential | Abstract bounded-operator intertwining passes to `exp(tQ)` checked |
| Approximate lumpability | Exact discrete residual-propagation/telescoping law checked; continuous Duhamel norm bound remains open |
| Constant-projector Caputo | Bochner-integral commutation core checked with explicit regularity/integrability hypotheses |
| Volterra packet reconstruction | Checked with Bochner interval integrals |
| Volterra packet path composition | Checked |
| Finite-horizon resolvent | Scalar-kernel factorial convolution bound and uniform convergence on `[0,T]` checked |
| Finite exponential Markovian lift | Memory output identity and mode derivative ODE checked |
| Kernel approximation certificate | Scalar and operator-valued L1-L∞ bounds checked |
| Unified hereditary Kalman synthesis | Structural ingredients largely checked; full Gaussian conditioning semantics remain open |

## Current hard boundaries

1. **Itô derivation.** The pinned Mathlib tree contains Brownian-motion basics but no developed stochastic-integral/Itô-formula layer adequate for directly deriving the manuscript's linear-SDE moment equations. The projector consequences are certified; the stochastic derivation itself is not claimed.
2. **Gaussian conditioning.** Mathlib provides Gaussian-law and Gaussian-independence results, which are used here, but no ready linear-observation conditioning theorem was found that would certify the full `Kalman update = Gaussian Bayes` theorem without a substantial new measure-theoretic conditioning development.
3. **Operator-valued resolvent convergence.** The current full uniform M-test is for scalar kernels. Operator-valued packet reconstruction and kernel-error bounds are checked, but the operator-valued resolvent M-test is a remaining generalization.
4. **Continuous approximate lumpability.** Exact finite power residual propagation is checked. The manuscript's continuous Duhamel integral/norm estimate remains a separate analytic target.

## Audit-only failures corrected

- The first axiom-audit run used the wrong root-qualified name for the Volterra reconstruction theorem. It actually lives in `Komorebi.UnifiedInference.ContinuousProjectorFamily`. The proof source itself had already compiled. The corrected audit was rerun and passed RC=0.
- A second audit attempt repeated the same qualification mistake while regenerating the list. After resolving the namespace from the source, the final audit passed. These were audit-script reference errors, not Lean proof failures.
