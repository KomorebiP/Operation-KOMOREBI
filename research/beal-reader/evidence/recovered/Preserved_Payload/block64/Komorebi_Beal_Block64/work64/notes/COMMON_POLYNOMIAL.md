# B64.4. Both split-place products belong to ONE actual polynomial

## An explicit base-field comparison, not a missing Tate-lattice descent

Conjugation in K sends phi to1-phi and delta=9-3phi to delta'=6+3phi.
There is the exact identity

    delta'=phi^2*delta.

At a split rational prime ell outside2,3,5, the two reductions of the twisted
curve for a fixed rational pair(A,B) are therefore isomorphic over F_ell.
Multiplying the y-coordinate by the appropriate nonzero phi residue gives the
isomorphism. In particular their full rank4 Frobenius polynomials agree.
This comparison does not identify the coefficient-field rootw with a base
residue, supply a semilinear global lattice action, or claim global descent
of the twisted curve.

For any one such actual quartic P, let D(P) be its one- or two-element set
of possible rank2 trace corrections in k=F49. If p_plus,p_minus are the
products predicted by the same(alpha,beta) at the two split places, good
reduction necessarily implies

    EXISTS ONE actual P such that p_plus and p_minus both belong to D(P).  (1)

The weaker independent-choice test was

    p_plus,p_minus belong to UNION_P D(P).                               (2)

Condition(2) permits taking one root from a polynomial attained at one residue
pair and the other from a different polynomial attained at another residue pair.
Condition(1) removes this defect. It is still a necessary overapproximation:
we do not prescribe which coefficient embedding selects which root, nor require
all further information about the equation residue or the global lattice.

No new counts are needed at the old test primes. Their full polynomial records,
not just their union trace sets, are frozen in the predecessor and hash-pinned.

## A convenient algebraic form when the opposite class descends

Let its common Frobenius value at the split places be b. Let the natural rows
be(l,c,d),(-l,c,d), and alpha=(u,r,1). Then

    p_plus=b*(l*u+c*r+d),
    p_minus=b*(-l*u+c*r+d).

Suppose l,u,b are nonzero. The two products differ. If(1) holds, they must be
the two distinct coefficient-conjugate corrections of that SAME polynomial,
so p_minus=p_plus^7. Equivalently

    b*(c*r+d) lies in F7,
    (b*u)^7=-b*u.                                                       (3)

The factor l is a nonzero prime-field scalar and can be removed from the
second equation. This is a conditional, conductor-independent local compatibility
lemma for a descended beta and an unramified good split test place. It does
not establish that u itself has trace zero, unless additional information on b
justifies that inference. It cannot be imposed at a ramified beta test place
or replace good/bad case distinctions.

Proof of(3): write z=b(c*r+d), e=b*l*u. Conjugacy of z+e and z-e is equivalent,
in odd characteristic, to z^7=z and e^7=-e. The converse holds as well for the
algebraic conjugacy relation, but not for membership in the ACTUAL curve's
finite polynomial list. That additional requirement is retained in(1).

## Concrete strictness control

After743 is added to the expanded conductor, the independent-choice system
has6 surviving tuples. Four use, at211, mixed products such as

    1+4w, 3+3w.

Both lie in G211, but the actual root pairs there are

    {0}, {6}, {3+w,3-w}, {1+3w,1-3w}, {3+3w,3-3w}.

No single pair contains those two mixed products. The common-polynomial test
removes these four tuples. TWO others remain. All six and the rejected pairs
are retained in verification/conductor64.json. The stronger test is not a
claim that every possible conductor is excluded.
