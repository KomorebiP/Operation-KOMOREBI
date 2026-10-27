# Explicit seven-torsion descent and the compatible three-class packet

**Komorebi H12, v0.9.0. Base: Gerbe Descent v0.8.0, retained byte-for-byte.**

## Status

The original equality U_Gamma=U_alg and the exact reality of C_pol U_Gamma^3
remain unproved. This block constructs a compact holomorphic projective model
for a particular primitive class from v0.8, including its lattice multipliers,
a trivialization cochain on the intermediate cover, and compatible lifts of the
unit and Eisenstein rotation on a THREE-CLASS packet. This model is not asserted
to be the descent of the distinguished gamma section.

A useful obstruction is also closed: if a single compact gerbe class is fixed
by BOTH M and omega M, only three classes remain, and none is nonzero seven-
torsion. The seven-component can instead be transported in a three-class orbit.

The new 41 Lean theorem constants are compiled and axiom-audited with bundled
Std. They certify integer/residue identities, not holomorphic gerbes or the
analytic gamma comparison. The 267 inherited declarations and evidence are
retained, not freshly replayed. Cumulative source inventory: 308.

## 1. Data and fixed actions

Let O=Z[omega], omega^2+omega+1=0, with Im omega>0, and let A=C^3/O^3. Write

    M = [0,1,0; -4,2,15; -1,0,4],
    R = M^(-1) = [8,-4,15; 1,0,0; 2,-1,4],
    J=2+3omega, Jbar=-1-3omega, J Jbar=7,
    B=omega M, Omega=omega I.

The v0.8 Hodge computation identifies topologically trivial holomorphic gerbe
classes with C^3/O^3. In those particular cyclic Hodge coordinates,

    M^* = R,          Omega^* = omega I,          B^* = omega R.       (1)

It also proves that every B-fixed holomorphic gerbe class is topologically
trivial, and that the B-fixed group has 252 elements and primitive component
E_omega[Jbar]. The argument uses the exponential sequence and the Hodge
projection; these analytic inputs are inherited, not new Lean assumptions.

### 1.1 Simultaneous invariance: exactly three classes

If eta is fixed by R and omega R, then omega eta=eta. Hence every coordinate is
in E_omega[omega-1], an additive group F3. On this subgroup, R reduces to

    [2,2,0; 1,0,0; 2,2,1].

The fixed equations force eta_0=eta_1=0, with eta_2 arbitrary. Thus

    H^2(A,O_A^*)^(M^*) intersect H^2(A,O_A^*)^(B^*)
        = {(0,0,z): (omega-1)z=0} ~= Z/3.                          (2)

This is a theorem about CLASSES, not a three-valued gamma phase bound.
It rules out a single nonzero primitive seven-class satisfying both invariances.
It does not rule out M-equivariant compact descents outside the B-fixed locus,
and does not refute the special-value identity.

The exact checker independently enumerates all 252 B-fixed classes in rational
coordinates and obtains exactly these three common classes.

### 1.2 A primitive class and its ordinary-unit orbit

Choose

    eta = (1,2,4)/Jbar  in C^3/O^3.                                (3)

It has exact order seven and belongs to the v0.8 primitive fixed subgroup.
The exact vector identity

    R(1,2,4)^T - 4(1,2,4)^T = 7(8,-1,0)^T

proves M^*eta=4eta. Since omega=2 modulo Jbar, Omega^*eta=2eta and B^*eta=eta.
Thus

    eta -> 4eta -> 2eta -> eta                                   (4)

under M^*. Its tensor norm has class (1+4+2)eta=0. Individual classes remain
nonzero. On the point-side E[J], M acts by doubling; the parameter-side action
is multiplication by four, so the one-dimensional pairing 3kl modulo seven is
preserved: 3(2k)(4l)=3kl mod7. No assertion about a gerbe's scalar evaluation
follows just from this pairing.

## 2. An actual constant cocycle for the primitive class

Write a period as lambda=n+omega m, with n,m in Z^3. Define INTEGER covectors

    alpha(lambda)=n0-2n2-3m0-m2,
    beta(lambda) =n1+3n2-3m1-2m2.                                 (5)

The name beta here denotes this covector, not the cubic-field generator.
In this note the covectors are used only in the finite descent construction.

Let

    E(lambda,mu)=alpha(lambda) beta(mu)-beta(lambda) alpha(mu),
    zeta=exp(2 pi i/7),
    phi(lambda,mu)=zeta^(4 E(lambda,mu)).                          (6)

The exponent is interpreted modulo seven. Bilinearity gives the normalized
2-cocycle identity

    phi(lambda,mu) phi(lambda+mu,nu)
      =phi(mu,nu) phi(lambda,mu+nu),
    phi(lambda,0)=phi(0,lambda)=1.

Its commutator is zeta^E, since 8=1 mod7. This is an explicit representative,
not merely a classification of possible cohomology classes.

### 2.1 Verify the Hodge class, including the factor of two

Let D=omega-omega^2. In the real coordinates z_i=x_i+omega y_i,

    dx_i^(0,1)=omega/D dbar z_i,
    dy_i^(0,1)=-1/D dbar z_i.

The numerators of the Hodge projections of alpha and beta are respectively

    a_H=(3+omega,0,1-2omega),
    b_H=(0,3+omega,2+3omega).

Their cyclic cross product is

    a_H cross b_H=(-5+3omega,-3-8omega,8+5omega)
                  =J(1,2,4)+7(-1,-1-2omega,-omega).              (7)

A logarithm of phi in the exp(2 pi i x) convention is 4E/7. Skew-symmetrization
of this cochain is 8E/7=E/7+E. The integral E contributes zero to the exponential
class, so the class is represented by E^(0,2)/7. Multiplying Hodge coefficients
by D^2, as in v0.8, equation (7) yields exactly

    [phi] = [(1,2,4)/Jbar] = eta.                                (8)

This also proves the class is nonzero and has order seven. The factor of two in
skew-symmetrization is essential. The constant-cocycle/Hodge dictionary is the
standard one in Ben-Bassat [1], sections 4, 7 (Definition 5) and 10. We have
spelled out the normalization rather than quoting a cocycle with a mismatched
exponential convention.

The Dixmier-Douady class vanishes: the chosen additive logarithm is already an
additive 2-cocycle, so its next boundary is zero. This does not make the
holomorphic class (8) trivial.

## 3. Seven-dimensional matrices give the full compact descent

On V=C^7, use the basis e_j, j in Z/7. For r in Z/7 define

    W_r(a,b)e_j = zeta^[r(a j+4ab)] e_(j+b).                     (9)

Then

    W_r(a,b) W_r(c,d)
       =zeta^[4r(ad-bc)] W_r(a+c,b+d).                          (10)

All labels are residues modulo seven. This identity follows by comparing the
exponent in each column. Before reducing modulo seven the difference is
-7r a d; the universal integer identity is compiled in Lean.

In particular, lambda -> [W_1(alpha(lambda),beta(lambda))] is a homomorphism
O^3 -> PGL_7(C). The quotient of C^3 x M_7(C) by

    (z,T) -> (z+lambda, W_1(lambda) T W_1(lambda)^(-1))           (11)

is a holomorphic bundle of matrix algebras on A. Scalar factors cancel in
conjugation, so (11) is a genuine lattice action. Its GL/PGL lifting gerbe has
cocycle phi. This constructs an actual holomorphic Azumaya representative of
eta, not an assertion of descent for the gamma section.

The period quotient (alpha,beta):O^3 -> F7^2 is surjective: (a,b,0,0,0,0) is an
explicit section at the residue level. Its kernel has index 49. Consequently
the matrix algebra becomes trivial on the corresponding degree-49 finite cover.

The size seven is minimal for a constant projective representation realizing
this commutator. For real basis periods e0,e1, the two matrices satisfy
W(e0)W(e1)=zeta W(e1)W(e0). In dimension d, taking determinants forces zeta^d=1,
so 7 divides d. Our dimension-seven representation attains the lower bound.
This is not a general period-index claim for arbitrary gerbes.

## 4. Explicit trivialization on the intermediate Stein cover

Let H=Z^3 and X=C^3/H. Define complex-linear forms

    a(z)=z0-2z2,         b(z)=z1+3z2.

For n in H set

    t_n(z)=exp[ (2 pi i)*4/7 * (a(z)b(n)-b(z)a(n)) ].           (12)

The multiplicative group-cochain boundary, in the specified convention, is

    t_mu(z+lambda) t_(lambda+mu)(z)^(-1) t_lambda(z).

For lambda,mu in H it equals phi(lambda,mu), exactly. Thus (12) is a concrete
holomorphic trivialization cochain for the model gerbe on X. It is normalized
by t_n(0)=1. This statement concerns the model, not the zero anchor F(0) of gamma.

All remaining period data can be written explicitly as well. Extend (12) to
lambda in O^3 by replacing a(n),b(n) with alpha(lambda),beta(lambda). Define

    r_alpha(lambda)=alpha(lambda)-a(lambda),
    r_beta(lambda)=beta(lambda)-b(lambda).

The gauge-transformed full cocycle is

    phi'(lambda,mu)=exp[(2 pi i)*4/7 *
        (r_alpha(lambda) beta(mu)-r_beta(lambda) alpha(mu))].   (13)

For lambda=n+omega m,

    r_alpha(lambda)=-3m0-m2-omega(m0-2m2),
    r_beta(lambda) =-3m1-2m2-omega(m1+3m2).

Formula (13) equals one when its FIRST argument is in H. It does not generally
equal one for an omega-period followed by a real period. Those mixed terms are
part of the line-bundle and coherence data of descent; they must not be dropped
or replaced by an ordinary scalar function on A.

Equations (11)-(13) give the full compact model and an explicit trivialization
of its restriction, rather than invoking Stein existence alone.

## 5. The twisted unit has an exact quadratic lift

Let B=omega M. In the quotient of period labels,

    (alpha(B lambda),beta(B lambda))
       =(alpha(lambda)+4 beta(lambda),beta(lambda)) mod7.      (14)

There are exact integral carry formulas:

    alpha(B lambda)=alpha(lambda)+4 beta(lambda)+7 k_alpha,
    beta(B lambda) =beta(lambda)+7 k_beta,

    k_alpha=-n1-2n2+2m1+3m2,
    k_beta=2n0-n1-8n2-m0+m1+4m2.

Thus E(B lambda,B mu)=E(lambda,mu) mod7, so phi is strictly B-invariant.

Define

    D_r e_j=zeta^(2r j^2)e_j.

A column-wise calculation proves

    D_r W_r(a,b) D_r^(-1)=W_r(a+4b,b).                       (15)

The exact integer exponent difference is -14r b^2, so it vanishes modulo seven.
In particular D_1 gives the lift (z,T)->(Bz,D_1 T D_1^(-1)) of the twisted unit
on the compact matrix-algebra model (11). Also D_r^7=I and D_r e0=e0.

There is no identification here of D_1 with an analytically normalized gamma
transport. Replacing D_1 by c D_1, c!=0, does not change the algebra conjugation.
The displayed finite-order lift is our explicit choice; it is not imposed on
all possible gamma equivariant structures.

## 6. Both symmetries act coherently on a three-class packet

Let A_r denote the matrix-algebra model using W_r, for r in {1,4,2}. Its Brauer
class is r eta. The ordinary unit and rotation act on period labels by

    K_M(a,b)=(2a+b,2b),
    K_Omega(a,b)=(4a,4b) mod7.                              (16)

Their determinants are 4 and 2, respectively. Consequently

    M^* A_r ~= A_(4r),      Omega^* A_r ~= A_(2r),
    B^* A_r ~= A_r.                                         (17)

These isomorphisms are explicit, not only equality of classes. Put

    S_d e_j=e_(d j),
    L_r=D_r S_2.

Then

    L_r W_(4r)(a,b) L_r^(-1)=W_r(2a+b,2b),
    S_4 W_(2r)(a,b) S_4^(-1)=W_r(4a,4b).                   (18)

The choices satisfy

    L_r S_4=S_4 L_(2r)=D_r,
    S_4^3=I,
    L_r L_(4r) L_(2r)=D_r^3.                               (19)

Hence the ordinary unit and Eisenstein rotation commute on the packet with
these lifts, and the relation (omega M)^3=M^3 is respected. This resolves the
coherence problem for this SPECIFIED finite model. It does not supply the
intertwiner between the gamma construction and this model.

The tensor product of the three Brauer classes is zero, since 1+4+2=7. As in
the earlier signed-norm work, the triviality of a full tensor norm is not a
calculation of the individual oriented section values.

## 7. What the construction changes about the gamma comparison

There are now two distinct statements:

1. A concrete primitive compact model exists, with explicit extra-period
   cocycle, intermediate-cover trivialization, twisted unit lift, and compatible
   ordinary-unit/rotation packet. Sections 2-6 prove this statement.
2. The actual fifth-smoothed gamma section, its unit transport, and its complex
   zero anchor identify with this compact model or packet in a way whose scalar
   evaluation is the independent CM unit. This is NOT proved.

By v0.8, both the actual smoothed gerbe pulled back to X and our model pulled
back to X are holomorphically trivializable. An unspecified isomorphism on X
therefore exists, but existence cannot fix the required scalar transport.
Prescribing such an isomorphism to force the desired special value would be
circular. Matching only cohomology classes or cocycle boundaries would also
leave normalization data unresolved.

A direct single-class extension preserving both original M automorphy and the
additional B symmetry cannot use a nonzero primitive seven-class, by (2). The
new three-class packet is a coherent alternative; it is not an assertion that
the actual gamma object already furnishes that packet.

The next missing comparison is concrete: construct from the ACTUAL gamma
cochains an isomorphism on X to this packet, retaining the mixed omega/real
terms (13), the lifted unit identities (18)-(19), and the analytic normalization.
Then independently compute its scalar pairing with the fixed CM data. The
current note does not infer reality of C_pol U_Gamma^3, does not put its phase
in a finite group, and does not re-run the earlier numerical gamma comparisons.

## 8. Verification boundary

New Std-only modules:

| Module | Theorems | Formal content |
|---|---:|---|
| H12ExplicitDescent | 20 | Universal integral period/carry identities, normalized bilinear cocycle and cochain numerators, Hodge coefficient computation |
| H12DescentPacket | 21 | Common F3 fixed classification, primitive orbit, universal Weyl and quadratic-lift exponent identities, packet coherence |

All 41 compile against pinned Lean 4.34.0-rc2. Every theorem's transitive axiom
list is audited. Only propext, Classical.choice, Quot.sound are allowed, with
no admitted proofs, project axioms, native_decide, or unsafe declarations. A
false integer control is required to be rejected.

The complex exponentiation, construction of analytic quotient bundles/gerbes,
Hodge identification with sheaf cohomology, and application of these facts to
the finite model are ordinary proofs here. Lean certifies their explicit
integer identities, not analytic geometry. The main gamma equality is absent
from all new formal statements.

The exact checker passes 35 named assertions and five negative controls. It
independently enumerates all 252 fixed parameter classes, all 7^6 inputs of the
rank-two period quotient, all 2401 Weyl products, 49 twisted intertwiners, 147
ordinary and 147 rotation intertwiners, and all 49 pairing covariance entries.
It also uses universal symbolic polynomial checks and exact rational Hodge
arithmetic. Those finite checks do not replace the separate universal Lean
identities and ordinary mathematical proofs.

The pinned runtime archive was reconstructed and its combined SHA256 matched
66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34. Only the compiler
and bundled libraries were needed; no Mathlib or inherited full replay is claimed.
No new floating-point or interval gamma test was performed.

## References

[1] Oren Ben-Bassat, Gerbes and the Holomorphic Brauer Group of Complex Tori,
arXiv:0811.2746v3, 5 February 2013. Sections 4 and 7 (Definition 5), section 10.
The paper uses exp(x)=exp(2*pi*i*x). Constant cocycle representatives and the
Hodge quotient are used, not an asserted gamma comparison.
https://arxiv.org/html/0811.2746v3

[2] Retained Komorebi H12 Gerbe Descent v0.8.0, PROOF.md, sections 2-4. Supplies
the B-fixed topological obstruction, precise cyclic Hodge coordinates, and
trivializability of the actual fifth-smoothed pullback on X. Its complete source
and evidence archive is preserved under prior/ with the base hash recorded.

These constructions specialize standard cocycle and finite Heisenberg algebra.
No historical novelty or general Hilbert-12 solution is asserted.
