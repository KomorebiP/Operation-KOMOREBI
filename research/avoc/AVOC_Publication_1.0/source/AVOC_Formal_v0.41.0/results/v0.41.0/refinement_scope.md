# Recorder/reveal refinement

The exact declaration inventory contains **24 named theorem declarations** for this module.

`AVOC/RecorderReveal.lean` defines a source-coupled virtual machine with begin, report, and fault commands. Its successful executions emit ordinary `ObservationRecorder.Command` values. The complete emitted list runs from the ordinary recorder initial state to exactly the recorded state. The same execution emits an effective trace for the inherited `ObservationReveal` machine. Every identity's terminal-log samples equal the reveal machine's reports and therefore form the initial segment of that identity's source.

The source-coupled machine constructs a fresh checked report from the next latent Boolean. It checks successful/rejected terminal replays before looking for that next Boolean, so a replay neither consumes a new observation nor fails merely because the source is exhausted. A fault finalizes its intent but consumes no source outcome. An unmatched operation, changed identity, report after terminal fault, or genuinely fresh report after exhaustion fails closed. Exact late begins do not reopen completed operations. An unresolved intent anywhere blocks the optional issuance gate.

Main interfaces:

- `run_refines`: complete ordinary recorder execution and reveal/log sample equality.
- `run_samples_eq_take`: recorded samples are each source's initial segment.
- `completed_samples_eq_source`: at completion, the samples equal the entire finite source.
- `completed_success_count_eq`: the corresponding success counts agree.
- `run_samples_length_le_source`: no identity emits more checked samples than its source contains.
- `pending_blocks_issue`, `resolved_allows_issue`, `issued_has_no_pending`: the issuance gate.

These results are universal over finite command lists whose modeled execution succeeds. They require no caller-supplied per-step next-bit premise. They do not authenticate physical operations, prove that an arbitrary external adapter implements the machine, or assert a physical sampling law. The probabilistic law remains a separately stated hypothesis on latent sources. A failed command produces no final state; no post-failure state is silently accepted.

Six kernel-computed examples cover mixed replay/fault/exhaustion behavior, final intent resolution, fresh exhaustion, unknown operation, changed identity, and report after fault. Four substantive negative tests establish rejection of pending issuance, report after fault, replay consuming the next Boolean, and fresh exhaustion succeeding.
