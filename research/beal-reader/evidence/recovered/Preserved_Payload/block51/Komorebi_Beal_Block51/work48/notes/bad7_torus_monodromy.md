# The remaining bad-seven branch: torus, monodromy and residual extension

Status: written local proof with primary-source inputs checked on
2026-09-19. The Frobenius value forced by the existing global argument is
**compatible** with this local structure. This note does not prove
irreducibility or eliminate a Diophantine solution.

## Contract and source boundary

Let positive pairwise-coprime integers satisfy A³+B⁵=C⁷, assume 7|C, and
let J be the Jacobian of

\[
y^2+(x^3+B)y=2Bx^3+3Ax+B^2.
\]

Write F=Q₇(√5)=K₍₇₎, R=O_F, k=F₄₉, and c=v₇(C)>0, with v₇(7)=1.
Let χ be the mod-seven cyclotomic character and ψ the unramified quadratic
character of G_F, so ψ(Frob₄₉)=−1. Frobenius is arithmetic throughout.
The predecessor's canonical scope has hash
`fb939ab48ffd726781aabd41328e7a31c594502cc9585c22e7a4df0b4d7448a1` at
`work47/notes/mod7_good_reduction_irreducibility.md`.

The new conclusions are:

1. J has toric rank two over F; both geometric loops have Frobenius −1.
2. The integral monodromy pairing, in the two loop basis, is 7c·I₂.
3. There is an actual exact sequence of G_F-modules

\[
0\longrightarrow(\mathbf F_7(\chi\psi))^{\oplus2}
\longrightarrow J[7](\overline F)
\longrightarrow(\mathbf F_7(\psi))^{\oplus2}
\longrightarrow0.                                      \tag{1}
\]

4. J[7] has a finite flat R-model. This is a constructed model of its
generic torsion representation, not the torsion of a good-reduction
abelian scheme: J has bad reduction here.
5. Every one-dimensional unramified local composition factor of J[7]
over Fbar₇ is ψ. Thus its Frobenius₄₉ value is exactly −1.

For uniformization we use Baker–Rabinoff, *The skeleton of the Jacobian,
the Jacobian of the skeleton, and lifting meromorphic functions from
tropical to algebraic curves*, arXiv:1308.3864v1 (18 August 2013).
Section 4.1 gives the canonical analytic uniformization and its torus;
§4.5 and Proposition 4.7 give the Jacobian's lattice identification and
principal-polarization compatibility. Theorem 2.9, proved in §6, equates
the period valuation pairing with the edge-length pairing; Remark 6.7
states the matrix interpretation for totally degenerate Jacobians. These
statements concern split semistable reduction; below we apply them after
an unramified quadratic extension and use their canonical constructions
for descent. [Versioned primary manuscript](https://arxiv.org/pdf/1308.3864v1).

For finite-flat descent we use Raynaud, *Schémas en groupes de type
(p,…,p)*, BSMF 102 (1974), Theorem 3.3.3 and Corollary 3.3.6(1), printed
p.268. For mixed-characteristic DVRs with e<p−1, a finite commutative
p-primary generic group has at most one finite-flat model; generic
morphisms extend uniquely, with flat kernels and cokernels. Here e=1<6,
including after unramified extension. [Primary source](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf).

The source PDFs were checked directly but not retained in a local cache;
no PDF-byte hash is claimed. The project-cache lookup for the versioned
Baker–Rabinoff identifier found no existing cache. This is an exact-source
application check, not a novelty search.

## Nodes and Frobenius over F₄₉

Completing the square gives z²=f(x), where

\[
f(x)=x^6+10Bx^3+12Ax+5B^2,\qquad
\operatorname{disc}(f)=2^{12}3^65^5C^{14}.
\]

The identity and semistable stable model are already proved in
`work46/mod7_oddC_written_proof.md`. Since A and B are 7-adic units, the
residue u=A²/B³ satisfies u³=B and u⁵=−A. The change x=uX, z=u³Z in the
special fiber gives

\[
Z^2=g(X)^2h(X),\quad g=X^2+X-1,\quad h=X^2-2X+5.
\]

The discriminants of g,h and their resultant are 5,−16,45, all units
at seven. There are two ordinary nodes, indexed by the roots r,s of g.
The normalization W²=h(X) is rational. The dual graph is one vertex with
two loops. Both nodes are k-rational because 5 becomes a square in k.

At r, the two tangent branches are split precisely when h(r) is a square
in k: the additional factor g′(r)² is already a nonzero square. Since
r²=1−r, we have h(r)=6−3r. Frobenius₇ interchanges r,s, and

\[
N_{k/\mathbf F_7}(h(r))=(6-3r)(6-3s)=45\equiv3\pmod7.
\]

An element of k× is a square exactly when its norm to F₇ is a square;
this follows immediately by raising to the powers 24 and 3. The value
3 is a nonsquare in F₇. Both nodes are therefore nonsplit over k.
Arithmetic Frobenius₄₉ fixes each node and reverses its two branches, so
it acts as −I₂ on H₁(Γ,Z) and its dual. Inertia acts trivially.

Let L/F be the unramified quadratic extension. The nodes split over its
residue field F₂₄₀₁, and all normalization components are rational.
Thus the split toric uniformization over L has rank two and no abelian
good-reduction part. Its character lattice and, through the canonical
principal polarization, its period lattice have the descent action −I₂
of Frobenius₄₉. This identifies both lattices over F as Z(ψ)². Resolving
a stable node only subdivides its loop and preserves this action.

## Exact thickness and monodromy pairing

The two nodes are conjugate over Q₇, since g has nonsquare discriminant
5 modulo seven and the scaling u lies in F₇. Consequently their
thicknesses agree. Here is a discriminant proof of their common value.

Over the unramified quadratic field F, Hensel factorization separates
the two double-root residue discs into monic quadratic factors f₁,f₂,
and separates the two remaining simple roots into linear factors.
All cross-resultants are units. Write D_i=disc(f_i). Then

\[
v_7(D_1)+v_7(D_2)=v_7(\operatorname{disc}(f))=14c.
\]

The nontrivial automorphism of F/Q₇ interchanges the two quadratic
factors, so the two valuations coincide. Hence v₇(D_i)=7c.

To check that this is the curve-node thickness, write the local equation
as z²=f_i(x)U(x), with U a unit. Over a strict henselization U has a
square root. Dividing z by it and completing the square in the monic
quadratic f_i gives an equation equivalent to uv=unit·D_i. Since 2 is
invertible, its thickness is exactly v₇(D_i), with no factor of two.
Therefore both edges have length n=7c in the normalization v₇(7)=1.

The two loops have no common edge. Their edge-length pairing is
diag(n,n). Applying the cited monodromy comparison over L gives

\[
\boxed{\langle\ ,\ \rangle_{\rm mon}=7c\,I_2.}             \tag{2}
\]

In compatible character/period bases, if q_ij are the multiplicative
period entries in L×, equation (2) means

\[
v_7(q_{ij})=7c\,\delta_{ij}.                              \tag{3}
\]

This determines valuations of the extension parameters, not their unit
classes or the splitting of the torsion extension.

## The actual p-torsion sequence

Over L the analytic uniformization is T^an/Y, with T=G_m² and Y≅Z².
For any positive integer m, including m=7 in residue characteristic
seven, its generic characteristic-zero geometric points give

\[
0\longrightarrow T[m]\longrightarrow J[m]
\longrightarrow Y/mY\longrightarrow0.                    \tag{4}
\]

This does not invoke a prime-to-residue-characteristic Tate-module
theorem. To see (4) directly, lift an m-torsion point to t in T; then
t^m is a period, whose class modulo Y^m is independent of the lift.
Every period has an mth root in the algebraically closed field. The
kernel is T[m], because Y is torsion free. Thus (4) is exact. The
uniformization is canonical and functorial, so the construction descends
with its Galois action to F.

For m=7, the torus character-lattice action −I₂ gives T[7]=(χψ)²,
while Y/7Y=ψ². This proves (1). Equivalently, for a suitable F₇ basis,

\[
\rho_{J[7]}(\sigma)=
\begin{pmatrix}
\chi(\sigma)\psi(\sigma)I_2 & B(\sigma)\\
0 & \psi(\sigma)I_2
\end{pmatrix},
\]

where B is the extension cocycle. Over L, its four Kummer parameters
are the classes [q_ij] in L×/(L×)⁷. Equation (3) removes their valuation
parts: these classes are represented by the units

\[
u_{ij}=q_{ij}\,7^{-7c\delta_{ij}}\in O_L^\times.             \tag{5}
\]

Neither (2) nor (5) says that B vanishes. In particular, divisibility of
the monodromy pairing by seven does not prove that J[7] is unramified:
even its torus constituent χψ has nontrivial inertia.

At the residue-characteristic prime, χ(Frob) is not the integer 49
reduced modulo seven. It depends on the lift of the unramified
Frobenius. Only the unramified constituent ψ has the canonical value
used here. Transplanting the prime-to-seven eigenvalues −49 into J[7]
would wrongly make an invertible Galois action have zero eigenvalues.

## A finite-flat model, constructed from the unit parameters

Put S=O_L. For a=(a₁,a₂) in {0,…,6}² define

\[
\mathcal G_a=
\operatorname{Spec} S[z_1^{\pm1},z_2^{\pm1}]/
\left(z_i^7-\prod_{j=1}^2u_{ij}^{a_j}:i=1,2\right).
\]

Each component is finite free of rank 7² over S. On their disjoint union
define multiplication of points (a,z),(b,w) by

\[
r_j\equiv a_j+b_j\pmod7,\quad0\le r_j<7,\qquad
d_j=(a_j+b_j-r_j)/7,
\]

\[
(a,z)(b,w)=
\left(r,\ \left(z_iw_i\prod_j u_{ij}^{-d_j}\right)_{i=1,2}\right).
\]

All multipliers are units. The carry identity proves associativity;
the identity and inverse are immediate from the same formula. Taking
the seventh power gives z_i⁷/∏u_ij^{a_j}=1, so this commutative group
scheme is killed by seven. Its kernel over a=0 is μ₇² and its quotient
is the constant group (Z/7)². Its total rank is 7⁴.

Its generic fiber is J[7]_L: the representative (a,z) maps to the class
in T/Y with coordinates z_i·7^{ca_i}; its seventh power is the period
∏_j q_ij^{a_j}. The carry law agrees with multiplication modulo Y.

The original F-defined generic group supplies Galois descent data on
this finite-flat model over S. Raynaud's fully faithful generic-fiber
functor, with e=1<6, extends each descent isomorphism uniquely. The
cocycle condition follows by uniqueness. Since S/R is finite étale,
effective descent for affine finite locally free schemes produces the
claimed finite-flat R-group scheme.

The same construction and schematic closure/quotient argument gives
finite-flat models for generic subquotients of powers of J[7]. One must
still identify a particular residual RM representation with such a
subquotient. Lattice independence by itself identifies only residual
semisimplifications; it does not identify arbitrary nonsplit extensions.
For an absolutely irreducible global residual RM constituent, the
composition-factor/subquotient argument suffices, with a finite
coefficient extension handled by restriction of scalars and powers.

## Exact consequence for the global reducibility route

Because F/Q₇ is unramified, χ|I_F has order six. The only unramified
characters among the local composition factors in (1) are therefore
copies of ψ. This remains true after any finite coefficient extension
or passage to subquotients. Consequently the globally selected
unramified constituent ν in the predecessor, if it exists, satisfies

\[
\boxed{\nu|_{G_F}=\psi,\qquad\nu(\operatorname{Frob}_{(7)})=-1.}
\]

For 14|C this agrees exactly with the independent calculation at two
and reciprocity in `work47/notes/reciprocity_two_seven.md`. It supplies
no contradiction. It is also compatible with A³B≡−1 mod7, which follows
directly here from A³+B⁵≡0 and A,B≠0 mod7.

The obstruction to finishing this route is not an unknown sign of
Frobenius at seven. The sign is forced and is the required one. A new
global obstruction must distinguish the remaining global characters or
control extension data that (1) allows; the unit classes in (5) have not
been calculated. No splitting, irreducibility, modular attachment, or
nonexistence conclusion is inferred from this local computation.

## Exact computational check and review scope

`work48/computations/bad7_local.py` checks the two F₄₉ node factors by
both a square enumeration and the Euler criterion, the integral
normalized polynomial identity, all six nonzero residue pairs solving
A³+B⁵=0 over F₇, and all 343 scalar carry triples. Its contract and
version-two run manifest are in `work48/computations/bad7_contract.json`
and `work48/verification/bad7_run/manifest.json`. These finite checks do
not prove any cited geometric theorem or the global inference.

The written proof was self-reviewed for the factor-of-two in thickness,
Frobenius convention at p=7, the difference between a torsion quotient
and a submodule, residual lattice scope, and effectiveness of the
unramified finite-flat descent. A fresh independent review has not yet
been completed. Conservative proofreading of this new file found no
remaining notation or cross-reference error; no predecessor was edited.
