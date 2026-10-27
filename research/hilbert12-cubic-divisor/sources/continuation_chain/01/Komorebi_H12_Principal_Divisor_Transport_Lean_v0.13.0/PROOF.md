# The actual principal correction: complete divisor, theta transport, and zero normalization

**Komorebi H12 continuation, v0.13.0. Base: Principal Seven Norm v0.12.0.**

## Status and exact target

The original identity U_Gamma=U_alg remains UNPROVED. In particular, this block
constructs neither the relative scalar on the real three-torus nor the
principal-norm coboundary required by v0.12's smooth rigidity theorem.

This block determines the actual meromorphic principal correction much more
precisely: its complete divisor is an explicit integer ceiling/sign formula;
its translation factors are finite theta products; and its removable value at
zero is an exactly normalized product of three theta values. A conjugation-only
shortcut fails at the divisor level: an order-four zero at tau survives in
R7(z)/conjugate(R7(conjugate(z))). Constant matrix/phase data cannot cancel it.

Twenty new Std-only Lean theorem constants are freshly compiled and audited.
They prove the universal integer divisor coefficients, unique seventh-residue
lift, smoothing weight and translation carries. The analytic interpretation,
zero-anchor theorem and conjugate-field argument have ordinary proofs below,
not hidden Lean axioms. No historical novelty, interval certificate, or fresh
replay of the inherited source inventory is claimed.

## 1. Definitions and inherited inputs

Fix omega=exp(2 pi i/3), beta=7^(1/3) omega^2, and

    epsilon=2-beta, rho=epsilon^(-1),
    tau=(beta^2+2beta)/15, t=-tau, s=-(beta+2)/15,
    d=(tau+2s+4)/7.

The numbers 1,t,s are Q-linearly independent; t,s,d have positive imaginary
parts. Set

    S5(z;a,b)=Gamma_ell(z;a,b)^5/Gamma_ell(5z;5a,5b),
    F(z)=1/S5(z+t;t,s),
    qt(z)=theta0(z;t)^5/theta0(5z;5t),
    qs(z)=theta0(z;s)^5/theta0(5z;5s).

The primary product convention [1] and retained proofs supply

    F(z+1)=F(z),
    F(z+tau)/F(z)=qs(z),
    F(z+s)/F(z)=1/qt(z),
    qs(z)=qt(rho z),
    F(0)=epsilon^2=H(s)/H(t), H(v)=eta(5v)/eta(v)^5.

Both qt and qs are even elliptic functions in their respective periods.
Their canonical rational form is inherited from v0.3:

    qt(z)=(a-b)^2/[(wp_t(z)-a)(wp_t(z)-b)],
    a=wp_t(1/5), b=wp_t(2/5).

All identities are identities of meromorphic functions. Nonzero-denominator
conditions are imposed for pointwise evaluations. No arithmetic candidate
appears in the new exact or numerical checker.

The retained actual principal norm is

    P7(z)=product_(k=0)^6 F(z+kd)
         =S5(z;s,d)/[S5(z;t,d) S5(z+s;t,d)].                 (1)

Define its correction by

    R7(z)=P7(z)/F(beta z).                                  (2)

The exact period identities used below are

    beta tau=2tau+4s+1, beta s=-tau, beta=-15s-2,
    beta d=-8s-1, 7d=tau+2s+4.                             (3)

The v0.12 proof of (1) and its explicit scalar obstruction are preserved
byte-for-byte in prior/v012_source_and_evidence.zip. We do not infer (1) from
new numerical agreement.

## 2. The base gamma divisor is an integral half-space difference

Let

    Lambda5=Z tau+Z s+(1/5)Z.

Every point in this lattice has a unique expression

    z=a tau+b s+c/5,   a,b,c in Z.

Define

    H(n)=1 if n>0, and 0 otherwise,
    w(c)=4 if 5 divides c, and -1 otherwise.

### Theorem 2.1

The divisor of F is supported on Lambda5, and

    ord_(a tau+b s+c/5) F = w(c)[H(a)-H(b)].                (4)

**Proof.** For positive periods t,s the defining gamma product has a simple
zero at jt+ks+integer when j,k>=1, a simple pole when j,k<=0, and no divisor
there in the mixed cones. Independence of 1,t,s prevents collisions.

The argument z+t has coefficients (1-a,b) in the (t,s) basis. Its positive-
period gamma order is H(b)-H(a). In

    F(z)=Gamma(5(z+t);5t,5s)/Gamma(z+t;t,s)^5,

the numerator contributes this order for every integer c; the denominator
contributes five times this order only if c is divisible by five. This gives
(4). Every possible zero/pole of these defining factors lies in Lambda5. QED.

The lattice itself is not discrete in C, but the selected nonzero divisor
coefficients form a locally finite set, as follows also from the meromorphic
product. Formula (4) does not declare every point of Lambda5 singular.

## 3. Complete divisor of the actual principal correction

Multiplication by beta on Lambda5, in the ordered basis (tau,s,1/5), is

    N5=[2,-1,0; 4,0,-3; 5,0,-2],
    N5^3=7I, det N5=7,
    N5^(-1)=(1/7)[0,-2,3; -7,-4,6; 0,-5,4].              (5)

Its kernel generator on the quotient is (1,2,20)/7, namely d. Thus

    beta^(-1)Lambda5=Lambda5+Z d.

Every potential divisor point of R7 is uniquely parametrized by

    z_(a,b,c)=(a tau+b s+c/5)/beta.                         (6)

Write

    j=ceil((3c-2b)/7)=-floor((2b-3c)/7),
    k=7j+2b-3c, so 0<=k<7.                                (7)

Exactly ONE numerator argument z_(a,b,c)+kd lies in Lambda5. Its integral
coordinates are

    (a_hat,b_hat,c_hat)=(j,2j-a,20j+5b-8c).                (8)

Indeed

    N5(a_hat,b_hat,c_hat)^T=(a,b-8k,c-5k)^T,

which is beta(z+kd)=beta z+k(-8s-1). The other six residue choices fail
integrality. Moreover

    c_hat-2c=5(4j+b-2c),

so w(c_hat)=w(c). In particular fifth smoothing is transported exactly, not
replaced by a heuristic weight.

### Theorem 3.1 (global ceiling formula)

R7 has no zeros or poles outside beta^(-1)Lambda5, and at (6),

    ord R7 = w(c)[H(j)-H(2j-a)-H(a)+H(b)].                 (9)

**Proof.** Apply (4) to the unique integral lift (8), subtract the denominator
order at beta z, and use equality of the weights. QED.

The bracket in (9) belongs to {-1,0,1}. For example, if a<=0 and j>0, then
2j-a>0 and the bracket equals H(b); if a>0 and j<=0, it equals H(b)-1.
In the two remaining cases it is a difference of two zero-one values.
Therefore

    ord R7 belongs to {-4,-1,0,1,4}.                       (10)

Both (9)'s integer coefficient identity and this universal bound are compiled
in Lean. The analytic divisor interpretation is the ordinary proof above.

Three entire rays are particularly informative:

    ord_(n tau) R7=4,             n>=1,
    ord_(n s) R7=-4,              n in Z, n!=0,
    ord_(-n) R7=4,                n>=1.                     (11)

For instance z=n tau has (a,b,c)=(2n,4n,5n), j=n, k=0. The other cases use
(a,b,c)=(-n,0,0) and (0,15n,10n). At zero the order is zero.

These ray assertions are universally Lean-checked as integer identities, not
inferred from the finite Python ray range.

## 4. Exact theta transition laws for R7

### Theorem 4.1

As meromorphic identities,

    R7(z+1)/R7(z)
      = 1/product_(r=1)^15 qt(beta z-rs),                  (12)

    R7(z+s)/R7(z)
      = qs(beta z-tau)/product_(k=0)^6 qt(z+kd),           (13)

    R7(z+tau)/R7(z)
      = [product_(k=0)^6 qs(z+kd)]
        [product_(r=0)^3 qt(beta z+rs)]
        /[qs(beta z) qs(beta z+tau)],                      (14)

    R7(z+d)/R7(z)
      = qs(z)/[qt(z) qt(z+s)
                  product_(r=1)^8 qt(beta z-rs)].          (15)

**Proof.** In (12), the numerator P7 is period one and beta=-15s-2. The
negative s-shift equation gives precisely the fifteen factors. In (13), shift
each numerator by s and use beta s=-tau in the denominator. In (14), shift
each numerator by tau; in the denominator beta tau=2tau+4s+1 gives two qs
factors and four reciprocal qt factors. The shift by 2tau in qt can be removed
because tau=-t is its elliptic period. Finally, P7(z+d)/P7(z)=F(z+7d)/F(z).
Equation 7d=tau+2s+4 and beta d=-8s-1 give (15). QED.

The opposite order of a zero/pole on the two sides of a displayed quotient
is handled by meromorphic continuation; it is not an exception to the identity.

### Exact consistency with the divisor formula

Under z->z+1, the integer coordinates in (6) change to

    (a,b,c)->(a,b-15,c-10).

The pivot j and weight are unchanged. Consequently (9) gives

    ord_(z+1)R7-ord_z R7
       =-w(c) 1_(1<=b<=15),                               (16)

exactly the divisor of the right side of (12). This identity is compiled in
Lean for all integer a,b,c.

Under z->z+d, the coordinates change to (a,b-8,c-5). The unique digit decreases
by one modulo seven; its pivot increases by one exactly when the old digit is
zero. These full carry formulas are also compiled, including negative b,c.

All theta factors in (12)-(15) have the inherited discriminant/rational
normalization. Their scalar constants are not discarded.

## 5. The zero anchor contains only three theta values

### Theorem 5.1

R7 is regular and nonzero at zero, and

    R7(0)=product_(j=0)^2 qt((t+d)/2+jd)^(-1).              (17)

**Proof.** Put H(a)=eta(5a)/eta(a)^5. Direct cancellation in the positive-period
gamma product gives, as z->0,

    S5(z;a,b) ~ [5/(2pi)^4] H(a)H(b) z^(-4).

Thus (1) gives

    P7(0)=[H(s)/H(t)]/S5(s;t,d).

Since F(0)=H(s)/H(t), its normalization cancels in R7, yielding

    R7(0)=1/S5(s;t,d).

The arithmetic period relation says

    s=(t+d)/2+3d-2.

The defining gamma product has exact central value

    S5((t+d)/2;t,d)=1,

because the two numerator/denominator factors coincide term by term, in both
the original and fifth-scale products. Three positive d-shifts give

    S5(s;t,d)=product_(j=0)^2 qt((t+d)/2+jd).

This proves (17) with no branch or root-of-unity choice. The three arguments
have s-coefficients 1/7,3/7,5/7 relative to (1,t,s), so they avoid the divisor
of qt. The value is therefore nonzero. QED.

For orientation, its numerical value is approximately

    2.54967020448463030709320798336e-10
      +6.28511666980532003631514434278e-10 i.

This decimal is a regression value, not the normalization proof.

### Uniqueness of this correction from its transported data

A nonzero meromorphic function on C having the same transitions (12), (13),
(15) and the same value (17) is R7. Indeed their ratio has periods 1,s,d.
These are Q-linearly independent, so the generated rank-three subgroup of C is
nondiscrete. A meromorphic function with arbitrarily small nonzero periods is
constant: at a regular point its derivative vanishes by difference quotients.
The zero value of the ratio is one, proving uniqueness.

This characterizes the analytic correction; it is not an arithmetic evaluation
of R7(1/3). A proposed model satisfying those full hypotheses has not been
constructed.

## 6. Conjugation alone leaves an uncancelled meromorphic divisor

Define the actual conjugate function

    R7#(z)=conjugate(R7(conjugate(z))).

Let K=Q(beta), Kbar=Q(conjugate(beta)). These two cubic subfields are distinct:
if equal, beta/conjugate(beta)=omega would lie in a cubic field, impossible
because [Q(omega):Q]=2. Their intersection is Q because their degree is prime.

The divisor of R7 is supported in K, by (6), and that of R7# is supported in
Kbar. Also tau is not rational. For example beta=2-1/(4+15tau), and beta has
degree three. Hence tau does not belong to Kbar.

By (11), R7 has a zero of order four at tau, whereas R7# is regular and nonzero
there. Thus

    ord_tau (R7/R7#)=4.                                    (18)

The same holds at every n tau, n>=1; the poles at n s, n!=0, are also unmatched.

This proves that the naive conjugation-asymmetric correction is NOT a
nowhere-zero holomorphic function on C. Multiplying by a constant root of
unity, a constant algebraic polarization, or a holomorphic unit does not
change its orders. The conclusion does not refute a special-value reality
identity at 1/3, which is rational and lies in K intersect Kbar. It refutes
only a proposed global cancellation which omits meromorphic comparison data.

Likewise a finite flat model supplied solely by constant matrices and
holomorphic invertible gauges cannot match this scalar divisor. It must be
equipped with an appropriate meromorphic section, or the proof must use a
special-value comparison that does not require the missing global ratio.
The prior finite gerbe model does not specify that section.

## 7. What the new data require of a relative comparison

For a scalar model correction A7 defined on this same z-plane, the quotient
R7/A7 can be regular and nonzero only after their divisor orders match. Formula
(9) is now an explicit necessary test at every possible singular point.
The first cheap discriminator is

    ord_tau A7=4.

A constant model correction fails that test. Agreement at tau alone is of
course not sufficient; the complete signed formula must be matched at all
its support points. Once that is done, the ratio has no finite zeros or
poles. Periodicity/torus descent, growth and the relative principal-norm
coboundary are further obligations, not automatic consequences of divisor
matching on C.

The main target is still Im(C_pol U_Gamma^3)=0, or U_Gamma^3=U_alg^3 before
branch selection. The v0.12 smooth transfer theorem is not applied here,
because its genuine periodic nonzero relative multiplier and its norm
compatibility have not been supplied. What we have obtained is the exact
analytic section data which such a comparison must preserve: divisor,
transition multipliers and a gamma-free scalar anchor.

A construction matching all three may support the desired smooth-relative
route; a direct phase-regulator evaluation remains a separate alternative.
Neither construction has been completed in this release.

## 8. Formal and computational scope

New formal modules:

- H12PrincipalDivisor (14 theorems): smoothed principal lattice; unique digit and
  integral lift for every integer input; equality of smoothing weights; complete
  possible orders; exact divisor-coefficient difference; all three ray formulas.
- H12DivisorCarries (6 theorems): unit-period and seventh-period pivot/digit
  carries, finite window boundary, and agreement of divisor transitions.

All 20 are compiled with Lean 4.34.0-rc2, commit
6a10ac8c22beadecabdbb0919c2b50214762f91d, using bundled Std and warnings as errors.
Their transitive axiom dependencies are audited; only propext, Classical.choice
and Quot.sound are allowed. No project axiom, admitted proof, native_decide or
unsafe declaration occurs. A deliberately false integer equality is rejected.

The analytic gamma divisor theorem, continuation, theta transport, zero-anchor
limit, nondiscrete-period uniqueness and field-intersection interpretation are
ordinary proofs, not formalized analytic geometry or gamma definitions.
No formal theorem asserts an actual gamma/arithmetic equality.

The exact Python checker uses independent Fraction coordinates to enumerate
all 15,625 triples a,b,c in [-12,12]. It checks all seven potential numerator
lifts at each point, the unique correct digit, signs/weights, and both carry
laws. Universal scope is supplied by the proof and Lean, not the tested box.
It also checks the rays through 100 and symbolic period identities.

Numerical runs at 40 and 70 requested digits (25 guard digits) each verify
14 meromorphic/anchor identities, four divisor-order diagnostics at offset
1e-8, and four negative controls. The divisor diagnostics are finite
asymptotic checks at tolerance 1e-3, not analytic order proofs. Equality
regressions use relative tolerance 10^(-digits+8). All gamma series obey the
inherited 20,000-term cap with explicit logarithmic truncation bounds.
Floating-point rounding is not interval-enclosed. No U_alg is evaluated.

The numerical continuation uses the inherited exact covariance to evaluate
qt through the better-conditioned s chart; the zero anchor is also checked
with the independent original guarded gamma evaluator. These are two code
paths, not independent human reviews or analytic foundations.

The failed initial Lean draft and timed-out combined numerical draft are
retained. The latter was replaced by four synchronous stages and covariance-
conditioned theta evaluation; neither tolerance nor target was weakened.
The inherited archive is preserved with its exact hash; it is not freshly
recompiled. Fresh-extraction replay results are supplied in evidence/.

## References and provenance

[1] Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields*,
arXiv:2311.04110v2, 30 November 2023. Primary product (1.1), negative-period
continuation and theta difference laws. Checked through the versioned HTML:
https://arxiv.org/html/2311.04110v2 . The source conjectures the arithmetic
special-value comparison; it is not used as proof of that claim.

[2] Retained v0.12.0 source/evidence archive under prior/. Supplies the actual
seven-point identity, unit/principal conventions and the smooth rigidity
criterion with its explicit still-missing hypotheses.

[3] Retained v0.3-v0.5 normalization/analytic blocks, transitively preserved in
the predecessor: phase-free theta covariance and zero normalization F(0).
Those inherited dependencies are not re-audited end to end here.

All new formulas above are derived in the stated conventions. No literature
priority or universal Hilbert-12 theorem is asserted.
