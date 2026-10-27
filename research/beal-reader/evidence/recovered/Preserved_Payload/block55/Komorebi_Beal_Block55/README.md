# Komorebi Beal — Block55 v5.5.0

Maximal-order Kummer filtering and actual diagonal triviality on stated
high-support classes. Start with work55/REPORT.md, TARGET_CONTRACT.md and
PROOF_BOUNDARY.md. Complete proofs, exact Python checks, source records,
negative controls and continuation instructions are included.

The original Block54 ZIP is preserved byte for byte in predecessor/ and
recursively includes the earlier checkpoints. The full reducible branch and
Beal are not solved. No new Lean certificate or independent review is claimed.

## Reproduce

Python3.10+, standard library only. From the extracted package root:

    python verify.py --replay-predecessors --report ../Block55_Replay.json

The same command works in PowerShell. The report must be outside the immutable
package. This checks payload and input hashes, replays Block54 and its selected
nested predecessors, then regenerates all new finite results in a fresh
scratch copy. A timeout is inconclusive.

To test a separately specified possible high-prime support, without modifying
frozen results:

    python work55/computations/maximal_layer.py --primes 197 491 883 1471 1667 --output ../support_test.json

A true all_42_tests_injective result excludes the actual eta only under the
written geometric and high-support hypotheses. A false result records a
surviving necessary first layer, not a realized Frey representation.

PACKAGE_SHA256SUMS.txt covers every payload except itself. Final archive CRC,
member-set, hash and fresh-extraction checks are recorded in a separate audit.
