# Holomorphic descent, complementary gerbe torsion, and the oriented Gauss character

**Komorebi H12 continuation, v0.8.0. Base checkpoint: CM Threefold Bridge v0.7.0.**

## Status and target

The original equality U_Gamma = U_alg is NOT proved. Equivalently, the exact
reality of C_pol U_Gamma^3 remains to be established using the inherited modulus,
positive-sign and branch inputs. No new numerical gamma comparison is performed.

This block proves an exact restriction on the proposed compact construction:
every holomorphic gerbe isomorphism class on A=E_omega^3 fixed by the TWISTED
automorphism B=omega M has zero Dixmier-Douady class. Its possible fixed classes
are then computed completely: in specified Hodge coordinates they form
E_omega[6 Jbar], of order 252 and additive structure Z/6 x Z/42. Their primitive
seven-torsion component is the conjugate of the point component in v0.7.0.

This is a theorem about fixed ISOMORPHISM CLASSES. It does not specify an
equivariant structure, a meromorphic section, or a normalized scalar evaluation.
It does not assert that the smoothed gamma construction has descended to A or
is fixed by B. B-invariance is an additional condition on the proposed descent,
not a consequence of the existing M-automorphy.

The actual fifth smoothing cancels the primitive triptic topological class. On
the explicit intermediate Stein cover X=C^3/Z^3=(C^*)^3, its pulled-back
holomorphic gerbe is therefore trivializable. This is an existence statement;
no preferred trivialization or descent through the extra Eisenstein directions
has been computed here.

Finally, the oriented elliptic pairing between 1/J and 1/Jbar is precisely
exp(6 pi i/7), the additive character in our retained Gauss sum. A necessary
qualification is proved as well: the FULL PRODUCT polarization pairing of the
embedded threefold points is 1, so the useful pairing is the specified
one-dimensional coordinate pairing, not an automatic threefold holonomy.

There are 51 new Std-only Lean theorem constants, freshly compiled and
axiom-audited. They certify integer exterior/Hodge matrices, elimination,
finite characters, and smoothing degree. Analytic cohomology and the gerbe
interpretation use the ordinary proofs and external inputs below, not Lean
axioms. The cumulative source inventory is 267; no fresh replay of all 267 is
claimed. The underlying theories are classical; no priority claim is made.

## 1. Fixed data and conventions

Put O=Z[omega], omega^2+omega+1=0, Im omega>0, and

    J=2+3omega, Jbar=-1-3omega, J+Jbar=1, J Jbar=7.

Let E=C/O, A=E^3, and use the actual original unit matrix

    M=[0,1,0; -4,2,15; -1,0,4],
    R=M^(-1)=[8,-4,15; 1,0,0; 2,-1,4].

Set B=omega M. In the real integral lattice basis

    (e0,e1,e2, omega e0,omega e1,omega e2)

the matrix of B is

    B_R=[0,-M; M,-M].                                      (1)

The predecessor gives p M=epsilon p for p=(tau,s,1), with
beta^3=7, epsilon=2-beta, tau=(beta^2+2beta)/15, s=-(beta+2)/15.
It also proves

    Fix(M)=h(E[6]), h(z)=(3z,3z,z),
    Fix(omega M)=g(E[6J]), g(z)=((5+omega)z,(-4-5omega)z,z),

and the oriented point P_J=(1,2,4)/J. We preserve the predecessor ZIP and hash.

Holomorphic O^*-banded gerbes up to isomorphism are classified by H^2(A,O^*).
Their topological class is the connecting image in H^3(A,Z) from the exponential
sequence. These are standard analytic gerbes, not only algebraic Azumaya classes.

## 2. The exact Hodge obstruction

The exponential sequence gives

    H^2(A,O) -> H^2(A,O^*) --DD--> H^3(A,Z) -> H^3(A,O).

For a complex torus, the last map is projection to H^{0,3}. An integral real
class in its kernel has only types (2,1) and (1,2). This is the standard
holomorphic-gerbe criterion in Ben-Bassat [1], section 6, Definition 2.

Write z_i=x_i+omega y_i and

    Omega=dz_0 wedge dz_1 wedge dz_2=alpha+omega beta_vol,

where alpha and beta_vol are the two INTEGRAL coefficient three-forms. They
are not the number-field generator beta. Put D=omega-omega^2=1+2omega;
D^2=-3. Since det B=1, both coefficient forms are B-invariant.

### Theorem 2.1: the entire integral invariant lattice

    H^3(A,Z)^(B^*) = Z alpha + Z beta_vol.                  (2)

Proof. In the lexicographic basis of the twenty ordered three-subsets of
{0,...,5}, form W=(wedge^3 B_R)^T. The exact matrix is retained in
`evidence/exterior_data.json`. Its fixed kernel has rank two. More strongly,
we provide integer elimination identities, not just a rank computation.

If v has twenty integer coordinates, each coordinate i other than 0 and 3
satisfies an identity

    d_i (v_i-alpha_i v_0-beta_vol_i v_3)
        = r_i dot (Wv-v),                                  (3)

with positive integer d_i <=270 and explicit integer row r_i. All eighteen
identities are in `evidence/elimination_certificate.json` and are universally
proved in Lean. Thus Wv=v forces v=v_0 alpha+v_3 beta_vol. Conversely the two
basis forms are fixed. Their coordinates 0 and 3 are (1,0) and (0,1), proving
integral primitivity, so no rational saturation has been omitted. QED.

Solving Omega and bar(Omega) for their two coefficients gives

    (a alpha+b beta_vol)^(0,3)
       = (a omega-b)/D * bar(Omega).                        (4)

For integers a,b this is zero only if a=b=0. Equivalently, after multiplying
by D^3, the two integer Hodge coordinates are (3b,-3a). The whole twenty-input
projection and its restriction to (2) are independently computed from exterior
products of dx_i,dy_i; the Lean core checks the resulting coefficient identities.

### Corollary 2.2: topological triviality is necessary

If a holomorphic gerbe CLASS g on A satisfies B^*g=g, then

    DD(g)=0.                                               (5)

Indeed its DD class is B-invariant by naturality and has zero (0,3) component
by the exponential sequence. Equations (2)-(4) force it to vanish.

This does NOT say that the gerbe is holomorphically trivial. Nor does it apply
to every M-invariant class: without the omega twist, the invariant H^3 lattice
has rank eight and its Hodge-allowed part has rank six. The exact checker
verifies both ranks as a negative control on the twist hypothesis.

## 3. Classify every remaining fixed holomorphic class

The kernel of DD is

    G0(A)=H^2(A,O) / im H^2(A,Z).                           (6)

Use the cyclic basis

    (dbar z_1 wedge dbar z_2,
     dbar z_2 wedge dbar z_0,
     dbar z_0 wedge dbar z_1)

of H^{0,2}. The elementary projections are

    (dx_i)^(0,1)=omega/D * dbar z_i,
    (dy_i)^(0,1)=-1/D * dbar z_i.

Their exterior products show exactly

    im H^2(A,Z) = D^(-2) O^3.                              (7)

For each cyclic component, dy_i wedge dy_j supplies coefficient 1/D^2,
and dx_i wedge dy_j supplies -omega/D^2. Conversely all coefficients are
in that lattice. Thus multiplying the Hodge coefficient vector by D^2
identifies G0(A) with C^3/O^3.

Pullback by B on this parameter torus is NOT B. It is

    C=det(bar B) (bar B)^(-1)=omega M^(-1).                 (8)

This is the standard exterior-square cofactor identity in the specified cyclic
basis. The exact 6-by-15 integral Hodge projection P and 15-by-15 exterior-square
pullback W2 obey

    P W2 = C_R P,

where C_R=[0,-R;R,-R]. A six-column minor of P has determinant one, giving an
explicit integral right inverse. These identities are universally Lean-checked,
including all 225 exterior-minor entries.

Since

    C^(-1)=omega^2 M,

fixed parameter classes for C are exactly Fix(omega^2 M). Define

    gbar(z)=((4-omega)z,(1+5omega)z,z).

The predecessor's fixed-point calculation, or its conjugate, now proves

    H^2(A,O^*)^(B^*)
       = G0(A)^(B^*)
       ~= gbar(E[6Jbar]).                                 (9)

This is an isomorphism of the indicated additive class groups, after the
specified coordinate identifications. Its order is 252, and its Smith
invariants give

    Z/6 x Z/42.                                           (10)

The 6-by-6 real matrix C_R-I has determinant 252 and Smith diagonal
(1,1,1,1,6,42). All 252 classes are also enumerated with exact rational
coordinates, independently of the Smith computation.

There is a split sequence

    0 -> E[Jbar] -> gbar(E[6Jbar]) -> h(E[6]) ->0,
    gbar(z) |-> h(Jbar z),
    h(t) |-> gbar(Jt).                                    (11)

It splits because Jbar J=7 and 7t=t on E[6]. Thus the gerbe-class side selects
the COMPLEMENTARY seven-torsion orientation to the point group Fix(omega M).

These 252 objects are classes, NOT 252 possible gamma numbers. Isomorphisms
between a gerbe and its pullback, meromorphic sections, and scalar
normalizations are additional data. The numerical phase problem has not been
reduced to choosing among 252 complex numbers. We have not selected the
particular class, or shown that the actual smoothed gamma has such a descent.

## 4. Fifth smoothing and an actual intermediate cover

Let L=Z tau+Z s+Z and L5=Z(5tau)+Z(5s)+Z. Multiplication by five induces

    [5]: [C/L] -> [C/L5].

In the ordered lattice bases (tau,s,1) and (5tau,5s,1), the lattice homomorphism
is diag(1,1,5). Hence pullback on H^3(Z^3,Z) multiplies the oriented generator
by five, not by 125.

The FHRZ gamma gerbe on an oriented triptic curve has primitive DD class
([2], Theorem 5 in the authors' four-page account; the full proof is in their
long paper). The tensor quotient associated with the fifth-smoothed local
section is

    S5 = G_L^(tensor 5) tensor ([5]^* G_L5)^(-1).

Its class satisfies

    DD(S5)=5-5=0.                                         (12)

Changing both orientation conventions changes the two signs together and does
not change this cancellation. This is a topological result for the ACTUAL
smoothing shape. It is not a computation of any specific class in (9).

There is a useful holomorphic correspondence that does not require the false
function descent excluded in the predecessor:

    A <- X=C^3/Z^3=(C^*)^3 -> [C/L].                       (13)

The left map is the covering induced by Z^3 subset O^3. The right map is
induced by the linear projection pi(v)=tau v_0+s v_1+v_2 together with the
identity map of its Z^3 acting groups. Equivariance is exactly
pi(v+n)=pi(v)+p(n). This is a map to a quotient STACK, not to an ordinary
Hausdorff elliptic curve. M acts compatibly on X and on the triptic data.
B=omega M does not preserve the chosen Z^3 cover; imposing twisted invariance
on the compact result requires additional transition data.

The manifold X is Stein: it is biholomorphic to the closed complex submanifold
of C^6 given by z_i w_i=1 for i=0,1,2. Cartan theorem B makes H^j(X,O)=0 for
j>0 [4]. The exponential sequence then identifies

    H^2(X,O^*) ~= H^3(X,Z) ~= Z.

By (12), the pullback of S5 to X is holomorphically trivializable. QED.

This is a genuine existence statement, but not a preferred trivialization.
Transport through the remaining deck group O^3/Z^3 still requires line-bundle
isomorphisms and their coherent multipliers. The equation F(pi(v+lambda))=
F(pi(v)) cannot be substituted for them. In particular the common zero-anchor
and the conjugation normalization are not determined by Cartan vanishing.

This correspondence turns the old non-descent obstruction into a precise next
construction: choose and normalize the Stein-cover trivialization, compute its
extra Eisenstein descent data, then test its B-invariance and its class in (9).
Existence on X alone supplies none of those three computations.

## 5. The complementary torsion points recover the exact additive Gauss character

Adopt the usual oriented elliptic pairing convention [3]

    e7((a+bomega)/7,(c+domega)/7)
       =exp(2 pi i (ad-bc)/7).                             (14)

Because

    1/J=(-1-3omega)/7,   1/Jbar=(2+3omega)/7,

we have ad-bc=3, and consequently

    e7(1/J,1/Jbar)=exp(6 pi i/7).                          (15)

The pairing on E[J] x E[Jbar] is nondegenerate: multiplying the two coordinates
by k,l gives exponent 3kl modulo seven, and three is invertible modulo seven.
This is checked on all 49 pairs. Reversing the orientations inverts the phase.

Let chi(1..6)=(1,omega,omega^2,omega^2,omega,1), chi(0)=0. It obeys
chi(2k)=omega chi(k), matching the original M action by doubling in the
seven-torsion point component. Hence

    G_pair=sum_(k=1)^6 chi(k) e7(k/J,1/Jbar)
          =sum_(k=1)^6 chi(k) exp(6 pi i k/7).              (16)

This is EXACTLY the retained Gauss sum, including the previously specified
additive phase, and

    G_pair^3=7J, xi=G_pair/beta.                            (17)

There is a fully finite certificate. In O[Z/7], with formal generator Z, put
G=sum chi(k) Z^(3k). Then

    G^3=7J-J(1+Z+...+Z^6).                                (18)

All seven coefficients of (18) are kernel-checked. Evaluating at a primitive
seventh root proves (17). An independent SymPy cyclotomic reduction checks the
same identity.

### The full product polarization does NOT give (15)

For the embedded threefold points

    P_J=(1,2,4)/J,  P_Jbar=(1,2,4)/Jbar,

the product polarization pairing has exponent

    3(1^2+2^2+4^2)=63=0 mod7.

Therefore it is 1. Equation (15) uses the specified one-dimensional
parameterizations/first-coordinate projections, not the threefold product
polarization. The two are explicitly distinguished and tested negatively.

Nor does (15) define a scalar evaluation of a gerbe at a point: a gerbe class,
a section/trivialization, and the cycles used for transport are different
levels of data. No gamma holonomy is equated with this finite pairing here.
The result identifies the correct arithmetic character available for a future
normalized comparison; it does not supply that comparison.

## 6. What still has to be proved

The retained target remains

    conjugate(C_pol U_Gamma^3)=C_pol U_Gamma^3,
    C_pol=epsilon a1 a2^3/omega.

This would imply the original equality using inherited modulus, sign and
branch facts. The current block proves no additional reality or gamma-power
identity and places no new root-of-unity bound on its discrepancy.

The three live obligations in the compact approach are now distinguished:

1. Construct a specific trivialization of the actual smoothed pullback on X,
   and its holomorphic descent multipliers for the three additional omega
   directions. Topological vanishing and existence on X are established;
   the normalized multiplier construction remains open.
2. Establish the required twisted compatibility and identify the resulting
   holomorphic class and chosen equivariant structure. The possible fixed
   classes have been classified, but the relevant class has not been selected.
3. Prove the scalar comparison to the oriented CM products, retaining the
   zero anchor, conjugation, and the distinction between the one-dimensional
   pairing and the trivial full-product pairing.

Even a successful class identification in step 2 would not eliminate step 3.
One must not conclude phase equality from equal topological classes, identical
coboundaries, or equal fixed-point counts. Those insufficiencies were already
exhibited in the predecessor work.

## 7. Formal and computational verification boundary

New formal modules, all importing bundled Std only:

- H12GerbeDescent: 29 theorems. Actual third exterior matrix and all 400
  minor entries; eighteen universal integer elimination certificates; the
  entire invariant lattice; Hodge-zero obstruction; conjugation parameters.
- H12FlatGerbeAction: 9 theorems. Actual second exterior matrix and all 225
  entries; integral Hodge projection and its right inverse; intertwining
  with omega M^(-1); opposite-twist fixed equality and parameter identity.
- H12WeilCharacter: 13 theorems. Oriented pairing residues, nondegeneracy,
  product-polarization countercheck, finite character/Jacobi/Gauss identities,
  and the actual fifth-smoothing lattice determinant.

These 51 theorem constants are freshly compiled and their transitive axiom
lists audited. The standard logical dependencies propext, Classical.choice,
and Quot.sound are allowed; there are no project axioms, admitted proofs,
native_decide calls, or unsafe declarations. A false integer theorem must fail.

The cohomology/Hodge/gerbe dictionary, complex torus interpretation, Cartan
application, and exponential pairing interpretation are ordinary mathematical
proofs applying the explicit coefficient theorems and cited external inputs.
They are not falsely described as Lean-formalized analytic geometry. The
actual gamma descent and arithmetic scalar comparison are not assumed in any
new formal declaration.

The exact checker verifies 58 assertions and five negative controls. It
independently recomputes all exterior entries, coefficient-volume forms, Hodge
projections, elimination certificates, ranks, Smith invariants, all 252 fixed
classes and 49 oriented pairings, and the finite Gauss cube. This bounded work
checks the specified finite lattices; the universal integer statements have
separate proofs and Lean certificates. No floating-point gamma test was run.

All new sources are replayed from a fresh extraction. The 216 inherited
sources/evidence are preserved in prior/v07_source_and_evidence.zip, not claimed
as freshly replayed. The cumulative inventory is 267, not 267 fresh checks.

## References

[1] Oren Ben-Bassat, Gerbes and the Holomorphic Brauer Group of Complex Tori,
arXiv:0811.2746v3 (5 February 2013), section 6, Definition 2 and the exponential
sequence; the topologically trivial class description is used in sections
1, 6 and 10. https://arxiv.org/html/0811.2746v3

[2] G. Felder, A. Henriques, C. Rossi, C. Zhu, A gerbe for the elliptic gamma
function, arXiv:math/0601337v1; Giovanni Felder's short account Elliptic gamma functions, triptic curves and
SL3(Z), arXiv:math/0604588v1 (27 April 2006), Theorems 4 and 5 on page 3.
These establish the primitive triptic DD class and cohomology interpretation,
not an invariant compact descent in this package.
https://arxiv.org/pdf/math/0604588
https://arxiv.org/pdf/math/0601337v1

[3] Steven D. Galbraith, The Weil pairing on elliptic curves over C, 15 February
2011 revision, section 3, page 2. The sign convention in (14) is explicitly
matched to the ordered period basis (1,omega).
https://www.math.auckland.ac.nz/~sgal018/pair-over-C.pdf

[4] Joachim Wehler, Stein Manifolds, LMU lecture notes, Draft Release 4.3,
4 September 2022, Theorem 6.22 (page 206, PDF page 210). Used only for the
vanishing of positive-degree coherent cohomology on the stated Stein cover.
https://www.mathematik.uni-muenchen.de/~wehler/20190530_Stein_Manifolds_script.pdf

[5] Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields,
arXiv:2311.04110v2. Equation (2.13) and the stated fixed pure-cubic example
supply the smoothing convention. Its modulus theorem is not a proof of the
complex comparison. https://arxiv.org/html/2311.04110v2

[6] Retained v0.7.0 proof and source archive, byte-for-byte under prior/.
All new claims are scoped above; neither an underlying classical mechanism
nor its verification is represented as a literature novelty theorem.
