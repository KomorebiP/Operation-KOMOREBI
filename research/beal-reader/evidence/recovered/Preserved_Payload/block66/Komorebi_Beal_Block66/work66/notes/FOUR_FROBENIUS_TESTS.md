# B66.5. Four actual Frobenius tests, with both reduction cases

The complete allowed conductor in this calculation is P2000: every prime
11<=q<=2000 that is inert in K and1 modulo7. Its25 columns are all included.
This does not bound an arbitrary conductor. The complete112 candidates from
Block65's independently computed necessary system are the starting boundary.
The original Block65 archive is replayed, not replaced by a transcript summary.

The new test primes421,449,631,659 all split in K. Hence none belongs to this
stipulated inert conductor, and beta is unramified at every test place. This
justifies evaluating its unramified Frobenius class. It does NOT imply good
reduction of the curve. Every test includes both good and bad reduction.

## Complete actual good-reduction loci

Count the inherited smooth Frey family

    z^2=x^6+10 B x^3+12 A x+5 B^2,

on every necessary equation pair with A^3+B^5 a nonzero seventh power. Zeros
in A or B are included whenever admissible. Orbit reduction is performed
only for the curve counts; every orbit member is individually checked for
seventh-power equation admissibility. The independent square-table program
uses another field basis and discrete-log curve canonicalization, and checks
smoothness at every admissible pair.

|q|Admissible pairs|Residual pairs|Degree-one classes|Degree-two classes|
|---|---:|---:|---:|---:|
|421|25260|300|427|62|
|449|28736|512|449|48|
|631|56790|1350|637|103|
|659|61946|1128|659|83|
|Total|172732|3290|2172|296|

Each count implementation uses2172 degree-one and296 degree-two counts.
The independent program also performs172732 smoothness checks. A failed
necessary degree-one residual trace test can avoid the degree-two count;
such entries are explicitly null, not claimed as completed computations.
All four twist signs are positive at both split places, verified directly
from delta=9-3phi. Full quartics and orbit memberships are retained.

For N1,N2 the rational quartic has S=q+1-N1 and C2=(S^2-q^2-1+N2)/2.
The two rank-two trace corrections are computed over the COEFFICIENT field
k=F7[w]/(w^2-5), not by substituting a base-field radical. The independent
program reconstructs them from trace and norm in a theta^2-theta-1 basis.
The common-polynomial rule is enforced, rather than independent union choices.

## Compatible new reciprocity columns

In Z[zeta7], with coefficients in order1,zeta,...,zeta^5, use generators

    421: (-2,-2,-2,-2,1,1),
    449: (-2,-2,-2,-1,2,1),
    631: (-2,-2,0,-1,0,2),
    659: (-2,-2,1,0,0,-1).

Their exact norms are the named primes. Their seventh-root zeros are
370,25,441,307 respectively. They fix the root normalizations for the actual
natural Kummer rows:

    421: (3,5,6), (4,5,6),
    449: (1,5,2), (6,5,2),
    631: (5,6,6), (2,6,6),
    659: (5,4,5), (2,4,5).

For EVERY allowed conductor prime q, let g_q be the least primitive residue
generator and z_q=g_q^((q-1)/7). The rational opposite value is computed with

    R(ell,q)=-sum_(b=1)^6 b log_(g_q)(pi_ell(z_q^b)) modulo7.

The b weights are chi^-1 weights. No ordinary eta rows are substituted.
The independent checker works in the inverse cyclotomic basis, verifies the
norms by full conjugate products, and checks all600 terms by direct seventh-
power symbols rather than logarithm tables. At these split tests there is no
inert factor2; the inherited43 value retains its separate factor2.

## Good/bad rule and complete refinement

For each tuple (alpha,s), compute the common descended b=sum_q R(ell,q)s_q
and the two products of b with the natural Kummer rows. If the curve is good,
B62's actual trace-product identity and B64's finite-curve comparison require
both products in ONE actual quartic's correction pair. If the curve is bad,
the exact toric trace requires BOTH products zero. The accepted condition is
the union of those two alternatives.

Both separately coded filters give the complete staged lists

    112 --421--> 38 --449--> 12 --631--> 6 --659--> 2.

Every newly permitted conductor column was included, including columns whose
coefficient is zero in a particular tuple. No test is applied at a ramified
place, and no good reduction is assumed without justification.

## The Block65 highlighted tuple is excluded at421

For alpha=(w,6,1), with nonzero inertia197/337/547/673/883=(2,4,5,2,2),
the new421 row gives beta421=1. The natural products are1+3w and1-3w.
The actual good pairs at421 are

    {2}, {4}, {3+w,3-w}, {4+3w,4-3w}, {5+3w,5-3w}.

Neither required product occurs, and neither is zero. Good and bad reduction
both fail. This closes that particular actual configuration, not the entire
25-prime necessary system. The two new survivors are described separately.
