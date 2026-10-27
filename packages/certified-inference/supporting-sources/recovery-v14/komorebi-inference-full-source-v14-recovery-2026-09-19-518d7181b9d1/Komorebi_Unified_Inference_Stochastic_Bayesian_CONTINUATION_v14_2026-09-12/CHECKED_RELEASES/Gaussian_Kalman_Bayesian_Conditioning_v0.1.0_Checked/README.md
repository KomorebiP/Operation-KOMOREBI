# Gaussian–Kalman Bayesian Conditioning v0.1.0 — Lean checked

This release closes the **scalar Gaussian location-observation semantic bridge** between an explicit Kalman posterior and Mathlib's canonical Bayesian posterior kernel.

## Model

Prior:

\[
X \sim N(m,p), \qquad p>0.
\]

Observation model:

\[
Y\mid X=x \sim N(x,r), \qquad r>0.
\]

Define

\[
m^+(y)=\frac{rm+py}{p+r},\qquad
p^+=\frac{pr}{p+r}.
\]

The explicit candidate posterior kernel is

\[
y\longmapsto N(m^+(y),p^+).
\]

## Checked results

### 1. Completing the square

The source proves the exact quadratic identity behind scalar Gaussian conditioning.

### 2. Gaussian density factorization

For every real `x,y`,

\[
\phi_{m,p}(x)\,\phi_{x,r}(y)
=
\phi_{m,p+r}(y)\,\phi_{m^+(y),p^+}(x).
\]

Both the `Real` and `ENNReal` density versions are checked.

### 3. Observation marginal

The Gaussian location kernel composed with the prior is proved exactly equal to

\[
Y\sim N(m,p+r).
\]

### 4. Joint-law disintegration identity

Lean proves

\[
N(m,p+r)\otimes K_{\mathrm{Kalman}}
=
\operatorname{swap}_*\bigl(N(m,p)\otimes K_{\mathrm{likelihood}}\bigr).
\]

The proof rewrites both joint laws as densities over product Lebesgue measure and applies the checked Gaussian factorization.

### 5. Canonical Bayesian posterior equality

Using `ProbabilityTheory.ae_eq_posterior_of_compProd_eq`, Lean proves

\[
K_{\mathrm{Kalman}}(y)
=
K_{\mathrm{posterior}}(y)
\quad\text{for }N(m,p+r)\text{-almost every }y,
\]

where `K_posterior` is Mathlib's canonical posterior kernel defined by disintegration.

This is a genuine semantic posterior statement, not merely Kalman update algebra.

### 6. Pointwise normalized Bayes formula

For every observation `y`, Lean proves the pointwise density identity

\[
\frac{\phi_{m,p}(x)\phi_{x,r}(y)}{\phi_{m,p+r}(y)}
=
\phi_{m^+(y),p^+}(x),
\]

and therefore the normalized Bayes measure equals the explicit Kalman Gaussian measure for every `y`.

## Exact boundary

This release proves the scalar **identity/location observation** model `Y = X + ε`. It does **not** claim the arbitrary finite-dimensional observation theorem

\[
Y=HX+\varepsilon
\]

with matrix-valued covariance. The pinned Mathlib has substantial Gaussian infrastructure, but no ready theorem giving general multivariate nonsingular Gaussian conditioning in the form needed here; that lift would require additional formal development.

The almost-everywhere qualifier in the canonical posterior theorem is mathematically appropriate: regular conditional probabilities are unique only up to an evidence-null set. The separate normalized-density theorem is pointwise for every observation because the Gaussian evidence density is strictly positive when `p,r>0`.

## Verification

Pinned environment:

- Lean / Lake: `leanprover/lean4:v4.34.0-rc2`
- Lean commit: `6a10ac8c22beadecabdbb0919c2b50214762f91d`
- mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- warning-as-error source check: RC = 0
- axiom audit: RC = 0
- theorem/lemma declarations: 18
- definitions: 4
- `sorry`: 0
- `admit`: 0
- custom `axiom`: 0

Representative semantic theorems audit only to ordinary Lean/Mathlib foundations:

- `propext`
- `Classical.choice`
- `Quot.sound`
