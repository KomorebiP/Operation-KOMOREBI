# Komorebi Beal — Block 56, version 5.6.0

Actual Frobenius precision and the complete high-support 97/293 branch.

The main new results under the explicit inherited hypotheses are:

    491 not dividing C => actual depth n=1.
    197 not dividing C => n<=2 and the actual eta_n is trivial.

Thus H(C) subset {97,293} has depth one, while a highest-layer support of
97/293 with additional high divisors is not universally excluded. Beal and
the full retained reducible branch remain unsolved here.

Start with work56/REPORT.md, TARGET_CONTRACT.md, and PROOF_BOUNDARY.md.
The exact original Block55 ZIP is included in predecessor/, recursively
preserving all earlier checkpoints and their distinct verification boundaries.

## Reproduce

Python 3.10 or later, standard library only. From the extracted package root:

    python verify.py --replay-predecessors --report ../Block56_Replay.json

The command also works in PowerShell. The report is written outside the
immutable package. The verifier checks all payload hashes, 13 named inherited
source leaves, the original predecessor bytes, selected predecessor replays,
and fresh complete results from all three production scripts. It also tests
that the independent counter rejects a deliberately altered point count.

Each production subprocess has a configurable wall limit, 180 seconds by
default. A timeout is inconclusive. No new Lean certificate or independent
mathematical review is supplied. Independent finite implementations do not
certify the inherited geometric hypotheses.

The exploratory NumPy files are frozen provenance, not required replay
commands. Production reproduction requires neither NumPy nor a compiler.

PACKAGE_SHA256SUMS.txt covers every payload except itself. The final fresh
ZIP replay and archive audit are recorded outside this immutable package.
