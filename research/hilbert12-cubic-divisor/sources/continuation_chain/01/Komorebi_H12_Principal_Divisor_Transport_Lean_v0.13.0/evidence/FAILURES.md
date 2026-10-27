# Failures and corrections

1. The first H12PrincipalDivisor Lean draft failed at a rewrite under a
   dependent Decidable instance and at two semicolon-scoped local proof blocks.
   The exact source and compiler diagnostics are retained. Replacing the rewrite
   by an explicit conditional goal and case splits, and writing the local proofs
   as separate lines, corrected the proof scripts. The theorem statements were
   not weakened.
2. The first combined numerical run hit the 45-second host execution limit and
   produced no accepted result. Its source is retained. A process inspection
   found no surviving numerical child. The final version splits anchor,
   transitions at two points, and divisor diagnostics into synchronous stages.
   It also evaluates theta_t through the already-proved covariance to the s
   chart during continuation. Tolerances, samples, term caps and targets are
   unchanged. Every stage then completed at both requested precisions.

Mathematical negative result: R7/R7# has a genuine order-four zero at tau.
This is not a software failure or a counterexample to the conjectured equality
at the rational point 1/3. It refutes the global cancellation that would omit a
matching meromorphic section.
