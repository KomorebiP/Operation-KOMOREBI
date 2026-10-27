# B62.5–B62.7. Consequences and exact conductor boundaries

Retain the explicit actual Frey-branch hypotheses. Put

    U={97,197,293,491,587,883,1373,1471,1567,1667},
    V=U union{43,113,127},
    Splus={43,113,127,197,883,1373,1667}.

## Depth one and the old complete high-support class

At depth one B62.4 excludes all beta ramification contained in Splus. The
other six primes of U cannot ramify in beta at ANY depth by the inherited
actual nodal-period test. Consequently

    n=1 => beta ramifies at a prime outside V.         (10)

The inherited result COMPLETE H(C) subset U already gives n=1. Combining it
with (10), any remaining hypothetical solution in that class must have an
actual beta-supporting prime q OUTSIDE V with

    v7(q^f_q-1)=1,
    v7(v_q(C))=0,
    phi and75A both seventh-power residues at K_v.     (11)

The first condition follows because every outside-U high divisor is excluded
by the COMPLETE H(C) hypothesis; actual beta support still requires h>=1.
The second follows from n=t+2s=1, t>=1: t=1,s=0. The final two follow from full
natural J[7] rationality at beta support and the retained complete local period
test. These conditions are simultaneous necessities, not sufficient conditions
for actual beta or a global integer solution.

It would be false to claim that H(C) subset U is now entirely eliminated.
Its possible low-h supporting primes are not bounded by H(C). Statement(11)
identifies the remaining route rather than silently deleting those primes.

## Higher depth with a completely trivial diagonal

The proof in Block61 actually yields the following extension of its explicitly
stated depth-two result:

    n>=2, eta_n=1 => beta cannot have all ramification in S.    (12)

Indeed n>=2 forces29,71,491 into C. B61.1 applies at any n with fully trivial
eta_n, making beta locally zero at these places. Cohomological descent, the
same correctly twisted three rows, and the incompatible197/1667 natural ratios
then give the identical contradiction. No step of that proof otherwise used
n=2. We record this as a NEW consequence, not a retrospective change of its
stated theorem.

At n>=2 beta needs h>=floor(n/2)+1>=2. Thus43,113,127 cannot add beta ramification
in (12), because each has h=1. Combining(10),(12) and the six period exclusions,

    eta_n=1 => beta ramifies outside V, for every n.    (13)

For arbitrary nontrivial eta, (13) is NOT claimed.

## A complete geometric-support exclusion, allowing other C divisors

Define the full set of geometrically eligible rational divisors

    E(C)={q|C, q outside{2,3,5,7}:
          q^f_q=1 mod7 and phi is a seventh power in F_(q^f_q)}.

At split q the power condition is independent of which prime is chosen:
the two phi residues have product -1, and -1 is a seventh power.
Every beta-supporting prime belongs to E(C). Every maximal-order inertia place
of a nontrivial eta belongs to E(C), by B55/B59, and has h>=2 by B54.

Suppose E(C) subset V. A nontrivial eta would have its highest-layer conductor
inside U: the only added primes43,113,127 have h=1, and cannot support that
layer. Block58 excludes every nontrivial highest layer contained in U.
Therefore eta_n=1. But beta would also have its ramification inside V,
contradicting(13). Hence

    NO actual representation in the retained reducible branch has E(C) subset V.

Equivalently every hypothetical integer solution in THAT retained branch must
have some q outside V dividing C with

    q^f_q=1 mod7 and phi a seventh-power residue.      (14)

Arbitrarily many other divisors failing that geometric eligibility test are
permitted in the exclusion. This is stronger than excluding integers whose
entire prime support lies in V, but it is not a bound on arbitrary E(C).

If eta is nontrivial, the outside-V place in this argument may be highest-layer
eta ramification rather than beta ramification. It is not necessarily the
separately forced divisor2549. Statement(14) is not a solution of Beal.

## Still unresolved

General depth one with a larger beta conductor; general depth two and higher
support; identification of all actual global coefficients and lattices;
independent upstream proof review; the separate CM nonboundary-point and higher
Hilbert-level branches; the complete(3,5,7) signature; and full Beal remain open
obligations. The additional columns at new ramified primes must be included
with chi^-1 covariance. Ordinary eta rows cannot be substituted.
