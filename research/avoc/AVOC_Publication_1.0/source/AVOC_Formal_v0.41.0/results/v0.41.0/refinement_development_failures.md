# Recorder/reveal development failures

All Lean invocation logs and metadata are retained as `refinement_build01` through `refinement_build05_finalcore`.

- Build 01 failed: an unused simplifier argument, a dependent equation already substituted by case analysis, fault sample simplification using an overly broad simp set, incorrect tactic sequencing of Boolean branches, and omission of the state equality in the empty-run case. These were proof elaboration/lint failures, not evidence that the theorem statements were false.
- Build 02 passed the universal projection/prefix theorem block.
- Build 03 failed only the warnings-as-errors check for three unnecessary `DecidableEq Key` parameters in issuance-gate lemmas. Those lemmas need only decidable list emptiness, so the unused parameter was explicitly omitted.
- Build 04 passed the complete module including gate and six examples in 2.370 seconds, with an empty diagnostic log and source/import stability metadata.

- Build 05 recompiled unchanged source against the finalized core recorder import; it passed in 2.574 seconds with stable hashes.

The four files `FalseRecorderPendingPlan`, `FalseRecorderReportAfterFault`, `FalseRecorderReplayConsumesNext`, and `FalseRecorderExhaustionSuccess` each failed as intended with Lean reporting that `decide` proved the target proposition false. Their logs and provenance are retained under `refinement_FalseRecorder*.log/json`. None failed because of missing imports, parsing, resource exhaustion, or unavailable decidability.

The initial agent report counted 25 theorem declarations using an unanchored text pattern. That pattern also matched the prose phrase "theorem checks" in the module comment. The generated declaration inventory correctly contains 24 named theorems. No theorem was missing, and no Lean source changed for this correction.
