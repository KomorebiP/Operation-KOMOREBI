# Beal research, Block 69
## Actual Frobenius refinement and an eight-prime support theorem

Version6.9.0. 20 September2026.

The two minimum seven-prime configurations from Block68 are excluded. Under the
retained geometric and representation hypotheses, actual depth one with COMPLETE
rational beta ramification at primes <=2000 now requires

    at least8 distinct ramifying rational primes;
    ramification at EACH of307,883,1483;
    normalized natural ratio a3/a5 equal to4 or6.

The full necessary system is not empty:18 tuples remain. No global Frey
representation or integer solution is constructed. This is not completion of
the reducible branch, the full (3,5,7) signature, or Beal.

## 1. Exact scope and the new tests

The authoritative predecessor is the original Block68 ZIP, SHA256
`e2ae63851e09a8a0304c83bd2d2c88b2204506f5a0f76014008d160ded3f0470`.
Its complete94-tuple cover was reproduced by its default verifier before release.
All28 conductor factors, including the degree-two factors307/797/1483, remain
included in every new Frobenius value. The coefficient domain comes from the
inherited all-depth theorem and the no-minus all-inert conductor argument.

Five new auxiliary primes are1289,1429,1471,1499,1709. They all split in
K=Q(sqrt5). The complete <=2000 eligible conductor list is all inert, so these
primes are outside beta's stipulated support. This justifies unramified beta
Frobenius evaluations, NOT good reduction of the curve.

At good reduction the two products alpha(F)*beta(F) must lie in the correction
pair of ONE actual Frey quartic. At bad reduction both products are zero. The
same rational equation residue has the same reduction type at the two places.
We keep both alternatives, with no arbitrary deletion of bad primes.

## 2. Actual finite curve data

The counted curve is z^2=x^6+10B x^3+12A x+5B^2. Every admissible pair is tested
member by member for A^3+B^5 being a nonzero seventh power.

| Prime | Admissible pairs | Degree-one counts | Degree-two counts | Residual-target pairs |
|---:|---:|---:|---:|---:|
| 1289 | 237,176 | 1,289 | 178 | 6,808 |
| 1429 | 291,516 | 1,431 | 208 | 4,692 |
| 1471 | 308,910 | 1,477 | 194 | 5,040 |
| 1499 | 320,786 | 1,499 | 238 | 4,922 |
| 1709 | 416,996 | 1,709 | 240 | 6,832 |

There are1,575,384 admissible pairs,7,405 first counts and1,058 second counts
in EACH implementation. The secondary implementation checks smoothness and
weighted-curve assignment for every admissible pair. A failed necessary first
trace test makes a second count unnecessary; such values are explicitly null.

The primary uses norm characters and weighted orbits. The separate program
uses a different quadratic-field basis, explicit square-root multiplicities,
and a different curve canonicalization. These engines are reused unchanged
from the verified predecessor and are hash-pinned. They share no arithmetic
imports with each other. Optional acceleration uses only bounded exact int64
operations, not floating point. No full group structure is inferred from counts.

## 3. Refinement of the complete predecessor cover

The exact stages are

    94 --1289-->74 --1429-->48 --1471-->42 --1499-->20 --1709-->18.

The primary refines every frozen tuple. A separate implementation reconstructs
trace correction pairs by trace/norm enumeration in another coefficient basis,
uses the independently rebuilt twisted columns, and reproduces EVERY stage case
and the complete18-tuple list. This is a complete refinement of the freshly
replayed predecessor cover, not a claim that the new program alone rederived
all upstream theorem reductions.

The residual support spectrum is8:2,9:12,10:4. Ratios4 and6 account for8 and10
tuples respectively. All18 ramify at307,883,1483. Four omit797; fourteen include
all three of307/797/1483. Thus797 is not forced by the current necessary system.

These counts concern normalized coefficient/character configurations, not
representations, solutions, probabilities or percentage completion.

## 4. A short explicit exclusion of the former minimum pair

The old pair had alpha=(+/-3w,4,1), with w^2=5 in the COEFFICIENT field, and
support307,463,617,883,967,1483,1723 with inertia5,4,2,3,4,2,5.
At1471 the new row on that support is

    (3,0,6,4,3,3,2),

so beta(F)=4. The two natural Kummer rows are(2,2,5),(5,2,5). The trace products
are therefore3+3w and3-3w. Neither is zero, and neither belongs to the actual
1471 good correction set. Good and bad reduction both fail. This exclusion
allows arbitrary additional divisors of C that do not alter beta's conductor.

The old seven-prime configurations remain preserved as countervectors to the
OLD necessary system. Their failure occurs only after the new actual data.

## 5. The exact eight-prime positive control remains

The two minimum surviving configurations are

    alpha=(+/-2w,4,1),
    support=(113,307,463,617,883,967,1483,1723),
    inertia=(4,6,2,3,5,6,1,2).

Their beta values at the five new primes are(4,0,5,3,2). The paired products are

    1289:3+/-2w;
    1429:0,0;
    1471:2+/-w;
    1499:+/-w;
    1709:6+/-2w.

Each pair is attained by one good Frey polynomial. At1429 zero is also allowed
by bad reduction. These tuples therefore genuinely survive the stronger finite
system. No simultaneous integer triple, integral endpoint realization, or all
smoothing-unit conditions have been supplied.

## 6. Failed routes and what did not change

An exploratory primary-only check at the inert primes113,127,197 found every
rational F7 correction available. In this descended regime those trace sets
supply no extra product restriction. The check is retained and replayable but
is not used for the arithmetic exclusion, nor called independently audited.
Any use at an actually ramified test place would require separate handling.

The attempted complete bounded-conductor exclusion FAILED:18 tuples remain.
The new lower bound is8, not9. The record deliberately tests rejection of an
invented zero-survivor result and of an inflated9-prime support claim.

The numerical conductor bound is on INDIVIDUAL ramifying rational primes.
Arbitrary extra C divisors unramified in beta are allowed. There is no bound
on an arbitrary conductor. The forced307/883/1483 conclusion is not asserted
when larger ramification is allowed. The prior local Frey positive families,
all-depth semilinearity, minus-component boundary and historical corrections
remain unchanged.

## 7. Verification and remaining goal

The default verifier deletes and rebuilds all16 scientific JSON outputs and
the generated fixture in a fresh scratch copy. It checks exact output hashes,
all payload hashes, ten immediate predecessor source members and six copied
source/input mappings. Its separate corruption tests reject changed degree-two
columns, an omitted conductor, a false zero list, an inflated support bound,
an invented common-polynomial pair, altered point counts and payload tampering.
Final fresh-extraction and archive-integrity results are recorded outside the
immutable ZIP to avoid self-referential checksum claims.

The original Block68 default replay passed in104.976 seconds in this block.
Its report and log are preserved. Earlier full historical-chain replays are
preserved as historical evidence and were not rerun here. No new Lean
compilation or independent mathematical review was performed. The universal
geometric and cohomological inputs remain explicitly conditional dependencies.

Next targets: the18 surviving configurations, especially the minimum pair
above, or an actual support-uniform period/endpoint/Frobenius constraint.
General higher depth, unrestricted support, the split minus component, integral
realization, CM and higher Hilbert branches, full signature and full Beal remain
separate open obligations.
