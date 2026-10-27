# Collections and actions verification

Author: **Komorebi P.** · 2026-09-06

The release passes **38 behavioral tests and 25 live command-line checks**. The complete recorded workflow reloads four workspaces and replays five saved revisions. No model training or ARC benchmark was performed.

## Demonstrated behavior

| Check | Result |
|---|---|
| Same-color component extraction | Three objects, with areas 3, 1, and 2 in scan order |
| Authored area filter | Keeps two objects and preserves the smaller distractor |
| Map and fold composition | Moves selected pixels while retaining source scene context |
| Supplied two-column movement proposal | Ten target-cell mismatches before the edit, zero afterward |
| Preview | Leaves the workspace bank unchanged |
| Receipt saved and bank reloaded | Candidate commits with its predicted outputs |
| Duplicate commit after revision advances | Rejected as stale |
| Collision attempt | Rejected without a workspace commit |
| Unmet required target | Rejected without a workspace commit |
| Branch edit and undo | Preserve the other branch and restore the expected head |

The example program, object grouping algorithm, movement proposal, and target are all authored. The ten-to-zero mismatch change checks evaluation and commit behavior. It is not an induction score or evidence that a controller learned the movement.

## Coverage

The 21 earlier machinery tests continue to pass. Seventeen additional tests cover:

- Typed empty collections, round trips, type mismatches, collection limits, and rejection of nested collections.
- Four-way versus eight-way connectivity, same-color grouping, deterministic order, and exact pixel coverage.
- Translation bounds, origin/source preservation, duplicate-coordinate rejection, and stale source pixels.
- Map, filter, and fold composition, preserved item order, empty-collection behavior, and shared execution budgets.
- Rejection of a collision after an earlier item has already produced a temporary fold result, with the entire bank unchanged.
- Observation, proposal evaluation, per-output residuals, and successful commit.
- Rejection of changed, stale, or library-incompatible receipts.
- Target requirements and protected-output constraints.
- Named graph rebinding and invalid-reference rejection.
- Receipt serialization, process-style bank reload, and persistent nested values.
- Explicit shape errors and signed scalar residuals.

The 25 command-line checks exercise both the existing CLI and the new JSON action interface. They cover observation, proposal exports, collision and target failures, commit after reload, duplicate commit, changed receipt data, object-value inspection, fork, compare, undo, graph edits, creation from program files, trace export, dependency inspection, history, and listing.

## Compatibility and provenance

Seven v0.6 example outputs, including the original grid pipeline and scalar workflow, match their saved earlier results in the new runtime. This checks representative behavior rather than proving universal backward compatibility.

The frozen kernel implementation, model checkpoint, and catalog remain byte-identical to their corresponding v0.6 files. The complete v0.6 archive is included unchanged, with SHA-256:

```text
2054ffcc6a014ce1cb29addd49600bf072b24dd1ac7b00c3a2cbb1f036583878
```

It contains the earlier complete v0.5 release. Native-source identities and the bank schema change in v0.7. Old bank files are rejected rather than silently relabeled. An automatic migration procedure has not been implemented.

The demonstration registry contains 29 supplied native operations, three frozen learned kernels, and three authored functions. None of the new collection or action machinery was learned.

## Limits of this verification

These are small, deterministic engineering workflows. Long histories, high-volume workloads, cross-scene object correspondence, automatic object grouping, autonomous action selection, and training from traces are untested or unimplemented.

Scalar replay allows an absolute tolerance of 10⁻⁹ by default. Categorical and geometric values require exact agreement. Receipt integrity checks are checksums, not cryptographic signatures or access controls.

Python was tested on Linux. The PowerShell wrapper was inspected but not executed on Windows. All ordinary runtime actions are local after dependency installation.

Machine-readable results are in `results/verification.json`, individual test results in `results/tests.txt`, and complete example records in `examples/recorded_run/`.
