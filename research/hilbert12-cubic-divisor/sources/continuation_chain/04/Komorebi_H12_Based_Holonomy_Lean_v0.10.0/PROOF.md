# Gauge-invariant class selection and based conductor holonomy

**Komorebi H12 v0.10.0. Base: Explicit Descent Packet v0.9.0.**

## Status and exact target

The original assertion U_Gamma=U_alg is NOT proved. The polarized reality assertion Im(C_pol U_Gamma^3)=0 is also not proved. The inherited modulus and interval branch results are not rerun here.

This block tests, corrects, and partially replaces the last brainstorm's proposed shortcut. It establishes:

1. an explicit universal description of the integer coinvariant lattice;
2. the distinction between a lattice character and the independent unit-generator character;
3. a holomorphic gauge counterexample to selection of a gerbe class by one raw mixed commutator;
4. a gauge-invariant seven-class detector after Hodge projection;
5. an explicit zero-anchored, inversion-symmetric holomorphic linearization on the Stein cover with arbitrary conductor-point phase;
6. a positive compact theorem: on the actual CM threefold every M-invariant holomorphic line bundle is topologically trivial and its lift becomes constant in a unitary-flat presentation;
7. a general based fixed-point theorem: on a flat equivariant line the unit action at a rational point of denominator r, divided by the action at zero, has r-th power one. Here r=3.

Fifty-two new Std-only Lean theorem constants are freshly compiled and axiom-audited. They certify the integral and finite coefficient statements, not holomorphic bundle theory or the actual gamma comparison. The 308 inherited declarations and their evidence remain in the unchanged predecessor ZIP, not freshly replayed. No historical novelty claim is made.

## 1. Data and the exact integer quotient

Let

    M = [0,1,0; -4,2,15; -1,0,4],
    R = M^(-1) = [8,-4,15; 1,0,0; 2,-1,4],
    D = M-I = [-1,1,0; -4,1,15; -1,0,3].

Use column vectors, and set

    ell(x,y,z)=x-y+3z.

The correct row identity is

    (1,-1,3)D=(0,0,-6).                                      (1)

The different tuple (-24,6,84) in the preceding brainstorm was an arithmetic error. It is not used here.

For every integer vector n=(x,y,z),

    n-ell(n)e0 = D(-z,y-4z,0),
    6e0 = D(-3,3,-1).                                       (2)

Consequently

    n in D Z^3  iff  ell(n) in 6Z,
    Z^3 / D Z^3 = Z/6.                                      (3)

These are universal statements with explicit integral preimages. For ell(n)=6k, a preimage is (-z-3k,y-4z+3k,-k). The Smith diagonal (1,1,6) is an independent check, not the only proof of (3).

Every M-invariant multiplicative lattice character has the form

    chi(n)=zeta^ell(n),  zeta^6=1.                           (4)

Indeed it factors through (3). Conversely (1) proves invariance. The ordinary period e2 has ell(e2)=3, so imposing chi(e2)=1 restricts zeta to mu3. This statement is about the lattice character, NOT about the scalar attached to the unit generator.

## 2. The unit character does not disappear

For the semidirect product

    Gamma = Z^3 semidirect_M Z,

abelianization is

    Gamma_ab = Z/6 direct-sum Z.                             (5)

Commutators with the unit generator impose exactly D Z^3 on the lattice, while the unit exponent remains free. Thus every scalar character has the form

    Psi(n,k)=alpha^k zeta^ell(n),
    alpha in C^*, zeta^6=1.                                 (6)

Restricting all scalars to be unitary still leaves alpha in U(1). Imposing exact period-one lattice normalization restricts zeta but does not restrict alpha. For example alpha=-1 and zeta=1 respects every lattice normalization but has unit value not in mu3.

This is the first failure in the earlier suggested implication. A finite lattice coinvariant quotient does not bound the unit-generator scalar.

### Why an invariant Picard class on the Stein cover is not enough

On X=C^3/Z^3=(C^*)^3, the exponential sequence and Stein vanishing identify Pic(X) with H^2(X,Z). In cyclic wedge coordinates M acts by R; det(R-I)=6, so Pic(X)^M=0. This removes the underlying holomorphic line-bundle class. It does not remove its possible M-linearizations. Section 5 constructs a counterexample on the trivial bundle itself.

On the compact threefold A=C^3/Z[omega]^3, the real lattice is Z^6, and the corresponding flat lattice character group has two cyclic-six factors, not just one. The real action of M is diag(M,M). Its coinvariant Smith invariants are (1,1,1,1,6,6).

## 3. A raw mixed commutator is not a holomorphic class invariant

The predecessor model has periods lambda=n+omega m and covectors

    a(lambda)=n0-2n2-3m0-m2,
    b(lambda)=n1+3n2-3m1-2m2,
    E(lambda,mu)=a(lambda)b(mu)-b(lambda)a(mu).

Its constant cocycle is

    phi(lambda,mu)=exp(2 pi i *4 E(lambda,mu)/7).

In particular E(e0,omega e1)=-3, so the commutator there is zeta7^(-3).

For ANY complex number u, consider the nowhere-zero holomorphic cochain

    b_lambda(z)=exp(2 pi i u m1 z0).                         (7)

This satisfies b_lambda(0)=1 for every lambda, and b_n(z)=1 for every real period n in Z^3. Its boundary is

    delta b(lambda,mu)
      =exp(2 pi i u m'_1 (n0+omega m0)).                     (8)

It follows that replacing phi by phi*delta b changes the mixed commutator at (e0,omega e1) by exp(2 pi i u). It changes neither the holomorphic cohomology class, nor the real-subgroup restriction, nor the normalization b_lambda(0)=1.

Thus a single mixed value can be changed arbitrarily within one normalized holomorphic gauge class. It cannot select that class unless an independently justified gauge restriction has first been imposed.

### The full Hodge projection does not change

Write a constant alternating form as

    E = sum_(i<j) Aij dx_i wedge dx_j
        + sum_(i,j) Bij dx_i wedge dy_j
        + sum_(i<j) Cij dy_i wedge dy_j,

with z_i=x_i+omega y_i and D_omega=omega-omega^2. Its normalized (0,2) coefficient in component (i,j) is

    H_ij=(Cij-Aij)-omega(Aij+Bij-Bji).                       (9)

The gauge (7) adds u dz0 wedge dy1 to the alternating logarithm. In (9), this changes B01 by u and C01 by u*omega. Their effects cancel exactly. The raw mixed entry changes; the class does not.

This is consistent with the holomorphic-cocycle/Hodge description in Ben-Bassat [1]. The coefficient calculations are also explicitly certified in H12MixedGauge.

## 4. The repaired one-coordinate class test

The predecessor identified the topologically trivial parameter group with C^3/O^3, O=Z[omega], and B=omega M acts on it as omega R.

Suppose a proposed class is known to be seven-torsion and B-fixed. Write it

    v=H/7 mod O^3, H in O^3.

Reduce O/7 by its two maps omega->2 and omega->4. The fixed equations become

    2R H(2)=H(2),  4R H(4)=H(4) mod7.

Their complete solution is

    H(2)=k(1,2,4),  H(4)=0,  k in F7.                       (10)

Chinese remaindering gives

    H=k J(1,2,4) mod7,
    v=k(1,2,4)/Jbar,

where J=2+3omega and Jbar=-1-3omega. The class is therefore selected by

    k=H_first(2) mod7.                                     (11)

If H is obtained from an integral alternating form E by (9), and the first cyclic component is (1,2), then

    k=C12-3A12-2B12+2B21 mod7.                             (12)

This test is applied AFTER the full holomorphic/Hodge projection, including its integral ambiguity, and AFTER seven-torsion and B-invariance have been established. It is not a raw commutator test. Gauge changes with zero (0,2) projection leave it unchanged; changing H by 7O^3 also leaves it unchanged.

For the predecessor model the full projected vector is

    H=(-5+3omega,-3-8omega,8+5omega),

so k=1. The exact Python checker enumerates the entire 7^6 parameter grid and obtains exactly these seven fixed classes. Lean independently proves the two three-variable fixed classifications and the coefficient recovery.

No H vector has been extracted from the actual extra-Eisenstein gamma descent in this block. Its torsion, class and compatibility cannot be supplied by choosing the answer k=1.

## 5. A stronger explicit obstruction on the Stein cover

On X=C^3/Z^3 let

    q(v)=exp(2 pi i v2),
    g(v)=(q(v)-q(v)^(-1))/(omega-omega^2),
    a_theta(v)=exp(i theta g(v)), theta real.                 (13)

This is a nowhere-zero holomorphic function on X. It has

    a_theta(0)=1,
    a_theta(-v)=a_theta(v)^(-1).

The actual conductor point p=(0,0,1/3) is fixed by M on X because

    (M-I)p=(0,5,1).

At p,

    g(p)=1,  a_theta(p)=exp(i theta).                        (14)

The map on the TRIVIAL holomorphic line bundle

    (v,t)->(Mv,a_theta(v)t)                                 (15)

is invertible and defines a genuine action of the infinite cyclic unit group by iteration. The lift at zero is the identity. Its action on the fiber at p nevertheless has arbitrary phase.

All six fixed points of M on X are represented by

    p_j=j(-1/2,1/2,-1/6),  j=0,...,5.

The corresponding g-values are exactly

    (0,-1,-1,0,1,1).

Thus (15) preserves the moduli at EVERY fixed point and respects inverse-point phases. It is a counterexample even after retaining these finite symmetries. It is not a modified gamma function with all its functional equations and contracting upstairs normalization.

A holomorphic gauge change b(v) replaces the multiplier by a_theta(v)b(v)/b(Mv), or its inverse convention. At a fixed point the quotient is one. Consequently the phase (14) is not removable by such a gauge.

The underlying line bundle is trivial and admits flat connections, but the specified unit linearization need not preserve a flat connection. That distinction is the exact missing hypothesis in the earlier proposed flat-character inference.

## 6. Positive result: compactness supplies the missing flatness for a comparison LINE

### Theorem 6.1

Let A=C^3/O^3 with the actual integer M above. If a holomorphic line bundle L on A has a holomorphic isomorphism covering M, then c1(L)=0. In a unitary-flat presentation L=L_chi, every such lift has a CONSTANT coefficient alpha, and chi(Mlambda)=chi(lambda).

**Proof of c1(L)=0.** The characteristic polynomial of M is

    h(X)=X^3-6X^2+12X-1,
    det M=1, h(1)=6, h(-1)=-20.

Its three eigenvalues epsilon_i are distinct. On H^1(A,C) each occurs twice. On H^2(A,C), the eigenvalues are their pairwise products. A product of distinct epsilon_i could be one only if the third were one, contradicting h(1)!=0. A product epsilon_i^2 could be one only if epsilon_i=+/-1, excluded by h(1),h(-1). Hence H^2(A,Z)^M=0. Naturality of c1 forces c1(L)=0. An independent exact exterior-matrix calculation gives determinant -155520 for wedge^2(diag(M,M))^T-I.

By the Appell-Humbert description of Pic^0 [1], a topologically trivial holomorphic line bundle on a compact complex torus has a unitary flat presentation

    (z,t) ~ (z+lambda,chi(lambda)t), |chi(lambda)|=1.

For completeness, this follows from the isomorphism from real cohomology to H^{0,1}: after an exponential linear gauge, the constant multipliers can be chosen unitary.

Write the lifted unit map as (z,t)->(Mz,a(z)t), where a is entire and nowhere zero. Compatibility gives

    a(z+lambda)=chi(Mlambda)chi(lambda)^(-1)a(z).

Therefore |a| is lattice-periodic and bounded on a compact fundamental domain. It is bounded on all C^3; Liouville, applied along complex lines, makes a constant alpha. Compatibility now forces chi(Mlambda)=chi(lambda). QED.

This is an ordinary analytic theorem, not a Lean formalization of Appell-Humbert or Liouville.

The compact hypothesis is essential: (13)-(15) are counterexamples on X. Nor does equality of two GERBE CLASSES automatically supply the genuine equivariant comparison line assumed by this theorem. That line, its coherence, and its relation to the observed scalar still have to be constructed from the actual data.

## 7. The based rational-point theorem

### Theorem 7.1 (general flat version)

Let V/Lambda be a complex quotient, let A preserve Lambda, and let a flat line be represented by a character chi with chi(A lambda)=chi(lambda). Suppose the lift of A has constant fiber coefficient alpha. If p is A-fixed modulo Lambda and rp lies in Lambda, the fiber multiplier at p divided by the fiber multiplier at zero has r-th power one.

**Proof.** Set c_p=Ap-p in Lambda. Under the convention

    (v,t) ~ (v+lambda,chi(lambda)t),

the fiber multiplier at p is alpha*chi(c_p)^(-1); at zero it is alpha. Their ratio is therefore chi(c_p)^(-1). Since

    r c_p=(A-I)(rp),

invariance of chi gives chi(c_p)^r=1. The free unit scalar alpha cancels. QED.

No exact period-one normalization is needed for this based statement. It works for any denominator r and for A=M or a return power, whenever the stated flat equivariant presentation holds.

### Actual conductor-three point

For p=e2/3 and A=M,

    c_p=(0,5,1), ell(c_p)=-2,
    3c_p=(M-I)e2.

Its class has exact order three in Z^3/(M-I)Z^3. In the rank-three flat presentation (4),

    hol_p/hol_0 = zeta^2,  (hol_p/hol_0)^3=1.               (16)

For the compact rank-six lattice, chi(n+omega m)=zeta^ell(n) eta^ell(m), with zeta^6=eta^6=1. The carry is real, so the same formula applies. Combined with Theorem 6.1, EVERY genuine M-equivariant holomorphic line on the compact threefold has the based cube property at this point.

For the three-step return,

    M^3=[-23,0,90; -90,-23,360; -12,-6,49],
    SNF(M^3-I)=(6,6,42),
    (M^3-I)p=(30,120,16).

Thus its entire invariant character group is not mu6. Nevertheless the general based theorem still bounds the normalized multiplier at a denominator-three point by mu3, provided equivariant flatness holds. One must still determine whether a proposed return observable is the original discrepancy or its third power; this identification is not automatic.

## 8. What happened to the proposed actual mixed gamma calculation?

The primary FHRZ construction [2], sections 3 and 4, uses a rank-three integral lattice and the group SL3(Z) semidirect Z^3. Its explicitly defined theta cochains Delta_a have integer lattice arguments. An extra omega e_i is not an argument of those rank-three cochains in the fixed cubic chart.

Indeed the original periods span K=Q(beta), [K:Q]=3, whereas omega is not in K. The six periods L+omega L have rational rank six. Therefore no integer change of the original three basis periods turns one of these genuinely extra translations into an old lattice translation. New descent data are required.

Using the scalar quotient

    g_lambda(z)=F(z+pi(lambda))/F(z)

instead does not solve the problem. Its mixed commutator is identically one: the four scalar values on a square cancel. That is a meromorphic coboundary, not the sought nonzero holomorphic gerbe class. The cleared cancellation is independently checked.

Thus the promised one-commutator computation did NOT produce an actual gamma seven-class. It failed for two mathematical reasons, not numerical resources: its raw value is holomorphic-gauge-dependent, and the required extra-translation cochain has not been constructed. The corrected full-Hodge selector (11)-(12) is ready to test such a construction when supplied.

## 9. Revised sufficient completion target

The main target remains U_Gamma=U_alg, equivalently the earlier polarized reality theorem together with inherited modulus, sign, and branch inputs.

A sufficient route now has an exact endpoint:

1. Construct the actual extra-Eisenstein gamma descent/packet, with normalized cochains and coherent unit transport. Use the full Hodge class, not a single raw commutator, to test the proposed primitive class.
2. Construct a GENUINE equivariant holomorphic comparison line on the compact threefold, or a verified equivariant-flat comparison on the cover. Prove that its based fiber multiplier at p=e2/3 is exactly d=U_Gamma/U_alg. This includes the arithmetic/analytic scalar identification; it is not a consequence of class equality.
3. Theorems 6.1 and 7.1 give d^3=1. The inherited rigorous distance bound |d-1|<1/2 then gives d=1.

For packets only returning after three units, step 2 must specify the observable and its exponent before applying step 3. A ninth-power conclusion must not be mislabeled as a cubic conclusion.

No comparison line with the required scalar identification has been constructed in this release. The new result is a valid endpoint theorem, a gauge-invariant class test, and explicit counterexamples to the earlier insufficient hypotheses. The remaining analytic construction is substantial and has not been made finite merely by changing terminology.

## 10. Formal and computational scope

New Lean modules, with bundled Std only:

- H12UnitCoinvariants: 21 theorems. Universal integer quotient and preimages, conductor carry and exact order, scaling, and finite character constraints.
- H12MixedGauge: 13 theorems. Holomorphic-gauge numerator identities, real/zero normalization, changed mixed coefficient with zero Hodge projection, and model class coefficients.
- H12AnchorObstruction: 9 theorems. Exact six-point interpolation coefficients, conductor label, based scalar cancellation, and orbit iteration.
- H12SevenClassDetector: 9 theorems. Both CRT fixed systems, coefficient recovery, and the class selector.

All 52 are freshly compiled; every theorem's transitive axioms are inspected. Only propext, Classical.choice and Quot.sound are allowed where needed. No admitted proofs, custom axioms, unsafe declarations or native_decide appear. A false arithmetic statement is required to fail.

These formal statements do not define analytic bundles, holomorphic cohomology, complex exponentiation of the example, or the main gamma comparison. The coefficient-to-analysis applications are the ordinary proofs above. The compact theorem and the general character-valued based theorem are not claimed as fully formalized analytic results.

The Python checker uses exact integers, rational arithmetic, symbolic polynomials and finite residue rings. Its 36 named assertions and five negative controls include all 216 denominator-six grid points, all 216 sixth-character coefficient triples, and all 117649 seven-parameter classes. Universal statements are proved separately, not extrapolated from the finite checks. No new floating-point or interval gamma computation was performed.

The compiler is Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d. The seven-part archive matched SHA256 66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34. Only bundled Std was needed. The 308 inherited declarations are retained with prior evidence, not freshly recompiled. The cumulative source inventory is 360, not 360 fresh checks.

## References and source boundaries

[1] Oren Ben-Bassat, Gerbes and the Holomorphic Brauer Group of Complex Tori, arXiv:0811.2746v3. Section 5, Theorem 1 and its Pic^0 description; sections on constant cocycles and Hodge projection. https://arxiv.org/html/0811.2746v3

[2] Giovanni Felder, Andre Henriques, Carlo A. Rossi, Chenchang Zhu, A gerbe for the elliptic gamma function, arXiv:math/0601337v1. Section 3.1 fixes Lambda=Z^3; section 4.3, Theorem 4.1 describes the actual group-Cech gamma/theta cochains and their domain. https://arxiv.org/html/math/0601337v1

[3] Explicit Descent Packet v0.9.0, unchanged in prior/v09_source_and_evidence.zip. It supplies the particular compact model, Hodge conventions and main target, not the missing actual gamma identification.

This is a scoped source check, not a general novelty search or an assertion that no more powerful analytic theorem exists elsewhere.
