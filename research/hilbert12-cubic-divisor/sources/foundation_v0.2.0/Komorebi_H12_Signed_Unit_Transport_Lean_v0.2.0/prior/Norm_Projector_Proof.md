# Exact norm projection, signed half-period recovery, and the first Lean core

**Checkpoint:** 2026-10-02. **Version:** 0.1.0.

## Status

This block proves a uniform classification of multiplication norms of the rational elliptic kernel from the preceding cubic-return construction. On a free rank-two subgroup of meromorphic functions modulo translation coboundaries and constants, odd norms prime to five are the identity, even norms prime to five are a split integral projector, and norms divisible by five vanish. The component killed by the doubling norm is nontrivial. An explicit norm-one rational factor is recovered from three signed half-period products.

Fifty algebraic/combinatorial/explicitly conditional lemmas are compiled in Lean 4.34.0-rc2 with the user's pinned Mathlib. The analytic theta identities, divisor-function dictionary, and the complex analytic limit theorem are ordinary mathematical proofs here or inherited inputs, NOT Lean-formalized facts. No gamma algebraicity, U_Gamma^3=U_alg^3, or general Hilbert-12 theorem is asserted. No literature priority claim is made.

## 1. Setting and inherited input

Let E=C/(Z+Zt), Im(t)>0, and let s represent a point S of infinite order. Define

    q(z) = theta0(z;t)^5 / theta0(5z;5t),
    psi(z) = q(z)^2 / (q(2z) q(2z+s)).

Here theta0 is the product in BCG [1]. The function q is even and elliptic, and

    div(q)=4[0]-[1/5]-[-1/5]-[2/5]-[-2/5].                 (1)

The preceding note, copied under prior/, proves the normalized multiplication law

    product_(eta in E[n]) q(z+eta) = q(nz),   if 5 does not divide n,
                                    1,       if 5 divides n.            (2)

These are exact meromorphic identities. In particular there is no unspecified scalar. Formula (2) follows directly by real root-of-unity averaging and vertical residue splitting in theta0. When 5 divides n, the frequencies retained by averaging have already been removed by smoothing. Removable points are interpreted meromorphically.

The H12 specialization is

    beta=7^(1/3) exp(-2*pi*i/3), epsilon=2-beta,
    rho=epsilon^(-1), t=-(beta^2+2beta)/15, s=-(beta+2)/15.

The infinite order of S follows from the rational independence of 1,t,s.

## 2. A complete multiplication-norm formula

For a nonzero meromorphic elliptic function f and an integer n>=1, define

    (N_n f)(w) = product_(nz=w) f(z).

There are n^2 preimages counted with multiplicity; in characteristic zero [n] is unramified. The product is a meromorphic function of w. Equivalently, choose z with nz=w and multiply f(z+eta) over eta in E[n]. It is independent of that choice.

### Theorem 2.1

For every n>=1,

    N_n psi(w) = 1,                                      if 5 | n;
    N_n psi(w) = q(w)^2/[q(2w) q(2w+n s)],                if 5 does not divide n and n odd;
    N_n psi(w) = 1/[q(w)^2 q(w+k s)^4], n=2k,             if 5 does not divide n and n even.    (3)

**Proof.** The numerator norm is (N_n q(w))^2. If n is odd, doubling permutes E[n], so the two denominator products are q(2w) and q(2w+n s) when 5 does not divide n. If 5 divides n they are both one, as is the numerator.

If n=2k, doubling maps E[n] onto E[k] with four preimages for each point. The denominator products are therefore the fourth powers of N_k q evaluated at w and w+k s. If 5 does not divide n, (2) gives q(w)^4 q(w+k s)^4. The numerator q(w)^2 cancels two powers. If 5 divides n then 5 divides k, and all relevant norms are one. This proves (3). QED.

At n=2 this says

    N_2 psi(w) = 1/[q(w)^2 q(w+s)^4]
               = q(w)^(-6) (q(w)/q(w+s))^4.               (4)

Thus taking the full doubling norm produces a sixth theta power and a specified boundary; it does not evaluate the original cubic-return target.

## 3. Every boundary multiplier is explicit

For n=2k+1 prime to five, define

    B_k(w)=product_(j=0)^(k-1) q(2w+(2j+1)s).

The empty product is one. Then

    N_(2k+1) psi(w) = psi(w) B_k(w)/B_k(w+s).              (5)

Indeed the ratio on the right telescopes to q(2w+s)/q(2w+(2k+1)s).

For n=2k prime to five, define

    C_k(w)=product_(j=0)^(k-1) q(w+j s)^4.

Then

    N_(2k) psi(w) = q(w)^(-6) C_k(w)/C_k(w+s).             (6)

Here the boundary is (q(w)/q(w+k s))^4. Consequently over any finite orbit window w_j=w_0+j s,

    product_(j=b)^(c-1) N_(2k) psi(w_j)
      = [product_(j=b)^(c-1) q(w_j)]^(-6)
        C_k(w_b)/C_k(w_c).                                (7)

The odd formula has the same endpoint structure with the unnormed product of psi and B_k endpoints. No closure of a finite permutation permits deleting these endpoints without checking the representative multipliers.

## 4. Exact quotient and independence of its two generators

Let M(E)^* be the multiplicative group of nonzero meromorphic functions on E. Quotient it by constants and all translation coboundaries R(w+s)/R(w), R in M(E)^*. Write [f] for a class and use additive notation for classes.

The norm maps descend to this quotient. In fact,

    N_n(R(w+s)/R(w)) = N_n R(w+n s)/N_n R(w),

which is a translation coboundary for the step s: use the product of N_n R(w+j s), 0<=j<n, as primitive. Norms of constants remain constants. Also N_m N_n=N_(mn).

Put e=[q], p=[psi]. We first prove that e,p generate a free Z^2, rather than merely assume independence.

For a finite divisor D and an infinite translation orbit O, let charge_O(D) be the sum of coefficients at points in O. Every translation coboundary has charge zero on every orbit, because its finite divisor telescopes.

Consider the disjoint orbits

    O_0={nS:n in Z},       O_half={-S/2+nS:n in Z}.

Their charges are

                         q        psi
    O_0                  4         4
    O_half               0        -4.                    (8)

To check this, nonzero integer or half-integer multiples of S cannot be torsion. At w=0, psi has order 8-4-0=4. At w=-s/2, only q(2w+s) meets the zero at the origin, giving order -4; the other points on each orbit contribute zero. The two orbits are disjoint because S has infinite order.

If q^a psi^b were constant times a translation coboundary, (8) would force

    4a+4b=0,    -4b=0,

hence a=b=0. Therefore

    Z e + Z p is isomorphic to Z^2.                       (9)

The formal Lean proof certifies the general finite-support pushforward argument and these two linear obstructions. The application from meromorphic functions to their divisors is the ordinary proof above, not hidden as a Lean axiom.

## 5. The norm is an integral projector

By (2), (5), and (6), on the subgroup (9),

    N_n = identity,                   n odd, 5 does not divide n;
    N_n = [[1,-6],[0,0]],             n even, 5 does not divide n;
    N_n = zero,                       5 divides n.        (10)

Coordinates (a,b) mean [q^a psi^b]. Let P be the middle matrix. Then

    P^2=P,
    image(P)=Z(1,0),
    kernel(P)=Z(6,1).                                 (11)

The primitive distribution class

    f=6e+p=[q^6 psi]

is nonzero: its charges in (8) are 28,-4. The basis e,f is integral, with determinant-one change of basis. In this basis every even norm prime to five is diag(1,0).

This is the exact loss of information under symmetric doubling. It leaves one component and deletes a second, genuinely nonzero one. Repeating the full doubling norm cannot recover the deleted component. Norms divisible by five delete both components.

The residue-ten matrix law is multiplicative for all natural indices. Its complete finite residue calculation and its lift to all m,n are kernel-checked in H12NormSemigroup. Analytic multiplication-by-zero norms are not defined or claimed; the matrix extension at zero is only a convenient algebraic zero element.

## 6. An exact norm-one rational factor

Define

    R_2(z)=q(z)^4/q(2z).                                 (12)

Then

    N_2 R_2(w)=1.                                       (13)

Indeed the numerator norm is q(w)^4, while each of the four denominator factors is q(w). Moreover,

    psi(z)=q(z)^(-6) R_2(z)^2 q(2z)/q(2z+s).              (14)

Both identities are branch-free and use integer exponents. Formula (12) is a rational elliptic function by the preceding rational wp representation. It is not constant: its divisor has coefficient 12 at zero, while its doubled norm has zero divisor. Thus norm one must not be confused with being the constant function one.

The last factor of (14) is a coboundary for translation by s/2, not automatically for translation by s. We retain that distinction. Equation (14) is not a replacement for the full-step boundary formulas (5)-(6).

## 7. Three signed half-period channels retain what the norm loses

Write

    A=q(z), B=q(z+1/2), C=q(z+t/2), D=q(z+(1+t)/2).

The untwisted norm is ABCD=q(2z). Define the three nontrivial multiplicative Walsh channels

    W_1=AB/(CD), W_2=AC/(BD), W_3=AD/(BC).                (15)

Their exact product is

    W_1 W_2 W_3 = A^4/(ABCD)=R_2(z).                    (16)

Thus all three together recover the explicit norm-one factor which the full norm cannot detect.

Each W_chi obeys

    W_chi(z+eta)=W_chi(z)^(chi(eta)), eta in E[2],

so N_2 W_chi=1. This is a permutation of four factors with integer exponents, not a new analytic phase convention.

The full fourth-power reconstruction reads

    (ABCD) W_1 W_2 W_3=A^4.                              (17)

Do not discard the trivial channel ABCD when reconstructing A. Nor does knowing the nontrivial channels alone fix arbitrary common scaling. The theta normalization (2) is a separate exact input.

These identities specify a better next comparison object: the individually oriented signed half-period channels, together with their trivial-channel normalization and the unit carries from the previous block. They do not yet evaluate their limits in the separate CM/ray-field realization, and they do not identify half-period translations with an Artin action.

## 8. What Lean has checked

The package uses Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, with Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The portable archive was restored from the user's Library and matched SHA256 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34.

| Module | Theorems | Formal content |
|---|---:|---|
| H12Taps | 8 | Arbitrary finite integer tap gain divisible by 3 when its first moment vanishes; optimal displayed stencil; algebraic cubic-unit identity |
| H12NormAlgebra | 10 | Field identities for four-sheet norms, boundary telescoping, norm-one factor, Walsh recovery, and an explicitly conditional cubic-comparison implication |
| H12OrbitObstruction | 11 | Finite-support orbit-charge conservation, invariant-label pushforward, and the two-orbit obstruction |
| H12NormProjector | 10 | Integral projector, exact image/kernel, split coordinates, and charge injectivity |
| H12PacketCarries | 5 | Actual rational unit/inverse matrices, their inverseness, and uniform half-grid carries |
| H12NormSemigroup | 6 | All residue-ten matrix products and their lift to arbitrary natural m,n |

All 50 theorem constants are checked in a fresh isolated compilation directory. Every theorem's axiom dependency list is audited. Only the standard dependencies propext, Classical.choice, and Quot.sound occur, where needed. Several finite results have no axiom dependencies at all. There are no admitted proofs, project axioms, native_decide, or unsafe declarations. A separate false-statement test is required to fail normally.

### Formalization boundary

The full analytic theorem (3), the quotient of meromorphic functions, the rational independence of the complex periods, theta/gamma convergence and functional equations, and the identification of the arithmetic candidate are not formalized in this release. Statements with supplied norm equalities or nonzero field elements retain those as explicit hypotheses. In particular pointwise_phase_comparison assumes BOTH an analytic and an arithmetic value for the same limit; the unproved arithmetic value is not manufactured by Lean.

The formalized integer projector becomes a theorem about analytic classes through Sections 2-5 of this ordinary proof. The two levels are reported separately.

## 9. Remaining research target

The preceding result gives an exact analytic approximant D_m with

    lim D_m=epsilon^6/U_Gamma^3.

The missing independent evaluation is

    lim D_m=epsilon^6/U_alg^3.                           (18)

If (18) is established, the elementary comparison lemma gives U_Gamma^3=U_alg^3, and a rigorous complex branch separation can select the cube root. Nothing here establishes (18) or membership of the actual discrepancy in mu_3.

The new theorem explains why symmetric full norms alone are insufficient: they erase the nontrivial distribution class f. Signed channels (15), all chart transitions, and the endpoint normalization must remain in the comparison. Their norm identities are useful constraints, not an algebraicity certificate.

## 10. Checks and provenance

The exact Python checker independently verifies 63 finite assertions: all divisor pushforwards and translation classes for 1<=n<=24; the two-charge matrix; the primitive and rational norm-one factors; polynomial identities; and all residue-ten norm matrices. The universal claims are proved above, not inferred from this bounded range.

At each of 50 and 90 requested decimal digits, with 20 guard digits, the numerical checker verifies 33 theta identities and four negative controls. It uses direct theta products both at an independent generic elliptic parameter and at the actual cubic t,s. It does not use the gamma-algebraic comparison. These are floating-point regressions, not interval certificates.

See evidence/FAILURES.md for the broad-import timeout, development corrections, axiom-report parser correction, and the interrupted batched numerical attempt. All final checks are rerun on the final sources. The source-and-evidence ZIP is also extracted to a fresh directory and rebuilt.

## Sources

[1] Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields (On Eisenstein's Jugendtraum), arXiv:2311.04110v2. Product definitions, smoothing and the fixed pure-cubic example. https://arxiv.org/html/2311.04110v2

[2] Retained preceding proof, Doubling norm descent: a rational elliptic normal form and its translation obstruction, copied under prior/. Supplies the exact theta distribution identity and the inherited analytic cubic approximant. Its SHA256 is in the manifest.

[3] Lean language reference, Elaboration and Compilation. https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/

The elementary group-product manipulations and divisor arguments are proved explicitly above; no literature novelty claim is made.
