# Recoverable run format, version 1

## Durable location

A new run directory contains `state.sqlite3`, `COORDINATOR_LOCK`, and `requests/`. SQLite is the authoritative source. It stores retained artifact text and proof data, not a reference to an uncommitted `state.json` update. Existing v0.19 JSON-store runs cannot be resumed with this adapter.

The caller must provide a protected local directory and use one cooperative coordinator at a time. Do not edit the database to clear an unresolved operation or change a consumed generation. Do not copy recorded test databases and assume they are portable resumable demos: their exact paths/environment/source pins are part of the historical evidence. Regenerate a fresh test/run on the target installation.

## Database records

`meta`: initialization header, exact configuration and source/environment pins, conservative attempt debits, status and last confirmed model-state summary.

`store`: one row holding native inherited gate state and optional checked receipt.

`operations`: contiguous run-scoped integer sequence; phase `intent`, `committed`, or `acknowledged`; selected action, exact formal intent, before native state/checked receipt, nominal fee, recorded recommendation; optional committed result, after native state/checked receipt and acknowledgement.

`invocations`: checker/planner/recovery process records. A started record without a completion is not counted as successful execution.

## Wire format sent to Lean

An intent is `[sequence, beforeView, actionWire]`.

A commit is `[intent, reportBool, afterView]`.

The store view uses the inherited exact projection: `[slot, checkedReceiptOrNull, admittedTicketOrNull]`.

The recovery request is:

```text
["avoc-recovery-v1", jobWire, identityWire,
 acknowledgedCommitList, incomingCommitOrNull, actualView]
```

The live raw checker has deterministic availability. Report bits used here are produced by actual stages and the declared gate, not user-provided success fixtures.

## State progression

1. Prepare intent and conservative fee debit in a transaction.
2. Execute inherited proof-stage checks into an in-memory gate state.
3. Publish native store + checked receipt + result + sequence phase atomically.
4. Send durable result and actual view to the Lean monitor.
5. Atomically mark that operation acknowledged and retain its confirmed model state.

A crash before 3 leaves an unresolved intent. Recovery refuses to infer a report or retry. A crash after 3 but before 5 can be reconciled without executing 2 again. A crash after 5 allows an idempotent duplicate acknowledgement. A stop operation can have an identical visible view before and after; its sequence result still records the commit.

If a physical write transaction was interrupted, SQLite recovery may write the database/journal while reopening. `inspect` performs no research-stage or planner invocation, but is not a guarantee of no operating-system writes.

Receipts are protected records, not cryptographic attestations. Changes by a hostile actor capable of replacing the protected store are outside this format's guarantees.
