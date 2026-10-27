# AVOC Formal v0.22.0

A theorem-backed, executable operational retry advisor, built on the preserved
v0.21 library and paid-attempt ledger. It is read-only and never admits a proof.

The new exact threshold `retry iff affordable and p*benefit > fee` is proved for
fixed persistent latent-reliability types and a fixed nonnegative resolution
benefit. Faults lower predictive success in this model; improving-service examples
show why the threshold must not be applied universally.

- `FORMAL_THEORY.md`: definitions, theorem statements, and examples.
- `PROOF_BOUNDARY.md`: exact hypotheses and non-claims.
- `REPRODUCE.md`: pinned build, runtime advisor and test commands.
- `THEOREM_INDEX.md`: complete declaration inventory.
- `results/v0.22.0/`: current proof, axiom, regression and demonstration evidence.
- `CONTINUE_HERE.md`: durable continuation instructions.

Main new modules: RetryControl, RetryBayesian, RetryEvaluation, RetryLedger,
RetryExamples, RetryDecisionCodec. Inherited mathematical sources are unchanged.
Runtime/cached binaries are not redistributed. Counts describe named declarations,
not mathematically independent discoveries or empirical productivity advances.
