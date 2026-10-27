# K-COS end-to-end target and the present proof boundary

This is a development companion to **The K-COS Method, first edition, official release 1.0.0**. It is not a replacement publication, and its name describes the verification goal rather than a completed end-to-end proof.

## The theorem we ultimately want

For a supported input encoding, the actual released program must either reject the requested tolerance or produce endpoints whose mathematical interpretation encloses the specified Gaussian quadratic-form tail. Acceptance must imply the requested multiplicative accuracy. The claim must account for matrix preprocessing or explicitly start after it, numerical spectral inclusion, transform approximation, finite arithmetic, parsing, and endpoint serialization.

A successful test, a kernel-checked reduction theorem, and a proof of the implemented program are different evidence. This branch is building the links between them.

## The mathematical chain now represented in Lean

For an exact finite real factor A and a finite column set s, let K be the existing `gramEntry s A`. For actual independent standard Gaussian coordinates Z, define

    p = P(Zᵀ K Z ≥ q).

`MatrixGaussian.lean` identifies the baseline finite sum with the Euclidean operator form, proves symmetry from the Gram entries, and obtains the spectral law using the proved spectral theorem and Gaussian basis invariance. The eigenvalues are the actual mathematical eigenvalues. They are not the values returned by a floating eigensolver.

The resulting equality is

    p = P(Σᵢ λᵢ Yᵢ² ≥ q),

where the coordinates Y live under the actual finite product of standard Gaussian measures. Their individual laws and independence are proved. All eigenvalues, including zero eigenvalues with their multiplicities, are retained. The event is a closed upper tail, so an atom at the threshold is included.

More generally, for X = BZ and a real symmetric operator M, the distribution of ⟨X, M X⟩ is reduced to the spectral law of B* M B. Neither injectivity nor surjectivity of B is required. This is a theorem about the explicitly defined linear-image Gaussian law. It is not yet a verified interpretation of an arbitrary stored covariance matrix or a noncentral Gaussian input.

## The conditional composition theorem

Suppose:

1. `lower i ≤ λ i ≤ upper i` for every actual eigenvalue.
2. The endpoint calculations have valid mathematical bounds `L ≤ P_lower` and `P_upper ≤ U`.
3. `acceptsRational L U ε = true` for exact rational endpoints and tolerance.
4. The chosen point estimate lies in `[L,U]`.

The formal development derives the actual probability enclosure and proves positivity and

    |estimate - p| / p ≤ ε.

The stochastic order in the first two steps is proved by a common coupling and measure monotonicity. It is not assumed. The generic chain is available as `gaussianWeightedTail_rational_acceptance`; the original Gram input is connected by `gram_quadratic_rational_acceptance`; central linear-image inputs are connected by `centralLinearGaussian_rational_acceptance`.

The eigenvalue bounds and endpoint probability bounds in items 1–2 remain explicit premises. Closing those premises is the central remaining work. These theorems must not be described as verification of the full numerical solver.

## Acceptance semantics

`acceptsRational` is an executable Lean Boolean decision on exact rationals. It checks positive lower endpoint, endpoint order, nonnegative tolerance, and the division-free inequality

    U ≤ (1 + ε) L.

For L > 0, the formal proof identifies this with `U/L - 1 ≤ ε`. Its soundness is lifted to the real probability and to every point estimate in the enclosure. The checker is additional verified source; the released Python engine has not been replaced by this checker or formally connected to it.

Two different error notions are proved separately:

    E/(S-E) ≤ τ    ↔    E ≤ τ S/(1+τ),
    (S+E)/(S-E)-1 ≤ ε    ↔    E ≤ ε S/(2+ε).

The first controls a midpoint estimate's relative error. The second controls the full symmetric interval's multiplicative width. Their positive-denominator and tolerance hypotheses are stated in Lean.

## What the recorded numerical checks mean

Four exact Lean checks use rational endpoints obtained from the retained worked example's finite tilted sum and its total-error bound. The 8,192-mode interval fails 2%, the 16,384-mode interval passes 2%, and both fail 0.1%. The source record and exact rational translations are included.

These checks establish only the acceptance inequalities for those recorded **tilted-functional intervals**. They do not establish that the finite sum or error bound is correct, prove the exponential prefactor, validate the probability-log interval, or formalize the JSON parser. No fresh run of the Python numerical solver is claimed.

## Remaining obligations

- Verify numerical spectral inclusion from the exact stored factor entries, approximate eigenvectors, residual bounds, and orthogonality bounds.
- Derive the positive weighted-square transform and the exponential-tilt change-of-measure identity under explicit integrability and domain conditions.
- Formalize the COS functional, finite-support/folding argument, packet remainder, and infinite-mode remainder with the actual rank and domain hypotheses.
- Verify the required exact interval operations and transcendental enclosures, or introduce a separately checked certificate format with proofs of all certificate semantics.
- Connect input decoding, executable branches, output parsing, and outward endpoint serialization to those mathematical definitions. A Python Boolean or a string-to-rational translation is not already that proof.
- Relate a supplied covariance representation to the explicit linear-image law, and extend the noncentral route separately.
- Prove any zero-eigenvalue removal and positive-rank restrictions used by the directed numerical backend. The present exact reduction intentionally retains zeros.

No theorem here claims universal runtime, a complete solver for all ranks, a new numerical benchmark, or independent external verification.
