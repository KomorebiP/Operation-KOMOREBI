# Verification contract, Block55

## Observed startup and development

The authoritative Block54 verifier returned PASS_DECLARED_CHECKS in an
observed completed process, including Blocks53-51 and six selected historical
checks. Its fresh report and log are preserved in verification/.

All three new production programs completed successfully and agree with the
frozen JSONs. The portable exploratory scan is retained and replayed as a
fourth declared job. Exploration is not a separate authoritative theorem.

The final release verification report is intentionally outside the immutable
package. It records the actual fresh extracted-ZIP run, rather than making
a circular claim about its own checksum or a future execution.

## Complete finite assertions

local_maximal_checks.py: n3..12 with the stated ranges for e,t and primitive
unit families;8000 nonrational matrix cases,6080 beta-unramified cases,
4000 tight upper-right valuations;1440 principal-unit power tests; explicit
split-norm491 negative control. General generated Q values are not all norms.

maximal_layer.py: ten rational primes,twelve places; all42 prime-field
candidate directions, all2352 F49 directions, all1024 rational supports,
all1585 ideal subsets of size1..5; exact compatible circuits and maximal
passing/minimal surviving supports;8 small main-class determinant certificates.

independent_certificate.py: no primary arithmetic imports; distinct field
basis and symbol algorithm; full2352 F49 directions; exact integer-minor
circuit test on1585 subsets; all1024 support decisions;360 symbol checks,
625 determinant benchmarks,8 small minor replays, independent local negative
control. This is not independent mathematical review.

## Reproduction and integrity

Run python verify.py --replay-predecessors from the root. Each process has an
explicit configurable wall-time limit, and timeouts are inconclusive. There
is no random seed or floating-point proof decision. The runner records argv,
Python/platform, exit status, timing, output, and before/after source/payload
hashes. No additional CPU or memory cap is imposed by the runner.

Reports are outside the immutable package. Fresh output files are required
and complete JSON equality is checked. The predecessor ZIP and nine named
source hashes are verified, as are the two byte-identical copied arithmetic
modules. A final altered-payload control tests that integrity checks fail.

PASS means the declared exact finite assertions and integrity tests passed.
It does not prove the upstream geometric leaves, formalize the prose,
independently review the mathematics, or establish novelty or Beal.
