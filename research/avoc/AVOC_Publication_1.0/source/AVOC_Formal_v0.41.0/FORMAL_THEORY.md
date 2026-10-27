# AVOC v0.41.0: lifecycle recorder to calibrated policy

The new block proves the operational correspondence that v0.40 handled only for
individual fresh log events. It provides a finite lifecycle machine, a universal
source-generative refinement, and a final probability theorem over its actual
terminal samples. The physical correspondence between an external provider and
the generative source remains outside this theorem.

## Why pending intents need a separate registry

The inherited `CalibrationLog.record` is intentionally immutable. Reusing an
operation ID with a changed outcome is rejected. Consequently, putting an
unfinished event into that log and later appending success for the same ID
cannot finalize an operation. `inherited_unfinished_terminal_conflict` proves
this concrete obstruction. The new machine leaves the inherited log unchanged
and keeps pending intents separately.

`ObservationRecorder.State` contains a pending list of (operation ID, identity)
and a terminal event list. Its commands begin an intent or finish an event.
One global operation-ID namespace covers both lists and all identities.

- A fresh begin adds one pending entry. Exact repeated begin is unchanged.
- A late begin for the same completed ID and identity is unchanged; it cannot
  reopen the operation. A changed identity is rejected.
- Fresh completion requires the matching pending ID and identity. It removes
  that pending entry and appends one success, rejection, or fault event.
- Exact terminal replay is unchanged. Changed outcome/identity reuse, unbegun
  completion, and an unfinished terminal outcome are rejected.

From the empty state, every successful finite run preserves unique pending and
terminal IDs, disjointness, and the absence of unfinished terminal entries.
Terminal history grows only by suffix append. An accepted terminal event remains
exactly once through every subsequent successful continuation. Fresh checked
success/rejection adds true/false once; fault contributes no binary sample.
These are universal Lean statements about the defined machine.

## Source-generative refinement

`RecorderReveal` adds finite latent Boolean sources and an effective reveal
trace. Its commands are begin, report, and fault. A report for a fresh pending
operation constructs its terminal outcome from the next source Boolean. A
report replay finds the prior binary terminal outcome before inspecting the
remaining source, so it consumes nothing even after exhaustion. A fresh report
from an exhausted source is rejected. Report after fault and fault after report
conflict with immutable terminal history.

Each accepted transition emits an ordinary recorder command. Induction proves
both that those emitted commands reproduce the actual raw recorder state and
that the associated source state equals the inherited reveal machine on its
effective trace. In particular,

    samples(identity, terminalLog)
      = source(identity).take(samples(identity, terminalLog).length).

The completed-prefix and success-count identities follow. The proof no longer
supplies a separate next-bit equality for each fresh event: the generative
transition constructs that bit. This is not a test that an arbitrary external
reported bit has the correct statistical source.

## Full policy composition

`RecorderPolicy.gatedCounts` runs the entire generative command list. A rejected
run returns no counts. A successful run with any pending ID, including an
unrelated identity, also returns no counts. A fully resolved run reads each
scheduled first-n checkpoint directly from its terminal log.

The inherited `availableCount` additionally requires enough reports. Both false
and true count toward sample readiness, while only true contributes a success.
A later report cannot change the count for an earlier fixed checkpoint.
`recorderPlan` passes these gated counts to the existing optional quote planner.

For each identity k, retain v0.40's finite rational latent source with its
conditional fresh-outcome law and fixed p_k in [0,1]. A finite predetermined
schedule fixes identities, sample sizes, positive grids, and nonnegative error
allocations. The source law yields each prefix's binomial count law. The recorder
refinement yields the observed-prefix correspondence. Shared checkpoints can
remain dependent, and command selection can depend on the whole outcome space.

`recorder_episode_coverage` and `recorder_issued_failure_le` prove

    P(an issued plan lacks the stated episode certificate)
      <= sum_j alpha_j.

Neither successful execution, absence of pending IDs, completion, count law,
log-prefix equality, nor effective-trace equality is a supplied premise of that
final composition. Failure/unfinished outcomes remain in the original probability
space and issue no plan. The primitive source law, predeclared schedule,
parameter-stratum choices, and deterministic setup/gross memberships remain
explicit premises.

The certificate supplies the specified true probabilities and deterministic
values plus inherited Q/value bounds and expected finite-horizon policy regret.
Quotes remain fixed during the episode. The comparator keeps the same
conservative upper-setup reservation guard. The theorem does not assert that a
plan will be issued, that operations finish, or that collected data are cheap.

## Executable correspondence and limits

The Lean JSON endpoint uses the same raw recorder transition. Its index-aware
executor has a theorem equating its successful state with the formal core run.
It reports the first rejected command index and exposes no state on rejection.
The separate Python reducer is compared with an independent dictionary model
and the actual Lean endpoint over a declared finite family. This is bounded
Python correspondence, not a universal host-language refinement.

The raw executable accepts supplied success/rejection/fault labels. The
source-generative machine constructs labels. Applying the statistical theorem
to a raw log requires a justified correspondence between those two situations.
A syntactically valid or complete log does not prove that correspondence.

Terminal samples use completion order. If real outcomes affect their completion
order, independent attempted outcomes need not be independent outcomes in that
order. For example, completing the successful one of two fair attempts first
makes the first reported bit succeed with probability 3/4. Waiting until both
operations finish resolves every intent but does not remove the prefix bias.
The exact finite ordering obstruction is retained as executable review evidence.
In a stronger twenty-attempt fair model, all successes finish before rejections,
then all intents are resolved. With n=m=10 and alpha=1/10, at least ten successes
make the first ten reports return [3/5,1], excluding 1/2. That event alone has
mass 308333/524288, greater than 1/10. No observation is missing and no fault is
needed. This finite computation is not labeled as a new Lean theorem.

## Preserved earlier results

All 191 inherited non-audit modules remain byte-identical to v0.40. Their finite
calibration, conditional source laws, censoring obstructions, reveal invariants,
robust policy results, semantic artifact backends, and recovery theory remain
available. The preceding active theory is preserved in provenance/v0.40_release_top.
