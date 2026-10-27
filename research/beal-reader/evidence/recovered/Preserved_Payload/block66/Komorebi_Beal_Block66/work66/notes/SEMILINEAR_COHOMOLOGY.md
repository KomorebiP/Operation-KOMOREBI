# B66.1. Natural coefficient rigidity without assuming opposite-class descent

All arithmetic statements retain the inherited actual depth-one hypotheses.
In particular the natural and opposite classes are those of ONE representation,
alpha=u[phi]+r[3]+[sqrt5] with a5=1 and u,r nonzero. Set k=F49, sigma(z)=z^7.
The symbol w satisfies w^2=5 in k. It is not the base-field radical sqrt5.
Let K=Q(sqrt5), L=K(zeta7), and choose j in G_Q inducing the nontrivial base
involution and fixing zeta7. No action of j on the natural Tate lattice is
assumed. The required comparison is the inherited equality of the two actual
split-place quartics, obtained from delta'=phi^2 delta.

## Statement

Without ANY assumption that beta descends to Q, one has

    u^7=-u,   r in F7^*,   j[beta]=sigma[beta] in H1(K,k(chi^-1)).       (1)

Thus the same36 natural directions alpha=(v*w,r,1), v,r in F7^*, apply to
all depth-one classes in this retained branch, including non-descended beta.
The conclusion is semilinear COHOMOLOGY compatibility. It is not descent of
the integral representation, a global Tate-lattice isomorphism, or beta=0.

## The actual finite joint image

Retain the explicitly proved independence of [phi],[3],[sqrt5] over L from
B65.1. Kummer theory gives a surjective map kappa=(X,Y,Z):G_L -> F7^3.
On G_L the coefficients of beta are trivial, so its restriction B is a
canonical additive character, unchanged by a coboundary. Define

    B'(g)=B(j g j^-1),
    V=image(g |-> (B(g),B'(g))) subset k^2.

B is nonzero: restriction from K to L is injective on seven-primary H1,
since [L:K]=6 is prime to7. Therefore V contains a nonzero pair.

For h in G_K with chi(h)=a, both B and B' transform under conjugation by a^-1.
For B' this follows by applying the cocycle covariance to j h j^-1 in G_K.
The Kummer triple transforms by a. Taking a=3 separates eigenvalues3 and5.
Consequently the F7-linear joint image

    W=image(g |-> (kappa(g),B(g),B'(g)))

is EXACTLY F7^3 plus V: the projectors (T-5I)/(3-5) and its complement extract
the two parts, and both projections are surjective by their definitions.
This proves independence of ACTUAL finite Galois values, not of arbitrarily
chosen abstract local classes.

The joint kernel is normal in G_Q. It is stable under Gal(L/K) by covariance.
Conjugation by j changes (X,Y,Z) to(-X,Y,Z) and swaps B,B'. Indeed j^2 is in
G_L, whose inner conjugation acts trivially on additive characters. These
actions generate Gal(L/Q). The kernel therefore defines a finite Galois
extension E/Q with Gal(E/L)=W.

For every (x,y,z,b,b') in F7^3 plus V, Chebotarev realizes its conjugacy class
at rational primes split in L. A suitable prime above such a rational prime
realizes the selected element itself. Exclude the finite bad set of the
actual Jacobian and the finite ramification set. Infinitely many GOOD primes
remain. This gives joint values at actual good Frobenius, not a freely chosen
prime that might divide C. No effective prime bound is asserted.

## A union of two proper kernels cannot cover F7^3

At paired K-primes the actual products are

    P(x,y,z)=b(ux+ry+z),       Q(x,y,z)=b'(-ux+ry+z).                   (2)

They belong to the one- or two-element correction set of ONE actual quartic.
Hence, for each vector (x,y,z), either Q=P or Q=P^7. The choice is not assumed
constant as the vector varies. Both P,Q, and sigma(P) are F7-linear functions.
Thus F7^3 is the union of ker(Q-P) and ker(Q-sigma(P)). Each proper kernel
has at most49 elements, whereas F7^3 has343 elements. At least one of the
two functions must vanish identically.

Fix a nonzero (b,b') in V. Q=P identically is impossible: the coefficient of z
gives b'=b and that of x gives 2bu=0, which would force b=b'=0. Therefore
Q=sigma(P) identically. Comparing the z,x,y coefficients gives, respectively,

    b'=b^7,        -b'u=b^7 u^7,        b'r=b^7 r^7.

A nonzero pair has b nonzero, so u^7=-u and r^7=r. Repeating the argument for
every pair in V, including the trivial pair, gives B'=sigma B on G_L.

Restriction H1(K,k(chi^-1)) -> H1(L,k) is injective. Therefore this equality
of restricted characters is the equality of cohomology classes in (1). The
j-action may be written with j or j^-1: their square differs by inner
conjugation in G_K, trivial on H1. Since chi(j)=1 there is no missing scalar
in this chosen comparison. QED.

## Precise improvement over B65.1

B65.1 assumed B'=B. That hypothesis forced B=B^7 and hence an F7-valued beta.
Here the consequence is B'=B^7, not B'=B. Natural coefficients are now rigid
without descent, while the opposite class may have a nonzero anti-invariant
component. See TWO_TWIST_DECOMPOSITION.md for its exact meaning.

## Evidence and limitations

The proof is written under the same actual trace-product and common-quartic
inputs as B65.1. Kummer theory, restriction/corestriction and Chebotarev are
checked in the source record. The finite union-of-kernels lemma is proved
above and separately enumerated in two coefficient-field bases. That finite
check does not independently verify the arithmetic inputs or Chebotarev.
No independent mathematical reviewer or Lean compilation is claimed.
