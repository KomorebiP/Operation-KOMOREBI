# Blocks 29–30: verification and finite-computation contract

Authoritative predecessor: the attached checked Block28 archive. Source predecessor
modules remain byte-identical. The previous Blocks29–30 candidate is historical
unverified evidence, not an alternative authoritative predecessor. This release
repairs its IdealClosureExamples proof only; none of its 78 theorem statements
changes.

The generic exact Python suite uses prime bases 2,3,5, precision r=0..3,
dimension 0..3, alphabet sizes 0,1,2, and three seeded random systems per tuple:
432 base systems plus the two specified nilpotent/correlated witnesses. It tests
capped valuations, generator membership, exact ideal transfer, bounded closure,
leastness against every profile where dimension<=3 and r<=3, gcd-based independent
ideal closure, cyclic coordinate roundtrips, and ordered transition simulation.
Small ideal boxes of cardinality<=128 are fully enumerated; larger boxes use
12 seeded vectors. Integer division is exact and all arithmetic is arbitrary
precision. Seed: 20260921. One equality of vectors counts as one assertion.

The actual-mask extension executes 72 deterministic mask/precision tuples
(p=2,3,5; r=1..4; six explicitly listed masks per pair), then four named stress
executions. Some stress tuples duplicate base cases; distinct-case count is
reported separately. Each case tests all complete transition columns against
independent polynomial multiply/Cartier-section/routing, compares valuation
closure with integer-gcd ideal closure, tests random admissible ideal vectors,
and compares 32 coefficient outputs with both the direct Mahler recurrence and
the unchanged support machine. Seed: 29302026.

Lean compilation, all-source-theorem #print axioms, imported-project theorem
constant inventory, extra kernel replay, positive examples and expected negative
controls are separate phases. Source and verification input SHA256 maps must be
unchanged during each final phase and match the released files. A nonzero exit
is not sufficient for a negative-control pass: the exact contradiction or sorry
diagnostic is required. Timeouts are inconclusive. Only final_* phases are fresh
authoritative verification; dev_* and history/* retain failed/development evidence.

Finite tests are not universal proofs. The Python implementation is not formally
proved equivalent to generated Lean machine code. Coordinate-ideal leastness is
not correlated-submodule minimality. Ambient p-adic digit exponents are not
runtime memory or bit-operation measurements. Runtime restore uses the exact
retained RC2 archive; dependencies are hash-pinned caches, not independently
rebuilt from source. The installed external manifest validator is not executed;
this release uses the included read-only hash/exit/coverage validator and retains
all machine-checkable input/output hashes in per-command records.
