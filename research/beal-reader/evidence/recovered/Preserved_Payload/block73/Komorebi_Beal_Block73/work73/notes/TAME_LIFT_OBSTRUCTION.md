# B73.3. One-order-later local lifting detects trace-invisible corrections

Let v have residue characteristic different from7 and residue cardinality Q=1 mod7.
Use arithmetic Frobenius F and a compatible generator T of the pro-seven tame
inertia quotient, so F T F^-1=T^Q. Suppose an actual representation is trivial
modulo7 on this local group and write, modulo343,

    rho(F)=I+7A+49A2, rho(T)=I+7M+49M2,
    h=(Q-1)/7 mod7.

Expansion gives

    rho(F)rho(T)rho(F)^-1 = I+7M+49*(M2+[A,M]),
    rho(T)^Q              = I+7M+49*(M2+h*M).

Indeed binom(Q,2) is divisible by7 and all terms of order3 or greater vanish
modulo343. Therefore EVERY lift to a representation modulo343 must satisfy

    BOX: [A,M]=h*M over k.                               (9)

The matrices A2 and M2 disappear from this equation. No choice of the next digits
repairs its failure. This is a local Galois-representation obstruction, not merely
a condition on abstract Weil polynomials or a new good-reduction assumption.

The tame relation itself follows by choosing a uniformizer in the maximal
unramified field and compatible prime-to-residue-characteristic roots. T multiplies
a root by a root of unity and arithmetic Frobenius raises that root of unity to Q.
Wild inertia has no pro-seven contribution at this residue characteristic.

## Actual beta support and the toric strengthening

At a depth-one beta-ramification place the pinned natural geometry gives residual
rho=I, N=7M mod49, M^2=0, M21!=0, and exact toric trace tr F=Q+1. Consequently
tr A=h. With M^2=0 and M21!=0, equation (9) and trace imply

    A*M=h*M, M*A=0.                                      (10)

For example put M=c[[theta,-theta^2],[1,-theta]], c!=0. Every solution is

    A=[[theta*y, theta*h-theta^2*y],[y,h-theta*y]], y in k. (11)

This follows by conjugating M to cE12; (9) and trace then determine both diagonal
entries and the lower-left entry, with one free upper-right entry. Thus the local
necessary space is nonempty for every c,h,y. The formulas do not determine the
actual global theta, and no actual candidate is excluded merely by (11).

## Upper-only corrections with fixed inertia

An unramified xi from (7) leaves M unchanged and replaces A by A+zE12, where
z=xi(F). The change in (9) is z[E12,M]. Its (1,1) entry is z*M21. Since M21 is
nonzero in the field k,

    both rho and rho_xi lift modulo343 => xi(F)=0.         (12)

A nonzero upper-only unramified correction, though invisible to EVERY mod49
trace, cannot preserve the actual mod49 inertia and admit the next local lift.
The hypothesis M21!=0 is essential. If M=E12, an upper correction commutes with M
and explicit toric integral lifts remain possible.

## Explicit unrepairable local example at883

Let Q=883^2=779689 and take

    T=[[1,0],[7,1]], F0=[[1,0],[0,Q]], F1=[[1,7],[0,Q]].

F0,T form an exact toric local model. F1,T define a genuine tame representation
modulo49 because Q=1 mod49 and their commutator vanishes there. They have the
same determinant and trace for every word modulo49. But

    F1*T - T^Q*F1 = [[49,0],[0,-49]] mod343,               (13)

which is nonzero. Adding arbitrary49-multiples to ANY entries of F1 or T cannot
change this defect. There is no mod343 representation lift with these prescribed
mod49 matrices. The independent program checks each coordinate direction; the
expansion (9) proves the assertion for simultaneous arbitrary changes.

This is a local matrix counterexample to automatic liftability, not a Frey curve
or a Beal counterexample. Holding the actual inertia matrices fixed is part of
(12). Allowing them to vary reopens local parameters and cannot be silently ignored.
