# Observation reveal machine

`AVOC/ObservationReveal.lean` implements an explicit recursive machine on finite
per-identity Boolean sources. The state stores emitted reports and the remaining
source for each identity. A `none` operation leaves the state unchanged. A
`some key` operation removes that identity's next Boolean and appends it to its
reports, including `false` for a checked rejection. Exhausted identities are
unchanged.

The conservation invariant is proved for each transition and then by induction
over the trace. Consequently every report list equals the corresponding initial
source prefix. Once a report list is at least as long as its source, it equals
that entire source, and its success count agrees exactly.

The trace is arbitrary. It may therefore be instantiated by a function of the
sample outcome, supporting adaptive allocation and stopping. The result is
pointwise; it establishes no law conditional on completion. Calibration should
use a fixed latent source law and the inclusion of completed report failures in
latent-source failures, with incomplete reports blocked.

Two bridge theorems connect actual `CalibrationLog.record` calls to reveal
transitions for every identity: fresh checked events append the next Boolean,
and fresh fault events leave samples unchanged. They require existing samples
to agree with state reports, checked outcomes to equal the next latent Boolean,
and the operation identifier to be fresh. The inherited recorder rejects
conflicting identifiers and preserves samples for exact replays; the caller
must take a new checked reveal step only for a fresh event. This is a formal
local bridge, not a complete refinement of a deployed recorder or its storage.

No theorem in this module establishes IID sampling, authentic observations,
unbiased fault censoring, physical resource spending, or conditional coverage
among completed runs. Those require separate assumptions or results.

## Verification

- `reveal_build_02.log` and its JSON metadata: warnings-as-errors build passed.
- `reveal_audit.lean` enumerates all 18 theorems. `reveal_audit.log` reports only
  Lean foundational axioms (`propext`, `Quot.sound`) or no axioms.
- Closed kernel example: `[false, true]` with report/fault/report operations
  emits `[false, true]`.
- `FalseFaultConsumesObservation.lean` claims a fault consumes the first source
  Boolean. `FalseRejectionSkippedObservation.lean` claims the first rejection
  may be skipped. Both produced substantive `decide` proof rejections reporting
  that the closed proposition is false (`reveal_negative_fault.log` and
  `reveal_negative_rejection.log`); neither failed on setup or free variables.

## Development failures

The first build (`reveal_build_01.log`) was rejected by warnings-as-errors
because `initial_conserves` inherited an unused `DecidableEq Key` parameter.
The parameter was explicitly omitted for that theorem. No mathematical claim
was changed and no proof gap was suppressed.

A diagnostic `git diff` command failed because this restored checkpoint is not
a git working tree. It made no file changes and supplied no verification
evidence.
