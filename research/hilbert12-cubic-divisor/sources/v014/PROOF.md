# Cubic divisor growth and a canonical principal-correction section

**Komorebi H12 continuation, v0.14.0. Base: Principal Divisor Transport v0.13.0.**

## Status and scope

The exact gamma/class-field equality remains unproved. This block proves that
both zeros and poles of the actual principal-seven correction have cubic
counting growth. In particular, no finite quotient of fixed-period Riemann
theta functions restricted to affine complex lines can match its global divisor.

An explicit genus-three canonical product does match the entire divisor.
The actual correction divided by that product is the exponential of a cubic
polynomial, times the known zero anchor. An exact reflection identity fixes the
quadratic coefficient using theta data. The period-one transition fixes the
cubic coefficient using theta data and an absolutely convergent divisor sum.
Together these give a branch-free, gamma-free formula for the cube of the
principal correction at 1/3. They are not an independent class-field evaluation.

Eleven new universal integer theorems and their fourteen unchanged inherited
coefficient dependencies are freshly compiled in Lean and axiom-audited.
The complex counting, canonical-product, reflection and reconstruction theorems
have ordinary proofs here, not Lean-formalized complex analysis. No historical
novelty, new arithmetic equality, or new interval certificate is asserted.

## 1. Fixed input

Use the retained embedding and conventions:

    omega=exp(2*pi*i/3), beta=7^(1/3)*omega^2,
    epsilon=2-beta, rho=epsilon^(-1),
    tau=(beta^2+2*beta)/15, t=-tau, s=-(beta+2)/15,
    delta=(tau+2*s+4)/7,
    F(z)=Gamma_ell(z;tau,s)^5/Gamma_ell(5*z;5*tau,5*s),
    q_t(z)=theta0(z;t)^5/theta0(5*z;5*t),
    R(z)=product_(k=0)^6 F(z+k*delta)/F(beta*z).

The primary gamma product and negative-period continuation are [1]. The
unchanged predecessor proves:

    F(z+1)=F(z), F(z+tau)/F(z)=q_s(z),
    F(z+s)/F(z)=1/q_t(z), q_s(z)=q_t(rho*z),
    F(0)=epsilon^2,
    R(z+1)/R(z)=K(z):=product_(r=1)^15 q_t(beta*z-r*s)^(-1),
    R0:=R(0)=product_(j=0)^2 q_t((t+delta)/2+j*delta)^(-1).

All these identities are meromorphic; zeros/poles are interpreted by
continuation rather than illegal pointwise division. R is regular and nonzero
at 0, 1, and 1/3. At 1 this follows from K(0), whose factors are nonzero. At
1/3 the divisor-lattice condition fails: beta/3=-5s-2/3 does not have a
rational coordinate in (1/5)Z. Independence of 1,t,s justifies these assertions.

For integer a,b,c let

    lambda(a,b,c)=(a*tau+b*s+c/5)/beta,
    j=ceil((3*c-2*b)/7), H(n)=1 if n>0 and 0 otherwise,
    w(c)=4 if 5|c and -1 otherwise.

The predecessor's complete divisor is

    m(lambda)=w(c)[H(j)-H(2*j-a)-H(a)+H(b)].                (1)

There are no other zeros or poles. The map from integer triples to lambda is
injective. The coefficient m is in {-4,-1,0,1,4}; the support below means only
points with m!=0, not the full nondiscrete lattice. The support is locally finite.

## 2. Cubically many explicit zeros and poles

Let n>=1 and 1<=i,j0,k<=n. Use j0 here for a free index, not the ceiling pivot.
Define

    Z_(i,j0,k)=lambda(-i,j0,5*(n+k)),
    P_(i,j0,k,r)=lambda(-i,j0,5*(n+k)-r), 1<=r<=4.

For every one of these triples, a<0, b>0, and 3c>2b. Hence the ceiling pivot
is positive, 2*j-a>0, and the bracket in (1) is exactly one. Therefore

    ord_Z R=4,
    ord_P R=-1.                                           (2)

There are exactly n^3 distinct Z points and 4n^3 distinct P points. Injectivity
within the pole family follows from 5(k-k')=r-r' with |r-r'|<=3. The two
families are disjoint modulo five in the c-coordinate.

Every point has

    |lambda| <= K0*n,
    K0=(|tau|+|s|+2)/|beta|.                               (3)

Indeed |a|,b<=n and 0<c<=10n. Thus the zero and pole counts, with multiplicity,
satisfy

    n_+(K0*n)>=4n^3,  n_-(K0*n)>=4n^3.                     (4)

These are universal statements. Lean proves their integer sign, weight,
injection, disjointness and box-coordinate ingredients. The complex embedding,
cardinality application and triangle inequality are ordinary arguments here.

### Upper bound and exact growth exponent

The base divisor of F is supported at a*tau+b*s+c/5 with H(a)!=H(b). Since
Im(t),Im(s)>0, those two signs ensure that

    |Im(a*tau+b*s)|=|a|Im(t)+|b|Im(s).

Inside a disk of radius r, this bounds |a| and |b| by O(r). The real part then
bounds |c| by O(r). There are O((1+r)^3) possible triples and multiplicities
are bounded by four. A finite union of affine translates and the beta-scaled
denominator gives the same upper bound for R.

Combining with (4), for all sufficiently large r,

    n_+(r) is bounded above and below by positive constants times r^3,
    n_-(r) is bounded above and below by positive constants times r^3. (5)

In particular the unsigned divisor count n_D=n_++n_- is Theta(r^3).
There is no claim that the signed sum n_+-n_- has cubic size; smoothing can
cancel signed mass. The obstruction uses the zeros and poles separately.

## 3. A precise exclusion of finite theta sections

Consider a nonzero function formed as a finite quotient of fixed-period
Riemann theta functions theta(A_l*z+b_l | Omega_l), with Im(Omega_l)>0, each
restricted factor not identically zero. Allow fixed integer powers, finite
sums/products, polynomial factors, and a nowhere-zero entire prefactor.
The matrices Omega_l and affine arguments are fixed, not varying with z.

The defining theta series, or completing the square in its Gaussian bound,
gives for each affine restriction

    |theta(A_l*z+b_l | Omega_l)| <= C exp(C'|z|^2).          (6)

See [2] for the definition and bounded Gaussian-scaled form. Finite derivatives
also satisfy an order-two bound by Cauchy estimates. A finite rational expression
can be written as a quotient of two nonzero entire functions with such a bound.
Jensen's formula [3] bounds the zero count of each by O(r^2). A nowhere-zero
entire factor changes no finite divisor.

Consequently every function in this specified class has at most quadratically
many zeros and poles. By (5),

    R cannot be represented in this class.                (7)

This holds for theta functions of any fixed finite dimension along an AFFINE
one-dimensional argument. It does not rule out an infinite product, nonlinear
pullback, a varying period matrix, a higher-gerbe construction with nontrivial
transition data, or a special-value equality at z=1/3. In particular it is not
a proof that the earlier compact projective model is useless; it says that a
finite ordinary theta-section pullback along such a line cannot supply this
specific scalar divisor.

## 4. A canonical product matching all singularities

Let D be the locally finite support in (1), excluding zero, with multiplicity m_l.
Define

    E3(w)=(1-w) exp(w+w^2/2+w^3/3),
    W_D(z)=product_(l in D) E3(z/l)^(m_l).                  (8)

Negative exponents are interpreted by taking a quotient of the separate zero
and pole products. The cubic upper bound implies

    sum_(l in D) |m_l|/|l|^4 < infinity.

For |w|<1,

    log E3(w)=-sum_(k>=4) w^k/k.

Thus the two products converge normally on compact sets away from their stated
poles. This is the usual Weierstrass M-test construction [4], with the exponent
and support specified explicitly here. We obtain

    div(W_D)=div(R), W_D(0)=1,
    (log W_D)^(j)(0)=0 for j=1,2,3.                        (9)

No gamma value or arithmetic candidate is used to choose this regularizer.
It uses only the fixed algebraic periods and the explicit integer multiplicities.
It is nevertheless a transcendental infinite product, not an algebraic section.

### Minimal ungrouped absolute genus

Both counts in (5) imply divergence of sum |m_l|/|l|^3. Thus the analogous
ungrouped E2 product is not absolutely convergent at any fixed nonzero argument.
Genus three is sufficient and minimal for this UNGROUPED ABSOLUTE construction.
Special orderings or groupings exploiting signed cancellation are not excluded.

### Explicit tail form

If n_D(r)<=A r^3 for r>=R0, then for T>=R0 and |z|<=T/2,

    sum_(|l|>T) |m_l|/|l|^4 <= 4A/T,
    |log(tail of W_D at z)| <= 2A |z|^4/T.                 (10)

The first bound follows by partial summation, and the second from
|log E3(w)|<=|w|^4/[4(1-|w|)]. These are analytic error bounds, not numerical
claims from truncating an unbounded integer search.

## 5. The remaining factor is a cubic exponential, not an arbitrary entire function

Away from the divisor, direct differentiation of the gamma product gives

    (log R)''''(z)=-6 sum_(l in D) m_l/(z-l)^4.             (11)

Here (log R)'''' means the third derivative of R'/R; it is single-valued.
To justify (11), use

    (log(1-exp(2*pi*i*w)))''''=-6 sum_(n in Z) 1/(w-n)^4.

This follows from the sine partial fractions (the exponential factor in the
sine identity has zero fourth logarithmic derivative). Apply it to each factor
in the defining double gamma products. The selected three-index cone supports
have O(r^3) counting, so the fourth-power sum is locally absolutely convergent.
This justifies rearrangement, scaling by beta, and cancellation of multiplicities.
No conditionally convergent third-power sum is used.

The same fourth logarithmic derivative is obtained from (8), since

    (log E3(z/l))''''=-6/(z-l)^4.

By (9), R/W_D is a nowhere-zero entire function. It has a global entire logarithm
on C, whose fourth derivative is zero. Its value at zero fixes the scalar:

    R(z)=R0 exp(alpha1*z+alpha2*z^2+alpha3*z^3) W_D(z).    (12)

The alpha_j are the branch-independent logarithmic jets (log R)^(j)(0)/j!.
This argument proves (12) for the actual gamma correction without assuming an
unproved finite-growth property for R/W_D. Divisor matching ALONE would only
produce exp(h(z)) for an arbitrary entire h; the exact fourth-derivative identity
is the additional input restricting h to a polynomial.

## 6. Exact reflection evaluates the quadratic coefficient in theta data

The gamma product and continuation give

    F(z)F(-z)=q_t(z)/q_s(z).

Also 7*delta=tau+2*s+4 and

    F(w+7*delta)/F(w)=q_s(w)/[q_t(w)q_t(w+s)].

Pair the factors with labels k and 7-k in P7(z)P7(-z). For each 1<=k<=6,

    F(z+k*delta) F(-z+(7-k)*delta)=1/q_t(z+k*delta-s).

The k=0 factor retains q_t(z)/q_s(z). Dividing by the denominator reflection
proves the exact identity

    R(z)R(-z)=T(z),
    T(z)=q_t(z)q_s(beta*z)/[q_s(z)q_t(beta*z)]
         *product_(k=1)^6 q_t(z+k*delta-s)^(-1).            (13)

All apparent singularities at zero are removable. T(0)=R0^2, in agreement with
the inherited three-theta zero anchor.

Set

    L_t(z)=(q_t'(z)/q_t(z))',
    S_t=wp_t(1/5)+wp_t(2/5),
    u_j=(t+delta)/2+j*delta, j=0,1,2.

The previous exact theta normalization gives

    L_t(z)=-4/z^2+2S_t+O(z^2),
    S_s=rho^2 S_t.

Taking the second logarithmic derivative of (13) at zero, and pairing its six
translated theta terms, gives

    alpha2 = (1/2)[(1-beta^2)(1-rho^2) S_t
                  -sum_(j=0)^2 L_t(u_j)].                 (14)

The factor 1/2 in (14) includes the fact that (log T)''(0)=4alpha2.
The numerical checker independently tests (13) from gamma products and
(14) against a symmetric small-argument diagnostic; the formula itself has
the analytic derivation above.

## 7. Period one evaluates the cubic coefficient; the special cube has no branch choice

The already normalized transition is

    K(z)=R(z+1)/R(z)=product_(r=1)^15 q_t(beta*z-r*s)^(-1).

Define the absolutely convergent divisor expression

    B_D(1)=(log W_D)''(1)
      =sum_(l in D) m_l[-1/(l-1)^2+1/l^2+2/l^3].          (15)

The summand is O(|l|^(-4)). The point 1 is outside the divisor, so no exceptional
term occurs. Differentiate log K twice in (12):

    (log K)''(0)=6alpha3+B_D(1).

Since L_t is even,

    alpha3=-(1/6)[beta^2 sum_(r=1)^15 L_t(r*s)+B_D(1)].     (16)

Finally,

    exp(alpha1)=K(0) exp(-alpha2-alpha3)/W_D(1).

This determines exp(alpha1), not an unjustified principal logarithm of it.
At z=1/3 the cube eliminates the remaining logarithm-lift choice, giving

    R(1/3)^3 = R0^3 K(0) [W_D(1/3)^3/W_D(1)]
               *exp(-2alpha2/3-8alpha3/9).                (17)

Everything on the right of (17) is specified by theta values/derivatives,
algebraic period data, and absolutely convergent genus-three divisor products
or sums. No gamma value, no arbitrary scalar, and no new root choice appears.
No arithmetic candidate is used to set its normalization.

Equation (17) is an independent analytic representation, not a class-field
evaluation. It cannot be invoked as proof of U_Gamma=U_alg. Establishing an
arithmetic interpretation of the displayed regularized product is still an
unresolved comparison.

## 8. Conjugation regularity is now explicitly repairable on C

For f define f#(z)=conjugate(f(conjugate(z))). The product W_D# has the conjugate
divisor. Hence

    [R/R#]/[W_D/W_D#]
      =(R0/conjugate(R0))
       *exp(sum_(j=1)^3 (alpha_j-conjugate(alpha_j))*z^j).  (18)

The right side is entire and nowhere zero and has modulus one on the real axis.
Thus a canonical meromorphic factor cancels ALL the unmatched divisor in the
naive conjugation quotient. It is not a holomorphic-unit gauge and not a finite
theta section. Its three remaining phase coefficients are visible in (18).

Regularity on C is not the periodic nonzero multiplier on T^3 required by the
principal-norm rigidity theorem. Neither periodic descent nor the identification
of a based multiplier with U_Gamma/U_alg follows from (18). Those are retained
as separate obligations.

## 9. Effect on the research target

Closed: an explicit regularizer for the full scalar divisor exists in the
correct rank-three product category; the arbitrary entire correction is reduced
to a cubic polynomial; the relevant quadratic/cubic normalization and the cube
at 1/3 have explicit gamma-free expressions.

Ruled out: a finite fixed-period theta formula along an affine line matching
this whole divisor, even in higher fixed theta dimension or after multiplication
by a nowhere-zero entire factor.

Open: the independently normalized arithmetic model has not been identified
with this regularized section. In particular no exact reality of

    C_pol*U_Gamma^3, C_pol=epsilon*a1*a2^3/omega,

is proved. The original scalar comparison and the required periodic
principal-norm relation remain open. The new formula may be compared at the
special point without falsely requiring a finite global elliptic isogeny or
finite ordinary theta section.

## 10. Verification and dependencies

Lean: H12CubicDivisorGrowth contains 11 new universal integer theorems.
H12PrincipalDivisor's 14 predecessor theorems are copied unchanged and freshly
recompiled as dependencies. All 25 have their transitive axioms audited; only
propext, Classical.choice and Quot.sound are allowed where present. Warnings
are errors, with one worker. A false integer equality must be rejected.
No admitted proofs, custom axioms, native_decide or unsafe declarations occur.

Not formalized: gamma divisors as analytic orders, cardinality-to-complex-radius
counting, Jensen/theta growth, canonical convergence, the fourth-derivative
identity, reflection, and the special cube formula. These are ordinary proofs
above; their analytic hypotheses are not hidden as project axioms.

Exact checks: 20 named assertions and five negative controls. The independent
Fraction-lattice check covers all 2197 triples in [-6,6]^3 and all seven possible
lifts. The family check covers 92480 points for n=1,...,16. Symbolic checks
include all three removed canonical jets, the fourth derivative, reflection
pairing and exact reconstruction exponents. Infinite claims have the separate
proofs above and, where listed, universal Lean statements.

Numerics: at 40 and 70 requested digits, with 25 working guard digits, four
reflection/anchor identities, one quadratic-jet asymptotic diagnostic, and three
negative controls are checked. No U_alg is evaluated, and no canonical product
truncation is advertised as an exact infinite evaluation. These are floating
regressions, not directed-rounding interval certificates.

The runtime archive hash is the retained pinned
66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34.
Only the compiler and bundled libraries are used. The complete inherited Lean
archive is preserved but not replayed. Logs, hashes, versions and failed drafts
are in evidence/ and MANIFEST.json.

## Sources and notation translation

[1] Bergeron--Charollois--Garcia, Elliptic units for complex cubic fields,
arXiv:2311.04110v2. Equations (1.1), negative-period continuation, and section 5.3
on Eisenstein triple products. https://arxiv.org/html/2311.04110v2
The source supplies classical product conventions, not the unproved arithmetic
special-value equality. The regularized-product mechanism is adjacent to that
section; no novelty claim is made for the general idea.

[2] NIST DLMF 21.2.1--21.2.2: Riemann theta series and bounded Gaussian-scaled
form. https://dlmf.nist.gov/21.2 . Completing its square on a fixed affine line
proves (6), in every finite dimension.

[3] Terence Tao, 246B Notes 1: Zeroes, poles, and factorisation of meromorphic
functions, 23 December 2020, Theorem 2 and Proposition 8 (Jensen's formula and
zero counting). https://terrytao.wordpress.com/2020/12/23/246b-notes-1-zeroes-poles-and-factorisation-of-meromorphic-functions/
Only this standard analytic implication is used, not a gamma theorem.

[4] NIST DLMF 1.10(ix)--(x): normal convergence of products and logarithmic
derivatives. https://dlmf.nist.gov/1.10 . The explicit genus-three summability
and tail estimates here prove the hypotheses for the present divisor.

[5] Retained v0.13 proof and full source/evidence archive, preserved in prior/.
It supplies the complete divisor, exact period-one transition and zero anchor.
Source and archive hashes are in evidence/predecessor.json.

These sources were checked through primary HTML pages. No external PDF, image,
or private document was uploaded to a third party. The new proofs received a
self-review, not an independent human or second-agent audit.
