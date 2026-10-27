# Reproduction contract

Run `python verify.py --replay-predecessors --report ../Block61_Replay.json`
from the package root. Python3.10+ standard library only. No GP/Sage/Lean or
network access is needed. The report must be outside the immutable package.

The verifier validates the exact payload member set and checksums, the original
Block60 ZIP, and named nested source leaves. It extracts the predecessor into
a temporary directory and replays Block60 with its declared selected nested
chain when requested. Each new program runs in a scratch copy and regenerates
its output; the ENTIRE JSON must match the retained certificate. Source hashes
before and after must agree.

## Scientific assertions actually tested

- 13,608 exact natural-basis trace/determinant examples over Q(phi), including
  13,104 nonrational and3,402 depth2 instances, plus the failed-precision control.
- Seven cyclotomic integral generators, with exact prime norms verified by two
  different methods.
-72 direct residue evaluations forming the three twisted Frobenius rows.
-144 coefficient/prime-transport checks in the independent implementation.
- Six nonseventh phi symbols at the two split places over29,71,491.
- Twelve direct natural Kummer symbols at the four inert supporting primes.
- Exact rank3 and kernel k(1,0,0,3), including all2401 F7^4 vectors and an
  independent determinant/Cramer reconstruction.
-2352 normalized F49 natural directions times48 nonzero ray vectors:
 112,896 joint pairs, zero compatible pairs, reproduced independently.
-1296 base-prime reindexings and72 conjugate Frobenius-entry checks in the
 primary implementation, plus generator-inversion normalization independently.

The finite tests do not authenticate the analytic period theorem, prove the
class-number input afresh, verify all Galois representation hypotheses, or
replace the written reduction of the arithmetic problem to these assertions.

## Negative tests and provenance

The verifier requires the independent program to reject altered residue data,
a wrong Frobenius matrix entry, and an invented surviving-pair count. A copied
package with a modified proof payload must fail the integrity audit. Timeouts
are INCONCLUSIVE, never mathematical exclusion or expected rejection.

Run reports include argv, Python/platform, process IDs, UTC times, elapsed
wall times, caps, full stdout/stderr, and pre/post input hashes. Default wall
limits are180seconds per new job and15 times that for the predecessor chain.
No extra CPU or memory cap is claimed. Hashes bind this bounded assertion and
its exact inputs, not correctness of an external mathematical source.

No new Lean compilation or independent mathematical reviewer is present.
A separate implementation is an arithmetic audit, not a separate reviewer.
The final ZIP audit and fresh-extracted execution report are external outputs.
