# Proof note: model residuals to actual posterior moments

## 1. Domain and exact conditional laws

Consider two models indexed by 0 and 1 on the same finite-dimensional real state
and observation spaces. Their state and observation dimensions may differ.
For each model, X has law N(m,P), and the conditional observation law is N(Hx,R),
with P positive semidefinite and R positive definite. Set

    S = H P Hᵀ + R
    K = P Hᵀ S⁻¹
    A = I - K H
    a(y) = m + K(y-Hm)
    C = P-KHP = A P Aᵀ + K R Kᵀ.

The unchanged finite-dimensional Gaussian development proves that

    η(y) = N(a(y),C)

is an actual Bayesian posterior version, and equals Mathlib's selected canonical
posterior for that model's evidence-almost every y. Its evidence is N(Hm,S).

The model record in this release contains only model data and positivity proofs.
In particular it does not assume this posterior identification.

## 2. Centered covariance, not second moment

For a measure μ on a real Hilbert space, define

    centeredCovOp(μ) = continuousLinearMapOfBilin(covarianceBilin(μ)).

The centered-integral theorem gives, under the finite-second-moment hypothesis,

    <centeredCovOp(μ) u, v>
      = ∫ <u,x-Eμ[x]> <v,x-Eμ[x]> dμ(x).

This is not the separately named Mathlib covarianceOperator, whose definition
at the pinned revision is uncentered. For a Gaussian N(m,P) with P semidefinite,
we prove

    centeredCovOp(N(m,P)) = matrixCLM(P).

No zero-mean assumption is used. The deterministic-Gaussian regression proves
that N(m,0) has centered covariance zero for arbitrary m.

## 3. Matrix/operator compatibility

The bridge proves matrixCLM preserves multiplication/composition, addition,
subtraction, zero, and identity. The transpose/adjoint identity was already
proved and is reused unchanged. Therefore the matrix innovation, gain,
closed-loop, and Joseph expressions agree with the older operator definitions.

The two inverse equations required by the perturbation theorem follow from
positive definiteness of S, itself derived from P semidefinite and R definite.
They are not additional hypotheses in the final model-to-posterior theorem.

It follows for every explicit-version observation y that

    ∫ x dη(y)(x) = kalmanPosteriorMean(K,H,m,y)
    centeredCovOp(η(y)) = josephPosteriorCov(K,H,P,R).

Here matrices on the right are interpreted as continuous linear maps on the
actual Euclidean Hilbert spaces. No default entrywise/supremum matrix norm is
silently substituted for the Euclidean operator norm.

## 4. Exact posterior discrepancies and norm certificates

Use subscript 0 for the comparison model and write ΔP=P-P0, ΔH=H-H0, ΔR=R-R0.
All norms below are Euclidean vector or induced operator norms.

The explicit innovation, gain, and closed-loop budgets are

    bS = ||ΔH|| ||P|| ||H||
       + ||H0|| ||ΔP|| ||H||
       + ||H0|| ||P0|| ||ΔH|| + ||ΔR||,

    bK = ||ΔP|| ||H|| ||S⁻¹||
       + ||P0|| ||ΔH|| ||S⁻¹||
       + ||P0|| ||H0|| ||S⁻¹|| bS ||S0⁻¹||,

    bA = bK ||H|| + ||K0|| ||ΔH||.

The covariance budget is

    bC = bA ||P|| ||A||
       + ||A0|| ||ΔP|| ||A||
       + ||A0|| ||P0|| bA
       + bK ||R|| ||K||
       + ||K0|| ||ΔR|| ||K||
       + ||K0|| ||R0|| bK.

The checked semantic theorem establishes

    ||centeredCovOp(η(y)) - centeredCovOp(η0(y0))|| ≤ bC

for arbitrary y and y0. Both priors may be singular. There is no perturbation
smallness assumption, although large or ill-conditioned discrepancies may give
a conservative bound.

The mean certificate is

    ||Eη(y)[X] - Eη0(y0)[X]||
       ≤ ||m-m0|| + bK ||y-Hm||
         + ||K0|| (||y-y0|| + ||ΔH|| ||m|| + ||H0|| ||m-m0||).

The innovation magnitude remains explicit; no uniform-in-unbounded-data estimate
is asserted.

The exact six-term covariance identity is also transferred to actual posterior
covariance operators. With E=centeredCovOp(η(y))-centeredCovOp(η0(y0)),

    E = (A-A0) P A*
      + A0 (P-P0) A*
      + A0 P0 (A*-A0*)
      + (K-K0) R K*
      + K0 (R-R0) K*
      + K0 R0 (K*-K0*).

The actual posterior mean receives the analogous exact three-source identity.

## 5. Multiscale transfer

Let F_c be finite idempotents with pairwise annihilation, and let coarse
projectors C_a be their declared exact fiber sums under ρ. For the actual E,

    C_a E C_b = Σ_{ρ(c)=a,ρ(d)=b} F_c E F_d.

Moreover,

    C_a E C_b = 0  iff  every indicated F_c E F_d = 0,

and the equivalent nonzero-descendant statement holds. The quantitative result
is a triangle-inequality bound by the SUM of descendant operator norms.
If each coarse projector is contractive, also

    ||C_a E C_b|| ≤ bC.

The record's word 'orthogonal' denotes algebraic pairwise annihilation.
Self-adjointness is not silently inferred from that word. No square-sum
Hilbert-Schmidt/Frobenius identity is asserted for the operator norm.
The no-cancellation result concerns resolved corners of E, not recovery or
identification of all primitive model errors.

## 6. Canonical versions and exceptional sets

For explicit posterior versions the displayed results are pointwise in y,y0.
For canonical kernels we prove the properly scoped statement

    for evidence_M-almost every y,
      for evidence_M0-almost every y0,
        both moment certificates hold.

This does not assert a common exceptional set on the diagonal y=y0 under a
single evidence law. Such a diagonal statement requires a separate null-set
transfer argument or using the explicit posterior versions.

## 7. What has not been closed

The result bounds actual posterior moments, not a named distance between laws.
It supplies the finite-dimensional semantic integration required before the
planned Wasserstein coupling theorem. It does not prove optimal transport,
optimal resolution selection, automatic positive-definiteness-preserving
pruning, full sequential filtering, singular innovation conditioning, or Itô
construction of general matrix-drift stochastic dynamics.

The exact two-state rational regression has P=ones(2), P0=I, H=H0=I, R=R0=I.
Its posterior covariance error is [[-1/6,1/3],[1/3,-1/6]]. Its operator norm is
1/2 whereas this general budget is 6. That confirms the structural conventions
and illustrates conservativeness, not sharpness or a performance advantage.

The universal result is the Lean proof. The single Python regression is not
used to establish any universal claim. Literature novelty remains unaudited.
