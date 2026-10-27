# Costed retry store format 1

`schema=avoc-costed-retry-store-1`. New initialization only.

Inherited tables retain logical operations and canonical native proof state.
Added tables:

- `attempts`: globally increasing generation, logical operation, fee, phase and
  unique authorization identity. Phases include active, superseded, published,
  settled and abandoned.
- `resolutions`: unique caller key, command kind, expected generation, operation,
  and resulting generation where applicable.

Meta includes frozen `[attempt_credit,attempt_count_limit]` and the Lean ledger:

    [charged,confirmed,reserved,currentTicketOrNull,published,terminal]

A ticket is `[logical_operation,attempt_generation,fee]`. These attempt generations
are separate from the proof artifact's own registration generation.

For a retry, the writer holds the same exclusive run lock used for normal stages,
checks the current uncommitted database row and full before-state, invokes the Lean
renew gate, and atomically records the charge and new attempt. Only then may stage
work run. Publication compares the current attempt ticket again. Old attempts are
retained as superseded rows and cannot publish. State/result/publication-account
changes are in one transaction; settlement follows the exact semantic monitor.

The committed proof history still has one operation per logical action. Failed
attempts do not create entries in that scientific history. Replay remains governed
by the inherited CommitRecovery monitor. The attempt ledger stores their costs.

An authorization key is idempotent for execution: if its request was already
reserved, the same key cannot initiate computation again. Reusing the key with a
different command or expected generation is rejected. There is no automatic retry
loop. Administrative abandonment clears the operational reservation and closes the
run while retaining its paid charge and last confirmed scientific checkpoint.

A fault during a ledger transaction may roll back diagnostic monitor-call rows
alongside the rejected transaction. This system does not claim complete physical
CPU-cost accounting. Scientific proof calls and nominal reservations are not
confused with those diagnostic counts.
