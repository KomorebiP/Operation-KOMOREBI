# Verification contract and observed development checks

## Already observed before packaging

The authoritative Block53 run with --replay-predecessors returned
PASS_DECLARED_CHECKS. Its log and report are retained in verification/.
It covers Block52, Block51 and six selected earlier checks, not every
historical computation in every nested archive.

All four new exact programs completed successfully with the frozen outputs in
verification/. The final package verifier regenerates them rather than merely
reading these reference results. Its isolated release run is recorded in the
separate final verification JSON, outside the immutable package, so no report
has to assert its own checksum or future execution success.

## Finite contracts

frobenius_compatibility_checks.py: n1..9, natural contents1..6, slopes0..6,
explicit primitive coefficient families over Z[phi], with exact hypothesis
filters. 9952 accepted nonrational cases,216 nonunit-first-coordinate cases,
and one K-norm491 case. All new inequalities, local alpha-zero at beta support,
exact inertia orders, depth3 eta/beta implication, and local lift capacities
are checked. Generated coefficient Q values are not all residue cardinalities.

reciprocity_checks.py: exact residue fields over13,29,43,71, including both
split places; all five global rows, complete kernel and its F49 extension,
11060 logarithm multiplication checks and malformed-input controls. The old
q1504231 abstract character power conditions are checked but not called an
actual diagonal.

ray_quotient.py: six full/reduced presentations for P0, P0+491,
P0+491+1471; integer Smith operations with replayable unimodular certificates;
2793 exhaustive small group presentations. The joint depth3 test gives a
rank3 Kummer matrix and exhausts2352 normalized F49 coefficient directions.

independent_reciprocity.py: no imports from the other arithmetic programs.
A sqrt5 basis, full multiplicative generators and logs independently check10
places,6132 group elements; all117649 six-variable vectors; all16807
five-row relation combinations;1344 nonrational unit-order cases; independent
Smith certificate replay; exhaustive reduced presentations and the same
2352 normalized Kummer directions. Different column generators are compared
up to units, never mistaken for differing mathematics.

## Interpretation

A PASS means the declared finite assertions and exact replay checks passed.
It does not prove every inherited geometric leaf, formalize class field theory,
review a proof independently, establish a global novelty claim, bound arbitrary
C, or prove Beal. The universal implications are supplied as written proofs
with explicit hypotheses and classical dependencies. A timeout or failed run
is recorded as such and is never counted as a contradiction or UNSAT.

The release runner records argv, Python/platform, timings, actual exit codes,
stdout/stderr, exact source/result hashes, before/after package hashes and
resource caps. No additional memory or CPU cap is imposed; wall-time caps
are explicit. Numerical tolerances and random sampling are not used.
