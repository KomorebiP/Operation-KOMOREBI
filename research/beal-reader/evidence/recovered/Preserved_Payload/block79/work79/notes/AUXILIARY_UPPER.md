# B79.4. Upper auxiliary ramification survives, with a splitting restriction

At a beta-unramified bad place, B79.1 leaves only upper inertia. If that inertia
is nonzero modulo49, normalize the primitive toric column to (1,7s). The exact
factorization then has

 N=mu[[-7s,1],[-49s^2,7s]], v7(mu)=1,
 F=I+(1,7s)^T(P,R), P=Q-1-7sR.

It follows that

    beta(F)=s*(Q-1)/Q mod7.                            (9)

If Q=1 mod7 this is zero. Inertia beta was already zero, so beta is fully locally
zero. If Q!=1 mod7, an unramified k(chi^-1) class is zero because its Frobenius
coinvariant quotient is k/(Q^-1-1)k=0. Therefore a necessary condition for upper
auxiliary inertia is

    beta|G_v=0 as a cohomology class.                 (10)

At Q!=1, (10) is not a claim that every chosen cocycle representative has beta(F)=0.

There is more information in a compatible local reference [[Q,R],[0,1]]:

    p(F)=-sR/Q mod7.

In the Q=1 case, auxiliary upper inertia with alpha(F)=0 forces p(F)=0. With
alpha(F)!=0 the parameter s can instead realize any prescribed p(F). These are
local formulae, not global independence statements.

## Why no analogous no-auxiliary theorem for q follows

For any allowed residue norm Q and unit u, the exact matrices

    N=7u E12,  F=[[Q,R],[0,1]]

satisfy N^2=0, F N=Q N, N F=N, det F=Q. They have nonzero upper mod49 inertia,
zero diagonal inertia, and zero opposite inertia. More generally a lower
conjugation by [[1,0],[7s,1]] gives the matrices above. The certificate checks
33,614 such packets in two coefficient bases, including 28,812 with Q=1 mod7.

Thus the proposed strengthening "all adjoint corrections are unramified wherever
beta is unramified" is false even for all-precision local toric matrices.
These packets are not asserted to be global Galois or Frey representations.

## A genuine local Frey control, conditional on the inherited period theorem

Use the inert prime l=5167, which is1 mod7, and take

    A=3238=75^-1 mod5167,    C=5167,
    B congruent3658 mod5167,
    B^5=5167^7-3238^3 in Q_5167.

The derivative 5B^4 is a unit, so there is a unique such l-adic B by Hensel.
Both implementations reproduce it modulo l^8. Direct symbols show that phi,
3,5 and75A are seventh powers in F_(l^2). The inherited local period criterion
therefore gives full natural J[7]-rationality. Natural node thickness is7 and
monodromy content is1. A local toric-adapted frame has nonzero upper first-order
inertia but zero opposite inertia.

This shows that local actual-family geometry itself permits that inertia shape.
It does not install this local frame as the common global natural endpoint,
construct a global beta, fix all local data at once, or produce an integer B.
The required global arithmetic coupling of upper auxiliary primes remains open.
