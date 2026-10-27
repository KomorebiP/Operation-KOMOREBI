# Gaussian–Kalman Bayesian Conditioning v0.2.0 — Checked

This release extends the checked scalar Gaussian semantic bridge from the identity observation model to the arbitrary scalar linear observation

\[
X\sim N(m,p),\qquad Y\mid X=x\sim N(hx,r),\qquad h\in\mathbb R,\ p>0,\ r>0.
\]

Define

\[
S=h^2p+r,\qquad K=\frac{ph}{S},\qquad
m_+(y)=m+K(y-hm),\qquad p_+=\frac{pr}{S}.
\]

Lean checks:

- positivity/nondegeneracy of `S` and `p+` from `p>0`, `r>0` with arbitrary real `h` (including `h=0`);
- the generalized completing-square identity;
- the Gaussian normalization-constant identity;
- exact pointwise real and ENNReal density factorization;
- exact observation marginal `Y ~ N(hm,S)`;
- prior/likelihood and evidence/posterior joint-density representations;
- the exact disintegration identity;
- evidence-a.e. equality of the explicit Kalman Gaussian kernel with Mathlib's canonical posterior kernel;
- pointwise normalized Bayes-density equality for every fixed observation;
- normalized Bayes-measure equality for every fixed observation.

## Verification boundary

`Checked` here means the source compiled with warnings treated as errors in the preserved pinned environment:

- Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- no `sorry`, `admit`, or custom axioms in the checked source
- representative theorem axiom audits reduce to `propext`, `Classical.choice`, `Quot.sound`

This release does **not** formalize finite-dimensional Gaussian conditioning. It does **not** establish literature novelty. It also does not by itself instantiate the separate multiscale Kalman perturbation theorem; that semantic/algebraic integration is the next proof block.
