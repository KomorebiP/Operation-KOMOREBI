# Signed unit transport, normalized return channels, and the remaining first-order phase

**H12 pure-cubic checkpoint. Version 0.2.0.**

## Status

This block constructs the exact signed transform of the full eight-point half-lattice gamma packet. It proves its one-step transport with all theta carries, gives an integral affine recurrence for every three-step return, and obtains four normalization-free rational elliptic product limits. Their guaranteed local cancellation orders are at least two, two, two, and three.

The computation also identifies an indispensable first-order normalization channel. Four high-order channels, the full norm, and vertex moduli do not by themselves fix the target phase: an explicit unit-permutation-invariant phase deformation preserves those data. The deformation is a counterexample to sufficiency of those snapshot constraints, NOT a new gamma function satisfying all functional equations or the normalized contracting limit.

There are **83 compiled and axiom-audited Lean theorem constants: 50 inherited and 33 new**. The analytic theta/gamma definitions, covariance, holomorphy, and asymptotics below are ordinary mathematical arguments with the indicated inherited inputs. They are not silently assumed as Lean axioms. This does not prove the gamma value algebraic, a power equality with the ray-field candidate, or a general Hilbert-12 result. No literature-priority claim is made.

## 1. Definitions and dependency boundary

Fix beta=7^(1/3) exp(-2*pi*i/3), and write

    epsilon=2-beta, rho=epsilon^(-1)=beta^2+2beta+4,
    tau=(beta^2+2beta)/15, t=-tau, s=-(beta+2)/15, z0=1/3.

Thus t and s have positive imaginary parts. Use the BCG elliptic-gamma product and its negative-first-period continuation [1]. Set

    F(z)=Gamma_ell(z;tau,s)^5/Gamma_ell(5z;5tau,5s),
    q_t(z)=theta0(z;t)^5/theta0(5z;5t),
    q_s(z)=theta0(z;s)^5/theta0(5z;5s),
    U=F(z0).

The retained notes prove the following inputs in these conventions:

    F(0)=epsilon^2;   F(z+1)=F(z);
    F(z+tau)/F(z)=q_s(z);  F(z+s)/F(z)=1/q_t(z);
    q_s(z)=q_t(rho*z);
    q_t is even and elliptic with lattice Z+Zt;
    F(1/3)F(2/3)=1;
    product_(a,b,c in {0,1}) F(z+(a+b*tau+c*s)/2)=F(2z).       (1.1)

The divisor of q_t is 4[0] minus the four nonzero rational fifths. The periods 1,t,s are Q-linearly independent. F is holomorphic and nonzero near zero, and |rho|<1. The last inequality follows from Norm(epsilon)=1 and 0<2-cuberoot(7)<1 at the real embedding.

The retained rational elliptic form is

    q_t(z)=c_t/Q5(wp_t(z)),
    Q5(X)=(X-wp_t(1/5))(X-wp_t(2/5)), c_t != 0.              (1.2)

This follows by comparing divisors and the leading coefficient at zero. Formula (1.2) is an identity in an analytically defined elliptic function field. It is not an assertion that these period-dependent coefficients are algebraic numbers.

Copies of the preceding norm-projector proof and scope are under prior/. The guarded analytic evaluator is copied unchanged there. The input archive SHA-256 and runtime restoration hash are recorded in the evidence.

## 2. Why the full eight-point packet is needed

Let V={0,1}^3, with v=(b,c,a) and index 4b+2c+a. Define

    w_v=z0+(b*tau+c*s+a)/2,
    T(b,c,a)=(a,b,c).

The familiar elliptic half-period plane in this notation has c=0. It is not invariant under T: T(1,0,0)=(0,1,0). We therefore retain the full rank-three half-grid instead of discarding the third-period component.

Multiplication by rho in the period basis (tau,s,1) is

    R = [8,-4,15; 1,0,0; 2,-1,4].

A direct calculation gives

    rho*w_v = w_(Tv)+A_v*tau+d_v,
    A_v=5+4b-2c+7a,
    d_v=1+b-c+2a.                                           (2.1)

Every A_v is between 3 and 16. Also

    rho*tau=8tau+s+2.

Hence covariance and t-periodicity imply

    q_s(w_v+j*tau)=q_t(w_(Tv)+j*s)                         (2.2)

for every integer j. In particular q_s(w_v)=q_t(w_(Tv)).

The sampled factors in this proof are nonzero. For q_t(w_v+j*s) to meet its divisor, the tau and s coefficients must be integers compatible with Q-linear independence. The bit coefficients then force b=c=0 and the relevant integer coefficient to vanish. The remaining rational argument is 1/3 or 5/6, neither a rational fifth modulo one. The same reasoning applies to T-transformed vertices and all integer j. The baseline F(w_v) lies in the nonvanishing product strip, and its integer lattice translates remain nonzero by the difference equations.

## 3. Signed channels and the exact one-step carry

For xi in V define the character

    chi_xi(v)=(-1)^(xi dot v).

For an arbitrary nonzero complex packet x=(x_v), define its multiplicative Walsh channel

    X_xi(x)=product_v x_v^(chi_xi(v)).                       (3.1)

Only integer exponents occur. No logarithmic branch is involved. Since

    chi_(Txi)(Tv)=chi_xi(v),

one has the exact permutation rule

    X_xi(x composed with T)=X_(Txi)(x).                     (3.2)

Now put x_v=F(w_v), y_v=F(rho*w_v), and

    B_v=product_(j=0)^(A_v-1) q_t(w_(T^2v)+j*s).            (3.3)

By (2.1), iterating the tau difference equation at w_(Tv), then using (2.2), proves

    y_v=x_(Tv)*B_v.                                        (3.4)

Therefore, with X_xi=X_xi(x), Y_xi=X_xi(y),

    Y_xi=X_(Txi)*mathcalB_xi,
    mathcalB_xi=product_v B_v^(chi_xi(v)).                  (3.5)

The same signed transform of q_s(w_v)=q_t(w_(Tv)) gives exact transport of the theta packet. These are statements about the actual analytic values, not merely a permutation of labels.

The character orbits are

    {000}, {111}, {001,100,010}, {011,101,110}.

Thus weight (the number of nonzero bits) is preserved, and the four channels of weight at least two form a closed subsystem of (3.5), with their explicitly given carries retained.

## 4. Which carries are free of the theta normalization constant?

Replace every q_t in (3.3) by its rational elliptic form (1.2). The exponent of c_t in mathcalB_xi is

    g_xi=sum_v chi_xi(v) A_v.

An affine function on the Boolean cube has Fourier support only in weights zero and one. For the actual carry A_v, the values are

| xi | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| g_xi | 76 | -28 | 8 | 0 | -16 | 0 | 0 | 0 |

This is both a direct eight-vertex calculation and an instance of the universal affine-spectrum theorem formalized in H12SignedGeometry.

**Consequently the four channels 011,101,110,111 have carries expressible entirely as rational products of Q5(wp_t(...)), with c_t cancelling exactly.**

The three first-order carries are not normalization-free. Their combined c_t exponent is -28+8-16=-36. Those factors must be retained. A cancellation of c_t is not an algebraicity proof and does not identify E_t with the separate equianharmonic CM curve.

## 5. Exact closed-label return after three unit steps

The third power of the actual inverse unit matrix is

    Q=R^3=[1033,-540,2070; 90,-47,180; 264,-138,529].       (5.1)

It is the identity modulo two. Thus three unit steps return every vertex label to itself. In rational coordinates the carry is

    rho^3*w_v=w_v+A_(1,v)*tau+B_(1,v)*s+d_(1,v),

    A_(1,v)=690+516b-270c+1035a,
    B_(1,v)= 60+ 45b- 24c+  90a,
    d_(1,v)=176+132b- 69c+ 264a.                            (5.2)

For n>=0, let c_(n,v)=(A_(n,v),B_(n,v),d_(n,v))^T satisfy

    c_(0,v)=0,
    c_(n+1,v)=Q*c_(n,v)+c_(1,v).                          (5.3)

Induction proves both

    rho^(3n)*w_v=w_v+A_(n,v)*tau+B_(n,v)*s+d_(n,v)          (5.4)

and integrality/affinity of every carry coordinate as a function of (b,c,a). The Lean theorem all_iterates_affine proves the latter for arbitrary natural n, not only a finite tested range. The analytic realization of (5.4) uses the inherited period-row eigenidentity.

Define an oriented product for integer N:

    Pi(N;z)= product_(j=0)^(N-1) q_t(z+j*s),                N>0;
              1,                                         N=0;
              [product_(j=N)^(-1) q_t(z+j*s)]^(-1),        N<0.

This avoids requiring any unproved positivity assertion about all return lengths. Using first the tau shifts and then the s shifts in (5.4), one obtains

    J_(n,v)=Pi(A_(n,v);w_(Tv))/Pi(B_(n,v);w_v)
           =F(rho^(3n)*w_v)/F(w_v).                       (5.5)

For a nontrivial character define

    mathcalJ_(n,xi)=product_v J_(n,v)^(chi_xi(v)).           (5.6)

Because F(rho^(3n)*w_v) tends to the same nonzero F(0), and the character sums to zero,

    lim_n mathcalJ_(n,xi)=X_xi^(-1).                      (5.7)

If weight(xi)>=2, the c_t exponent in (5.6) vanishes for every n: it is the signed sum of the affine function A_(n,v)-B_(n,v). Thus (5.5)-(5.7) supply four exactly normalized rational elliptic product limits.

For n=1 the Walsh spectrum of A-B is

    (9720,-3780,984,0,-1884,0,0,0).

These formulas identify the limits analytically. They do NOT independently evaluate the limits in the ray field.

## 6. Cancellation order of each signed return

Here is a uniform moment theorem, which also explains why weight is useful.

Let w_v=u+b*d_b+c*d_c+a*d_a be an affine cube in any characteristic-zero coefficient ring, and let xi have weight d>0. Then

    sum_v chi_xi(v) w_v^k=0,                              0<=k<d,

    sum_v chi_xi(v) w_v^d
      =(-1)^d d! 2^(3-d) product_(xi_i=1) d_i.             (6.1)

**Proof.** Expand w_v^k. If k<d, every monomial misses at least one of the d selected bit variables; summation over that bit cancels it. At degree d, the only surviving terms contain every selected bit once and none of the unselected variables. Their multinomial coefficient is d!, the selected signed bit sums are each -1, and each unselected bit contributes 2. This proves (6.1).

For our packet d_b=tau/2, d_c=s/2, d_a=1/2. Write the normalized local logarithm

    log(F(z)/F(0))=sum_(k>=1) c_k z^k

near zero. Then for nontrivial xi,

    G_xi(h)=product_v F(h*w_v)^(chi_xi(v))
           =1+O(h^d).                                    (6.2)

For xi=111 the leading logarithmic term is

    log G_111(h)=-6*d_b*d_c*d_a*c_3*h^3+O(h^4).            (6.3)

Combining (5.5) with h=rho^(3n),

    mathcalJ_(n,xi)=X_xi^(-1)
                   (1+O(|rho|^(3n*d))).                 (6.4)

Thus the three weight-two channels have order |rho|^(6n), and the top channel has order |rho|^(9n), as relative return errors. This follows from holomorphy and the moment identities, not from fitting numerical data. The numerical checker tests the leading cubic coefficient independently from the gamma series at its stated tolerance.

## 7. The indispensable first-order normalization mode

Define the three orbit aggregates

    P1=X_001 X_010 X_100,
    P2=X_011 X_101 X_110,
    P3=X_111.

Walsh reconstruction gives, for an arbitrary nonzero packet,

    X_000 P1 P2 P3=x_000^8.                               (7.1)

For the gamma packet, the full multiplication law (1.1) and conductor inversion give

    X_000=F(2/3)=U^(-1), x_000=U.

Hence

    U^9=P1 P2 P3.                                        (7.2)

This is a normalized packet identity, not a proof of any arithmetic power equality. It is an alternative comparison target and does not improve the exponent in the already available, still unevaluated cubic-return route.

### Exact insufficiency of high-order channels and the full norm

For any lambda!=0 define a second packet by

    x'_v=lambda^(3*weight(v)-4) x_v.                      (7.3)

Its signed factors satisfy

    X'_000=lambda^4 X_000,
    X'_xi=lambda^(-12)X_xi, weight(xi)=1,
    X'_xi=X_xi, weight(xi)>=2.                            (7.4)

Also x'_000=lambda^(-4)x_000. Therefore the constraint X_000=x_000^(-1) is preserved. The exponent in (7.3) is invariant under the unit permutation T. If |lambda|=1, all eight vertex moduli are preserved. Nevertheless the target phase changes unless lambda^4=1.

The first-order aggregate detects this deformation:

    P1'=lambda^(-36)P1,

whereas P2 and P3 are unchanged. Thus the high-order products and full norm cannot by themselves determine U.

This is a precise counterexample to sufficiency of the listed finite snapshot data. It does not preserve or claim to preserve all gamma identities, the independently computed carry values at every argument, or the common holomorphic limit at zero. Those additional analytic constraints matter. The new normalized return formulas retain them; an arithmetic comparison must do so too.

## 8. Where the arithmetic comparison remains

The earlier theorem gives D_m -> epsilon^6/U_Gamma^3. The missing independent evaluation D_m -> epsilon^6/U_alg^3 remains open.

For the new packet, an alternative sufficient theorem would independently evaluate P1,P2,P3 with product U_alg^9. Equation (7.2) would then imply U_Gamma^9=U_alg^9, after which a separately rigorous branch enclosure could select the intended value. This package supplies no such independent arithmetic evaluations and no membership assertion for the actual discrepancy in mu_9 or mu_3.

What has become explicit is the division of labor:

- the unit carries transport the actual signed channels, not just their labels;
- four channels cancel the elliptic normalization constant and have stronger local jet cancellation;
- the first-order aggregate retains a nonzero normalization gain and detects a remaining common phase mode;
- the exact trivial-channel conductor norm remains part of reconstruction.

Neither equality of coboundaries nor full norms alone fills the missing comparison. Rational elliptic product formulas are analytic objects until their arithmetic identification is proved.

## 9. Lean scope and verification

The pinned compiler is Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, with Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The restored seven-part offline archive matched SHA-256 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34.

The inherited six modules contain 50 theorems. New modules:

| Module | Theorems | Formal content |
|---|---:|---|
| H12SignedGeometry | 18 | Character transport, exact affine spectra, low-degree jet cancellations, Walsh reconstruction and affine phase gauge |
| H12SignedAlgebra | 11 | Signed products in an arbitrary commutative group, carried transport, eighth/ninth-power reconstruction, exact gauge effects |
| H12ThreeStepTransport | 4 | Actual inverse-unit cube, uniform rational half-grid carry, integral affine recurrence for every iterate |

All **83 theorem constants** compile in a clean isolated build and have their full axiom dependency lists inspected. Only propext, Classical.choice, and Quot.sound are admitted standard logical dependencies. No project axiom, admitted proof, native_decide, or unsafe declaration is allowed. An intentionally false integer equality must be rejected.

In the group formalization, multiplicative Walsh operations are derived through Lean's Additive type tag and exact commutative-group identities. This is not an analytic logarithm. The ninth-power theorem explicitly assumes the conductor norm identity. The analysis realizing these abstract theorems on F is in Sections 1-8, not hidden in the formal declarations.

The new exact Python checker passes 124 assertions, including all 64 character pairings, explicit symbolic moments, matrix/carry identities, and carry regressions for n=1,...,6. The arbitrary-n statement has a separate induction proof in Lean; bounded tests do not supply that quantifier.

At each of 40 and 70 requested decimal digits (25 guard digits), the numerical checker passes 44 equality checks, one cubic-leading-term asymptotic check, and three negative controls. Theta functions at t and s are evaluated from their respective products; gamma uses the retained guarded series and continuation. No U_alg appears in this numerical checker. These are floating-point regression checks, not interval certificates. See evidence/ for exact bounds, cutoffs, errors, commands, and failure history.

## References

[1] Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields (On Eisenstein's Jugendtraum)*, arXiv:2311.04110v2, 30 November 2023. Product definitions, negative-period continuation, and the pure-cubic example. https://arxiv.org/html/2311.04110v2

[2] Retained Norm Projector Lean v0.1.0 proof and scope, copied under prior/. Its own cited Doubling Norm Descent and Conductor Adapted Taps notes supply the inherited covariance, multiplication and return formulas.

[3] Lean language reference, Elaboration and Compilation. https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/

The new elementary finite-group, polynomial, and carry identities are proved explicitly above and/or in the Lean core. No priority claim is inferred from their verification.
