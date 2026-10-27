# B71.2. Identifying the actual local coefficient action

A formal identity R^2=5I is not enough to identify R with actual RM. This note
supplies the additional comparison on the local natural Tate sequence at7.
It does not construct a global semilinear Tate-lattice isomorphism.

## Functoriality through the ACTUAL period extension

Gregory-Liedtke, p-Adic Tate Conjectures and Abeloid Varieties (2019), section4.4,
Lemma4.9 and Proposition4.11, describe the Tate module extension by its Kummer
period matrix, including ell=p. A G_F-equivariant endomorphism induces matrices
on the split torus Tate lattice and on the period quotient, intertwining that
matrix of extension classes. Apply this to multiplication by the actual
coefficient w in the natural integral O_E action.

Denote its two induced integral matrices by S_T,S_Y in M2(Z7). The valuation
part of the intertwining relation is

    (7c I) S_T = S_Y (7c I).

This is an identity over Z7, BEFORE reduction. Although7c is not a unit, it is
nonzero and Z7 has no torsion, so it can be cancelled. Thus S_T=S_Y=S. The same
matrix intertwines the full completed periods and, after reduction, satisfies

    P*Sbar=Sbar*P.

No reduction of7c followed by invalid cancellation is made. No Rosati or global
matrix-identification hypothesis beyond H2 is needed for this implication.
The action preserves the actual natural lattice, not just a rational isogeny class.

## The nonzero period coordinate determines Sbar up to sign

Use B71.1: P=ZI+2XR and X is NONZERO. Since the scalar part commutes,

    X*(R*Sbar-Sbar*R)=0.

The entries of the commutator are in F7, and multiplication by a nonzero scalar
cannot kill X. Therefore Sbar commutes with R. Its characteristic polynomial is
T^2-5: the two-dimensional torus and quotient are one-dimensional over the
unramified coefficient field E, and their integral submodules are O_E-stable.
In particular trace(Sbar)=0 and Sbar^2=5I.

The centralizer of the irreducible2-by-2 matrix R over F7 is F7[R]. Write
Sbar=aI+bR. Trace zero gives a=0 and squaring gives b^2=1. Thus

    Sbar=epsilon*R, epsilon in{1,-1}.                 (1)

The sign records which local coefficient embedding matches the marked action.
It must NOT be silently fixed independently of the actual representation.
An exact negative control is S=[[2,1],[1,-2]]: S^2=5I, but S does not commute
with R. The extra period relation, not the square relation alone, excludes it.

## Passing to the local rank-two E-extension

In the local graded bases related by the valuation identification, R represents
multiplication by epsilon*w. The matrix P therefore represents the scalar
Kummer extension

    kappa_7 = Z+2*epsilon*w*X
            = (3*q7(A)+5)H+2*epsilon*w*X.            (2)

The residual cyclotomic character is nontrivial on7-adic inertia. Hence the global
natural chi-subline equals the local toric chi-subline; a map from that line to
the trivial quotient is zero. The two residual graded lines are k-lines. Changing
their two bases rescales the extension by ONE nonzero c in k*, and changing a
splitting adds only a coboundary. Consequently the SAME global natural class
has local restriction c*kappa_7, for a nonzero c.

This c cannot be set to1 by assertion. The next proof determines it from the
coefficient comparison. Also, equality(1) does not identify base omega with
coefficient w: it identifies the matrix by which w acts on a marked local module.
