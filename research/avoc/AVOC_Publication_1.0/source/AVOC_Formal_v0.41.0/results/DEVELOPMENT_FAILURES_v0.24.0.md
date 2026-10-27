# AVOC v0.24.0 — development failures and repairs

1. Interactive container session allocation was unavailable. Runtime restoration
   and build/test jobs were run as supervised ordinary subprocesses within this
   task instead. All jobs completed before packaging.
2. An initial new-module check ran before its inherited VerifiedUpgrade import had
   been built. It failed at the missing .olean, not at mathematics. The dependency
   was compiled and that attempt was not counted as proof or negative evidence.
3. Early proof scripts treated Resolution match branches in constructor order rather
   than the branch order of the defined function. Explicit branch proofs repaired
   abandon safety/accounting. Cases that eliminated bound variables were changed
   to use the remaining target rather than nonexistent names.
4. A few reflexive Int inequalities needed explicit reflexivity after rewriting.
   An unnecessary simpa triggered warnings-as-errors and was replaced. The original
   do-style replay simplification was made more transparent by explicit Except
   pattern matching. Generic restore idempotence was corrected by substituting the
   proved actual-state equality before reusing its hypothesis.
5. No live promotion-store or oracle assertion failed in the final suite. Crash
   exits and rejected malformed/forged inputs are expected test outcomes, not
   successful research evaluation results.

Development compiler diagnostics are retained in results/v0.24.0/dev_*.log.
The final collector verifies current outputs and sources. No old or interrupted
log is substituted for a passing current compilation. External dependency cache
and machine correctness remain explicitly outside the fresh local-proof scope.
