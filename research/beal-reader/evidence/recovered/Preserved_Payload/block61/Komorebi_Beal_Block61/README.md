# Komorebi Beal research — Block 61
## Twisted opposite-extension reciprocity and a depth-two support exclusion

Version 6.1.0. Research date: 19 September 2026.

The original Block60 ZIP in `predecessor/` is the sole execution predecessor.
Its bytes, nested predecessors, and historical corrections are unchanged.

**New conditional theorem.** At actual depth two, the opposite extension cannot
have all ramification above {197,883,1373,1667}. Consequently, under the inherited
actual Frey-representation hypotheses,

    COMPLETE H(C) subset U  =>  n=1,
    U={97,197,293,491,587,883,1373,1471,1567,1667}.

Additional low-congruence divisors are unrestricted. The four local families
from Block60 are retained. No individual one of their primes is universally
excluded when other beta-ramification primes are allowed.

Run with Python 3.10 or later, standard library only:

    python verify.py --replay-predecessors --report ../Block61_Replay.json

Reports must be outside this immutable package. The default per-job wall limit
is 180 seconds; a timeout is inconclusive. The optional predecessor replay runs
Block60 and its declared selected nested chain, not every experiment ever made.

Start with `work61/REPORT.md`, `TARGET_CONTRACT.md`, `PROOF_BOUNDARY.md`, and the
proof notes. `PACKAGE_SHA256SUMS.txt` binds all payload files. The final ZIP's
fresh-extraction audit is external to avoid a self-referential checksum claim.

Evidence: written proofs conditional on named inherited geometric inputs,
exact finite certificates, and a separate arithmetic implementation. No new
Lean compilation, independent mathematical review, or solution of Beal is claimed.
