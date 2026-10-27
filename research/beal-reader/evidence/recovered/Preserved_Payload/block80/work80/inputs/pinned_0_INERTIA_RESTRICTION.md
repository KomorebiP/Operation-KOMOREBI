# B79.1. The first-stage cochain has no auxiliary ramification

All arithmetic statements retain TARGET_CONTRACT.md. Fix a variable place v
outside 2,3,5,7. The natural reference has rho0(T)=I on inertia. At a bad place,
write rho(T)=I+N, N in7 M2(O), N^2=0. Reduction gives

    M=N/7 mod7=[[p(T),q(T)],[beta(T),-p(T)]],
    p(T)^2+q(T)beta(T)=0.                              (1)

If beta is unramified at v, beta(T)=0 for EVERY inertia element. Since k is a
field, (1) forces p(T)=0. There is no passage from a zero square in O/49 to a
zero element: the square-zero inference takes place in k, which has no nilpotents.
At a good place both rho and rho0 are unramified. Consequently

    p(I_v)=0 for every v outside S0 union Ram(beta),
    S0={places over2,3,5,7}.                          (2)

This holds for arbitrary additional bad divisors of C. At beta-unramified places
q(T) need not vanish. The matrices left by (1) are EXACTLY q(T) E12.

The cochain p is not generally a character: dp=-alpha cup beta. Nevertheless
it descends as a cochain to G_(K,Sigma_p), Sigma_p=S0 union Ram(beta).
Indeed alpha and beta already descend to this quotient. For i in an omitted
inertia subgroup their values and p(i) vanish. The p multiplication law gives
p(gi)=p(g)=p(ig); conjugates and products of such inertia elements also vanish.
Continuity then gives factorization through their closed normal closure.

This is a finite, justified ramification set for Stage P once beta's complete
support is fixed. It does NOT give a finite support bound for the upper q-stage.

## Integral refinement at an upper-ramified auxiliary place

If q(T)!=0, natural content is t=1. In the factorization of H2,
N21= -mu*y^2 is divisible by49, so y is divisible by7 and x is a unit.
After normalizing x=1 write y=7s. Then

    N11,N22 in49O,   N21 in343O,   v7(N12)=1.          (3)

The lower first-order coefficient vanishes by two EXTRA digits in the actual
matrix, not just by the one digit needed for beta(T)=0. If content t>=2,
all of N is zero modulo49 and neither first-order p nor q has inertia.

Thus the two possibilities are exhausted: no mod49 inertia, or purely upper
mod49 inertia of content one. The converse at the local MATRIX level is
constructed in AUXILIARY_UPPER.md; no global Frey converse is claimed.
