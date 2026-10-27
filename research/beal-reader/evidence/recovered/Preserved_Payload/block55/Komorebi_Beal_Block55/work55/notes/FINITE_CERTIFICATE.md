# Exact finite certificate and its reduction

The universal theorem B55.3 is not an enumeration over Diophantine solutions.
For a declared set of possible high-congruence prime divisors it reduces
actual eta triviality to exact residue symbols and restricted matrix ranks.
The tested finite universe U has ten rational primes and twelve places.
It includes the inert h=3 prime1373 and is NOT asserted to cover arbitrary C.

## Primary implementation

maximal_layer.py imports a byte-identical copy of the previous phi-basis
residue arithmetic. For every place it computes complete seven-primary logs,
then reduces them modulo7. It constructs the five global rows and the three
natural Kummer rows in matching coordinates. For each of42 normalized F7
candidates it selects the Kummer zero columns and computes exact F7 rank.
It checks all1024 rational subsets of U.

It also enumerates all1585 prime-ideal subsets of cardinality1 through5. A
column subset is a circuit precisely when its kernel has dimension1 and
a kernel generator has no zero coordinate. A compatible circuit additionally
admits a normalized Kummer coefficient vector with nonzero ratio. The
universal circuit bound ensures these subsets suffice for the criterion.
The circuit-containment classification agrees with all1024 direct rank tests.

All2352 normalized F49 directions are separately enumerated. Their zero sets
are checked to be contained in the corresponding valid F7 zero set from the
proof of B55.4. Of these,2310 normalized directions are outside F7. None is
silently discarded or identified with the actual coefficients.

## Independent implementation

independent_certificate.py imports no primary arithmetic module. It uses
sqrt5-basis residue fields and direct seventh-power symbols instead of full
seven-primary logs. Each entire column is compared to the primary column up
to a single nonzero scalar. Prime tests, split roots, symbol orders, every
pairwise product and inverse of the five named units are checked directly.

Ranks are obtained from exact integer minors by fraction-free Bareiss
elimination, not the primary modular row-reduction procedure. All1585 subsets
are examined. Circuit minimality is tested by deleting each column. The
compatible circuits are tested against all2352 F49 directions, without using
the42-direction reduction. Their containment independently reproduces the
classification of all1024 rational supports. The coefficient bases differ,
but the complete sets of zero patterns and ranks agree.

## Observed finite results

124 rational supports pass the criterion;900 leave a first-layer survivor.
There are8 maximal passing rational sets and15 minimal surviving rational
sets. There are23 compatible prime-ideal circuits:6 of size2,8 of size3,9 of
size5. Natural Kummer rank is1 for6 circuits and2 for17 circuits.

The main H_* matrix passes all42 tests. Its seven columns have ranks checked
on every relevant Kummer zero set; the complete matrix is NOT required to
have independent columns. That distinction is essential: seven arbitrary
columns in a five-row matrix cannot all be independent.

The independent program checks360 named symbol products/inverses and625
exact determinant benchmarks, besides the complete direction and subset
classifications. Independent code is not an independent mathematical reviewer.

## Surviving certificates

The minimal two-place example97,293 has alpha=(0,1,1) and character vector
(6,1). The full JSON also records a five-place circuit over rational primes
883,1373,1471,1667. Its natural Kummer rank2 forces alpha=(0,1,1) if that
circuit occurs inside the actual maximal support. Neither fixture supplies
full actual Frobenius data or a Frey solution.

## Local arithmetic audit

local_maximal_checks.py checks8000 nonrational matrix instances, including
6080 with maximal eta ramification but unramified beta. The natural
upper-right valuation bound is tight in4000 cases. All1440 declared
principal-unit power tests verify that the highest character layer is
supported exactly at maximal inertia orders.

An independent direct integer calculation rechecks the Q491 negative control:
nonmaximal eta inertia can coexist with nonzero local alpha. No universal
statement is inferred merely from the finite sample counts.

## Eight small minors for the main H_* result

Use one-based column numbering in the seven-column H_* matrix in
ARITHMETIC_CONSEQUENCES.md, and row numbering(phi,2,3,sqrt5,7).
Every admissible Kummer zero set is contained in one of the eight sets below.
Thus these eight nonzero minors, together with the42-test zero-set coverage,
are a compact certificate for full diagonal triviality on H_*.

| Maximal zero columns | Selected rows | Integer determinant | Modulo7 |
|---|---|---:|---:|
|1,2,4,6|1,2,3,5|-66|4|
|1,3,4,5|1,2,3,5|-18|3|
|2,3,4|1,2,3|-5|2|
|2,4,5|1,2,3|-5|2|
|2,4,7|1,2,3|12|5|
|3,4,6|1,2,3|5|5|
|3,4,7|1,2,3|9|2|
|4,5,6,7|1,2,3,5|6|6|

The primary code computes these determinants by signed permutations. The
independent implementation recomputes them using fraction-free elimination.
