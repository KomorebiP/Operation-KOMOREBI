# Block70 — Nine-prime classification and finite-sieve limits

The new conditional classification leaves eight normalized depth-one configurations.
With complete rational beta ramification at primes<=2000, every actual configuration
must have ratio a3/a5=6 and exactly nine ramifying rational primes. Six are mandatory:

    307,337,547,883,1483,1933.

The other three are precisely three of197,673,743,797, in one of four explicitly
recorded inertia patterns. Neither those patterns nor their eight coefficient
conjugates have been realized globally or excluded completely.

A separate result addresses the unrestricted-support problem: any fixed finite
collection of the present homogeneous zero-or-good Frobenius tests admits a nonzero
abstract inverse-cyclotomic character on a sufficiently enlarged conductor. An exact
24-row witness has21 nonzero ramification coordinates beyond3000. This is a theorem
about the specified necessary system, not an actual Frey representation, Beal
counterexample, or barrier to a proof with stronger arithmetic input.

## Actual new Frobenius constraints

The split tests2129,2269,2311 are outside the bounded beta conductor. Both good and
bad reduction of the curve are retained. All28 conductor columns, including the
three degree-two factors, are recomputed. The progression is

    18 ->14 ->12 ->8.

Two distinct arithmetic implementations cover2,145,002 admissible good equation
pairs, with6,717 degree-one curve counts and357 targeted degree-two counts. Every
omitted degree-two count has an exact trace or retained positive-witness reason.
The target-specific certificate does not pretend to list all good quartics.

At2269 the old eight-prime pair predicts scalar products6,6. Its trace/norm target
is(5,1). All41 admissible curve classes in the requisite trace5 slice are counted
to degree2; their actual residual correction pairs are6+/-w,6+/-2w,6+/-3w, never
{6}. Bad reduction would require zero. This excludes the old pair in both cases.

## Exact surviving patterns

|u|Ordered ramification support|Inertia|
|---|---|---|
|+/-3w|307,337,547,673,743,797,883,1483,1933|4,4,2,4,3,6,3,1,3|
|+/-3w|197,307,337,547,673,797,883,1483,1933|5,1,4,2,6,4,1,4,2|
|+/-w|197,307,337,547,673,743,883,1483,1933|1,5,4,1,4,1,6,5,4|
|+/-w|197,307,337,547,743,797,883,1483,1933|4,5,5,6,2,4,2,1,6|

Here alpha=(u,6,1) and w is the coefficient-field root, not the base radical. Every
tuple passes the new necessary tests. Extra unramified divisors of C are allowed.
A new ramified prime changes the global values and must add its column everywhere.

## Why another finite homogeneous list cannot handle unrestricted support alone

Chebotarev gives arbitrarily many inert q=1 mod7 where3 and5 are seventh powers.
At those primes phi and sqrt5 are seventh powers as well, so ALL natural Kummer
rows vanish. For N such primes the inverse-cyclotomic ray-character space has
F7 dimensionN. Each prescribed unramified test-zero value adds at most one linear
equation. Taking N larger than the number of equations yields a nonzero character
with every test product zero. The specified bad alternatives accept that abstract
data. No actual matrix representation or common global curve is produced.

The explicit calculation uses25 conductor primes between5167 and194167. Its matrix
has24 rows and rank24. A nonzero kernel vector has21 ramifying coordinates, all
natural Kummer rows zero, and all24 test values zero. A separate weighted-product
implementation verifies it. Local Hensel families at its supporting primes pass
the old level-seven period test, but no simultaneous integer B or global endpoint
is asserted. The infinite statement has a written proof, not merely this example.

This scoped limitation points to a different needed input: a conductor bound,
necessarily-good local requirement, nonhomogeneous character value, or a relation
from the same integral representation or global period data. It does not invalidate
the bounded exclusions or rule out a finite certificate using stronger facts.

## Evidence and correction

The exact original Block69 ZIP is preserved. Its current default verifier was
observed to pass in213.2 seconds. That was not a fresh replay of its entire nested
historical chain. The final Block70 replay is recorded outside the immutable ZIP.

A draft bug initially required beta(F)=0 for the bad alternative. It was corrected
to BOTH products zero, which also allows nonzero beta when the natural local value
is zero. The incorrect exploratory output and source are retained as unaccepted;
selected counts and both implementations were rerun. Corruption tests target this
boundary as well as count omissions, false survivors, residue columns and payloads.

There is no new Lean compilation or external mathematical review. The universal
arithmetic conclusions remain conditional on the inherited actual geometry and
representation hypotheses. Separate finite implementations are not a substitute
for independent acceptance of those proofs. No global novelty claim is made.

## Remaining tasks

The eight bounded configurations, unrestricted conductor and depth, the minus
component, integral realization, other signature branches, full signature and
full Beal remain unresolved. The all-depth semilinear theorem is preserved, not
reproved by this finite block. The next priority is an actual common global
constraint not already neutralized by the homogeneous zero-or-good alternative.
