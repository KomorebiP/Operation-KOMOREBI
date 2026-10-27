# Independent audit of the arithmetic normalizer cover

**Normalized claim.** For `K=Q(sqrt(5))`, there is a geometrically
connected smooth projective curve `X_N/K` and a finite map
`pi:X_N -> P^1_K` of degree 1176 and genus 191, constructed from the
projective residual RM system of the explicit generic Frey family.
Every positive primitive solution of `A^3+B^5=C^7` whose residual
rank-two representation is directly congruent to the named form `l`
gives a point `P in X_N(K)` with `pi(P)=-B^5/A^3`. This parameter is
nonzero and different from one. There is also a known boundary
`K`-point above zero, obtained from the unique unramified geometric
point in that fiber.

**Primary verdict: proved as written.** The arithmetic construction
and specialization implication now have concrete proofs, in addition
to the finite-group calculation. This is an abstract cover-existence
and necessary-condition theorem. It supplies neither a defining
polynomial nor the complete `K`-rational-point set, and it does not
exclude the last modular form or the Diophantine equation.

The audit is independent of the author of the frontier note. A further
independent sub-review handled the finite-group scripts, while this
reviewer checked the arithmetic, geometric and specialization bridges.
Its separate record is `work49/notes/last_form_cover_group_audit.md`.
The accepted main proof `last_form.md` and all earlier proofs were
left unchanged. Proof-audit and literature-check workflows were used;
final proofreading was confined to this audit.

## Frozen artifacts

Checked on 2026-09-19 against the author's final frozen frontier note.

| Artifact | SHA-256 |
|---|---|
| `work49/notes/last_form_cover_frontier.md` | `a2036fc5656430cad7075fd991d91dcf42f37f2a6647ac7d712fccdea3d1680a` |
| `work49/notes/last_form_cover_group_audit.md` | `0964a1d67d2f00afc194b7b74de066d52b583a99ca7bad6fc178177354d61b9b` |
| `work49/computations/lastform_monodromy.py` | `5ec88e85d945e0766dbeb71f525341c734943c7effe0862c41fb9466521b785c` |
| `work49/computations/lastform_normalizer.py` | `d4e29c74f6c23860236241430fa0f6fe0afbfaefdf645a4f6eb362d82951577b` |
| `work49/verification/lastform_monodromy_run/result.json` | `babdfbb4f609e8cd14c7727f47c9392fb1efd0eae6059aaec9c2b319d6264458` |
| `work49/verification/lastform_normalizer_run/result.json` | `9532e1563d356e2baa355f74e7f6646fc24e2d03e4e6f62a7c3fa07d45ae3e98` |
| `work49/notes/last_form.md`, antecedent only | `09027c91b714a1a38a5eff7a97af4fe6bdb5d41d0c29b0a72a767be66fbbe873` |

The finite-group sub-review reran both scripts under Python 3.12.14,
obtaining byte-identical outputs. It also independently implemented
the finite-field arithmetic and checked the compatible-pair coverage,
centralizer orbits, generated groups, full normalizer and order-five
fixed-point counts. The computations establish finite group assertions;
the arithmetic conclusions use the separate written argument below.

## Source contract

The geometric and RM source was checked in the exact primary version:
Pacetti--Villagra Torcomian, *On the generalized Fermat equation of
signature (5,p,3)*,
[arXiv:2512.17845v1](https://arxiv.org/html/2512.17845v1), dated
19 December 2025. The cached PDF `/tmp/level_pv25.pdf` has SHA-256
`d5983c0949129942c3510d9c3a8de1fbf8998e4b0e5b5d822ddf94a795048004`.
Section 2.1, equations (4) and (6), supplies the plus system's
geometric local monodromy. Section 7.1, equation (32) and its surrounding
construction, realizes that system by the genus-two family with RM
algebra `K` over the generic base `K(t)`. This review uses those exact
family and representation statements; it does not import the source's
large-prime Diophantine conclusions at residual prime seven.

[Stacks Project, Theorem 58.6.2, tag 0BND](https://stacks.math.columbia.edu/tag/0BND),
parts (1)--(3), was independently inspected on 2026-09-19. It gives
finite etale covers as finite fundamental-group sets, the base-point
conjugacy convention, and compatibility with pullback. It applies to
the connected scheme `U=P^1_K-{0,1,infinity}`. Compactifying by
normalization and using characteristic zero gives the smooth
projective curve. The group-theoretic branch indices then give its
genus by Riemann--Hurwitz.

The previously audited `last_form.md` supplies actual CM realization,
absolute irreducibility of the target residual factor and its exact
identification with `l`. Its CM flag is not used as an arithmetic
input here.

## Dependency graph and obligations

1. The explicit generic family is the source's plus RM family.
2. One stable integral lattice and the source's common monodromy
   relation give the simultaneous residual trace conditions.
3. Exhausting those conditions gives full geometric `PSL2(F_49)`.
4. The relative polarization gives cyclotomic determinant; therefore
   projective arithmetic image is also exactly `PSL2(F_49)`.
5. Its arithmetic kernel gives a regular Galois cover over `K`; the
   normalizer quotient gives the degree-1176 curve.
6. The explicit untwisted specialization dictionary and residual
   simplicity put any solution attached to `l` in the fixed-coset
   locus, hence give a `K`-point of that one quotient.

| Obligation | Status | Reason |
|---|---|---|
| Generic smooth family and source dictionary | Passed | Direct substitutions and discriminant verify the same family over `K(t)`. |
| RM defined over the arithmetic base | Passed source application | The exact source identifies the generic RM algebra over `K(t)`, not merely over an algebraic closure. |
| Integral simultaneous monodromy | Passed | A single stable lattice preserves the common product relation; the order-five and order-three reductions prevent the unipotent from disappearing. |
| Exhaustive geometric image computation | Passed | All 96 trace-compatible lifts are covered by four centralizer orbits, each generating the full group. |
| Generic determinant | Passed | A trace-refined alternating pairing proves it directly over the function field. |
| Arithmetic descent and regularity | Passed | Arithmetic image is contained in the same group already surjected onto geometrically. |
| Normalizer size and conjugacy | Passed | The order is 50; an outside-PSL normalizer element repairs any outside-PSL conjugator. |
| Degree and genus | Passed | Complete cycle types give degree 1176 and genus 191. |
| Specialization on the chosen lattice | Passed on the stated `l` branch | The target is absolutely irreducible, so equality of semisimplifications upgrades to the required actual rank-two isomorphism. |
| Rational-point implication | Passed | The specialization image fixes a coset in `G/N`. |
| Boundary point above zero | Passed | It is the only geometric point of ramification index one in that fiber. |
| Defining equation or complete rational-point enumeration | Out of scope | Neither is asserted or computed. |

## Exact family and integral specialization

Put `A_t=-t^3`, `B_t=t^2` and

`C_t: Y^2=X^6+10t^2 X^3-12t^3 X+5t^4`.

The discriminant is a nonzero constant times `t^18(t-1)^2`.
Consequently the projective genus-two curve and its Jacobian form
smooth proper families over `U`. With `x=t/X`, `y=tY/X^3`, direct
expansion gives

`y^2=5x^6-12x^5+10t x^3+t^2`,

the exact source equation. A birational map between these smooth
projective curves is an isomorphism; the apparent chart denominators
do not introduce a quadratic twist.

For a positive primitive solution, let `t_0=-B^5/A^3` and
`u=A^2/B^3`. Then

`u^3 t_0^2=B`, and `u^5(-t_0^3)=A`.

The scaling `(X,Y) -> (uX,u^3Y)` therefore identifies the specialized
curve with the actual completed-square Frey curve over `Q`. Both `A`
and `B` are nonzero and `t_0<0`, so this is a point of `U`.

The rational RM action extends along the smooth Jacobian family and
commutes with its lisse rational Tate representation. A stable lattice
for the full arithmetic fundamental group gives a lisse integral
system; its fiber at `t_0` is a stable lattice in the specialized
rational RM representation. This assertion does not require the
actual natural Tate lattice to be free over a maximal RM order.

If that specialization is directly congruent to `l`, the target
rank-two residual module is absolutely irreducible by the accepted
local-three argument. Stable-lattice independence identifies the
semisimplification of the fiber of the chosen generic lattice with
that simple module. The fiber itself then has length one and is
isomorphic to it. This is the precise reason lattice dependence does
not obstruct specialization on this branch. No assertion that all
specializations preserve nonsplit extensions is made.

## Simultaneous monodromy and the finite calculation

The local determinant-one matrices of the plus system satisfy a
single product relation `M_0 M_1 M_infinity=I`. On one common stable
lattice, reduction preserves the exact orders five and three at
zero and infinity. If the unipotent at one reduced to identity, the
relation would equate those two incompatible finite orders. Hence
its reduction has order seven.

Taking `A=M_infinity`, `B=M_0` gives

`tr(A)=-1`, `tr(B)=beta`, `beta^2+beta-1=0`, `tr(AB)=2`.

The cyclic reordering is legitimate: `M_infinity M_0=M_1^{-1}`.
These are actual simultaneous lift signs; knowing only projective
orders would not suffice. The separable characteristic polynomial
of `A` allows its fixed rational canonical form over `F_49`.

For that fixed `A`, every possible `B` has the form
`[[x,y],[z,beta-x]]` with `y=z+beta+2-x`. Thus enumerating `x,z`
over `F_49`, for both roots `beta`, loses no pair. The verified
96 possibilities fall into four explicitly computed orbits. Each
representative generates all 58,800 projective determinant-one
matrices. This proves full geometric image, rather than merely
exhibiting one unrelated triangle-group quotient.

## Generic determinant and arithmetic descent

It would be invalid to apply the number-field-only determinant theorem
from BCDF directly with base `K(t)`. The new note instead gives a valid
relative argument.

After identifying the Tate twist with a one-dimensional coordinate
space, the Weil pairing is an alternating form with cyclotomic
multiplier. Rosati fixes the real quadratic RM field: its other
possible involution sends `sqrt(5)` to `-sqrt(5)` and violates
positivity. The pairing is therefore balanced for `K_(7)`.
Nondegeneracy of the field trace gives a unique `K_(7)`-valued
alternating refinement. The displayed trace identity proves
bilinearity in both arguments and nondegeneracy. Galois commutes
with this coefficient field and scales the refinement by `chi_7`.
On a rank-two space its determinant is consequently `chi_7`.

The continuous arithmetic image is compact, so a common stable
`O_(K,7)` lattice exists. Upon reduction, determinants are in `F_7*`.
Those elements are squares in `F_49*`, since their orders divide six
and `F_49*` has order 48. Therefore projective arithmetic image is
contained in `G=PSL2(F_49)`. Its geometric subgroup is already `G`,
so the arithmetic image equals `G` and has no nontrivial constant-field
quotient.

The finite fundamental-group quotient thus defines a Galois cover
`Z -> U` over `K`. Geometric surjectivity makes it geometrically
connected. The quotient by a subgroup `N` is constructed over `K`
directly from this arithmetic cover. There is no separate descent of
an arbitrarily chosen complex cover and no missing arithmetic twist.

## One normalizer quotient suffices

For the target CM Jacobian, seven is inert in `Q(zeta_5)` and its real
subfield has residue field `F_49`. The CM coefficient residue extension
is `F_2401/F_49`. An integral CM lattice may be chosen, and the
previously proved residual irreducibility identifies its reduction
with the target representation. Over the CM base field the action is
multiplicative in `F_2401`; the nontrivial quadratic base automorphism
acts by the coefficient conjugation. Hence the target lies in a
nonsplit Cartan normalizer. Its projective determinant condition puts
it in an order-50 subgroup of `G`.

The PGL normalizer has order 100 and contains an element outside `G`:
the determinant of multiplication by an element of `F_2401*` is its
norm to `F_49*`, and that norm is surjective. All nonsplit normalizers
are PGL-conjugate. If a given conjugator is outside `G`, multiply it
on the right by such an outside-`G` element of the source normalizer.
The product lies in `G` and has the same effect on its order-50
intersection with `G`. Thus there is one `G`-conjugacy class of the
relevant subgroups. Coefficient conjugation also preserves their
type. This resolves the otherwise genuine question of whether a
second quotient or a twist would be required after an arbitrary
representation isomorphism.

## Genus, fixed cosets and the boundary point

For `N` of order 50, the degree is `58800/50=1176`. The checked cycle
types on the left cosets `gN` are:

| Local point | Order | Cycles | Contribution to ramification |
|---|---:|---|---:|
| infinity | 3 | `3^392` | 784 |
| zero | 5 | `1^1 5^235` | 940 |
| one | 7 | `7^168` | 1008 |

The order-three and order-seven actions have no fixed coset because
neither order divides 50. For order five, centralizer size 25 and
intersection of its conjugacy class with `N` of size two give exactly
one fixed coset. This remains true for both order-five trace classes.
The frozen scripts' phrase “right cosets” is a terminology error:
their implemented `gN` and left action are correct. The manuscript
records this correction without changing the old computation hashes.

Riemann--Hurwitz gives

`2g-2=-2*1176+784+940+1008=380`, hence `g=191`.

At `t_0`, the fiber of `Z/N` is the finite `G_K` set `G/N`, with
action through the projective specialization. Image containment in
a `G`-conjugate of `N` is precisely the condition that this action
has a fixed coset. A fixed geometric point of a finite etale
`K`-scheme has residue field `K`. This proves the stated necessary
`K`-rational-point condition.

At the compactified fiber over zero there is exactly one geometric
point of ramification index one, the remaining 235 points having
index five. Because the map and zero are defined over `K`, Galois
preserves those indices and fixes the unique index-one point. It is
therefore a `K`-point. This does not identify other boundary points,
give that point an additional moduli interpretation, or settle the
nonboundary points relevant to positive solutions.

## Remaining gap in the research program

No missing implication remains in this cover-construction theorem.
The unresolved research step is to determine or suitably constrain
the nonboundary `K`-points of this genus-191 curve, especially those
whose image has the primitive power form `-B^5/A^3`. Cartan-normalizer
image is only necessary for the exact residual congruence, and that
congruence is only one required condition for an integer solution.
Neither reverse implication is proved. An explicit cover equation,
point enumeration and global exclusion remain absent.

Proofreading covered the complete new audit. No main proof or frozen
computational input was modified.
