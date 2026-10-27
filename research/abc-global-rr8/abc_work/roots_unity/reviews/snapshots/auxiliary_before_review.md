# Root filters and the nonzero auxiliary-polynomial step

Parent: ABC-20261025-RR2, archive SHA-256
f5b5e7336d5cae31502106100997cf02733b1054f62e3df39827002cfe7e9469.
The target remains full primitive integer ABC. This is an executed test of
a possible proof mechanism, not a proof of that target.

## Why cancellation could in principle help

A roots-of-unity projection can cancel coefficients. To turn that cancellation
into a height inequality, one possible strategy is to construct a small
nonzero integer auxiliary value divisible by a large product M of local
prime-power contacts. If its absolute value is smaller than M, there is a
contradiction. A proof must establish both small height and nonvanishing.

The following calculation tests that strategy exactly. It does not assume
that cancellation itself cannot be useful in other constructions.

## The evaluation lattice

Fix coprime positive integers A,B, degree D>=1, and M>=1. Put

    E(u)=sum_(j=0)^D u_j A^j B^(D-j),
    L_M={u in Z^(D+1): E(u)=0 modulo M},
    L_0={u in Z^(D+1): E(u)=0 as an integer}.

The image of E on Z^(D+1) is Z. Indeed its coefficients include A^D and
B^D, whose gcd is 1. Bezout's identity proves surjectivity. Consequently

    E(L_M)=M Z,   L_M/L_0 is isomorphic to M Z.             (A1)

The exact-zero lattice L_0 has rank D. For each j=0,...,D-1, the vector
with entries -A at j and B at j+1 belongs to L_0, since

    -A A^j B^(D-j)+B A^(j+1)B^(D-j-1)=0.

These D vectors are linearly independent and have coordinate height
max(A,B). They need not form an integral basis of L_0, which is not needed
for the argument.

Let S_D(A,B)=sum_(j=0)^D A^j B^(D-j). If H=max_j|u_j| and
u is in L_M but not L_0, then

    M<=|E(u)|<=H S_D(A,B),
    H>=M/S_D(A,B).                                        (A2)

This is the missing nonvanishing cost. A bound for merely a nonzero
coefficient vector in L_M can select an exactly vanishing polynomial.
Even D independent short vectors may all lie in L_0. A roots-of-unity
change of coordinates does not remove this subspace.

For D=1, A=2,B=1 the minimum nonzero evaluation height is exactly

    min{max(|u_0|,|u_1|): 0!=u_0+2u_1=0 mod M}
       =ceil(M/3).                                       (A3)

The lower bound is (A2). For the upper bound let H=ceil(M/3),
u_1=H,u_0=M-2H. Then |u_0|<=H for every M>=1 and E(u)=M.
In contrast, the exact-zero vector (-2,1) has height 2, independent of M.

Taking M=1093^2 gives an exact example tied to the RR2 exceptional prime:
the shortest coefficient-height candidate can already be exactly zero,
whereas a nonzero multiple of M needs height ceil(1093^2/3)=398217.
The fact that 1093^2 divides 2^182+1 is checked independently in RR2.
The lattice statement does not require that divisibility as an assumption.

## Test outcome and scope

The attempted proof move was: use modular root-contact conditions to obtain
a short auxiliary coefficient vector, then infer a small nonzero integer.
That inference fails unless the vector is proved to lie outside L_0.
The explicit cheap vectors above show the exact obstruction at every degree.

This does not refute ABC or rule out a well-chosen auxiliary construction.
It identifies the extra estimate such a construction must supply: a controlled
integral representative with nonzero evaluation, compared with the local
contact modulus and the evaluation height. A degree bound, coefficient
bound, and nonvanishing certificate must be proved jointly.

The next open continuation is to use root-contact constraints that distinguish
different arithmetic inputs without forcing only the already-known rational
relation BX-AY. No such estimate was obtained in this calculation. The route
remains open under that additional obligation.

## Finite contract

`verify.py` independently enumerates every coefficient pair of smaller
coordinate height for D=1,A=2,B=1,M=1,...,100 and checks the exact minimum
ceil(M/3). It also checks the D displayed exact-zero vectors and their
independence for 1<=D<=6 and coprime bases 1<=B<A<=10, using exact rational
row reduction. These computations check the stated finite assertions only.
