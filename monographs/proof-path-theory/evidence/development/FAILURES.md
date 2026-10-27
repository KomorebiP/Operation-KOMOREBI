# Development failures and corrections

- The direct GitHub runtime download failed because the shell could not resolve the host. The complete seven-part offline archive was recovered from the user Library, its assembled SHA-256 verified, and extracted successfully.
- The first Python-based full runtime extraction exceeded the execution window after many files. A full `tar --zstd` extraction then succeeded. The partial extraction was not treated as the final runtime check.
- Initial Lean elaboration failures (unused simplifier arguments, a deprecated import, and insufficient unfolding for finite decision procedures) were fixed and the final statements recompiled. Logs are retained here.
- The first full verification wrapper was interrupted by the outer container call timeout after all seven source builds, all seven own-kernel replays, and the axiom audit. That interrupted run is not marked PASS. A separate complete invocation follows.
- Running `leanchecker --help` without the compiler on PATH failed to locate `lean`. The replay wrapper explicitly sets the correct PATH.
- The second wrapper invocation reached and correctly rejected the placeholder, but its exact diagnostic matcher expected single quotes rather than Lean’s backticks. The wrapper failed closed. The matcher was corrected before the final run.
- An initial explicit diagram equivalence exposed a universe restriction in `ViewDiagram.fiber`. The universe parameter was generalized; the statement now compiles at its intended generality.
- The third run completed all mathematical rejection checks; the custom-axiom report abbreviated the name inside its namespace, so the policy diagnostic matcher failed closed. Printing outside that namespace restores the full name and permits a strict final policy check.

The complete `verify_release.py` invocation subsequently finished with PASS, including all fresh Lean checks and corrected diagnostic matching.

A later synchronous verification call was interrupted by the outer tool execution window, closing its output pipe. Its RUNNING/FAIL reports were not accepted. The final delivery invocation runs to completion without that enclosing timeout.
