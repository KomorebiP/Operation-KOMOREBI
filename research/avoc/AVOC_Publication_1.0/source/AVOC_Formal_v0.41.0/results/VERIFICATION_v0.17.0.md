# AVOC v0.17.0 — verification record

## Actual final result

PASS: **90/90 local compilation targets**,
**883/883 theorem axiom reports**,
**33/33 substantive negative rejections**.

The release adds 87 theorem/lemma declarations to 796 inherited declarations.
The 81 inherited non-audit modules are byte-identical to v0.16.0. There are
87 non-audit AVOC modules, 376 definition-like declarations and 14,321 non-audit
Lean source lines. Counts include helper lemmas and examples, not independent
mathematical discoveries.

## New modules

- `AVOC/FilteredObservation.lean`: 8 theorem/lemma declarations.
- `AVOC/ArtifactWorkflow.lean`: 16 theorem/lemma declarations.
- `AVOC/ArtifactWorkflowControl.lean`: 13 theorem/lemma declarations.
- `AVOC/ArtifactWorkflowGuarantee.lean`: 8 theorem/lemma declarations.
- `AVOC/ArtifactWorkflowSource.lean`: 8 theorem/lemma declarations.
- `AVOC/ArtifactWorkflowExamples.lean`: 34 theorem/lemma declarations.

## Build and trust scope

Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All nine dependency
revision pins were rechecked and no tracked dependency worktree changes found.
The seven-part portable kit passed the part CRC/SHA and combined SHA checks.

The local build directory began empty. The unchanged inherited targets were
compiled first; final versions of new modules and the aggregate were compiled
after the edits. Every final target has a current-source successful record, with
warnings treated as errors, matching source/output/log hashes and no timeout.
This is not a fresh source rebuild of mathlib or an independent Lean kernel.

The machine-readable audit records the container's actual UTC clock. Its timestamps
are runtime provenance, not inferred elapsed effort or promised user-local dates.

## Axiom and source audit

`AVOC/FullAudit.lean` names exactly all 883 inventory declarations. Its reports
contain only propext, Classical.choice and Quot.sound where required. There are
no custom or native-evaluation axioms. The independent comment-aware per-module
census matches the full index. Source scanning finds no proof placeholders,
project axioms, native_decide or unsafe proof declarations. The legitimate action
constructor named admit is not classified as a proof-placeholder tactic.

## Negative tests

All 33 negative files fail substantively, without import/setup errors, timeouts,
or merely deprecated syntax. The five additions attempt to claim:

- rejection leaves the prior probability 1/2 instead of 1/4;
- public rejection has the posterior of one hidden raw reason (1/3);
- verification has already completed the task;
- rejected verification consumed the pending ticket;
- the complete successful path spent only two, rather than three, units.

Positive library theorems independently prove the contrary facts. Failed proof
scripts alone are not treated as mathematical negation proofs.

## Independent exact model checks

`checks/test_artifact_workflow.py` uses fractions.Fraction, not floating point:

- 9,000 finite reported-channel comparisons;
- 3,798 zero-predictive-mass report entries included;
- 45 workflow configurations;
- 1,689 reachable state instances and 4,812 transition checks;
- 162,870 adaptive-tree value combinations evaluated, including subtrees and
  repeated values, compared with a separate Bellman maximization calculation.

The tested worlds have two states and three raw outcomes. Channel rows use a
fixed rational grid; reporting maps range over all Boolean maps on the three
outcomes. Workflow enumeration includes both possible report branches, including
zero-probability ones. These are finite implementation checks, not exhaustive
real-world process validation.

The numerical witness agrees with the Lean results: posterior 3/4 after success,
1/4 after public rejection, registered two-step value 5/2, initial three-step
value 3/2, and total successful expenditure three.

## Real checker and file checks

The inherited executable checker/gate regression was rerun for this release:
6,363 proof comparisons, 692 truth-table implications, 35 binding comparisons,
21 real-file cases (19 expected rejections), and 20 actual single-request checker
invocations. Historical v0.16 logs were not substituted.

The new six-case stage test made five additional actual checker invocations.
It confirms retention after verification rejection and rejected admission,
no admission by verification alone, stale-generation rejection, consumption on
successful admission, and receipt replay rejection. These engineering tests do
not prove a full filesystem/MDP refinement, and the inherited Python API does not
itself maintain the new Bayesian controller state or its nominal fee ledger.

## Evidence locations

- `AUDIT.json`, `SOURCE_PROVENANCE.json`
- `results/v0.17.0/final_local_build_summary.json`
- `results/v0.17.0/axiom_audit_summary.json`
- `results/v0.17.0/negative_summary.json`
- `results/v0.17.0/source_scan.json`
- `results/v0.17.0/input_integrity.json`
- `results/v0.17.0/workflow_regression.json`
- `results/v0.17.0/artifact_gate_regression.json`
- `results/v0.17.0/reported_file_stages.json`

Payload integrity is an additional packaging check, not a substitute for the
above proofs and tests. See the development-failure record and proof boundary.
