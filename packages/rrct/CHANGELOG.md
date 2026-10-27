# Changelog

## 0.60.0.dev1

### Persistent fuzzy-to-J bridge

- Added an evaluator-blind, pure-NumPy experiment joining learned fuzzy coalition formation to a moving Jacobian-discovered sparse workspace.
- Added a serial causal ladder spanning membership, J-space access, broadcast, provenance-conditioned planning, and consequence-driven recurrence.
- Added same-rank PCA and seeded random-subspace controls plus longest-supported-prefix reporting.
- Added membership-shuffle, J-space-cut, broadcast-cut, provenance-cut, planner-cut, and feedback-cut interventions with explicit upstream-preservation measurements.
- Added exact checkpoint/resume of gates, readouts, moving frame, event fabric, counters, rows, and RNG state.

### Public instrumentation surface

- Added immutable `JacobianFrame` and resumable `MovingJacobianFrame` NumPy APIs.
- Added sparse nonnegative coding, reconstruction, swap, projection, ablation, idempotence, Jacobian-energy, activation-variance, and reportability measurements.
- Added an optional local-only Hugging Face decoder adapter with residual hooks, target-token VJPs, norm-matched patching, and projector ablation.
- Forced local model paths, `local_files_only=True`, `trust_remote_code=False`, and lazy optional dependency loading.

### Reliability and scientific corrections

- Bound sweep cell identities to the resolved base-configuration digest and reject mismatched ledgers.
- Verify completed-run configuration, summary, run-state, and checkpoint digests before resume skipping.
- Moved checkpoint/runtime ownership into experiment-registry metadata.
- Marked the v0.59 continuous runtime as an oracle-assisted legacy scaffold after confirming evaluator-state copying in its repair path.
- Expanded the all-family smoke matrix from eight to nine scientific/engineering families.

## 0.59.0.dev1

### Block A — reliable local execution

- Added an AST-backed feature-truth contract with strict rejection of unused nondefault settings.
- Added atomic run-state checkpoints with configuration and state digests.
- Added exact continuous-run resume, including fuzzy packets, memory, model estimates, counters, event state, and RNG state.
- Added resumable process-parallel sweeps with stable cell identifiers, retries, GPU worker caps, and atomic sweep state.
- Added source/configuration freezes, freeze verification, frozen execution, and run audits.
- Added dedicated Windows and Bash launchers for resume, freeze, frozen runs, continuous runs, and audits.

### Block B — continuous open-set runtime

- Added one persistent controller operating across unannounced task, world, self, partner/sensor, and memory events.
- Added moving fuzzy packet formation and dissolution with birth/death patience and membership hysteresis.
- Added open-set change detection, active probing, self/world attribution, model repair, provenance quarantine, planning, recurrence, and continuity metrics.
- Added staged-resume and uninterrupted-trajectory equivalence tests.
- Expanded the smoke matrix from seven to eight scientific families.

## 0.58.0.dev1

- Added the common configurable offline workbench, presets, sweeps, result bundles, local launchers, safety boundaries, and canonical release archive.
