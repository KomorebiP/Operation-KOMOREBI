# B67.2. Deep cyclotomic restriction preserves the actual joint image

Let K=Q(sqrt5), L1=K(zeta7), and Le=K(zeta_(7^e)), e>=1. The compositum Le/K
is abelian. Its degree overL1 may be divisible by7; no prime-to-seven
restriction argument is used for that step.

Let f:G_L1 -> W be a continuous additive homomorphism to a finite F7-vector
space, with covariance under some h in G_K given by T. Suppose T-I is an
automorphism of W. Then

    f(G_Le)=f(G_L1)=W,                                    (1)

where W denotes the actual image.

Proof. For any g in G_L1, the commutator hgh^-1g^-1 belongs to G_Le, because
Le/K is abelian. Additivity and covariance give

    f(hgh^-1g^-1)=(T-I)f(g).

The right-hand side ranges over W. This proves(1). It proves preservation
of ACTUAL joint values, not independence of separately chosen local classes.

## Application to the Kummer and opposite characters

Retain the independent three Kummer coordinates kappa=(X,Y,Z) onG_L1,
from[phi],[3],[sqrt5], and B=beta|G_L1. Choose a base-conjugation lift j fixing
all7-power roots of unity at the finite level in question, and put
B'(g)=B(jgj^-1). By B66's eigenspace argument their actual joint image is

    W=F7^3 direct_sum V,   V=image(B,B') subset k^2.

For h with chi_bar(h)=3, T acts by3 onF7^3 and by5 onV. Therefore T-I acts
by2 and4 respectively, so it is invertible. Formula(1) preserves all joint
values at EVERY finite cyclotomic level. No claim that B and B' are mutually
independent is made or needed.

This simultaneously explains why the Kummer coordinates do not become
seventh powers in the cyclotomic tower and why the nonzero opposite image
cannot disappear on restriction. The explicit nontrivial weights, rather
than a coprime extension degree, are the reason.

## Kernel normality and good Frobenius realization

On G_Le, j negates X and fixes Y,Z, and swaps B,B'. The square j^2 lies in
G_Le and its inner conjugation acts trivially on additive characters. All
other elements of Gal(Le/K) act on the two parts by chi and chi^-1. Therefore
the joint kernel is normal in G_Q and cuts out a finite Galois extension E/Q.
For every desired joint value inW, Chebotarev realizes its conjugacy class at
rational primes split inLe; a suitable prime aboveell realizes the selected
element. Remove the finite bad set of the actual Jacobian and the ramification
set ofE. Infinitely many GOOD primes remain. Thus all joint values can be
realized with ell=1 modulo7^e and identical paired actual quartics.

This is an existence theorem, not an effective bound for a test prime.

## A necessary negative control

A coordinate with TRIVIAL cyclotomic weight can disappear. A nonzero homomorphism
Gal(L2/L1)=C7 -> F7 has full image onG_L1 and zero image onG_L2. It has T=I,
so the commutator argument cannot recover it. The nontrivial character
hypothesis must not be deleted or replaced by the assertion that restriction
always preserves finite seven-primary images.
