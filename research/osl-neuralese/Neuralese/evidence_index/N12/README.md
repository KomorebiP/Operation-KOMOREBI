# Komorebi Neuralese G1-D1 v0.1.0

G1-D1 is the next read-only block after the registered G1 v0.1.1 pilot failed
its scientific gates. It diagnoses one fixed object: seed 711001, its registered
configuration, and checkpoint
`ea0f9506334f6958c43e73596eb7404f785abd92be7668024b0c01efac1eae75`.
The complete pilot result and intact v0.1.1 source package are bundled so that
no seed, split, checkpoint, or training choice can drift during diagnosis.

## What D1 measures

D1 asks where final-state signal is *detectable* in the frozen computation:

1. the frozen source activation
2. workspace states `z0` through `z4`
3. decoded answer-space injections `decode(z0)` through `decode(z4)`
4. registered-label behavior after controlled state and projection changes

The probes are compared with a structured raw-metadata baseline containing the
start state, transition-at-start, the complete transition map, and application depth. Separate
start-state and transition-at-start probes expose simple literal prompt
heuristics. Evidence is reported separately for IID detection, lift over that
baseline, and depth-OOD transfer.

The intervention block tests own states at every depth, recurrent versus
no-feedback state, same-final and incompatible-final donors, mean and
mean-centered states, literal zero injection, and the leading-rank-one versus
residual parts of the output projection. Incompatible-donor transport is
measured as a paired semantic difference-in-differences, not just donor
accuracy.

These measurements localize evidence; they do not prove that a particular
algorithm was computed, that information is absent, or that a component had a
training-time causal role.

## Run

The normal runner uses the bundled pilot and registered model location:

```powershell
& ".\Run_Neuralese_G1D.ps1"
```

An explicit model path can be supplied with `-Model`. Diagnostic output is
written to a timestamped `Downloads\Neuralese_G1D_Runs\pilot-711001-*`
directory unless `-Output` is used. After independent verification, the wrapper
also creates a neighboring `*-results.zip` for the next debrief.

The run performs no optimization of the checkpoint or backbone. It does make
several thousand inference passes and prints progress for feature extraction
and interventions. A static-only artifact audit is available with
`-StaticOnly`. Full diagnosis intentionally requires the pilot's recorded
Python, PyTorch/CUDA, Transformers, NumPy, and GPU identity; a mismatch fails
closed instead of silently changing the numerical protocol.

## Main artifacts

- `diagnostic_report.md`: concise, claim-bounded interpretation
- `checkpoint_spectrum.json`: singular spectra of every workspace matrix
- `state_geometry.json`: collapse and class-separation measurements
- `probe_results.json`: raw-metadata, source, state, decoded-injection, and
  literal-heuristic controls, each with IID and OOD results
- `recurrence_results.json`: paired recurrent/no-feedback trajectory differences
- `bridge_results.json`: state-depth, donor, zero, and projection interventions
- `intervention_predictions.jsonl`: registered-label logits and target margins
- `dynamic_replay.json`: exact recurrent, no-feedback, and zero replay checks
- `feature_bank.pt`: restricted-loadable per-problem trajectory tensors
- `diagnostic_verdict.json`: conservative branch localization with a
  diagnostic-only claim

## Claim boundary

D1 is post-hoc diagnosis of a failed pilot. Its probes and interventions cannot
turn seed 711001 into a G1 pass, establish replication, establish that a general
Neuralese emerged, or prove a causal mechanism. A label such as “consistent
with signal loss” means only that the registered measurements fit that
localization better than the tested alternatives. Any repair must use fresh
development data and new confirmatory seeds.
