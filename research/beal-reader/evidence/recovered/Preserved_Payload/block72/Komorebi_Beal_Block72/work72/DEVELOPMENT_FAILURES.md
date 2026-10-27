# Failures, non-closures, and controls

The predecessor default replay and both new scientific implementations completed
successfully. There was no failed production arithmetic run in the development
phase. A process-status query after a completed exploratory run reported no live
process; its successful output had already been written. That is not treated as
an arithmetic failure or as a process still running.

The substantive attempted exclusion FAILED: all eight patterns admit higher local
lifts, with28224 augmented choices at the declared second precision. The proof
explains why higher local liftability alone cannot remove these residual choices.

Rejected strengthenings are explicitly tested:
- Dropping7c[7] modulo49 when7 does not divide c is false.
- Extending the error-power window using only1+7^(7c)O_F is unjustified;1+7^(7c)
  is a counterexample at the next level.
- An arbitrary lift of a square-root matrix modulo7 need not intertwine the
  period matrix modulo49.
- A global residual chi-line need not lift to a global line modulo49. The displayed
  two-generator matrix control disproves that inference.
- A successful local higher Kummer lift does not construct a global alpha_j at
  an unjustified precision, or the same global beta, or an ordinary integer B.

All historical failures remain in the exact unmodified predecessor ZIP.

## Incomplete provisional aggregate verification

The first direct tool invocation of the aggregate package verifier timed out at
the outer tool boundary before it wrote a final report. A subsequent process
listing showed no surviving verifier/scientific process. Its empty log and exact
provisional archive checksum are recorded in FAILED_AGGREGATE_ATTEMPT.json. It
is not counted as a pass or an arithmetic failure. The final verification is
launched as a separately monitored subprocess in a fresh archive extraction; only
its observed result is the final execution evidence.
