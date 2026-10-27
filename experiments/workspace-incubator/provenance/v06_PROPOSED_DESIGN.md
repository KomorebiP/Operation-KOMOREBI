# Proposed v0.6: native access repair with working dynamics held fixed

Status: design only, not implemented or trained in v0.5.

## Why this is the next decision

Long-loop native factual recall remains poor for some program families even though
an external joint linear decoder recovers most retained facts. Repeating the native
cue does not repair it. The next question is whether cue-conditioned communication
and access can be repaired without relearning or protecting memory by fiat.

## Separate three claims

1. Information is available to a joint external decoder (observed diagnostic).
2. Agents can retrieve it through their own permitted cue/message interfaces
   (not established under the hard stress).
3. A compact naturally writable workspace mediates that retrieval (not established).

Do not count a readout trained on both full hidden vectors as success on2 or3.

## Candidate comparison

Freeze v0.5 parents before development. Retain both initialization lineages.
Compare a matched continuation with all weights trainable against an access-phase
repair with observation encoding and working-operation transitions held fixed.
Because observe/receive cells are currently reused in multiple phases, a genuine
phase-local repair must explicitly use separate copied access parameters or a
separately declared access adapter. Report the added parameters and extra compute.
It is not the same architecture merely because it begins with copied weights.

During access, the normal cue is supplied to both agents. Communication retains
the eight-dimensional receiver-only wires. No full-state central reader, semantic
latent coordinate, protected factual tensor or truth-bearing message is supplied.
Terminal correct recalled answers and private-memory objectives are allowed.
Do not supervise the desired Jacobian or message geometry.

Use matched mixtures of ordinary programs, long nonidentity words, neutral words
and repeated identity tokens. A chosen family may be used in development, but
hold out genuinely new lengths and program generators for the resulting test.
Preserve the same event/cue/answer contract and delayed consumer information barrier.

## Tests

Score all-eight-fact recall, current working computation, private recall and
recurrence depth. Compare with a joint supervised decoder as a descriptive ceiling,
not as an eligible agent. Test one-way/cut/shuffled messages during the access phase
separately from working-phase cuts. Monitor regressions on fresh/stale world events.
Use actual native histories, not artificially projected states.

If native access improves, rerun matched native working interventions and test
whether the active content remains separately manipulable from retained facts.
A new projection support audit is required before any localized-space claim.
The earlier failed support tests cannot be silently treated as repaired.

## Failure decisions

If only the external decoder succeeds, the gap remains native access. If the
all-weight control wins while an access-only repair fails, frozen working drift
may need joint repair. If only a higher-capacity adapter wins, distinguish capacity
from phase specialization. If current calculations regress, do not trade away the
previous working-state result to claim improved memory. Keep all failed lineages.
