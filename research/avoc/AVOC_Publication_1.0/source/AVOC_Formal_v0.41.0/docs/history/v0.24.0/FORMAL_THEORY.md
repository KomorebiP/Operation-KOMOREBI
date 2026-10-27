# AVOC v0.24.0 — prepaid durable component-upgrade campaigns

## 1. Preserved authority and promotion criterion

The inherited authority fixes a contract, a sound checker, valid lower and upper
utility bounds, evaluation/switching tariffs, credit, objective, core identity and
positive improvement margin. For old component v and candidate w, promotion still
requires U(v) + switchCost(v,w) + margin <= L(w), along with exact parent/revision,
core/objective, sound check and credit conditions. No new empirical utility bound
is inferred from receiving a candidate score.

The inherited step charges a funded trial even when rejected. Previously the
whole transition happened in memory after evaluation. This block separates the
reservation from settlement without changing the settled promotion decision.

## 2. Exact request and persistent state

A Ticket contains a run-scoped operation key, the COMPLETE pre-reservation
Upgrade.State, and an Upgrade.Proposal. Full-state binding includes trial count,
all evaluation expenditure, switching expenditure, and cumulative margin. Binding
only the active component and revision would miss paid rejected trials.

A Journal contains:

- current Upgrade.State;
- at most one pending Ticket;
- the ordered closed-ticket records, distinguishing evaluated outcomes and abandonment.

The physical backend separately retains canonical commands. It does not accept a
client's replacement campaign history as an authoritative deployment request.

## 3. Prepayment and its invariant

For ticket t, charged(a,t) copies the old state, increments funded trials, and adds
the protected evaluation tariff. It leaves active component, revision, switching
expenditure and guaranteed gain unchanged.

Journal safety requires Upgrade.Safe for current. If t is pending, it also requires
Upgrade.Safe(t.before), Funded(t.before,t.proposal), and current=charged(a,t).

Proved: charged_safe, begin_safe, finish_safe, abandon_safe and apply_safe.
A reservation counts an AUTHORIZED trial even if physical evaluation is interrupted.
Its recorded cost is not an assertion that all intended work finished.

## 4. Two-phase refinement of the original gate

reserve_exact gives the precise prepaid state. finish_reserved_exact then gives
exactly Upgrade.step(a,t.before,t.proposal).next, closes the ticket, and emits only
the original switching debit. The evaluation debit on finish is zero.

Therefore the settled decision is the original v0.23 decision. In particular,
prepayment is not subtracted twice, and an interrupted reservation cannot promote
by itself. Abandonment leaves current unchanged, so it never refunds that trial.
A finished evaluated request cannot subsequently be abandoned to remove its cost.

## 5. Idempotence and conflicts

begin_idempotent, finish_idempotent and abandon_idempotent prove exact repeated
requests return the same journal with zero additional debit. Reusing a closed key
with a changed ticket is an error. A new ticket with a stale complete parent state
is an error, even when its parent active version and revision still match.

Finish on an already abandoned key returns the existing abandoned disposition,
not a new evaluation or promotion. A new evaluation needs a fresh key and a fresh
reservation. The implementation additionally binds a campaign event epoch.

These statements concern canonical state and nominal charges. Replay and duplicate
inspection still execute validation and can recompute pure checks.

## 6. Complete replay and accounting

replay begins from the initial component and processes every accepted command.
Safe, active utility nondegradation, and the original endpoint net bound survive.
For a PaidTrace whose successful responses have evaluation debits e_i and switching
debits s_i:

    final.evaluationSpent = initial.evaluationSpent + sum e_i
    final.switchSpent = initial.switchSpent + sum s_i
    initial.evaluationSpent + initial.switchSpent + sum e_i + sum s_i <= credits

The proof follows each executable command, not only the final numerical labels.
Interrupted or abandoned prepaid reservations are included.

restore replays the commands and requires equality with the supplied complete
Journal. Successful restore is safe and exactly equals that checkpoint.
Restoration is idempotent. This does not authenticate a history's physical origin
or detect an adversary replacing both the log and matching checkpoint consistently.

## 7. Actual component dispatch

DurableUpgradeRuntime.checkedRestore returns a CertifiedJournal. Its current
component has the protected Contract. For the inherited catalogue, invocation
therefore equals the reference retry decision for every input satisfying
Retry.NoRevival. The runtime executes the stored version, not a caller-selected
replacement. Exact-value reporting is NOT part of this action-only contract.

## 8. SQLite publication and process interruptions

The Python driver sends the actual saved commands and snapshot to the Lean gate.
The database stores immutable request identities, contiguous event commands, and
an active dispatch pointer. Every changed command publishes its event, full
snapshot and dispatch pointer in one explicit transaction. Frozen authority and
selected source/runtime fingerprints are checked on every access.

A crash before begin commits leaves no authorized reservation. A crash after begin
commits leaves a paid pending evaluation. A crash during finish publication leaves
either the pending state or the complete promoted/rejected state, assuming the
SQLite/OS transaction contract. A crash after promotion but before a response is
reconciled by replay. Repeating finish does not add another switch or reservation.

The tests terminate actual processes and reopen the resulting SQLite database.
They do not prove SQLite, its filesystem, or power-loss durability.

## 9. Exact demonstration

The inherited incorrect always_retry candidate is charged 3 and rejected. The
threshold candidate is charged 3, passes, and has switching tariff 1. The declared
workload utility improves from -70 to -7. The endpoint net is therefore 56.
Repeated finish and repeated exact begin have no new nominal debit. The promoted
threshold component remains selected on reopen and executes 7 counted state visits
on the protected workload. This reuses the known specialization, not a new algorithm.

Checked examples also show a paid abandonment, failure-log omission rejection,
forged active checkpoint rejection, and equal active/revision values with unequal
full paid ledgers. A small current-state value cannot erase prior evaluation costs.

## 10. Remaining scientific scope

This is durable promotion of a fixed compiled catalogue under supplied sound
contracts and bounds. It is not arbitrary self-modification, autonomous candidate
generation, a production speed benchmark, a net-optimal metareasoning strategy, or
proof of sustained recursive improvement. Evaluation/replay tariffs remain nominal.
