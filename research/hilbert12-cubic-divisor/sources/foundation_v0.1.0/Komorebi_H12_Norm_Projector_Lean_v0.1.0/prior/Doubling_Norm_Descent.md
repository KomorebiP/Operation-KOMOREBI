# Doubling norm descent: a rational elliptic normal form and its translation obstruction

**Checkpoint:** 2026-10-02.  
**Scope:** the fixed pure cubic example beta^3=7.  
**Results:** exact rational elliptic representation of every preceding cubic approximant; exact rank-two theta and rank-three gamma multiplication norms; an eight-point unit-stable half-grid with all carries; and a proof that no positive power of the new kernel is an elliptic translation coboundary.  
**Boundary:** no independent arithmetic evaluation of the limiting product is proved. In particular U_Gamma^3=U_alg^3 and U_Gamma=U_alg remain unproved. These results do not assert literature novelty or a general Hilbert-12 theorem.

## 1. Inherited conventions and inputs

Use the fixed complex embedding beta=7^(1/3) exp(-2 pi i/3), and put

    epsilon=2-beta,
    rho=epsilon^(-1)=beta^2+2 beta+4,
    tau=(beta^2+2 beta)/15,
    t=-tau,
    s=-(beta+2)/15,
    z0=1/3.

Here s is an analytic period, not a Galois automorphism. Both t and s have positive imaginary part; 1,t,s are Q-linearly independent. Let

    F(z)=Gamma_ell(z;-t,s)^5/Gamma_ell(5z;-5t,5s),
    U=F(z0),
    Theta(z)=theta0(z;t)^5/theta0(5z;5t).

The retained conductor-adapted tap note, reproduced under prior/, supplies

    F(0)=epsilon^2,
    F(2/3)=U^(-1),
    F(z)F(-z)=Theta(z)/Theta(rho z),
    Theta(z;s)=Theta(rho z;t),
    rho=4-15t,
    rho t=8t-s-2.

Theta is even and elliptic with lattice Lambda_t=Z+Zt. The logarithmic series is

    L(z)=-5 sum_(n>=1,5 not dividing n)
          [p^n exp(2 pi i n z)-q^n exp(-2 pi i n z)]
          /[n(1-p^n)(1-q^n)],
    p=exp(2 pi i t), q=exp(2 pi i s), F=exp L.

It converges on -Im(t)<Im(z)<Im(s). Difference laws supply continuation outside this strip. The working-checkpoint eta normalization and covariance are inherited, not claimed independently re-proved in this block. BCG's product/continuation conventions are the external analytic input [1].

The return sequence is

    a_0=0, a_1=5, a_2=60,
    a_(m+3)=12a_(m+2)-6a_(m+1)+a_m.

With z_m=rho^m/3, there are integers d_m such that

    z_m=z0-a_m t+a_(m-1)s+d_m.

The preceding block proves

    D_m = Theta(z_m)/Theta(rho z_m)
          * product_(j=a_(m-1))^(a_m-1) Psi(z0+j s),
    Psi(z)=Theta(z)^2/[Theta(2z)Theta(2z+s)],
    lim D_m=epsilon^6/U^3,
    D_m/(epsilon^6/U^3)=1+O(|rho|^(3m)).                   (1.1)

This block gives new exact normal forms for the quantities in (1.1).

## 2. Rational elliptic normal form

Write wp=wp_(Lambda_t). Define

    e_1=wp(1/5), e_2=wp(2/5),
    Q(X)=(X-e_1)(X-e_2).

These e_i denote the selected five-torsion x-coordinates, NOT the conventional half-period roots sometimes also called e_i. Let c_t be the coefficient of z^4 in Theta(z) at zero. It is nonzero; directly from the product,

    c_t=(2 pi)^4/(5 H_5(t)^2),
    H_5(t)=eta(5t)/eta(t)^5.

### Proposition 2.1

    Theta(z)=c_t/Q(wp(z)).                               (2.1)

**Proof.** Its divisor on E_t=C/Lambda_t is

    div(Theta)=4[0]-[1/5]-[-1/5]-[2/5]-[-2/5].

Indeed theta0 has simple zeros on its period lattice; its fifth power and the smoothed denominator give exactly those orders. The four pole points are distinct and none is two-torsion. The even function wp has a double pole at zero and identifies the points z and -z. Consequently 1/Q(wp(z)) has the same divisor. Their quotient is a holomorphic nowhere-zero function on the compact elliptic curve, hence constant. Since wp(z)=z^(-2)+O(z^2), its leading coefficient is one at z^4. Comparing gives c_t. QED. The classical wp properties used here are recorded in [2].

Substituting (2.1), every c_t cancels from Psi:

    Psi(z)=Q(wp(2z)) Q(wp(2z+s))/Q(wp(z))^2.              (2.2)

The endpoint is also independent of c_t:

    Theta(z_m)/Theta(rho z_m)
       =Q(wp(rho z_m))/Q(wp(z_m)).                       (2.3)

### Theorem 2.2: one two-sided rational elliptic orbit

Let

    x_n=wp(z0+n s), y_n=wp'(z0+n s), n in Z.

For b=a_(m-1), c=a_m, the exact preceding cubic approximant is

    D_m = Q(x_c)/Q(x_b)
          * product_(j=b)^(c-1)
             Q(x_(-2j)) Q(x_(-2j-1))/Q(x_j)^2.           (2.4)

**Proof.** The return relation implies wp(z_m)=x_b and wp(rho z_m)=x_c. Also 2z0=-z0 modulo Lambda_t. Evenness of wp then gives

    wp(2(z0+j s))=x_(-2j),
    wp(2(z0+j s)+s)=x_(-2j-1).

Use (2.2)-(2.3) in (1.1). QED.

All x_n and Q(x_n) in this formula are finite, and Q(x_n) is nonzero. Otherwise z0+n s would be zero or one of the selected fifths modulo Lambda_t. Q-linear independence of 1,t,s rules this out, including n=0.

### Exact rational recurrence

Put A=wp(s), B=wp'(s). From the classical addition theorem [3],

    lambda_n=(y_n-B)/(x_n-A),
    x_(n+1)=-x_n-A+lambda_n^2/4,
    y_(n+1)=-y_n+lambda_n (x_n-x_(n+1)).                 (2.5)

Backward iteration uses (A,-B). The points lie on

    y^2=4x^3-g2(t)x-g3(t).

The denominator x_n-A never vanishes: that would give z0+n s=+s or -s modulo Lambda_t, again impossible by independence.

Thus the finite product is rationally generated from the six analytic constants

    x_0, y_0, A, B, e_1, e_2,

with no further theta evaluations or eta factors required by its algebraic recurrence. This is rationality in the function-field sense. It does NOT assert these seed constants are algebraic numbers, and it does NOT identify E_t with the separate CM curve of period omega. The product length still grows with the return window; no logarithmic-time evaluation of the whole product is claimed.

For stable numerical verification one may use the exact homothety epsilon Lambda_t=Lambda_s: epsilon=4+15s and epsilon t=1+4s, whose integer basis matrix has determinant one. Thus wp_t(z)=epsilon^2 wp_s(epsilon z), with the analogous cube factor for its derivative. This is a change of elliptic chart, not an endomorphism of E_t.

## 3. Exact multiplication norms

For n>=1 define the full two-dimensional norm

    N_n^theta(z)=product_(a,b=0)^(n-1) Theta(z+(a+b t)/n).

### Proposition 3.1

    N_n^theta(z)=Theta(nz)  if gcd(n,5)=1,
    N_n^theta(z)=1         if 5 divides n.               (3.1)

**Proof.** For theta0 the real shifts give

    product_(a=0)^(n-1) theta0(z+a/n;t)=theta0(nz;nt).

The remaining b-shifts split the infinite product into residue classes:

    product_(b=0)^(n-1) theta0(nz+b t;nt)=theta0(nz;t).

For the smoothed denominator, multiplication by five permutes real residue classes when gcd(n,5)=1, giving theta0(5nz;5t). When n=5m, each real residue modulo m occurs five times and the denominator equals the numerator identically. These identities hold first where products converge and then meromorphically, with removable values interpreted by continuation. QED.

In particular,

    product_(eta in E_t[2]) Theta(z+eta)=Theta(2z),        (3.2)
    product_(eta in E_t[2], eta!=0) Theta(eta)=16.        (3.3)

Representatives for E_t[2] are 0,1/2,t/2,(1+t)/2. Equation (3.3) follows by comparing the fourth-order zeros in (3.2). There is no uncomputed normalization constant.

Therefore the doubling kernel has the exact eight-factor form

    Psi(z)=Theta(z)
            /[product_(eta!=0 in E_t[2]) Theta(z+eta)
              *product_(eta in E_t[2]) Theta(z+s/2+eta)]. (3.4)

### Theorem 3.2: full rank-three gamma multiplication norm

Define

    N_n^Gamma(z)=product_(a,b,c=0)^(n-1)
                   F(z+(a-b t+c s)/n).

Then

    N_n^Gamma(z)=F(nz)  if gcd(n,5)=1,
    N_n^Gamma(z)=1      if 5 divides n.                 (3.5)

**Proof.** Use the logarithmic series on the nonempty common strip

    -Im(t)/n < Im(z) < Im(s)/n.

The sum over a kills every Fourier frequency not divisible by n. For a remaining frequency n l, its n-fold factor cancels the n in the denominator. Writing P=p^l and Q=q^l, the two finite geometric sums give

    P^n sum_(b=0)^(n-1) P^(-b) sum_(c=0)^(n-1) Q^c
      =P (1-P^n)(1-Q^n)/[(1-P)(1-Q)],

and the negative exponential has the identical denominator reduction with P replaced in the numerator by Q. This is exactly L(nz). If 5 divides n, every surviving frequency was already omitted by smoothing, so the logarithmic sum is zero. Exponentiation and meromorphic continuation prove the theorem. QED.

At n=2 the eight factors have precisely the half-lattice representatives in Section 4. At n=5 one must not replace the right side 1 by F(5z). The smoothing-prime exception is essential.

## 4. The eight-point arithmetic packet, including carries

Use original period basis (tau,s,1) and

    M=[0,1,0; -4,2,15; -1,0,4],
    R=M^(-1)=[8,-4,15; 1,0,0; 2,-1,4].

For v=(b,c,a) in {0,1}^3 put

    w_v=z0+(b tau+c s+a)/2,
    T(v)=(a,b,c).

Then

    rho w_v=w_(Tv)+A_v tau+d_v,
    A_v=5+4b-2c+7a,
    d_v=1+b-c+2a.                                      (4.1)

The exact values are:

| v | T(v) | A_v | d_v |
|---|---|---:|---:|
|000|000|5|1|
|001|100|12|3|
|010|001|3|0|
|011|101|10|2|
|100|010|9|2|
|101|110|16|4|
|110|011|7|1|
|111|111|14|3|

The forward epsilon action likewise has only an s carry:

    epsilon w_v=w_(T^(-1)v)+(5-2b+c+7a)s+(1-b+2a).

Modulo two the inverse unit rotates coordinates. The half-grid decomposes exactly as

    {000}, {111},
    100 -> 010 -> 001 -> 100,
    110 -> 011 -> 101 -> 110.                            (4.2)

This is the structural reason for 8=1+1+3+3; it is not inferred from floating-point proximity.

### Theorem 4.1: exact theta carries

    F(rho w_v)/F(w_(Tv))
       = product_(j=0)^(A_v-1) Theta(w_(T^2v)+j s).      (4.3)

**Proof.** Iterate the tau difference law in (4.1): the multiplier is the product of Theta(w_(Tv)+j tau;s). Covariance replaces this by Theta(rho w_(Tv)+j rho tau;t). Apply (4.1) to Tv and rho tau=s-8t+2. Periodicity removes every integral t and 1 term. This gives (4.3). All factors are finite and nonzero: their rational coordinates cannot meet the fifth-torsion divisor, by the same independence argument as above. QED.

The complete doubling norm at z0 is

    product_v F(w_v)=F(2/3)=U^(-1).

Define Z_*=F(w_111), and C_1,C_2 to be the products of F(w_v) on the two three-cycles in (4.2). Since F(w_000)=U,

    Z_* C_1 C_2=U^(-2).                                (4.4)

Equation (4.4) does NOT determine C_1,C_2 separately, and neither is being identified with an algebraic conjugate or an Artin orbit. The second fixed point cannot be omitted. The carries in (4.3) give an explicitly normalized analytic transport, not a proof of its comparison with the independent CM/ray-field construction.

## 5. A precise obstruction to elementary elliptic telescoping

Let S denote the point represented by s in E_t; it has infinite order. Write D=div(Theta). Then

    div(Psi)=2D-[2]^*D-(z -> 2z+s)^*D.                   (5.1)

At zero the orders are 8-4-0=4. At any other point nS, n in Z minus {0}, all three Theta factors are finite and nonzero: a nonzero integer multiple of S cannot be torsion. Consequently

    sum_(n in Z) ord_(nS)(Psi)=4.                      (5.2)

### Theorem 5.1

For every nonzero integer k, no nonzero elliptic meromorphic function R on E_t and no constant C in C^* satisfy

    Psi(z)^k = C R(z+s)/R(z).                          (5.3)

**Proof.** A meromorphic function on E_t has a finite divisor. On every translation orbit, the divisor coefficients of R(z+s)/R(z) telescope and have sum zero. The orbit of zero has coefficient sum 4k on the left side, which is not zero. QED.

The same conclusion holds for a finite algebraic cover pi:C->E_t with an automorphism lifting translation by S. If a meromorphic R on that cover gave (5.3) after pullback, taking its function-field norm would yield an elliptic primitive for a nonzero power Psi^(k deg pi), contradicting the theorem. This is a statement about a global dynamically compatible primitive; it does not obstruct special-value identities or transformations involving additional period charts.

For reference, the complete divisor has 40 distinct support points, zeros of total degree 32, and poles of total degree 32. The exact checker records every point using rational coordinates on 1,t,s. The proof needs only the charge (5.2).

There IS a gamma primitive:

    V(z)=F(z)^2/F(2z),
    V(z)/V(z+s)=Psi(z).                                (5.4)

It is not elliptic. This precisely explains why substituting an arbitrary rational elliptic primitive is not legitimate.

## 6. Why the third period is structurally necessary

The cubic unit multiplier does not preserve Lambda_t:

    rho*1=4-15t in Lambda_t,
    rho*t=8t-s-2 not in Lambda_t.                       (6.1)

The last assertion follows from Q-linear independence of 1,t,s. Thus z->rho z is not an endomorphism of E_t. The full rank-three lattice Z+Zt+Zs is stable, but the chosen rank-two elliptic chart is not.

Equations (5.2) and (6.1) delimit the next comparison. One cannot obtain it by making the new kernel a rational coboundary on the single elliptic curve E_t, nor by treating rho as a CM endomorphism of that curve. The rank-three unit transport and changes of elliptic chart must be retained.

The working target is still the independent identity

    lim D_m = epsilon^6/U_alg^3.                         (6.2)

The present theorem instead identifies the same limit with epsilon^6/U_Gamma^3 and supplies its rational recurrence, division norms, and finite carries. No limiting argument here replaces the missing evaluation (6.2).

## 7. Verification and interpretation

The accepted exact script checks 78 assertions over rational/integer polynomial rings and rational divisor-coordinate groups. The identities proved uniformly above are not inferred from finite ranges.

At each of 50 and 90 requested decimal digits, with 25 additional working digits, the numerical script checks 69 equalities and five negative controls. These include the 2x2 and 3x3 theta norms, 8-point and 27-point gamma norms, the smoothing-prime exception, all eight carry formulas, direct Weierstrass reconstruction, rational cubic approximants for m=1,2, and the group-law recurrence for six forward and six backward steps.

The gamma series has an explicit truncation majorant. Floating-point rounding is not enclosed; these are numerical regressions, not rigorous complex intervals. The evaluator is retained from the previous package and is explicitly attributed as such. This block does not independently review the complete older Stark, eta, or CM proofs.

One 90-digit attempt failed at the last negative control because a direct gamma-series point near the strip boundary exceeded the inherited 20,000-term resource cap. It did not produce a passing result. The control was changed from z-t to z+t, which tests the same non-periodicity away from that boundary. The cap and the evaluator were not weakened. Both full runs were then repeated successfully. The failed source and description are retained under evidence/.

## 8. Sources and reproducibility

[1] Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields (On Eisenstein's Jugendtraum)*, arXiv:2311.04110v2. Product, sign continuation, difference laws, and the specific beta^3=7 example. https://arxiv.org/html/2311.04110v2

[2] NIST DLMF 23.2, Weierstrass definitions, parity and poles. https://dlmf.nist.gov/23.2

[3] NIST DLMF 23.10, Weierstrass addition identities. https://dlmf.nist.gov/23.10

[4] NIST DLMF 23.6, theta representation used in the numerical wp evaluator. https://dlmf.nist.gov/23.6

[5] Attached predecessor *Conductor-adapted argument taps: a cubic-power theta return*. Copied verbatim under prior/conductor_adapted_taps.md. Its source archive SHA256 is recorded in the evidence manifest.

No priority claim is made for the classical distribution laws, the standard divisor argument, or the elliptic group law. The present contribution is their explicit application to the retained cubic approximant and arithmetic half-grid, with its exact carried normalization and non-telescoping obstruction.

From the package root, first validate the shipped record:

    python checks/validate_manifest.py evidence/manifest.json --root .

Then reproduce (which changes runtime-bearing output hashes):

    python checks/run_all.py

The version-one validator checks manifest structure and output hashes, not mathematical truth. It has the legacy provenance limits stated in its output.
