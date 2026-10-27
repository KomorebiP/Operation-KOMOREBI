# The global cover left by the final CM form

Status: exact finite-group computation, a written geometric-monodromy
translation, and an abstract arithmetic-cover construction, all checked
by a fresh independent review. The finite-group calculation also has
an independent implementation. No defining polynomial or complete
rational-point set has been computed, and the final form has not been
excluded.

## 1. Why the identified CM form suggests a global cover

The preceding note identifies the surviving form with the CM Jacobian

    D: Y^2=X^6+324X,

whose CM field is E=Q(zeta_5) and real coefficient field is K=Q(sqrt(5)).
Seven is inert in E, since its order modulo five is four. Thus the
coefficient residue extension is F_2401/F_49. The residual rank-two CM
representation restricts over E to a character valued in F_2401*, and
Gal(E/K) interchanges it with its F_49-conjugate. Its image belongs to the
normalizer of a nonsplit Cartan in GL2(F_49).

The determinant is the mod-seven cyclotomic character, with values in
F_7*. Every element of F_7* is a square in F_49*, since a^24=(a^6)^4=1.
Consequently the projective image lies in PSL2(F_49). The intersection
of this group with the nonsplit Cartan normalizer has order 50: its
cyclic Cartan part has order 25 and inversion doubles it. Denote this
dihedral subgroup by N.

This supplies a necessary *global image* restriction for a comparison
with the last form. It is stronger information than any fixed finite
list of congruences on A,B,C. Applying it requires an arithmetic cover
realizing the generic projective residual representation.

## 2. The actual geometric monodromy source

The checked version is Pacetti–Villagra Torcomian,
*On the generalized Fermat equation of signature (5,p,3)*,
[arXiv:2512.17845v1, section 2.1, equations (4) and (6)](https://arxiv.org/html/2512.17845v1#S2.SS1).
The source states the characteristic-zero local monodromy conjugacy
classes for the plus motive and their realization in its geometric
adic representation. With q=5,r=3 the three local types have eigenvalues
(zeta_5^s,zeta_5^-s), a nontrivial unipotent pair, and
(zeta_3,zeta_3^-1). Their determinants are one. The geometric base is
the projective line punctured at 0,1,infinity. This exact version was
read on 2026-09-19. No Dickson-classification theorem is imported.

The following is our integral reduction argument. A continuous adic
representation of this profinite geometric group has compact image,
so choose a stable O_(K,7)-lattice. Its reduction is over F_49. The
order-five and order-three eigenvalues keep their exact orders after
reduction, since seven divides neither order. The unipotent local
matrix cannot reduce to the identity: the common global relation
M_0 M_1 M_infinity=I would then identify an order-five element with
the inverse of an order-three element. It therefore reduces to a
nontrivial unipotent element, of order seven.

It matters that this is one common lattice and one triple satisfying
the global relation. Independently conjugating the three local normal
forms would not determine their joint reduction.

Set A=M_infinity and B=M_0. Then AB=M_1^-1, after the usual cyclic
reordering of the relation. In determinant-one lifts the traces satisfy

    tr(A)=-1,   tr(B)=beta,   beta^2+beta-1=0,   tr(AB)=2.

Both beta values are covered below. These simultaneous lift signs come
from the source's actual determinant-one matrices and their common
product relation; projective orders alone would not supply them.
Scalar twists, including the Tate normalization, do not alter the
geometric projective image.

## 3. Exhaustion of every residual trace-compatible pair

Work in k=F_7[s]/(s^2-5), with a+bs encoded as a+7b. A determinant-one
matrix of trace -1 has the separable polynomial X^2+X+1. Every such
matrix is GL2(k)-conjugate to

    A=[[0,-1],[1,-1]].

This is elementary rational canonical form. Conjugation by GL2(k)
normalizes SL2(k) and PSL2(k), so it does not change whether the
projective group is all of PSL2(k). Thus fixing A loses no cases.

Write B=[[x,y],[z,beta-x]]. The trace condition for AB forces

    y=z+beta+2-x.

The determinant condition then tests each of only 49^2 pairs (x,z),
for each beta. The exact enumeration finds 48 matrices for each of
the two roots beta, encoded as 24 and 31. The projective centralizer
of A has order 24. Its explicit conjugation action divides each set
of 48 matrices into two orbits of 24, so four representatives cover
all 96 possibilities.

For each of those four representatives the script generates the
subgroup by breadth-first multiplication and obtains all 58,800
elements of PSL2(F_49). The ambient group is independently constructed
by listing every determinant-one 2-by-2 matrix and dividing by +/-I.
No probabilistic group recognition and no guessed subgroup order is
used. Thus **every residual pair with these trace conditions generates
PSL2(F_49)**.

This finite exhaustion replaces the proposed appeal to Dickson's
classification. Under the cited integral geometric realization it
establishes the generic projective geometric image, not merely the
existence of one unrelated triangle-group quotient.

The result is `verification/lastform_monodromy_run/result.json`; its
validated manifest pins both the script and its finite-field helper.

## 4. Normalizer quotient and its exact genus

The separate script constructs a nonsplit norm-one torus explicitly.
For a nonsquare delta in k it uses matrices

    [[x,delta*y],[y,x]],     x^2-delta*y^2=1,

modulo +/-I. This torus has order 25. Adjoining a determinant-one lift
of the inversion reflection gives a subgroup N of order 50. Closure,
the inversion action, and all group orders are checked exactly.

The script enumerates all left cosets gN and the left action of a
generating triple of orders 3,5,7 with product one. The degree and
complete cycle types are:

| Local order | Cycle type on 1176 cosets | Ramification contribution |
|---|---|---:|
| 3 | 392 cycles of length 3 | 784 |
| 5 | one fixed point and 235 cycles of length 5 | 940 |
| 7 | 168 cycles of length 7 | 1008 |

Indeed [PSL2(F_49):N]=58,800/50=1176. For an independent check of the
unique fixed coset at order five, its centralizer has order 25 and
its conjugacy class meets N in two elements, giving 25*2/50=1. Raising
an order-five element to its square interchanges the two order-five
classes and preserves this fixed-point count. The order-three and
order-seven elements cannot fix a coset because neither order divides
50. Thus these cycle counts apply to both order-five trace classes.

For a connected characteristic-zero cover with this branch-cycle
action, Riemann–Hurwitz gives

    2g-2 = -2*1176 + 784 + 940 + 1008 = 380,
    g = 191.

All three permutations are retained in
`verification/lastform_normalizer_run/result.json`; their product is
checked to be the identity. The generating subgroup is the full group,
so the action is transitive. The group and coset hashes are also retained.

The geometric finite cover attached to the cited residual monodromy
therefore has a **degree-1176 normalizer quotient of genus 191**. An
abstract cover realizing the finite branch-cycle triple also exists by
the characteristic-zero covering correspondence. These statements do
not specify an arithmetic model or its rational points.

## 5. The arithmetic cover and exact specialization dictionary

Let U=P^1_K minus {0,1,infinity}, and define the smooth genus-two family

    C_t: Y^2=X^6+10t^2 X^3-12t^3 X+5t^4.

It is the Frey family with A_t=-t^3 and B_t=t^2. Its discriminant is
2^12*3^6*5^5*t^18*(t-1)^2, so it is smooth over U. The source family in
PV section 7.1, equation (32), is related by

    x_PV=t/X,       y_PV=tY/X^3.

Direct substitution gives exactly PV's
y_PV^2=5x_PV^6-12x_PV^5+10t x_PV^3+t^2. This is an isomorphism of the
smooth projective curves over K(t). The paragraph following (32)
identifies its generic RM algebra over K(t) as K and its motive as the
plus system. Thus its rank-two geometric representation is the one in
sections 2–3 above, in the geometric Tate-module normalization.

For a primitive positive solution put

    t_0=-B^5/A^3,       u=A^2/B^3.

Then u^5 A_(t_0)=A and u^3 B_(t_0)=B. The rational change

    X_actual=uX,       Y_actual=u^3Y

identifies C_(t_0) with the actual completed-square Frey curve. All
variables are nonzero and t_0 is neither zero nor one. No scalar or
quadratic twist is introduced by this dictionary.

Here is the generic determinant argument, which does not apply a
number-field-only determinant theorem to the function field K(t).
The canonical polarization gives a Q_7-valued alternating Weil pairing
on the rank-four Tate module. Rosati fixes the real multiplication:
on a totally real quadratic field the nontrivial involution would give
Tr(sqrt(5)*(-sqrt(5)))=-10, contradicting positivity. Thus the pairing
is balanced for K_(7), in the sense e(av,w)=e(v,aw).
By nondegeneracy of the field trace it has a unique K_(7)-valued
alternating refinement E, characterized by

    Tr_(K_(7)/Q_7)(a E(v,w))=e(av,w)   for every a in K_(7).

This refinement is K_(7)-bilinear and nondegenerate. Galois commutes
with RM and multiplies it by the cyclotomic character, so on the
rank-two K_(7)-module its determinant is precisely chi_7.

Choose one O_(K,7)-lattice stable under the arithmetic fundamental
group pi_1(U). It exists by compactness of the continuous adic image;
one may also take the O_(K,7)-span of a stable Z_7-lattice. Its reduction
defines a representation into GL2(F_49). Projectivization has image
in PSL2(F_49), because its determinant lies in F_7*, all of whose
elements are squares in F_49*. Its geometric image is the full
PSL2(F_49) by the verified trace-pair calculation. Consequently its
arithmetic image is that same group, with no extra constant-field
quotient.

The kernel of this projective representation defines a connected
finite etale Galois cover Z->U over K with group G=PSL2(F_49).
It is geometrically connected because the geometric image is G.
The precise cover correspondence and compatibility with pullback to
the specialization are supplied by
[Stacks Project, Theorem 58.6.2, tag 0BND](https://stacks.math.columbia.edu/tag/0BND),
parts (1) and (3), checked on 2026-09-19. It applies since U is
connected and a geometric base point has been chosen.
Let N be the nonsplit Cartan normalizer containing the projective
image of D[7], using a compatible identification of coefficient
fields. Its GL2 conjugacy class agrees with the explicit normalizer
used in section 4: both arise from multiplication and conjugation in
the unique quadratic extension F_2401/F_49. Such a change of basis
normalizes PSL2(F_49) and preserves the recorded coset cycle types.

In fact these normalizers form a single PSL2(F_49)-conjugacy class,
which is needed for the fixed-coset conclusion below. The full PGL2
normalizer has order 100 and contains elements of nonsquare
determinant: multiplication in F_2401 has determinant its norm to
F_49, and that norm is surjective. Given a PGL2 conjugator of
nonsquare determinant, multiply it on the right by such an element
of the source normalizer. The product lies in PSL2 and induces the
same conjugation of N. This also removes a possible ambiguity from
coefficient conjugation; it does not require choosing a new twist
of the arithmetic cover.

Take Y=Z/N and let X_N be its smooth projective compactification over
K. This constructs the arithmetic quotient directly over K, rather
than guessing a field of definition for a separately constructed
complex cover. It has degree 1176 over P^1_K and genus 191. An explicit
affine equation for X_N has not been calculated.

At a specialization t_0 as above, the chosen generic stable lattice
specializes to a stable lattice in the correct rank-two Frey system.
If the latter is congruent to the last form l, its residual
representation is absolutely irreducible. Stable-lattice independence
therefore identifies the actual specialization of the chosen lattice
with that residual representation: its semisimplification is simple,
so no local extension has been silently discarded. A coefficient
conjugation preserves the nonsplit-normalizer condition.

The projective specialization image is contained in a conjugate of N.
The geometric fiber of Y over t_0 is the G-set G/N. This image fixes
a coset, and a Galois-fixed geometric point of this finite etale
K-scheme is a K-rational point. Therefore every primitive solution
attached to l supplies

    P in X_N(K),       pi(P)=-B^5/A^3 in Q minus {0,1}.

This is an abstract construction and a necessary-condition theorem.
It does not assert a converse from an arbitrary K-point to an integer
solution, or from Cartan-normalizer image to the exact named congruence.

## 6. The remaining global problem

There is one known K-rational boundary point. The branch point t=0 has
order-five inertia, and its cycle type is one fixed point plus 235
cycles of length five. Thus the compactified cover has exactly one
geometric unramified point above zero; all the other points there have
ramification index five. Galois preserves zero and the ramification
index, so it fixes that unique point. Its residue field is K. This
argument identifies a boundary point, without assigning it any further
moduli interpretation.

What remains is to determine the K-rational points of X_N, or prove a
weaker rigidity theorem that excludes those with the primitive power
conditions. No such point set has been determined here. A defining
equation, useful quotients and rational-point algorithms also remain
to be developed.

The relevant image parameter t is rational, but the representation
and its constructed cover are based over K. We do not replace the
required K-rational-point assertion by one about Q-points on an
unverified Q-model. Even a proof of finiteness would not by itself
list or exclude the points. The local restrictions 8778|B and five
not dividing C remain useful conditions on this global problem.

## 7. Reproduction and evidence limits

Both runs use exact finite-field and integer arithmetic, no randomness,
and bounded standard-library Python. Each has a 60-second wall limit,
50-second CPU limit, 1-GiB address-space limit and one-core affinity cap.
Their actual runtime and hashes are in their validated manifests.

The mathematical bridges from the cited monodromy classes to the finite
matrix exhaustion and from the generic family to the arithmetic cover
are written arguments. A second programmer independently implemented
the field arithmetic and verified all 96 compatible pairs, generation
from all four centralizer orbits, the normalizer and the coset counts.
The parent also independently obtained the degree, fixed-point counts
and genus before the run. The fresh arithmetic-cover audit is recorded
separately. No higher-level
Hilbert form computation or rational-point search was performed in this
route. The computation output's original non-claims about the absence
of an arithmetic construction refer to what the scripts establish;
section 5 supplies that construction separately in writing.

Terminology correction: the frozen normalizer script and its contract
call gN "right cosets". The implemented sets gN and their left action
are correct; in standard terminology these are left cosets. This is a
label error in the original computational record, not a change in the
permutations or arithmetic. The retained hashes are not rewritten to
hide that correction.
