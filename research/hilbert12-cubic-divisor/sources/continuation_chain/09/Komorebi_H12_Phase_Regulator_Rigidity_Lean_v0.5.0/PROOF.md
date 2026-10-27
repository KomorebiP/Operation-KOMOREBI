# A phase-sensitive Green functional, exact logarithm lifts, and an analytic Lean core

**Komorebi H12 continuation, version 0.5.0.**

## Status

The growing cubic-return product can equivalently be compared through one complex-valued integral of the logarithmic second derivative. This integral retains the phase and has an explicit, sharp stability bound. The fundamental integration identity, its exponentiated cubic comparison, contraction rigidity, and conditional cube-root separation are now kernel-checked in Lean using actual analysis, not only polynomial algebra.

The actual logarithm lift at the zero anchor and the conditional final cube-root separation are established by directed interval calculations with explicit infinite-series tails. The interval implementation is trusted mpmath.iv elementary arithmetic, not a Lean-verified numerical kernel. Its experimental status is disclosed.

There are 14 new Lean theorem constants, 154 including the unchanged inherited 140. The principal unresolved assertion remains U_Gamma^3=U_alg^3 (or an equivalent phase-sensitive integral identity). A tiny interval containing the discrepancy does not prove it is zero. No novelty or general Hilbert-12 claim is made.

## 1. Inherited analytic and arithmetic inputs

Fix

    omega = exp(2 pi i/3), beta = 7^(1/3) omega^2,
    epsilon = 2-beta, rho = epsilon^(-1),
    t = -(beta^2+2beta)/15, s = -(beta+2)/15.

Both t and s lie in the upper half-plane. We use the BCG elliptic-gamma product and its negative-first-period continuation [1]:

    F(z) = Gamma_ell(z;-t,s)^5 / Gamma_ell(5z;-5t,5s),
    U_Gamma = F(1/3), F(0)=epsilon^2, F(z+1)=F(z).

The zero anchor is an inherited exact theta/eta theorem, not inferred from numerical agreement in this package. The preceding block supplies the rational fifth-isogeny expressions

    G(z+s)-G(z) = 5 wp_t(z)-25 wp_(5t)(5z)-2(a_t+b_t),
    G(z-t)-G(z) = 25 wp_(5s)(5z)-5 wp_s(z)+2(a_s+b_s),

where G=(F'/F)' and a_v=wp_v(1/5), b_v=wp_v(2/5).

Let p=exp(2 pi i t), q=exp(2 pi i s). On the horizontal strip

    -Im(t) < Im(z) < Im(s),

the absolutely convergent series

    L(z) = -5 sum_(n>=1, 5 does not divide n)
        [p^n exp(2 pi i n z)-q^n exp(-2 pi i n z)]
        /[n(1-p^n)(1-q^n)]                                     (1)

is a specific holomorphic logarithm of F: exp L=F. It is periodic as a logarithm, L(z+1)=L(z), not merely after exponentiation. It and all derivatives converge uniformly on narrower closed substrips. In particular the real interval [0,1] is in its nonvanishing domain. Write G(x)=L''(x) there, interpreting restriction to the real line as a complex-valued real derivative when applying Lean.

The independent arithmetic candidate is fixed by the retained Gauss/CM branch, not fitted to F. Its input formulas are transcribed in prior/ARITHMETIC_INPUT.md. They give an algebraic unit U_alg in the identified ray field. The previously retained modulus comparison |U_Gamma|=|U_alg| is not re-proved here and is not needed to execute the interval inequality tests.

## 2. The conductor-three Green identity

For any continuous complex-valued g on [0,1], define

    R3(g) = -2 integral_0^(1/3) x g(x) dx
            + integral_(1/3)^1 (x-1) g(x) dx.                  (2)

### Theorem 2.1 (exact endpoint identity)

If L is twice continuously differentiable on the real interval, then

    R3(L'') = 3L(1/3)-2L(0)-L(1).                              (3)

Proof. The two primitives are

    (x L'(x)-L(x))' = x L''(x),
    ((x-1)L'(x)-L(x))' = (x-1)L''(x).

Apply the fundamental theorem of calculus on the two subintervals. The coefficient of L'(1/3) is -2/3+2/3=0. The remaining endpoint terms are precisely (3). No logarithm or phase convention is used in this integration identity.

This theorem is compiled in H12PhaseRegulator. The proof uses Mathlib's interval integral and HasDerivAt framework and the fundamental theorem of calculus. The supplied first- and second-derivative functions are genuine derivatives in the formal statement, not names for unrelated scalar data.

### Multiplicative corollary

For F=exp L,

    exp(R3(L'')) = F(1/3)^3/[F(0)^2 F(1)].                      (4)

If F(1)=F(0), this becomes

    exp(R3(G)) = F(1/3)^3/F(0)^3.                              (5)

Crucially, (5) does not require L(1)=L(0). It only requires periodicity of the exponentials at the endpoints. Lean certifies both (4) and (5).

For the actual gamma function,

    exp(R3(G)) = U_Gamma^3/epsilon^6.                          (6)

Thus the existing return limit has the exact alternative expression

    lim D_m = exp(-R3(G)).                                    (7)

The fact that the two analytic descriptions agree is not an independent arithmetic evaluation of either one.

### Tap interpretation

The endpoint stencil is (-2,3,-1) on the nodes (0,1/3,1). It annihilates constants and linear functions:

    -2+3-1=0,  -2*0+3*(1/3)-1=0.

Consequently the comparison retains the cubic target while discarding precisely the two affine integration terms. This is a Green-integral version of the earlier conductor-adapted tap construction.

## 3. Winding, rather than an erased integration constant

For a periodic nonzero F and a continuous logarithm along [0,1], there is an integer k with

    L(1)-L(0)=2 pi i k.

Equation (3) then gives

    F(1/3)/F(0) = exp(R3(G)/3) exp(2 pi i k/3).                (8)

Cubing removes the winding choice; taking a cube root without retaining it does not.

For the particular logarithm (1), k=0, so

    U_Gamma = epsilon^2 exp(R3(G)/3).                          (9)

There is nevertheless a nontrivial lift at the anchor: the periodic logarithm L(0) is not the principal logarithm of epsilon^2. Section 7 certifies

    L(0) = 2 Log(epsilon)-2 pi i,                              (10)

where Log is the principal logarithm. It also certifies Im L(1/3) in (-pi,pi), hence L(1/3)=Log(U_Gamma). Therefore

    R3(G) = 3 Log(U_Gamma)-6 Log(epsilon)+6 pi i.               (11)

This is an exact analytic identity with its integer lift fixed by the inherited anchor theorem and a validated interval isolation of that integer. It makes no assertion that U_Gamma=U_alg.

A negative control is instructive. The function exp(2 pi i z)F(z) has the same logarithmic second derivative, the same period one and zero anchor, and the same cubed value at 1/3, but its unpowered value is omega U_Gamma. It fails the exactly normalized full doubling law. Thus none of these weaker constraints is silently promoted to equality of the unpowered values.

## 4. A sharp stability bound

The signed kernel in (2) is negative on both open subintervals and its absolute integral is

    integral_0^(1/3) 2x dx + integral_(1/3)^1 (1-x) dx = 1/3.

Consequently

    |R3(g)-R3(h)| <= (1/3) sup_[0,1] |g-h|.                  (12)

The constant 1/3 is sharp, for example on a constant difference. If the rightmost supremum is at most delta, then

    |exp(R3(g)-R3(h))-1| <= exp(delta/3)-1.

The inequalities are ordinary analytic consequences of the integral norm bound. The sharp bound is not claimed as a compiled Lean theorem in this release; the exact endpoint identity and comparison implications are compiled.

## 5. Exact Fourier multiplier and support reduction

For kappa != 0, direct integration yields

    R3(exp(kappa x)) = [3 exp(kappa/3)-2-exp(kappa)]/kappa^2.   (13)

Its continuous value at kappa=0 is -1/3. For a nonzero integer frequency n,

    R3(exp(2 pi i n x)) = 3(omega^n-1)/(2 pi i n)^2.

Differentiating (1) termwise and applying (13) gives

    R3(G) = -15 sum_(n>=1, gcd(n,15)=1)
        [p^n(omega^n-1)-q^n(omega^(-n)-1)]
        /[n(1-p^n)(1-q^n)].                                 (14)

The 5-smoothing removes multiples of five, while the conductor-three Green multiplier removes multiples of three. This support statement is exact. It is not a claim that the remaining frequencies already identify a cyclotomic arithmetic value.

The complex integral is therefore evaluated without quadrature error by integrating an absolutely and uniformly convergent Fourier series termwise. The numerical checker implements (14) directly, separately from the evaluations of L(0) and L(1/3).

## 6. A weaker sufficient comparison than full gamma reconstruction

The compiled theorem same_regulator_same_normalized_cube says the following. Suppose L_f,L_g have their stated genuine continuous second derivatives on the real line, their exponentials agree at the zero anchor and are periodic at the endpoints, and

    exp(R3(L_f'')) = exp(R3(L_g'')).

Then exp(L_f(1/3))^3=exp(L_g(1/3))^3. Equality of the second derivatives is a sufficient but stronger hypothesis. No arithmetic gamma identity is included implicitly: both functions, derivative hypotheses, and the comparison input are explicit.

There is also an ordinary global consequence of the preceding isogeny system. Suppose nonzero meromorphic functions f,g on C have the same two inhomogeneous equations for (f'/f)' and (g'/g)', have period one, and are holomorphic and nonzero at zero with f(0)=g(0). Their G-difference has periods 1,t,s, a nondiscrete subgroup, and is therefore constant. The quotient has the form

    f/g = B exp(C z^2/2 + A z).

Period one forces C=0 and A=2 pi i k for an integer k. The common zero anchor fixes B=1. Hence f(1/3)^3=g(1/3)^3 WITHOUT imposing the full eight-factor multiplication law. Equal zero windings, or the full doubling law, further remove k. The global meromorphic and nondiscrete-period steps are ordinary proofs, not newly formalized results.

A separate compiled analytic theorem proves that a phase d continuous at zero, invariant under z -> rho z with |rho|<1, is constant. If d(0)=1, then d=1. Its hypotheses are stronger than finite snapshot invariance: they include coherent invariance under every iterate and continuity at the common contraction anchor. This explains exactly why the earlier finite phase deformations do not establish freedom in the actual normalized gamma function.

None of these results constructs the missing arithmetic comparison function.

## 7. Interval certificate and what it proves

The interval implementation uses mpmath.iv elementary arithmetic at 90 and 120 decimal digits. Exact integer-root bounds are constructed for 7^(1/3) and sqrt(3), checked by integer inequalities, and converted to containing intervals. Omega is formed as -1/2+i sqrt(3)/2. No algebraic branch is fitted.

We certify

    |p| < 19/20,  |q| < 3/5.

For truncation after N terms the error in either L(0) or L(1/3) is at most

    E_N = 5/[(N+1)(1-r^(N+1))(1-v^(N+1))]
          *[r^(N+1)/(1-r)+v^(N+1)/(1-v)],
    r=19/20, v=3/5.                                       (15)

Indeed, for n>N, bound 1/n by 1/(N+1), each inverse denominator by its geometric lower bound at N+1, and sum the two geometric tails. Restoring the omitted multiples of five only enlarges the bound. The error in (14) is at most 6E_N because |omega^n-1|<=2.

The production run uses N=2500. There are 2000 retained logarithm terms and 1333 active regulator terms. Both interval runs certify

    E_N < 8*10^(-58).

A rectangle of coordinate radius E_N (or 6E_N) is added to the computed partial sum. Thus truncation AND the interval library's arithmetic rounding are retained. Machine-readable binary interval endpoints, algebraic input bounds, versions and commands are recorded in evidence/interval_90.json and interval_120.json.

### Anchor integer

The inherited exact identity exp L(0)=epsilon^2 implies

    [L(0)-2 Log(epsilon)]/(2 pi i) is an integer.

The containing interval has real part strictly between -3/2 and -1/2. The unique possible integer is -1, proving (10). Imaginary enclosure around zero is a consistency check; the exact integer property comes from the inherited exponential equality, not from a small imaginary residual.

### Certified conditional branch selection

The independent ray-field value is evaluated from the fixed six-term Gauss sum and rational formulas in prior/ARITHMETIC_INPUT.md. The run certifies

    |U_Gamma/U_alg-1| < 10^(-56) < 1/2.                     (16)

The upper interval endpoint is approximately 1.3027901163*10^(-57).

If a separate proof establishes U_Gamma^3=U_alg^3, then (16) selects U_Gamma=U_alg. The compiled lemma cube_comparison_with_enclosure proves this implication. Its proof shows that every nonidentity complex cube root r of one has |r-1|^2=3.

Equation (16) ALONE is not an equality or algebraicity certificate. In particular it does not place the actual discrepancy in mu_3.

### Concrete phase lift

The validated integral is approximately

    R3(G) = 3.893333256063297421253355989489840028...
            +10.785115541569283379759434534856227438... i.

Its imaginary part lies between 3pi and 4pi. Replacing it by Log(exp(R3(G))) subtracts 4pi i. Consequently taking that principal logarithm and then dividing by three multiplies the correctly reconstructed value by omega. This failure is verified as a negative control, not silently normalized away.

All 28 interval assertions and three negative controls pass at both precisions. Assertions of the form 'zero lies in a residual interval' are consistency checks, not standalone proofs of equality. The analytic identities being checked have the separate proofs above.

### Numerical trust boundary

The mpmath documentation states the enclosure contract for iv and also warns that interval support is experimental [3]. This implementation uses supported elementary operations only and avoids noninteger interval powers for its algebraic inputs. The certificate is conditional on those implementations; it is not a formal verification of mpmath or of transcendental interval routines inside Lean. Independent interval-backend replication remains a useful audit.

## 8. A finite elliptic-isogeny bridge to the separate CM curve is impossible

The isogeny formulas are useful within their analytic charts. They cannot supply a finite chain of elliptic isogenies from E_t to the equianharmonic CM curve E_omega.

In fact,

    225 t^3-42t+7=0,
    beta=2-1/(4-15t).

Since X^3-7 is Eisenstein at seven, Q(beta) has degree three; the displayed formulas give Q(t)=Q(beta). Thus t has degree three over Q.

If a nonzero isogeny C/(Z+Zt) -> C/(Z+Zomega) existed, it would lift to multiplication by a nonzero complex scalar alpha. The lattice inclusions would give

    alpha=a+b omega,  alpha t=c+d omega

for integers a,b,c,d. Hence t=(c+d omega)/(a+b omega) belongs to Q(omega), which has degree two. This is impossible. The same applies to a finite chain, using composition and dual isogenies for reverse arrows.

More generally an isogenous period is a rational fractional-linear transform, preserving this field-degree obstruction. The proof is ordinary uniformization and field algebra; the package checks its elimination polynomial, but does not claim a Lean formalization of elliptic uniformization.

This excludes one proposed type of comparison, not the special-value identity. A phase-sensitive period identity can exist without an isogeny between the two auxiliary elliptic curves. It indicates that the remaining bridge must use the rank-three unit transport, a period/regulator comparison, or another genuinely higher-level construction rather than a finite sequence of ordinary elliptic isogenies.

## 9. Remaining exact theorem

The primary target is now equivalently

    exp(R3(G)) = (U_alg/epsilon^2)^3.                       (17)

With the certified branches, a lifted version is

    R3(G) = 3 Log(U_alg)-6 Log(epsilon)+6 pi i.              (18)

The enclosure of the difference in (18) has modulus below 10^(-55), but zero is not inferred from that enclosure. The existing modulus theorem fixes its real part; the phase-sensitive identity is still needed.

Once (17) is independently established, the formal Green theorem gives the cubic equality and the interval-backed branch theorem finishes the original equality. There is no longer a separate computational branch-selection task to improvise after the power comparison.

## 10. Formal scope and provenance

New modules:

- H12PhaseRegulator: seven theorems using genuine complex-valued interval integrals, HasDerivAt, the fundamental theorem of calculus, and Complex.exp.
- H12ContractingRigidity: three theorems, including an analytic limit proof using continuity and norm contraction for arbitrary iterates.
- H12CubicBranch: four theorems proving cube-root norm/separation and the explicitly conditional enclosure implication.

All source files containing the 140 inherited theorems are unchanged. The total 154 compile against Lean 4.34.0-rc2 (6a10ac8c22beadecabdbb0919c2b50214762f91d) and Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Every theorem's transitive axiom list is audited; only propext, Classical.choice and Quot.sound are allowed. No admitted proofs, project axioms, native_decide or unsafe declarations are accepted. A false arithmetic theorem must be rejected.

This release does NOT formally define elliptic gamma, prove that its logarithm has the required derivatives, prove the real-place Stark identities, or prove (17). The analytic arguments above establish the gamma application of the formal generic theorem. The interval arithmetic and the no-isogeny uniformization argument also remain outside Lean.

The exact checker passes 41 assertions and four negative controls. The interval checks pass as specified above. Failure and replay details are in evidence/. The portable runtime was restored with the pinned combined SHA-256; the multi-gigabyte runtime is not included in this source handoff.

## References

[1] Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields, arXiv:2311.04110v2. Definitions, continuation, the original example, and the boundary between the modulus theorem and conjectural special-value identification. https://arxiv.org/html/2311.04110v2

[2] Mathlib, interval-integral fundamental theorem of calculus; actual verification uses the pinned source revision. https://leanprover-community.github.io/mathlib4_docs/Mathlib/MeasureTheory/Integral/IntervalIntegral/FundThmCalculus.html

[3] mpmath documentation, interval contexts and experimental-support warning. The executed version is recorded in the evidence, not inferred from the latest documentation. https://mpmath.readthedocs.io/en/latest/contexts.html

[4] Retained Fifth Isogeny Transport v0.4.0, preserved as prior/v04_source_and_evidence.zip, and its source hashes.

[5] Retained H12 CM/Gauss branch note in Komorebi_H12_ALL_MARKDOWN_2026-10-02.md, file_id file_00000000b3f081f582f72d0414888258. The exact branch table and reconstruction are transcribed in prior/ARITHMETIC_INPUT.md.
