# AVOC v0.41.0

This release separates pending intents from immutable completed observations.
It proves unique global operation IDs, matching-intent completion, idempotent
replay, conflicting-reuse rejection, and no reopening after completion.

A source-generative model connects full recorder executions to the preceding
reveal machine. Fresh reports consume the next latent Boolean; replay consumes
none. The terminal log supplies the actual sample lists used by the policy.
Any rejected run, unresolved intent, or insufficient selected sample blocks
issuance. The final error bound remains unconditional over all runs.

The Python and actual Lean endpoints process exact finite command requests and
return snapshots. An optional injective identity registry exports completed
records in the existing calibration format. No command executes a paid operation,
stores a durable journal, or authenticates real observations.

Read FORMAL_THEORY.md and PROOF_BOUNDARY.md before applying the result.
RECORDER_EXECUTABLE.md describes the interface and bounded comparisons.
results/VERIFICATION_v0.41.0.md records the final release checks.
GAP_LEDGER.md and CONTINUE_HERE.md identify the remaining work.
