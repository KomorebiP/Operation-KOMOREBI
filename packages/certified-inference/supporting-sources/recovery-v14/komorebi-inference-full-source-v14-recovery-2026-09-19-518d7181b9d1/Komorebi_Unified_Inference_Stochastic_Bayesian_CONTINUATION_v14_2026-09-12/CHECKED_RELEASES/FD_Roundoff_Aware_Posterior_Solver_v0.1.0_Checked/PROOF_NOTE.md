# Rounded gain updates to actual Bayesian posterior tolerance

## 1. Scope and the boundary closed

The retained reference model has exact rational data H,L,N,m,y,sigma with
P=L L^T and R=N N^T+sigma I, sigma>0. State and observation coordinate sets are
arbitrary finite types in Lean; the Python producer requires positive dimensions
and enforces explicit caps. The prior may be singular and H rectangular.
Complete self-adjoint rational packet families are fixed throughout a solve.

The preceding v10 hybrid used exact rational Richardson updates and rounded
verification. This release actually executes rounded gain updates. Their local
roundoff is derived from the arithmetic graph, bounded throughout iteration,
and budgeted together with the existing outward certificate inflation. The
implemented early-stopping solver successfully returns, with an actual-posterior
Wasserstein tolerance, for every positive rational requested tolerance.

The actual posterior is the retained explicit Bayesian version at the represented
observation. The approximate law is the mathematical Joseph Gaussian of the
returned represented gain. No new canonical-kernel exceptional-set claim is made.

## 2. Exact model preprocessing and arithmetic convention

Set S=H P H^T+R, v=y-Hm, A=P H^T and

    Lambda = sigma + trace(S),  tau = 1/Lambda,
    rho = 1-sigma/Lambda,       q = rho^2.

The inherited Gram/floor and spectral proofs derive 0<=q<1 and

    energy(F (I-tau S)) <= q energy(F),

where energy is the sum of squared entries (squared Frobenius norm).
No exact innovation inverse or exact Kalman gain is computed.

The model, trace-step preprocessing, precision budgets, iteration-fuel arithmetic,
and final tolerance comparisons remain exact rational arithmetic. In particular,
the conservative initial fuel uses the exact initial residual score. Gain states
are subsequently computed from centers of the rounded update graph, not from
exact rational Richardson updates. Signed integer parts are unbounded.

The graph uses the existing dyadic ball operations. Each input, product,
addition/subtraction, and declared finite-sum node is rounded as specified by v9.
A finite-sum node exactly sums its centers/radii before its specified recentering;
this is not a claim about sequential IEEE-754 additions, BLAS, machine-word
arithmetic, finite exponents, overflow, or a hardware floating-point execution.

## 3. Whole-update error is proved from execution

Let h=2^(-t), where t specifies a requested local update accuracy. For a current
represented gain B, the evaluator constructs outward balls for

    B + tau (A-B S).

It recomputes the rounded prior, noise, innovation, residual, and correction,
including the rounding of tau as an input to the correction multiplication.
The exact graph is used only as the proof specification.

The precision-independent budget for entry (i,j) has radius coefficient k_ij(B).
The executable policy computes k(B)=sum_ij k_ij(B) and

    p_update(B,t) = precisionFor(k(B), h).

The retained integer-log theorem gives k(B)*2^(-p_update)<=h. Soundness of each
entry budget then proves

    |roundedStep(B)_ij - exactStep(B)_ij| <= h.

This includes all roundoff in the declared update graph, not just final rounding
of an otherwise exact update. No monotonicity of p_update across iterations is
assumed. Its dependence on the represented state is explicit.

With d=(state dimension)*(observation dimension), the local matrix error E obeys

    energy(E) <= d h^2.

Every resulting gain entry lies on its selected dyadic grid. Empty coordinate
types are covered by the universal statements; their summed local energy is zero.

## 4. Propagation and the roundoff floor

For an arbitrary update error E, exact algebra gives

    F(B_next) = F(B)(I-tau S) - E S.

For the rounded and ideal trajectories started from the SAME initial B_0, their
gain discrepancy D_n satisfies

    D_(n+1) = D_n(I-tau S) + E_n,  D_0=0.

A finite-coordinate Young inequality yields the robust energy estimate

    energy(U+E) <= ((1+q)/2)*a + 3e/(1-q)

when energy(U)<=q*a, energy(E)<=e and a,e>=0. Induction therefore proves

    energy(D_n) <= 6 d h^2/(1-q)^2

for EVERY n. This is a uniform tracking tube, not a claim that a fixed nonzero
roundoff budget tends to zero. The constants are sufficient, not sharp.

Write

    w = (sigma+||v||^2)/sigma^2,
    a(B) = energy(F(B))*w,
    J = 12 d energy(S) w/(1-q)^2.

Using rectangular Frobenius submultiplicativity and the ideal residual contraction,

    a(Bhat_n) <= 2 a(Bexact_n) + J h^2
              <= 2 q^n a(B_0) + J h^2.

The release separately proves the corresponding actual-distribution estimate

    W2^2(actualPosterior, JosephGaussian(Bhat_n))
        <= 2 q^n a(B_0) + J h^2.

The transport is the retained all-coupling infimum with nonnegative extended
costs. This is an upper bound, not optimality of the chosen coupling.

## 5. Computed precision and finite horizon

For eps>0, the executable policy chooses

    t = precisionFor(J, eps^2/8),
    N = solverFuel(B_0, eps/4).

The predictor guarantees J h<=eps^2/8. Since 0<h<=1, it also guarantees
J h^2<=eps^2/8. The ideal solver theorem supplies a(Bexact_n)<=eps^2/16 for n>=N.
Hence the ACTUAL rounded iterate satisfies

    a(Bhat_n)<=eps^2/4,  n>=N.

The policy is intentionally conservative. It uses an h rather than h^2 threshold
to reuse the existing exact integer-log bound. Neither an optimal bit count nor
a tight iteration bound is claimed.

## 6. Actual executable return, not only a recurrence estimate

At each current gain B, certifyGain tries any supplied finite list of certificate
precision probes, followed by

    p_verify = sufficientPrecision(B, eps^2/4).

All candidates are produced by the original outward evaluator. A successful
return has both exact checker theorems. A failed verification causes roundedGainStep
to execute. A finite fuel parameter controls this recursion.

At iteration N the exact score slack above guarantees success of the verification
fallback. Thus solveRoundedFuel cannot exhaust its computed fuel unsuccessfully.
The public solveRounded rejects nonpositive eps or invalid setup before iteration.

The main theorem rounded_solver_reaches_posterior_tolerance proves

    exists p,c,
      solveRounded(...) = some(p,c),
      checkCandidate(c) = true,
      checkTolerance(c,eps) = true,
      W2(actualPosterior, approximation(c.gain)) <= eps.

No local roundoff hypothesis is left to the caller: it is proved from the executed
update and its computed precision. Successful-return soundness is a separate
theorem without pre-assumed setup validity. Another theorem proves that the
returned gain is an ACTUAL rounded iterate with index no greater than the fuel.

## 7. Kernel-checked executions and a necessary boundary

Scalar P=H=R=1, m=0,y=1, B_0=0, eps=1/20:

    local-accuracy exponent t=20, conservative horizon N=23040,
    actual early return after 4 rounded updates,
    gain=16967772033/34359738368,
    verification precision=12, certificate score=729/2097152,
    W2<=1/20.

The first update arithmetic precision is 36 bits (the exact diagnostic records
36 bits for every update). A checked inequality confirms the returned gain is
NOT the exact Richardson fourth iterate 40/81.

Singular two-state prior P=ones(2), H=R=I, y=(1,-1), rotated rational packets,
B_0=0, eps=1/4:

    t=21, conservative horizon N=8534,
    actual early return after 3 rounded updates,
    gain=(1372190511463/4398046511104)*ones(2),
    verification precision=12, score=215859/4194304,
    W2<=1/4.

The independent exact diagnostic records 42-bit update arithmetic at each of
those three steps. Both actual solver return equations and posterior guarantees
are kernel reductions, not conclusions inferred from the Python runs.

A checked fixed-precision counterexample evaluates the scalar update at zero
fractional bits: zero maps to zero. Every such coarse iterate stays zero with
residual energy one. This demonstrates why adaptive precision cannot be replaced
by an unsupported fixed-precision convergence claim. Zero tolerance and invalid
noise-floor inputs are also proved rejected.

## 8. Reproduction and limits

See FINAL_VERIFICATION_RECEIPT.json for actual compilation and axiom-audit counts.
All inherited active Lean sources are unchanged. Pinned Mathlib caches were
reused; unrelated historical modules were preserved, not rebuilt.

The Python producer emulates the exact declared dyadic graph using Fraction
arithmetic. Its PASS_ROUNDED_SOLVER_PROVISIONAL must be followed by compilation of
the exported explicit Lean instance. Parser/exporter fidelity is not proved.
Resource caps can prevent completion; capped runs never export success proofs.
The ideal finite-termination theorem does not assert a machine-resource or
bit-complexity bound.

The model and packet geometry remain fixed. There is no new model-changing
adaptive policy, sequential filtering theorem, stochastic-integral foundation,
uncertain-input theorem, verified rounded posterior-array/sampler output,
performance superiority, or literature-priority claim. All conclusions concern
the mathematical Joseph Gaussian of the returned represented gain.
