# A geometric period obstruction from the marked two-node degeneration

This note proves the new source-to-project comparison. It retains the actual
stable-model and natural-torsion identifications H1,H4. It does not infer an
actual Jacobian from matrices satisfying toric relations.

## B59.4. The paired branch cross-ratio

Let F=K_v with residue field k_v of characteristic q outside{2,3,5,7}.
The normalized twisted nodal special fiber is

    Z^2=delta*g(X)^2*h(X),
    g=X^2+X-1, h=X^2-2X+5, delta=3(5-sqrt5)/2.

The normalization, with Y=Z/g(X), is the conic

    Y^2=delta*((X-1)^2+4).

Write a=phi-1 and b=-phi for the two nodes. Their preimages are

    P_a^+=(a,delta), P_a^-=(a,-delta),
    P_b^+=(b,phi*delta), P_b^-=(b,-phi*delta).

Indeed h(a)=delta and h(b)=phi^2*delta. All four points are distinct:
g has discriminant5, h discriminant-16, and resultant(g,h)=45, all units.
The conic has a rational point and is P^1 over k_v. Its parameter
lambda=(Y-delta)/(X-a), obtained by lines through P_a^+, has marked values

    lambda(P_a^+)=a-1=phi-2, lambda(P_a^-)=infinity,
    lambda(P_b^+)=3phi-6, lambda(P_b^-)=3phi.

Using [A,B;C,D]=(A-C)(B-D)/((A-D)(B-C)), their cross-ratio is

    c=[P_a^+,P_a^-;P_b^+,P_b^-]
     =((phi-2)-(3phi-6))/((phi-2)-3phi)
     =-5+3phi=(-7+3sqrt5)/2=-phi^(-4).

Reversing either node orientation replaces c by c^(-1), which leaves every
7-power test unchanged. Exchanging the two nodes leaves the same paired
cross-ratio. Arbitrary repartition into different node pairs is NOT allowed.

## B59.5. The off-diagonal period reduces to this cross-ratio

The special fiber is a single rational component with two split self-nodes.
Its stable dual graph is a bouquet of two loops. Mumford's Theorem4.20
uniformizes the smooth generic curve over F by a split Schottky group.
Choose the two generators given by the two oriented loops, lifting a vertex
of the universal covering tree. The paths for a generator and its inverse
leave that vertex through the two branches of the corresponding node.
Their attracting/repelling ends specialize to those branch points on the
normalized component. This is the node/component dictionary of Mumford3.3
and the fixed-end construction in the proof of4.20, applied to this bouquet.
Thus the four generator fixed points have distinct reductions, exactly the
four marked points just calculated; generator multipliers have positive
valuation, the two positive node lengths. Node thickness greater than one
changes these multiplier valuations, not the four branch reductions.

After an integral projective coordinate change none of the four reductions
is infinity. This is possible because #k_v>=11. Their pairwise differences
are then units. Apply the product formula in Ichikawa1993 §1.2. For i!=j,
the identity double-coset factor is the cross-ratio of the fixed points.
Every nonidentity factor is 1 modulo the maximal ideal by Proposition2.4:
it belongs to 1+I^length before specializing the multipliers into the
maximal ideal. Corollary2.5 gives convergence, and §2.6 identifies the
specialization with the actual Jacobian periods. The positive-degree terms
vanish on reduction, so in this node-cycle marking

    q_12 in O_F^*, reduction(q_12)=c or c^(-1).

Equivalently §2.7 has constant off-diagonal term c_12, defined on printedp6
as exactly this paired cross-ratio. No other cross-ratio permutation or
unknown residue unit is inserted. The special-fiber marking determines
this unit; smoothing parameters contribute only principal units here.

This is a statement about the actual Jacobian period lattice, not about
all abelian surfaces with the same monodromy valuations. That distinction
is precisely why the old toric matrix controls do not settle this test.

## B59.6. Rational torsion forces period powers

For the split Schottky uniformization J^an=T^an/Lambda, T=G_m^2 and
Lambda subset (F^*)^2 is the free period lattice. For a positive integer M
there is a Galois-equivariant sequence on geometric points

    0 -> mu_M^2 -> J[M] -> Lambda/M Lambda -> 0.

A direct proof: if z^M=lambda in Lambda, then the class of z is M-torsion.
Every lambda has an Mth root geometrically; changing z by a period changes
lambda by an Mth power of a period. The kernel is T[M], since Lambda has
no torsion. This is also the finite-level form of the Tate/Kummer sequence
in Gregory–Liedtke2019 §4.4, (7), Lemma4.9(2)–(3).

Suppose the FULL natural J[M] is F-rational. Choose an Mth root z of any
lambda in Lambda. Its class in J[M] is Galois fixed. For g in G_F,
g(z)/z belongs to Lambda and also T[M], because lambda is F-rational.
The intersection is trivial. Hence z is F-rational. Every coordinate of
every period generator is therefore an Mth power in F^*.

Take M=7^d. In particular q_12 is a 7^d power, so its residue c is a
7^d power in k_v^*. Since -1 is itself an odd 7^d power, and -4 is coprime
to7^d, c=-phi^(-4) gives

    FULL J^nu[7^d] locally rational => phi in (k_v^*)^(7^d).

The converse for the FULL Jacobian is not asserted. The other period
coordinates also matter. For the single unit q_12 alone, residue power
is sufficient as well, since x -> x^(7^d) is an automorphism on principal
units at q!=7, but that does not make the other periods powers.

## Consequences with the same natural representation

At every beta-supporting place, B59.1 supplies d=min(t,floor(t/2)+1),
so phi must be a 7^d power. At depth two, d=2 and phi must be a forty-ninth
power. At locally trivial eta and beta support the exponent is7^n. At a
maximal-order eta inertia place, B59.3 supplies the stronger7^t condition,
even if beta is unramified there. None of these conclusions assumes that
an arbitrary local toric model is the Frey Jacobian.
