# Posterior coupling, gain residuals, and squared tolerance certificates

## 1. Mathematical contract

All state, observation and latent spaces here are finite-dimensional real Euclidean
spaces, indexed by arbitrary finite types. State and observation dimensions may
be different. A model has mean m, covariance P >= 0, arbitrary real observation
matrix H, and observation-noise covariance R > 0. The observation model is the
Gaussian likelihood N(Hx,R). Its explicit Bayesian posterior version is already
proved by disintegration in the retained Gaussian-conditioning chain.

Write

    S = H P Hᵀ + R,     K = P Hᵀ S⁻¹,
    a(y) = m+K(y-Hm),   C = P-KHP.

The retained proof derives S positive definite, its two inverse equations,
C positive semidefinite, and

    C = (I-KH)P(I-KH)ᵀ + K R Kᵀ.

Neither the conditional law nor any inverse equation is a hypothesis replacing
what the final result should prove. P and C may be singular.

## 2. Transport is an infimum over all actual plans

For measures μ,ν on a Euclidean space, let Γ(μ,ν) consist of all measures γ on
pairs whose first and second pushforward marginals are μ and ν. Define

    W2Sq(μ,ν) = inf_{γ in Γ(μ,ν)} ∫ ||x-x0||² dγ,
    W2(μ,ν) = sqrt(W2Sq(μ,ν)).

The implementation uses ENNReal and the nonnegative extended integral. Thus a
nonintegrable quadratic cost cannot become a zero totalized Bochner integral.
For probability μ, every marginal-compatible plan is proved to have unit mass.
The infimum is not restricted to Gaussian plans or to the construction below.
The usual W2 square relation and the diagonal zero-cost check are proved. This
release does not develop all metric axioms or an optimal-coupling existence theorem.

Every common-source measurable pair f,g yields a genuine plan via the joint map
z -> (f(z),g(z)). The two marginal identities and the change-of-variables cost
identity are proved in QuadraticTransport.lean.

## 3. The exact quadratic moment

For a Gaussian N(c,Q) with Q >= 0,

    ∫ ||z||² dN(c,Q) = ||c||² + tr(Q).

FDGaussianQuadraticMoment.lean proves coordinate second moments from actual
Gaussian means and variances, then sums over finite Euclidean coordinates. It
also proves integrability and the ENNReal form. This avoids any confusion between
centered covariance and the uncentered second moment of a nonzero-mean law.

For independent U~N(0,P), V~N(0,Q), define

    Z = c + A U + B V,
    Z0 = c0 + A0 U + B0 V.

The inherited affine Gaussian transport identifies the laws. The difference is
Gaussian with mean c-c0 and covariance

    (A-A0)P(A-A0)ᵀ + (B-B0)Q(B-B0)ᵀ.

Consequently the exact quadratic coupling cost is squared mean error plus the
trace of that covariance. FDGaussianCoupling.lean proves the laws, marginal
identities, cost and all-plan infimum bound as separate theorems.

## 4. An arbitrary gain defines a valid approximation

For any matrix B of the gain dimensions, let

    J(B) = (I-BH)P(I-BH)ᵀ+B R Bᵀ,
    ηhat_y = N(m+B(y-Hm),J(B)).

J(B) is proved positive semidefinite. With X~N(m,P) and e~N(0,R) independent,

    Z_B = X+B(y-HX-e)

has exactly this law. In Lean the source is centered U=X-m and the equivalent
sample is m+B(y-Hm)+(I-BH)U-B e. For B=K, its law is the already-proved Bayesian
posterior η_y. The joint samples for K and B use the SAME U,e. This yields an
actual coupling of η_y with ηhat_y; Gaussian covariance matching alone is not
used as a substitute for the marginal proof.

The arbitrary-gain approximation is not asserted to be the original model's exact
conditional law. When the residual below vanishes, it is proved equal to η_y.

## 5. Residual identities

Put v=y-Hm and F=P Hᵀ-B S. Since K S=P Hᵀ,

    K-B = F S⁻¹.

Expanding Joseph covariance and using the exact gain identities gives

    J(B)-C = (K-B)S(K-B)ᵀ = F S⁻¹ Fᵀ >= 0.

FDInexactGainAlgebra.lean proves these identities and positivity. No P inverse or
C inverse is introduced. Covariance excess is nonnegative for this particular
fixed-model Joseph approximation; it is not an ordering claim for arbitrary
model changes.

The centered observation H(X-m)+e has covariance S. Hence the coupling difference
has mean (K-B)v and covariance (K-B)S(K-B)ᵀ. The exact cost is

    ||F S⁻¹ v||² + tr(F S⁻¹ Fᵀ).

FDInexactGainCoupling.lean proves this as the cost of the actual joint measure,
then concludes

    W2Sq(η_y,ηhat_y) <= ||F S⁻¹ v||²+tr(F S⁻¹ Fᵀ).

The upper certificate is finite. Optimality of this particular coupling is not claimed.

## 6. Remove the exact inverse from the reported majorant

Suppose σ>0 and the explicit quadratic noise-floor hypothesis holds:

    σ||x||² <= <x,Rx>  for every observation-space x.

Since HPHᵀ >= 0, the same floor holds for S. Coercivity, Cauchy-Schwarz and the
actual inverse equation imply ||S⁻¹||op <= 1/σ. This is proved, not assumed in
the final residual-only theorem.

Define ||F||F² = sum_i sum_j F_ij². Finite-dimensional Cauchy-Schwarz gives

    ||FQv||² <= ||F||F² ||Q||op² ||v||²,
    tr(FQFᵀ) <= ||Q||op ||F||F².

The latter upper bound is sufficient for Q=S⁻¹, which is positive definite.
The theorem therefore yields

    W2Sq(η_y,ηhat_y) <= ||F||F² (1/σ+||v||²/σ²).

This displayed budget uses P,H,R,B,m,y and σ, not K, C, or S⁻¹. It retains the
observation innovation rather than asserting uniform control over all unbounded y.

For ε>=0, the checked squared condition

    ||F||F² (σ+||v||²) <= ε² σ²

implies W2(η_y,ηhat_y)<=ε. The main declaration is

    Komorebi.FiniteDimensionalGaussianKalman.posterior_wasserstein2_le_of_residual_tolerance

in FDResidualEnergyCertificate.lean. This is a mathematical stopping implication.
It does not verify floating-point evaluation, an eigenvalue routine producing σ,
an iterative solver's termination, or a cost/complexity improvement.

## 7. Full two-model factor coupling

A FactoredGaussianModel contains m,H,L,N with positive-definite N Nᵀ. Its prior
covariance is L Lᵀ, derived positive semidefinite. Both models use the same finite
latent coordinate types. The model record does not contain a posterior-identification
assumption. That is supplied by the retained conditioning proof.

Define

    U = (I-KH)L,  V = K N.

The sample a(y)+Uξ+Vζ, for independent standard Gaussian vectors, is proved to
have the actual posterior law. Both models use the positive observation-noise
factor convention consistently; the covariance remains Joseph's expression.

The cost of the joint shared-noise samples is exactly

    ||a(y)-a0(y0)||² + ||U-U0||F² + ||V-V0||F².

FDPosteriorFactorCoupling.lean proves both actual marginal equations, that cost,
and

    W2Sq(η_y,η0_y0) <= ||a(y)-a0(y0)||²+||U-U0||F²+||V-V0||F².

Canonical-posterior equality is inherited evidence-a.e. separately for each model.
The comparison itself is pointwise for the explicit posterior versions. No common
canonical exceptional set for distinct evidence laws is silently assumed.

## 8. Verification and independent checks

31 active modules have final-source successful pinned-runtime receipts. The audit
covers all 119 theorem/lemma declarations (53 retained dependency declarations,
66 new declarations). Only the three standard axioms listed in AXIOM_AUDIT.json
occur. Six symbolic regressions cover exact gain, zero residual, zero prior,
zero observation, and the zero-gain covariance identity; a seventh check gives
nonnegativity of the residual majorant.

checks/exact_checks.py separately checks 24 constructed rational matrix cases with
state/observation dimensions from one through three, including rectangular maps
and singular/deterministic priors. It checks residual identities, a separate
sampler-coefficient cost calculation and the noise-floor majorant. A 16-point
Rademacher enumeration checks a quadratic expectation independently; it is not
a Gaussian-law proof. A factor-sign example records nonoptimality of a chosen
coupling. These finite diagnostics are not used to infer universal claims.

## 9. Remaining boundaries

- No general Wasserstein metric-space instance, triangle-inequality development,
  optimal-plan theorem, or equality with an independently defined transport API.
- No covariance-discrepancy-to-factor-discrepancy conversion or automatic optimal alignment.
- No self-adjoint Hilbert-Schmidt packet-energy refinement theorem yet. Algebraic
  pairwise annihilation does not by itself justify a square-sum norm identity.
- No certified floating-point implementation, admissible pruning algorithm, monotone
  adaptive improvement theorem, optimal resolution selection or termination proof.
- No full finite-horizon filtering semantics or new continuous-time Itô derivation.
- No singular-innovation/pseudoinverse conditioning or nonlinear/non-Gaussian extension.
- No identification of primitive model defects from identical posterior laws.
- No literature-priority claim. Declaration counts include support identities.
