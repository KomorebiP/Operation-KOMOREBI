# Beal research, Block 73
## Nontriangular deformation and a delayed tame lifting obstruction

The next bounded work package is complete. Its new obstruction acts on the actual
mod49 deformation and its required mod343 lift, rather than on another finite
Frobenius list. None of the eight residual coefficient/character patterns is
eliminated. Arithmetic applications remain conditional on the pinned actual
geometry and representation hypotheses.

## 1. The missing depth-one global object is now explicit

An auxiliary global triangular Kummer lift rho0 of the residual natural class can
be chosen from phi,3,sqrt5. It is NOT the actual representation. The same actual
rho modulo49 is uniquely written in a fixed frame as

    rho=(I+7X)rho0, X=[[p,q],[beta,-p]].

The complete equations are

    beta(gh)=beta(g)+chi(g)^-1 beta(h),
    p(gh)=p(g)+p(h)+alpha(g)chi(g)^-1 beta(h),
    q(gh)=q(g)+chi(g)q(h)-2alpha(g)p(h)-alpha(g)^2chi(g)^-1beta(h).

They retain the lower-left7*beta and identify the two upper correction equations.
The known cup-zero statement only supplies the first primitive; it does not solve
the actual global/local-constrained deformation. See ADJOINT_DEFORMATION.md.

At seven a STRICT LOCAL alignment of the actual toric line makes the local upper
correction a Kummer class. Its valuation defines a gauge-invariant functional
nu7 on locally admissible adjoint classes. Block72's actual periods give

    nu7(X)=v7(C)*v/(2epsilon) mod7.

This now makes sense at n=1 without asserting an actual global triangular alpha2.
The sign and common graded scalar are retained. It is not a zero-valuation theorem.

## 2. Trace-invisible does not mean integrally liftable

For any k(chi) cocycle xi, rho+7xi E12 is a representation modulo49 with exactly
the same determinant, trace at every group element, alpha and beta. The class
xi=lambda[7] shifts nu7 by lambda, so a freely chosen mod49 lift alone would still
accommodate the fixed-seven period valuation.

But suppose the LOCAL residual representation is I at a non-seven place and write
F=I+7A+49A2, T=I+7M+49M2. Expanding FTF^-1=T^Q modulo343 gives

    [A,M]=hM, h=(Q-1)/7 mod7.

The next digits A2,M2 cannot repair a failure of this relation. At beta support,
M21 is nonzero. An unramified upper correction replaces A by A+xi(F)E12 and leaves
M unchanged. Its commutator defect has first entry xi(F)*M21. Hence nonzero xi(F)
is incompatible with a mod343 lift keeping the same mod49 inertia.

The explicit Q=883^2 matrices T=[[1,0],[7,1]], F=[[1,7],[0,Q]] satisfy the tame
relation modulo49, but have defect [[49,0],[0,-49]] modulo343, independent of all
possible next-digit corrections. They are local matrix controls, not Frey curves.
See TAME_LIFT_OBSTRUCTION.md.

## 3. The [7] direction is detected in every frozen pattern

All eight patterns ramify at883. In its residue field F_(883^2), the seventh-power
symbols of phi,3,sqrt5 are1, but the symbol of7 is296, a nontrivial seventh root.
Thus a nonzero [7] upper correction has an unramified but NONZERO Frobenius value
at883. It is forbidden by the next-level relation for any actual lift with the
same inertia. The three old unit-generator corrections cannot cancel that value.

A general comparison theorem sharpens the statement. Fix the complete mod49
rank-two trace character, the normalized beta cocycle, the entire mod49 inertia
at every finite place except seven, and the same residual frame. If two such
representations both lift modulo343 locally, their difference is an upper Kummer
cocycle. Its unramified-outside-seven class is a[phi]+b[7]. The883 condition makes
b=0. Their fixed-seven valuation functional is therefore identical.

This is a rigidity statement INSIDE a specified trace/inertia fibre, not a claim
that the fibre has been computed from eight residual patterns, or that its value
is zero. The hypotheses cannot be weakened to finitely many traces or beta alone.
See TRACE_INERTIA_FIBRE.md.

## 4. Nonclosure and the next mathematical task

The first-order inertia directions, diagonal corrections, and full global q class
have not been determined for any of the eight patterns. The local relations alone
remain solvable: for every nonzero c and every theta,h,y,

    M=c[[theta,-theta^2],[1,-theta]],
    A=[[theta*y,theta*h-theta^2*y],[y,h-theta*y]]

satisfy the needed local equations. We check2744 integral toric local packets for
the eight frozen883 components. These packets do not construct a global Frey
Jacobian. We do not assert that all eight have a constrained global adjoint lift.

The next step is to determine the actual global adjoint deformation with its local
conditions, then evaluate nu7. A contradiction would require a value incompatible
with v7(C)*v/(2epsilon), or a genuine nonsolvability certificate. No such value or
certificate is supplied by this block. Arbitrary higher depth/conductor, the minus
component, integral realization, CM/higher Hilbert branches, full signature and
Beal remain separate obligations.

## 5. Finite evidence

Two arithmetic implementations use distinct coefficient bases: w^2=5 and phi^2=phi+1.
Neither imports the other. They agree on every output field, including:

-43218 adjoint basis/action checks and4096 mixed-characteristic matrix pair checks;
-4096 explicit secondary-cocycle identities;
-all2352 lower-nonzero nilpotents overF49, normal-form/rank certificates and16464
 particular toric solutions, plus115248 upper-shift commutator checks;
-a complete100842-case prime-field enumeration, with2058 solutions;
-392 coordinate-direction checks on the unreparable mod343 example;
-all four883 residue symbols, the frozen eight components, and2744 local packets.

The rank certificates imply806736 local F49 packets for scalar h inF7; these are
NOT806736 individually executed tests. The universal claims have written proofs.
No new point counts, Lean compilation or independent mathematical reviewer.

The fresh-extraction replay, process status, manifest and integrity audit are
recorded separately. The original Block72 default verifier was observed to pass
before this work in20.794 seconds. No full historical-chain replay is claimed.
