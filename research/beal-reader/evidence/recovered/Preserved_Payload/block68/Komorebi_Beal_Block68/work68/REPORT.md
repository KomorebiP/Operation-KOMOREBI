# Beal research, Block 68
## Degree-two cyclotomic conductors and a seven-prime support bound

Version 6.8.0. 20 September 2026.

The next bounded block is complete. Under the retained actual geometric and
representation hypotheses, an actual depth-one opposite extension whose EVERY
ramifying rational prime is at most 2000 must ramify at at least seven distinct
rational primes. At least two of them belong to {307,797,1483}. Its normalized
natural coefficient ratio a3/a5 is 4 or 6 in F7.

This is not an exclusion of the whole bounded class. The full necessary system
has 94 surviving tuples. It is not a proof of the complete reducible branch,
the (3,5,7) signature, or Beal. The size bound is on individual ramifying primes,
not on the numerical conductor product and not on all prime divisors of C.
Arbitrary additional C divisors unramified in beta are permitted.

## 1. What changed

The prior complete 25-prime class consisted of inert primes q=1 modulo 7 up to
2000. The inherited complete geometric-eligibility scan has three more primes
in this range: 307,797,1483, all inert and -1 modulo 7. They do NOT split
completely in Q(zeta7). Each has three prime ideals of residue degree two.

These three conductor columns are now computed and included simultaneously in
all actual Frobenius values. The old 25-prime calculation still gives zero,
but adding all three columns gives 532 tuples under the frozen old tests.
Three new actual Frobenius tests reduce this to 94, not zero.

The declared all-inert support allows the opposite cohomology class to descend:
the all-depth two-twist theorem, absence of inert ramification for its minus
part, and the inherited fixed-prime/inertia-injectivity inputs kill that part.
This is not descent of the Tate lattice. In this scope the normalized natural
class has alpha=(v*w,r,1), v,r in F7*, and normalized opposite inertia is F7-valued.

## 2. Correct residue-degree-two reciprocity

For a conductor prime q with residue degree f in {1,2}, choose a primitive
residue element g, put z=g^((q^f-1)/7), and use its logarithm modulo seven.
For an integral generator pi_l of an unramified test prime, the row is

    R_(l,q) = -f^(-1) sum_(b=1)^6 b*ell_q(pi_l(z^b)) mod 7.

The coefficient b is the inverse-cyclotomic covariance in these conventions.
When f=2, b and -b describe the SAME prime ideal. The residue Frobenius changes
the logarithm's sign, so their weighted summands agree. Dividing the embedding
sum by two, or summing once over {1,2,3}, counts each prime ideal once.

At all three new primes, the natural Kummer row (phi,3,sqrt5) is (0,0,0).
They cannot be discarded using the old ratio filters. The complete data include
all residue evaluations, primitive-element checks, Galois reindexings and the
three irreducible quadratic factors of Phi7 at each new prime.
See notes/DEGREE_TWO_RECIPROCITY.md.

## 3. Three new actual Frobenius certificates

The actual counted curve is

    z^2=x^6+10 B x^3+12 A x+5 B^2.

Every good equation residue requires A^3+B^5 to be a nonzero seventh power.
Admissibility is checked member by member; weighted curve isomorphisms are not
assumed to preserve that condition.

|Prime|Admissible good pairs|Degree-one counts|Degree-two counts|Residual-target pairs|
|---:|---:|---:|---:|---:|
|701|70,100|705|108|1,700|
|911|118,430|915|116|1,976|
|1009|145,296|1,011|163|2,736|
|Total|333,826|2,631|387|6,412|

Both point-count implementations agree. The second checks polynomial smoothness
and class membership at every admissible pair. Degree-two counts are omitted
only after a failed necessary degree-one condition; these entries are null.
The counters use exact integers, not floating approximations. NumPy, when
available, only accelerates bounded int64 operations; scalar fallbacks remain.

All three primes split in K and are outside the stipulated all-inert beta
conductor. Thus beta is unramified there, but the curve need not be good.
The filter allows either one ACTUAL good quartic accommodating both split-place
products, or the bad-place product zero. No auxiliary good-reduction assumption
or false contradiction from a newly forced divisor is used.

## 4. Complete enlarged calculation and exact surviving support

All 28 columns are included. The finite refinement is

    532 --701--> 288 --911--> 138 --1009--> 94.

The primary uses incremental affine-space splitting. The separate solver uses
an invertible basis of Frobenius-value rows, enumerates all permitted values on
that basis, and checks the remaining equations. It returns the IDENTICAL full
candidate list. The old 25-prime subclass is independently recalculated as zero.

Among the final 94 tuples, 28 have ratio 4 and 66 have ratio 6. Their rational
ramification sizes are:

    7 primes: 2 tuples; 8: 30; 9: 38; 10: 24.

The new-prime subsets have these exact counts:

    {307,797}: 8; {307,1483}: 12; {797,1483}: 10;
    {307,797,1483}: 64.

Therefore an actual depth-one beta with all ramifying rational primes at most
2000 needs at least SEVEN distinct ramifying rational primes and at least TWO
of the three new primes. This excludes the bounded cases with at most six
ramified primes, or with at most one of the three new primes. It does not force
any particular single prime among the three, and it is not a support bound
for unrestricted conductors.

## 5. Explicit minimal survivors

The two minimal-support candidates are

    alpha=(+/-3w,4,1),
    support=(307,463,617,883,967,1483,1723),
    inertia=(5,4,2,3,4,2,5).

The opposite values at 701,911,1009 are respectively 2,1,4. Their required
paired products are 6+/-2w, 1+/-2w, 5+/-2w. Each belongs to one actual good
polynomial pair at its corresponding test prime. These are genuine survivors
of the stated necessary system, not a rounding artifact or omitted case.

They do not construct a global Frey representation, the common integral
endpoint lattices, all smoothing-unit/fixed-prime data, or an integer solution.
The prior local positive Frey families remain valid. A further actual global
constraint is needed to distinguish these tuples from realizable arithmetic.

## 6. Audit of the all-depth proof

The separate logical pass found no defect in the DISPLAYED conditional chain:
the determinant identity, the two precision inequalities, actual-image
separation by distinct cyclotomic weights, the commutator on the deep abelian
cyclotomic tower, joint-kernel normality, good Chebotarev realization, and the
union-of-two-kernels argument. The final cohomology restriction uses the
commutator first and the prime-to-seven degree-six restriction only afterward.

This is same-assistant self-review, not external independent acceptance. It
retains the actual Frey/RM, half-depth precision, analytic period, and common
cocycle normalization inputs. It does not prove an integral Tate-lattice
comparison, full eta triviality, ordinary descent without its extra hypotheses,
or unrestricted higher-depth vanishing at 13. See notes/ALL_DEPTH_AUDIT.md.

## 7. Evidence and reproduction

The exact original Block67 ZIP is preserved. Its full selected nested replay
completed in this session with exit zero; the observed execution record is
stored in verification/Block67_Replay_exit.json. That replay took about 645.4
seconds. New development proceeded while it ran; it had completed before
release packaging.

The new release verifier deletes all 13 scientific output JSONs and the generated
extended fixture in a clean scratch copy, regenerates them, compares their full
contents, checks every package hash, and resolves 19 exact named inherited
source leaves. The old fixture is reconstructed from its three pinned source
outputs, rather than trusted merely by filename.

The separate residue checker performs 2,682 direct symbol checks, 2,682
conjugation checks, 384 degree-two representative tests and 168 cyclotomic-unit
checks on the extended table. The separate finite solver checks 2,596 right-hand
side assignments on complete invertible-row-basis covers across the two declared
universes. These are exhaustive algebraic covers, not counts of representations.

Optional-vector/scalar agreement is checked independently of the large runs:
1,158 primary backend comparisons at 11,13,17, and a full secondary reference
at 29. These audits are explicitly backend comparisons and do import the two
count modules. The separate scientific count, column and sieve implementations
do not import primary arithmetic.

The default release replay runs all NEW tests. The retained full historical
replay is separate evidence; add --replay-predecessors to execute it again.
Final fresh-extraction execution and archive-integrity records are external to
the immutable ZIP. No success flag replaces a regenerated scientific output.

## 8. Failures and remaining goal

The attempted universal exclusion of the bounded 28-prime system failed: 94
necessary-system tuples remain. No new production arithmetic run failed in
development. Deliberate corruptions are required rejection controls, not hidden
scientific errors. Broad source searches were unhelpful; direct author-hosted
PDF theorem pages were inspected instead. All historical failures remain nested
unchanged.

No new Lean compilation or independent mathematical review occurred. General
higher depth, unrestricted prime support, the split minus component, integral
realization, CM/higher Hilbert branches, the full signature, and full Beal remain
separate unresolved obligations. The next target is an actual common-global
constraint on the 94 tuples or a support-uniform obstruction, not an assertion
that another finite zero test has solved the unrestricted problem.
