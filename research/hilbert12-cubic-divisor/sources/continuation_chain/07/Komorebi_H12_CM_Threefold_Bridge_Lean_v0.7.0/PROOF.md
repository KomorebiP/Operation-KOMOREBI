# A CM threefold for the cubic unit: its oriented seven-torsion fixed sector

**Version 0.7.0. Base checkpoint: Polarized CM Comparison v0.6.0.**

## Status and target

The original target remains the exact identity U_Gamma=U_alg, equivalently the
polarized reality assertion Im(C_pol U_Gamma^3)=0 with the inherited modulus,
positive-real-part and branch data. This block does NOT prove that assertion.

It constructs an explicit common higher-dimensional geometry for the actual
integer return matrix and the CM point 1/J. On the CM abelian threefold
(C/(Z+Z omega))^3, the omega-twisted fixed group of that matrix is an explicitly
split extension of its ordinary fixed group by the oriented order-seven kernel
E[J]. The point (1,2,4)/J belongs to that kernel, and the original matrix acts
on it by doubling. Complex conjugation exchanges this J sector with the
conjugate-J sector. A separate integral calculation identifies the index-seven
order defect produced by adjoining the conjugate cubic generator.

There are 44 newly compiled and axiom-audited Std-only Lean theorems. They
certify coefficient identities, a universal conductor calculation, and integer
relation lattices. The analytic uniformization and the application of those
identities to complex tori are ordinary proofs below, not hidden formal axioms.
The cumulative source count is 216 including the inherited 172, but no complete
fresh replay of that inherited project is claimed. No novelty claim is made.

## 1. Fixed data and the actual unit matrix

Let omega=exp(2 pi i/3), J=2+3 omega, and Jbar=-1-3 omega. Thus

    omega^2+omega+1=0, J+Jbar=1, J Jbar=7.

Use beta=7^(1/3) omega^2, epsilon=2-beta, and

    tau=(beta^2+2 beta)/15, s=-(beta+2)/15.

The retained arithmetic/analytic return matrix is

    M = [0,1,0; -4,2,15; -1,0,4],    det M=1.

The period row p=(tau,s,1) satisfies p M=epsilon p. This equality uses only
beta^3=7. Its interpretation for the original gamma function, zero anchor,
Stark modulus and arithmetic candidate remains inherited from v0.6.0.

Let O=Z[omega], E=C/O, and A=E^3. Every integer matrix acts on A as a
holomorphic group homomorphism. M and its integer inverse therefore define
an automorphism of this CM abelian threefold. Multiplication by omega on
all three factors also commutes with M.

For comparison, put

    T=[0,0,7; 1,0,0; 0,1,0], B=2I-T,
    D=[0,-2,15; 2,-1,0; 1,0,0].

Then B D=D M and det D=15. D gives an isogeny of CM threefolds of degree
15^2=225. This is NOT an asserted isogeny between the original elliptic
curve E_t and E. On seven-torsion D is invertible because 15 is prime to 7.

## 2. Both fixed-point groups have explicit parameterizations

Write E[a]=ker([a]:E->E) for a nonzero Eisenstein integer a. Define

    h(z)=(3z,3z,z),
    g(z)=((5+omega)z,(-4-5omega)z,z),
    c=3+omega=-omega J.

Direct matrix multiplication gives

    (I-M)h(z)=(0,-6z,0),
    (omega M-I)g(z)=(0,6cz,0).                         (2.1)

These are identities on the universal cover, hence on A. Conversely, the
first and third equations of (I-M)x=0 force x=h(x_2); the remaining equation
is 6x_2=0. For the twisted matrix the first equation gives x_0=omega x_1.
The third then gives x_1=(-4-5omega)x_2 and x_0=(5+omega)x_2. The remaining
equation is 6c x_2=0, equivalent to 6J x_2=0 since -omega is a unit.

Consequently the displayed maps, not merely an abstract cardinality argument,
give isomorphisms of O-modules

    Fix(M)=h(E[6]),
    Fix(omega M)=g(E[6J]).                             (2.2)

Multiplication by a=a0+a1 omega on O has integer matrix

    [a0,-a1; a1,a0-a1],

whose determinant is a0^2-a0 a1+a1^2=|a|^2. Hence E[a] has |a|^2 elements.
In particular

    |Fix(M)|=36,       |Fix(omega M)|=252.

Restriction of scalars and exact integer Smith forms give the stronger
additive descriptions

    Fix(M) ~= (Z/6)^2,
    Fix(omega M) ~= Z/6 x Z/42.                        (2.3)

The determinant identities are

    det(I-M)=6, det(omega M-I)=6J,
    det(omega^2 M-I)=6Jbar.

The orientation is retained: the omega twist selects J, not Jbar.

## 3. A split exact sequence isolates the seven-torsion component

Define the map on the actual fixed groups by

    Phi(g(z))=h(Jz).

It is well defined by the uniqueness of the third coordinate in (2.2).
It is surjective: the section

    h(t) |-> g(Jbar t),   t in E[6],

satisfies Phi(g(Jbar t))=h(7t)=h(t), since 6t=0. Its kernel is g(E[J]).
Thus there is an explicit split exact sequence

    0 -> E[J] -> Fix(omega M) -> Fix(M) -> 0.           (3.1)

The concrete inclusion most directly related to the unit recurrence is

    iota7(z)=(z,2z,4z),     z in E[J].

For Jz=0, 7z=0. Reduction modulo J gives omega=4, so

    g(z)=iota7(2z).

Multiplication by two is invertible on E[J], so iota7(E[J]) is precisely
the kernel in (3.1). The splitting can also be seen from 7+(-6)=1:

    g(z)=g(7z)+g(-6z),     z in E[6J].                 (3.2)

The first term is the chosen lifted ordinary component; the second lies
in the seven-torsion kernel. Neither this sequence nor these maps are
inferred merely from a ratio of determinants.

## 4. The actual CM point is a twisted fixed point

The parameter z_J=1/J is nonzero and has exact order seven in E, because
7/J=Jbar lies in O while 1/J does not. The distinguished point

    P_J=iota7(1/J)=(1/J,2/J,4/J) in A                   (4.1)

therefore has exact order seven. Matrix multiplication gives, for arbitrary z,

    M iota7(z)-iota7(2z)=(0,56z,7z).                  (4.2)

On E[J] this is zero, so M acts as [2]. Moreover

    (omega M-I)iota7(z)
      =Jz (1+omega,26+18omega,7+6omega).               (4.3)

It follows that omega M fixes P_J and the whole cyclic subgroup it generates.
Its two nonzero M-orbits are represented by

    1 -> 2 -> 4 -> 1,      3 -> 6 -> 5 -> 3             (mod 7).

The source-to-companion change has the particularly simple restriction

    D iota7(z)=(56z,0,z)=(0,0,z) on E[J].              (4.4)

Thus the first coordinate of P_J is the exact point used by the retained
Gauss/CM identity

    xi = Omega^2 / wp_O(1/J),       xi^3=J,

and U_alg is the previously constructed rational expression in beta,omega,xi.
That analytic CM evaluation and its branch are inherited; this release does
not re-prove the Weierstrass/Gauss comparison. The new result is its explicit
embedding into the twisted fixed sector of the ORIGINAL return operator.

The finite cubic character in the retained Gauss sum is

    chi(0)=0; chi(1..6)=(1,omega,omega^2,omega^2,omega,1).

It satisfies chi(2a)=omega chi(a), and its Jacobi sum is exactly J. The
checker re-proves both the finite Jacobi sum and the Gauss cubic in the
rational quotient defined by omega^2+omega+1 and Phi_7(zeta).

## 5. Conjugation exchanges the two oriented sectors

Since conjugation preserves O, it acts antiholomorphically on E and A.
The matrix M has integer entries, so

    conjugate(Fix(omega M))=Fix(omega^2 M).

Also conjugate(E[J])=E[Jbar], and conjugate(P_J)=iota7(1/Jbar).
Using omega^2 in place of omega while retaining 1/J is incorrect: none of
the six nonzero points of iota7(E[J]) is fixed by that opposite twist.

The desired scalar comparison Im(C_pol U_Gamma^3)=0 could eventually be
realized by a normalized conjugation-compatible transport between these
oriented sectors. This construction has not supplied that transport identity.

## 6. Why the original conjugation problem needs more than one cubic chart

Let r=7^(1/3)>0, so beta=omega^2 r and bar(beta)=omega r. Write

    K=Q(beta), Kbar=Q(bar(beta)), M0=Q(r,omega).

Then [M0:Q]=6 and K intersect Kbar=Q. Indeed an intersection other than Q
would have degree three, forcing K=Kbar. This would put
bar(beta)/beta=omega^2 in a degree-three field, impossible for a quadratic
irrationality.

Consequently K+Kbar has dimension five over Q. No rational change of the
original three basis coefficients turns the original period field into its
conjugate. Even a scalar homothety alpha K=Kbar is impossible: alpha would
belong to Kbar, and division by alpha would give K=Kbar.

For the actual elliptic parameter t=-(beta^2+2beta)/15,

    225t^3-42t+7=0, beta=2-1/(4-15t).

Thus Q(t)=K. A nonzero holomorphic isogeny E_t -> E_(-bar(t)) would imply
-bar(t) is a rational fractional-linear transform of t, hence in K. It is
also a nonrational element of Kbar, a contradiction. Antiholomorphic
conjugation still exists; the result excludes a holomorphic isogeny, not
conjugation itself or the desired special-value identity.

## 7. The joint integral order has exactly a seven-element defect

Define the explicitly specified orders

    R=Z[r,omega],        A0=Z[beta,bar(beta)].

R is NOT asserted to be the full ring of integers of M0. All conductor
statements in this section are relative to R.

With the R basis (1,omega,r,r omega,r^2,r^2 omega), one has

    A0=Z + rR
       =Z{1,7omega,r,r omega,r^2,r^2 omega}.             (7.1)

Proof: Z+rR is a subring containing beta and bar(beta). Conversely its
six basis elements are generated by them, using

    r=-beta-bar(beta), r omega=bar(beta),
    r^2=beta bar(beta), r^2 omega=beta^2,
    7omega=beta bar(beta)^2.

This proves equality and [R:A0]=7. The quotient R/A0 here is an ADDITIVE
quotient, isomorphic to Z/7, not a quotient ring by an ideal.

Let I=rR. Then

    R/I ~= F7[omega]/(omega^2+omega+1) ~= F7 x F7,       (7.2)

via omega -> (2,4). A0/I is the diagonal F7. For
x=A+Bomega+r(...)+r^2(...), membership in A0 is exactly B=0 mod 7.
The image of J is (1,0); the image of Jbar is (0,1).

Thus the Jacobi pair separates the two residue components which A0 glues.
Their characteristic-zero identities are

    J+Jbar=1, J Jbar=7, J^2-J=-7.                       (7.3)

They are NOT idempotents before reduction; their exact failure is retained.

The conductor (A0:R) equals I. To prove the reverse inclusion, if xR is
contained in A0, both x and x omega lie in A0. Their omega coefficients are
B and A-B, so A and B are divisible by seven. Thus x is in rR. The other
inclusion follows because rR is an R-ideal contained in A0. This universal
coefficient theorem, with arbitrary x and arbitrary y, is compiled in Lean.

Conjugation swaps the two factors of (7.2), and negates the additive defect
R/A0. Each conjugate unit epsilon_j=2-omega^j beta acts on that additive
defect by multiplication by two. The cubic automorphism fixes the defect.
The residue 1 -> 2 -> 4 thus appears both in the order calculation and in
(4.2). No analytic gamma value is inferred from this finite agreement.

Localizing at 15 preserves this seven-primary defect. This matters because
the actual periods have denominator 15, which is invertible modulo seven.
No global identification with the unlocalized period-generated ring is claimed.

## 8. A precise, but not yet instantiated, unit-character rigidity criterion

The units epsilon0=2-beta and epsilon1=2-r are multiplicatively independent.
If epsilon0^m epsilon1^n=1, taking absolute values at the chosen embedding
and its cubic rotation gives -m/2+n=0 and m-n/2=0 after division by the
nonzero log(2-r). Thus m=n=0. The third conjugate is

    epsilon2=(epsilon0 epsilon1)^(-1).

On the exponent lattice Z^2, cubic rotation and conjugation act by

    S(m,n)=(-n,m-n),     K(m,n)=(-m,n-m).

Rotation coinvariants are exactly Z/3, detected by (m+n) mod 3. The formal
core proves image(S-I)=ker((m+n) mod 3), with an explicit inverse witness.
For semilinear phases, reflection imposes K+I instead of K-I. These combined
relations span ALL of Z^2; explicitly

    x=(S-I)(-x_0,0)+(K+I)(-(x_0+x_1),0).                (8.1)

Consequently a unitary character chi on this two-unit group satisfying
chi(Su)=chi(u) and chi(Ku)=overline(chi(u)) is trivial. Rotation alone permits
cube roots; the additional coherent conjugation condition removes them.

This is only a potential rigidity endpoint. No such comparison character
whose value is U_Gamma/U_alg has been constructed in this release. The
abstract implication is not a substitute for the missing analytic transport.

## 9. The projection obstruction: a common threefold is not a descended gamma function

On the universal cover C^3 define

    pi(v)=tau v_0+s v_1+v_2.

It obeys pi(Mv)=epsilon pi(v), so it intertwines the actual unit dynamics.
But pi(O^3) is not a discrete elliptic lattice. It contains both 1 and the
irrational real r: beta=-15s-2 is in it, and bar(beta)=omega^2 beta is also
in it, so r=-beta-bar(beta) is in it. Multiplying by O shows that its closure
is all of C.

Therefore pi does not induce a nonzero homomorphism from A to a compact
elliptic quotient of C. In particular, F(pi(v)) cannot be presumed to be a
meromorphic FUNCTION on A. Descent as a function would make the nonconstant
meromorphic F invariant under a dense period subgroup, which is impossible.
The additional omega-period directions require transformation data, not
silent identifications. The elliptic-gamma literature's higher automorphy
and gerbe framework is relevant background [3], but is not a proof of a
normalized arithmetic comparison on this new model.

## 10. What remains to close the original target

The inherited arithmetic factor is

    C_pol=epsilon a1 a2^3/omega,
    C_pol U_alg^3=|epsilon|^4 |a1|^6 |a2|^4 > 0.

The retained modulus and interval-sign facts turn the unresolved statement

    conjugate(C_pol U_Gamma^3)=C_pol U_Gamma^3

into the original equality. Nothing above proves that statement, the cube
equality, or a root-of-unity constraint on the actual discrepancy.

What has changed is that the same unit M, the CM point 1/J, its conjugate,
and the complementary residue projectors now occur in one explicit geometry.
A next analytic construction should compare the NORMALIZED gamma automorphy
along M with a section/period evaluated on the oriented seven-torsion sector.
It must handle pi's non-descent, the extra Eisenstein lattice directions, and
the scalar zero-anchor. Evaluating a determinant or counting fixed points
alone does not do this. The fixed-point bridge is genuine; that scalar
comparison is still an open arrow.

## 11. Verification and formal scope

- 44 new theorem constants across H12ConjugationOrder (25),
  H12ConjugationRelations (8), and H12CMThreefold (11).
- All are freshly compiled with Lean 4.34.0-rc2, one worker, warnings as errors.
- Bundled Std only: no Mathlib dependency in these new modules.
- Every theorem's transitive axioms are audited against propext,
  Classical.choice, Quot.sound; no admitted proofs, project axioms,
  native_decide, or unsafe declarations. A false integer equality is rejected.
- The complex torus/field interpretation, degree and exact-sequence statements
  are ordinary proofs applying the coefficient identities. Their analytic
  uniformization is not formalized here. No gamma quantity appears in the
  new formal statements.
- Exact Python checks use SymPy rational reductions and a separate integer
  Eisenstein-coefficient multiplication. All 252 twisted points and all
  36 ordinary points are enumerated with rational representatives. The
  degree-seven fibers, section, conjugate sector and unit doubling action
  are verified on the entire finite groups. This is not a bounded proxy
  for the universal conductor theorem, which has its own proof and Lean check.
- No new floating-point or interval gamma comparison is performed. The
  inherited interval evidence remains inherited, not falsely called replayed.

The complete seven-part runtime archive hash matches its pin. Full extraction
hit the execution limit twice; the complete available compiler/Std was used
successfully, and the new verification does not require the incomplete
Mathlib extraction. The inherited 172 sources and evidence are preserved in
prior/v06_source_and_evidence.zip. No fresh 216-theorem cumulative replay is
claimed. Failure details, actual commands, hashes and fresh-extraction replay
are in evidence/ and MANIFEST.json.

## References and attribution boundary

[1] Retained Polarized CM Comparison v0.6.0, preserved byte-for-byte under prior/.
    It supplies the independent algebraic candidate, C_pol, and the precise
    unresolved reality statement, not a proof of that statement.
[2] Retained Gauss/CM note in Komorebi_H12_ALL_MARKDOWN_2026-10-02.md,
    original file PROOF(20261002-154405).md, Sections 3-5. Its exact branch is
    xi=Omega^2/wp_O(1/J)=beta^(-1) sum chi(a) exp(6pi i a/7).
[3] Felder, Henriques, Rossi, Zhu, A gerbe for the elliptic gamma function,
    arXiv:math/0601337; Felder and Varchenko, The elliptic gamma function
    and SL(3,Z) x Z^3, arXiv:math/9907061. Only the general higher-automorphy
    framework is cited here; no external theorem identifying our gamma value
    with the fixed-point construction is claimed or used.
[4] Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields,
    arXiv:2311.04110v2. Product conventions and distinction between proved
    modulus comparison and conjectural complex special values.

All new matrix, residue, and character identities have their elementary proofs
above. This is an advance within the retained research program, not a claim
that the underlying CM torus, order, or finite-character mechanisms are new.
