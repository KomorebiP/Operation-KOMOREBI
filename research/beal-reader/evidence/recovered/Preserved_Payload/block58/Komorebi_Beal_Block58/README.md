# Komorebi Beal — Block 58, version 5.8.0

Good/bad Frobenius closure and discriminant rigidity.

Under the explicit inherited representation hypotheses, both five-place
highest-layer patterns retained in Block57 are now excluded. More strongly,
a nonzero highest layer must ramify outside the declared ten-prime universe U.
The new reciprocity matrix has full column rank without using the Kummer filter.

A separate discriminant argument proves n>=3 => 2549 divides C. Hence
COMPLETE H(C) subset U now implies n<=2 and eta=1. Depth two and depth one
remain unresolved. This does not prove the full signature or Beal.

Read work58/REPORT.md and work58/PROOF_BOUNDARY.md. The exact original Block57
ZIP, containing all earlier nested checkpoints, is in predecessor/.

## Reproduce

Python 3.10 or later, standard library only, from this package root:

    python verify.py --replay-predecessors --report ../Block58_Replay.json

The report must be outside this immutable package. The default per-job wall
limit is 180 seconds. A timeout is inconclusive. The verifier regenerates all
three new certificates, compares complete results, checks provenance and
payload hashes, and requires rejection of altered arithmetic.

No new Lean compilation or independent mathematical reviewer. Independent
arithmetic implementations do not independently certify the upstream geometry.
