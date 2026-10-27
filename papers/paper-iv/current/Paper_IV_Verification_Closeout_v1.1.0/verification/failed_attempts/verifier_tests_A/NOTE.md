# Initial control-test failure

The first Python verifier-control run executed 38 tests. Thirty-seven passed.
The descendant-cleanup test failed because its 0.25-second total deadline expired
before the parent emitted its startup message. The test therefore did not establish
that a descendant had started. This failed receipt is preserved, not promoted.

The repaired fixture uses an explicit child-readiness file, separate bounded startup
and execution deadlines, and process-group termination. The production Lean runner
still uses its original bounded total per-command deadline. No Lean source or proof
hypothesis changed for this repair.
