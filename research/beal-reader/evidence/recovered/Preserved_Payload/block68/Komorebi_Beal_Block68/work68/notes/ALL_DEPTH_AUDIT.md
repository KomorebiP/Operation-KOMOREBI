# Logical audit of the all-depth semilinear argument

This is same-assistant adversarial review, not independent mathematical review.
It audits the displayed implications in B67.1–3, conditional on their inputs.
It does not independently reconstruct the underlying Frey geometry.

## Trace bridge

For F=[[a,b],[7^n c,d]], det F=Q, D=d-1 and t=tr F-Q-1, direct expansion gives

    t(1+D)=7^n bc-(Q-1)D+D^2.

Put m=floor(n/2)+1 and h0=ceil(n/2). If D is in7^m O and Q-1 in7^h0 O,
then h0+m=n+1 and2m>=n+1. Both error terms vanish modulo7^(n+1).
Since1+D is a unit congruent to1 modulo7, t is divisible by7^n and
(t/7^n) mod7=bar(b)bar(c). This includes even and odd n. Full eta=1 is
not assumed. The old shallow n3,Q8 counterexample remains a valid control.

## Actual image and cyclotomic restriction

On G_L1, L1=K(zeta7), the independent Kummer triple and paired opposite values
form an actual F7-linear image. Cyclotomic conjugation with residual character3
acts with weights3 and5. Projection polynomials in that operator separate the
Kummer image from the paired opposite image; independence of the latter's two
coordinates is neither claimed nor needed.

For Le=K(zeta_(7^e)), Le/K is abelian. Thus [h,g] belongs to G_Le for g inG_L1,
and f([h,g])=(T-I)f(g). T-I acts by2 and4, hence is invertible. Every joint
value survives restriction. No false prime-to-seven-degree assertion is used.
The trivial-weight counterexample in the predecessor remains necessary.

## Normality and realization

Choose j inducing base conjugation and fixing the finite cyclotomic field.
It changes the phi coordinate's sign, fixes the other two Kummer coordinates,
and swaps the two opposite values. Its square lies in G_Le, where inner
conjugation acts trivially on additive characters. The joint kernel is stable
under base and cyclotomic conjugation, hence cuts out a finite Galois extension
over Q. Chebotarev realizes any required joint conjugacy class; a prime above
the rational prime selects the chosen element. Deleting a finite ramified/bad
set leaves good split primes. This is existence, not an effective prime bound.

## Common polynomial and return to cohomology

The two trace products are P=b(ux+ry+z), Q=b'(-ux+ry+z). At each vector inF7^3,
Q=P or Q=P^7 because both occur in one actual quartic's correction pair.
Each alternative is the kernel of an F7-linear map. Two proper kernels have
at most98 elements together, fewer than343, so one equality is identically true.
For a nonzero paired value, Q=P identically would force b=b' and2bu=0,
a contradiction since u!=0. Comparing coefficients in Q=P^7 gives
b'=b^7, u^7=-u, r^7=r. It is not necessary to make one root choice at every prime.

For the cohomology difference j beta-sigma beta, first use the nontrivial-weight
commutator again to return from G_Le to G_L1. Only then invoke restriction
injectivity across [L1:K]=6. The argument does not use degree6 at the wrong step.

## Remaining leaves

The exact actual rank-two determinant and global half-depth precision; common
natural/opposite cocycle normalization; Kummer independence; nonzero u; the
actual common-quartic comparison; and the relevant classical Galois results
are essential inputs. The audited steps do not prove these leaves. We found
no internal defect in the displayed all-depth implication, but do not promote
this self-review into independent upstream acceptance or a Lean certificate.
