# Komorebi Beal — Block 57, version 5.7.0

Forced bad-prime Frobenius and augmented reciprocity.

The actual nontrivial highest diagonal-character layer CANNOT have ramification
contained in the two inert places above 97 and 293. This remains true when C
contains arbitrary additional prime divisors, including 197 and 491.

The key new input is local triviality at the forced bad primes above 11,19,31,
whose toric characters are distinct modulo seven. Their six prime-ideal rows
strengthen the old five-row ray-character presentation.

Start with work57/REPORT.md and work57/PROOF_BOUNDARY.md. The original Block56
ZIP is preserved in predecessor/, including its recursively nested releases.
No proof of the entire reducible branch, full signature, or Beal is claimed.
No new Lean compilation or independent mathematical review was performed.

## Reproduce

Python 3.10 or later, standard library only. From this package root:

    python verify.py --replay-predecessors --report ../Block57_Replay.json

The same command works in PowerShell. Reports must be written outside the
immutable package. The verifier checks payloads and source hashes, replays
Block56 and its selected nested checks, regenerates the three new certificates,
and requires rejection of a deliberately altered residue logarithm.

Per-job wall limits default to 180 seconds. A timeout is inconclusive.
PACKAGE_SHA256SUMS.txt covers every payload except itself. The final ZIP
replay and archive audit are external to avoid circular checksums.
