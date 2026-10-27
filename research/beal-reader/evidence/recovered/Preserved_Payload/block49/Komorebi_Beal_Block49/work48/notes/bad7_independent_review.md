# Independent audit of the bad-seven uniformization argument

Reviewed on 2026-09-19 by the level-lowering reviewer, independently of
the author of the local proof. The reviewed file is
`work48/notes/bad7_torus_monodromy.md`, SHA-256
`8c970f3e4cf00b0fd437394b86984c6121d7ddb0bd293ffdbbcc5640c2930508`.
No predecessor or reviewed proof was edited for this audit.

**Verdict:** the full-Jacobian finite-flat conclusion is valid under the
stated primitive-solution hypotheses and the cited uniformization and
finite-flat theorems. I found no missing substantive local input. Two
routine details are supplied below: the rational-point hypothesis of
Baker–Rabinoff Proposition 4.7, and a precise passage from analytic
uniformization to algebraic seven-torsion. The proof does not establish
splitting of the residual extension, crystallinity of the original Tate
module, or global irreducibility.

## Exact claim and dependency boundary

Assume positive pairwise-coprime integers satisfy A³+B⁵=C⁷ and 7 divides
C. Put c=v₇(C), F=Q₇(√5), and let J be the displayed genus-two
Jacobian. The audited conclusions are:

| Claim | Audit result |
|---|---|
| Stable special fiber has two nonsplit nodes over F₄₉ | Verified from the equation |
| Frobenius₄₉ acts by −I₂ on both relevant lattices | Verified using graph action and the canonical polarization |
| Both node thicknesses equal 7c | Verified by Hensel factorization and the local quadratic equation |
| Period valuation matrix is 7cI₂ | Valid application of the cited monodromy comparison |
| Actual sequence 0 → (χψ)² → J[7] → ψ² → 0 | Valid, including extensions and residue characteristic seven |
| Full J[7] has a finite flat O_F-model | Verified by the explicit unit construction and unramified descent |
| Any unramified one-dimensional local composition factor equals ψ | Follows from the sequence and order six of χ on inertia |

Here ψ is unramified quadratic and χ is the residual cyclotomic
character. These statements require no global residual irreducibility
assumption. The final transfer to a chosen residual RM representation
has the separate lattice qualification discussed below.

## Sources actually inspected

Baker–Rabinoff, arXiv:1308.3864v1, dated 18 August 2013, was inspected
as an exact-version PDF. Its SHA-256 is
`acf7cd5977d24d8561718b33c0d855996f131cbb075189eedff6bdb9a64e6010`.
The relevant locators are §4.1, equations (4.1.1)–(4.1.4), printed
pp.8–9; §§4.5–4.6 and Proposition 4.7, pp.10–11; Theorem 2.9 and its
proof, pp.15–16; and Remark 6.7, p.16. They provide split semistable
uniformization, the canonical Jacobian lattice identification, and the
valuation/edge-pairing comparison. Section 4 allows an arbitrary
complete non-Archimedean ground field; algebraic closedness is imposed
later in §7, which is not being used here.
[Versioned primary source](https://arxiv.org/pdf/1308.3864v1).

Raynaud, *Schémas en groupes de type (p,…,p)*, BSMF 102 (1974),
Theorem 3.3.3 and Corollary 3.3.6(1), printed p.268, were inspected in
the primary scan. The bound is e<p−1, and the statements apply to
finite commutative groups killed by a power of p. They are not confined
to rank-p groups or to groups already carrying a finite-field action.
Strict henselianity is not a hypothesis of these statements; it occurs
in the following Corollary 3.3.7. Thus O_L, with e=1<6, is covered.
[Primary scan](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf).

This was an exact application audit, not a novelty search. The existing
predecessor and the exact local computation script were also read.
Their assertions were not substituted for the mathematical checks below.

## Geometry and exact thickness

Primitivity and 7|C imply that A and B are seven-adic units. In the
residue field u=A²/B³ satisfies u³=B and u⁵=−A. Direct expansion gives

\[
(X^2+X-1)^2(X^2-2X+5)=X^6+10X^3-12X+5.
\]

This verifies the normalized special-fiber equation. The two double
roots and two simple roots are distinct: the two discriminants are 5
and −16, and the cross-resultant is 45. At infinity, monicity and
degree six give two distinct smooth rational points. The normalization
W²=X²−2X+5 has genus zero and rational points at infinity. Consequently
there is one geometrically rational component, with four distinct
preimages of the nodes; it is a stable genus-two fiber.

For a root r of X²+X−1, the tangent square class is h(r)=6−3r.
Its norm to F₇ is 45≡3. If t∈F₄₉×, then
N(t)³=t²⁴, so this norm is nonsquare precisely when t is nonsquare.
Each node is therefore nonsplit over F₄₉. Frobenius₄₉ fixes each node
and swaps its branches. This reverses both loop orientations; it does
not permute the two loops. The unramified quadratic extension L/F
splits the branches. Its normalized component is already rational, so
the resulting reduction is split and totally toric.

The thickness argument also checks out. The simple roots split over
F₄₉ since every F₇× element becomes a square there. Hensel factorization
over O_F therefore has two monic quadratic factors and two linear
factors. All cross-resultants are units. Conjugation over Q₇ exchanges
the two quadratic factors by uniqueness of Hensel factorization.
Writing their discriminants D₁,D₂, the displayed global discriminant
gives v(D₁)+v(D₂)=14c, hence v(D₁)=v(D₂)=7c.

To test the possible factor-of-two error, write a local quadratic as
x²+ax+b and absorb the complementary unit by an étale square root.
The equation becomes

\[
w^2=(x+a/2)^2-D_i/4.
\]

Thus (w−x−a/2)(w+x+a/2)=−D_i/4. Since 2 is a unit, the node's
thickness is v(D_i), not half that value. Resolving the node subdivides
the edge into 7c unit edges and leaves its total length unchanged.
The two loop cycles share no edges, giving exactly 7cI₂.

## Uniformization and the actual seven-torsion

Proposition 4.7's hypothesis X(L)≠∅ is satisfied by either rational
point at infinity identified above. The character and period lattices
are identified through the canonical principal polarization, so their
identifications respect the original F-descent. Both have the graph
action ψ². The cited comparison therefore yields periods q_ij∈L×
with v(q_ij)=7cδ_ij. There is no extra ramification scale: L/F and
F/Q₇ are unramified and v(7)=1 throughout.

One can make the analytic/algebraic torsion step completely explicit.
For every a∈{0,…,6}², take all seventh roots in the split torus of the
period q^a. Their coordinates are algebraic over L. Analytification
sends them to J[7]. Distinct a and distinct torus roots give distinct
classes: if their ratio were a period q^b, taking seventh powers and
using injectivity of the period lattice would give a−a′=7b; in the
chosen representative range this forces a=a′ and b=0. There are 7⁴
such classes, which exhaust the characteristic-zero group J[7]. This
also justifies working first over the completed algebraic closure if
desired; no prime-to-seven torsion theorem is involved.

The resulting exact sequence retains the full extension. The lattice
quotient has action ψ², and torus torsion has action (χψ)². Thus its
one-dimensional unramified composition factors are exactly ψ, since
χ|I_F has order six. Its arithmetic Frobenius value is −1. This is a
statement about an unramified constituent, not about assigning the
integer 49 to χ at a prime above seven.

## Direct audit of the unit-Kummer group scheme

Set u_ij=q_ij/7^(7cδ_ij). These are units. Every displayed component
has the S-basis z₁^i z₂^j, 0≤i,j<7, because each defining polynomial
is monic with unit constant term. Hence the disjoint union has rank
49·49=7⁴ and is finite free, not merely generically finite.

The multiplication respects the equations: its ith coordinate has
seventh power

\[
\prod_j u_{ij}^{a_j+b_j-7d_j}=\prod_j u_{ij}^{r_j}.
\]

Associativity follows coordinatewise from the integer carry identity.
For an explicit inverse, put a′_j=−a_j modulo seven in {0,…,6} and
e_j=(a_j+a′_j)/7. Its ith coordinate is
z_i^{-1}∏_j u_ij^{e_j}; the same calculation verifies its component
equations and product equal to the identity. Adding (a,z) seven times
has total carry a and coordinate z_i⁷∏_j u_ij^{-a_j}=1. This checks
that the group scheme is killed by seven, even on the special fiber.
Projection to a is faithfully flat onto the constant group (Z/7)²,
with kernel μ₇².

The proposed generic-fiber map is also correct: t_i=z_i7^(ca_i)
has seventh power ∏_j q_ij^{a_j}. On multiplying two representatives,
division by the period q^d gives

\[
\frac{t_i t'_i}{\prod_jq_{ij}^{d_j}}
=z_iw_i\prod_j u_{ij}^{-d_j}\,7^{cr_i},
\]

exactly the stated carry law. The torsion count above proves that this
is an isomorphism of generic finite group schemes, including their
Galois actions over L.

The F-defined generic group supplies isomorphisms from each conjugate
S-model to this one. Raynaud extends them uniquely; their inverse and
cocycle identities extend by uniqueness as well. Effective finite
étale descent of affine finite locally free schemes then gives a
finite flat O_F-model. This checks existence by construction: Raynaud's
uniqueness theorem alone would not have supplied existence.

## RM transfer, GP Theorem 4.3, and excluded conclusions

Generic subgroups extend by schematic closure, and finite flat
quotients give models of subquotients. After any finite coefficient
extension, tensoring a representation with that coefficient field is,
on underlying F₇-spaces, a direct sum of copies. The required
coefficient action extends by full faithfulness. Therefore an
absolutely irreducible global RM constituent occurring in the residual
semisimplification can be obtained as a subquotient of powers of J[7]
and is finite flat locally. The original note correctly does not claim
that lattice independence identifies arbitrary nonsplit RM reductions
with an actual summand of J[7]. Without an actual subquotient
identification, semisimplification alone does not justify that claim.

Golfieri Madriaga–Pacetti, arXiv:2412.08804v2, Theorem 4.3, printed pp.17–18,
is a separate finite-flat source for the residual hypergeometric
representation. Its condition p∤2ABC concerns the equation
coefficients; these are all one in the present specialization. It
therefore includes 7|C in the present base-variable notation. The
source's bad-reduction proof uses Mumford curves, but does not supply
this note's explicit genus-two period matrix or unit classes.
[Versioned primary source](https://arxiv.org/pdf/2412.08804v2).
The explicit proof audited here does not invoke GP Theorem 4.3, so
accepting that theorem was not used to excuse a gap in the construction.

Neither route by itself proves that the residual extension splits, that
the full residual representation is unramified, or that an arbitrary
rank-two lift has the needed parallel crystalline Hodge type. In
particular, the characteristic-zero Tate module of this bad-reduction
Jacobian is not made crystalline by the finite-flat model of J[7].
The separate weight/lifting argument in `level_lowering.md` remains
necessary for that modular application. The unit classes are
undetermined; the finite computation and this audit supply no global
irreducibility or Diophantine nonexistence conclusion.

No additional computational run was needed: the geometric and group
scheme implications were checked in writing, and the existing finite
script was read without overwriting its run records. This is an
independent written audit, not a formal proof-assistant verification.
