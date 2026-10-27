# Exact monodromy at three and five on the remaining branch

Status: written local proof, awaiting fresh independent review. This calculation
**does not** show unramified seven-torsion after twisting. It proves the opposite
for the natural Jacobian lattice. No conclusion about integer nonexistence is
drawn here.

## Statement and conventions

Let positive pairwise-coprime integers satisfy A^3+B^5=C^7 and suppose 15|C.
Put K=Q(sqrt(5)), D=3(5-sqrt(5))/2, and let nu be the quadratic character
of K(sqrt(D))/K. Let J be the Jacobian of

    Z^2 = f(X) = X^6+10BX^3+12AX+5B^2.

The quadratic twist J^nu is the Jacobian of Z^2=D f(X). Write c_l=v_l(C)
with the ordinary rational-prime valuation. At F_3=K_(3) use v_3(3)=1;
at F_5=K_(sqrt(5)) use v_5^K(sqrt(5))=1, so v_5^K=2v_5.

Then J^nu has split totally toric reduction over both F_3 and F_5.
In the two twin-loop bases, its integral monodromy pairing is

    at F_3: (7c_3-3) I_2;
    at F_5: (14c_5-5) I_2.                         (1)

The constants -3 and -5 are necessary: they come from the nontrivial
depths of the principal clusters, rather than from the discriminant
term C^14 alone. In particular the matrices modulo seven are respectively
4 I_2 and 2 I_2, both invertible.

There are actual exact local Galois sequences

    0 -> mu_7^2 -> J^nu[7] -> (Z/7)^2 -> 0,       (2)

whose restriction to inertia is nontrivial at both places. The inertia
operator has rank two for a suitable tame inertia element. The full
four-dimensional residual Artin conductor at each place is therefore
two. With an integral rank-two RM decomposition, each factor has rank-one
monodromy and conductor exponent one after twisting.

These assertions concern the natural seven-torsion representation of the
Jacobian. A different stable lattice in the characteristic-zero
representation may have a different residual extension. In particular,
this calculation does not obstruct a Ribet lattice change that kills
local monodromy modulo seven.

## Exact-source contract

The cluster definitions and semistability criterion used below are from
T. Dokchitser, V. Dokchitser, C. Maistret and A. Morgan, *Arithmetic of
hyperelliptic curves over local fields*, arXiv:1808.02936v2, 15 October
2018. Definition 1.7 and Theorem 1.8(1),(7),(8), printed p.4, give the
criterion and toric rank. Definitions 1.11--1.12 and Theorem 1.14(3)--(5),
printed pp.5--6, give the homology generators, length pairing and Galois
action. These assertions are proved in the body of that source, in
particular Theorem 9.3 and Theorem 10.3. The project uses the ordinary
normalized discrete valuation of the local base field, not a valuation
renormalized after a ramified extension.

The source was available in the existing local scratch cache and read
directly. Its PDF SHA-256 is
`f46f20a4adf8215c566252779a3b4b9028890df36013c7b747fcec2c0313f3a5`.
The previously downloaded PDF and its text extraction agree on the exact
version. A fresh web open of its versioned abstract URL failed; that
failure supplies no evidence and does not invalidate the retained source.
[Versioned primary manuscript](https://arxiv.org/pdf/1808.02936v2).

To identify the graph length pairing with the valuation of the analytic
period matrix, use M. Baker and J. Rabinoff, *The skeleton of the
Jacobian, the Jacobian of the skeleton, and lifting meromorphic functions
from tropical to algebraic curves*, arXiv:1308.3864v1, 18 August 2013,
Theorem 2.9 and Remark 6.7. The retained PDF has SHA-256
`acf7cd5977d24d8561718b33c0d855996f131cbb075189eedff6bdb9a64e6010`.
This comparison is applied only after proving split semistability below.
[Versioned primary manuscript](https://arxiv.org/pdf/1308.3864v1).

This is a verification of source applications. No novelty claim or global
literature-completeness claim is made.

## The common limiting polynomial

Put

    g(X)=X^2+X-1,     h(X)=X^2-2X+5,
    F_0(X)=X^6+10X^3-12X+5=g(X)^2 h(X).

For either root r=(-1 +/- sqrt(5))/2 of g, direct calculation gives

    h(r)=3(2-r)=3(5 -/+ sqrt(5))/2,
    g'(r)=2r+1=+/-sqrt(5).

Writing z=X-r, the nonzero coefficients of F_0(r+z) are

| power of z | coefficient |
|---:|---|
| 2 | 5 h(r) |
| 3 | 10(4r-1) |
| 4 | 15(1-r) |
| 5 | 6r |
| 6 | 1 |

The two choices of h(r) have ratio phi^2, where
phi=(1+sqrt(5))/2. Thus D h(r) is a square in K for both choices of r.

## Three-adic cluster picture

Primitivity makes A and B units at three. There is a unique fifth root
u of -A in Q_3: fifth powers permute F_3^*, and the Hensel derivative
5u^4 is a unit. Put beta=B/u^3. Then

    beta^5=1+C^7/u^15,     beta=1+epsilon,
    v_3(epsilon)=7c_3.

The last equality follows by factoring beta^5-1; the second factor is
5 modulo three and is a unit. Scaling X=u x and Z=u^3 z gives

    F(x)=F_0(x)+10 epsilon x^3+10 epsilon+5 epsilon^2.

The roots r of g lie in F_3=Q_3(sqrt(5)). They are distinct modulo
three. For either root, r, r-1 and 2-r are units. Hence the valuations
of the coefficients of F(r+z), starting with degree zero, are

    (7c_3, 7c_3+1, 1, 0, 1, 1, 0).             (3)

Indeed the constant perturbation is 20r epsilon+5 epsilon^2 and the
linear perturbation is 30r^2 epsilon. The other perturbations have
strictly higher valuation than their displayed limiting coefficients.

The lower Newton polygon has vertices

    (0,7c_3), (2,1), (3,0), (6,0).

It follows that two roots lie at distance valuation

    d_t=(7c_3-1)/2

from r, one further root lies at valuation one, and the other three
lie at valuation zero. The first side has residual polynomial of the
form a+b Z^2 with a,b nonzero. Since the residue characteristic is
three, its two roots are distinct after an unramified extension and
a possible quadratic uniformizer extension. Thus the two close roots
have mutual distance exactly d_t, not merely distance at least d_t
from r. This gives a twin t in a principal cluster s of size three
and depth d_s=1. Repeating at the other root of g gives the other
disjoint principal triple and its twin. Their parent is the full
six-root cluster of depth zero.

In particular the relative twin depth is

    delta_t=(7c_3-3)/2.                          (4)

The two triple clusters are defined over F_3, and each can be factored
into a quadratic twin factor and one linear factor over an unramified
extension. Over the maximal unramified field the only possible further
root ramification is quadratic. This follows either from these
quadratic factors or from the distinct binomial roots just described;
there is no additional inseparable residual polynomial. All proper
clusters are inertia-invariant.

For the twisted polynomial D F, the leading-coefficient valuation is
one. On either principal triple,

    nu_s = v_3(D)+3d_s = 1+3=4.

The full root cluster has exactly two children and is not principal.
Consequently the cluster semistability criterion is satisfied over
F_3 itself: the roots have ramification index at most two, principal
depths are integral, and the principal nu_s are even. Each triple
contains only its even twin and one odd singleton, so both normalized
components are rational. The dual graph has two loops joined by a
bridge. Each loop has length 2delta_t=7c_3-3. The bridge contributes
nothing to H_1 or its length pairing.

## Five-adic cluster picture

There is a unique cube root u of B in Q_5, by the same Hensel argument
using the bijection x -> x^3 on F_5^*. Put alpha=A/u^5=-1+epsilon.
Then

    alpha^3+1=C^7/u^15,
    v_5(epsilon)=7c_5,     v_5^K(epsilon)=14c_5.

Here alpha^2-alpha+1 is a unit modulo five. After scaling the curve,

    F(x)=F_0(x)+12 epsilon x.

Work over F_5=Q_5(sqrt(5)) with its integral normalized valuation.
For r a root of g, r, 1-r and 4r-1 are units, whereas

    v_5^K(g'(r))=1,     v_5^K(h(r))=1.

The valuations of F(r+z) are consequently

    (14c_5, 14c_5, 3, 2, 2, 0, 0).             (5)

The lower Newton polygon has vertices

    (0,14c_5), (2,3), (5,0), (6,0),

with the degree-three point on the middle side. Its first segment
has distinct quadratic residual roots because five is odd. Hence
there are two roots in a twin t_r at mutual depth

    d_t=(14c_5-3)/2=7c_5-3/2.

The two centers r_+,r_- have distance valuation one. The two twins
are therefore disjoint and have mutual distance one. The middle
side supplies the remaining root in the five-root cluster, also at
distance one from both centers, while the last root has distance
zero from that cluster. To see the singleton assertion without
assuming that a repeated residual cubic separates, factor around
both close twins; the remaining two roots deform the two distinct
roots of h, whose discriminant -16 is a unit at five. The h root
near the twins has distance one from each r because h(r) has
valuation one and h' at that h root is a unit. Its perturbation has
strictly higher valuation. Thus the principal five-root cluster s
has depth one and exactly two twin children and one singleton.

Each twin is stable under G_(F_5), because its center r belongs to
F_5 and its disc is disjoint from the other twin disc. Over the
maximal unramified field their root splitting needs ramification
degree at most two, as for the two quadratic factors at three.

The relative twin depths are

    delta_t=(14c_5-5)/2.                         (6)

Since v_5^K(D)=1, the sole principal cluster has

    nu_s = 1+5d_s = 6.

The full six-root cluster again has exactly two children and is
not principal. The semistability criterion therefore holds already
over F_5. The unique principal normalized component is rational,
and the two twins supply its two loops. Their lengths are
2delta_t=14c_5-5.

## Splitness and the pairing

The twins at either place are individually Galois-invariant. For a
twin t_r, the square class defining its graph character is

    D product_{root a outside t_r} (r-a).

Relative to the limiting polynomial, this differs from

    D g'(r)^2 h(r)                              (7)

by an element of 1+the maximal ideal. One can use r as the twin
center: the perturbation moves each outside root by valuation
strictly greater than its distance to r. For a root in the other
twin this uses its own first Newton-polygon segment; for a singleton
it follows from the simple-root Hensel factorization. Every element
of 1+the maximal ideal is a square at odd residue characteristic.
Expression (7) is a square in the base field, because D h(r) is a
square and g'(r)^2 is visibly a square. The graph characters are
therefore trivial, including arithmetic Frobenius. This proves
splitness, not only trivial inertia.

In the source's notation each twin has t^*=t because its parent is
not ubereven. The two distinct twins thus give independent generators
of H_1, their cross pairing is zero, and their diagonal pairing is
2(d_t-d_parent). Equations (4) and (6) prove (1) directly from
Theorem 1.14(3)--(5). No assumption that a discriminant valuation
alone determines a period matrix is made.

By the graph/analytic comparison, choose compatible torus-character
and period-lattice bases for the split uniformization J^nu=T/Y.
The period entries q_ij then satisfy

    v(q_ij)=n_v delta_ij,

where n_v is the corresponding integer in (1). The uniformization
is defined over the local base field because both lattices have
trivial Galois action.

## Actual residual inertia and the failed unramified shortcut

The analytic uniformization gives (2) by taking seventh roots of
the periods. Since the residue characteristics three and five are
different from seven, seventh roots of local units lie in the
maximal unramified extension. To prove this, take a seventh root
of their residue class in the algebraic residue field and apply
Hensel's lemma, whose derivative seven is a unit. Thus the inertia
class of a period is determined by its valuation modulo seven.

For a suitable tame inertia element sigma, the action in the
torus/period basis is

\[
\rho(\sigma)=\begin{pmatrix}I_2&n_vI_2\\0&I_2\end{pmatrix}.       \tag{8}
\]

over F_7, after choosing a generator of mu_7. The mod-seven tame
character is nonzero on sigma. Since n_3=4 and n_5=2 modulo seven,
the off-diagonal block has rank two. Inertia invariants therefore
have dimension two, and wild inertia acts trivially, giving full
Artin conductor exponent two. Rank-two RM factors have one
invariant dimension and conductor one.

The initially suggested route “all monodromy lengths are multiples
of seven because the equation contains C^7” fails precisely at the
principal-cluster correction: the lengths are 7c_3-3 and 14c_5-5.
The discriminant valuations do correctly contain 14c_l, but the
fixed factors 3^6 and 5^5 and the nonzero cluster depths cannot be
discarded. Twisting cancels the quadratic graph character; it does
not erase these integral lengths or the residual extension.

Finally, equation (8) is lattice-dependent after reduction. It
cannot be transported unchanged to every Galois-stable lattice
inside V_7(J^nu). Only the characteristic-zero monodromy rank is
lattice-independent. Any global argument using a deliberately
reversed residual extension must re-evaluate its local extensions
on that chosen lattice.

## Orientation of a reducible natural RM representation

Assume the integral rank-two RM representation is globally reducible
and its semisimplification after twisting is 1 plus the mod-seven
cyclotomic character, as in the inherited character classification.
Then its natural-lattice extension has the orientation

    0 -> chi_bar -> V_bar -> 1 -> 0,

and is globally nonsplit. Indeed, the rank-one nonzero local
monodromy at three makes the toric chi_bar-line the unique local
invariant line. Every globally invariant line must restrict to it.
The two local characters are distinct, since arithmetic Frobenius
at the norm-nine prime has chi_bar-value 2 modulo seven. The global
subcharacter is consequently chi_bar, and local nonsplitting
already prevents global splitting. A reverse extension therefore
cannot be the same natural residual lattice.

## Scope of exact verification

The companion exact symbolic check works in Q[r]/(r^2+r-1). It
checks the limiting factorization, all translated coefficients,
the perturbation formulas, and the square-class identity relating
the two radicands. It also checks the two displayed Newton polygons
for c=1 through 100, as a finite error check on formulas whose
uniform inequalities are proved above. These computations do not
prove the geometric source theorems or the uniform local claim.

Self-proofreading covered the entire new note. It found no remaining
notation inconsistency or uniquely forced mathematical-token correction.
The display in (8) was rendered as a matrix. The independent mathematical
audit is tracked separately from this editorial check.
