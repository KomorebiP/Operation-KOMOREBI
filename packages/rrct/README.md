# RRCT v0.60 Persistent Fuzzy-to-J Workspace Bridge

RRCT `0.60.0.dev1` turns the proposed fuzzy-workspace/J-space connection into a bounded, falsifiable experiment.

The new family is:

```toml
experiment.family = "persistent_fuzzy_j_workspace"
```

It tests a serial causal hypothesis:

```text
learned fuzzy membership
        → moving Jacobian-discovered workspace
        → sparse nonnegative accessible content
        → causal broadcast
        → provenance-conditioned planning
        → later consequence and recurrence
```

The package preserves the v0.59 reliability control plane, adds stricter resume and sweep-integrity checks, and retains the canonical RRCT/Komorebi release archive.

## What is new

- evaluator-blind synthetic controller inputs; hidden event labels and terminal targets are withheld until post-commit scoring/feedback
- task-independent event schedules to prevent event-type leakage
- learned fuzzy gates optimized from terminal consumer loss rather than membership labels
- a public NumPy Jacobian-frame API with exact JSON resume
- moving J-lens estimation, fixed-rank projector discovery, and sparse nonnegative codes
- same-rank PCA and seeded random-subspace controls
- measured membership shuffle, J-space cut, broadcast cut, provenance cut, planner cut, and feedback cut
- longest-supported-prefix reporting, so a late link cannot hide an earlier failed link
- an optional local-only Hugging Face adapter for residual capture, target-token VJPs, norm-matched patching, and projector ablation
- stricter completed-run and sweep-resume digest validation

## Package scope

- **308 configuration keys**
- **39 major feature switches**
- **33 intervention controls**
- **9 scientific/engineering families plus one all-family smoke matrix**
- **15 presets and 8 sweep templates**
- **14 canonical prior release archives**
- Windows PowerShell and Bash launchers
- no required network access

This is an engineering and bounded functional-research platform. Its metrics are not probabilities of consciousness, subjective experience, sentience, or moral status.

## Fast start

Run the new bounded synthetic bridge:

```powershell
.\RUN_FUZZY_JSPACE.ps1
```

Run a shorter diagnostic:

```powershell
.\RUN_FUZZY_JSPACE.ps1 -Set "jspace.steps=48","jspace.calibration_steps=12","run.name=fuzzy_j_local_trial"
```

Verify the package, run tests, and execute the all-family smoke matrix:

```powershell
.\RUN_V060_LOCAL_CHECKS.ps1
```

## Causal protocol

The synthetic bridge separates controller-visible task cues from evaluator-only event truth and terminal targets. A terminal outcome is revealed only after the controller commits its prediction and plan. Evaluation reports every link separately:

1. formation: learned fuzzy membership predicts useful access
2. geometry: the moving Jacobian frame captures task-relevant sensitivity
3. access: sparse content remains decodable and beats matched controls
4. broadcast: intervention changes downstream report/inference outputs while preserving upstream code
5. planning: provenance and workspace state affect committed actions
6. recurrence: later access changes as a consequence of earlier outcomes

The result also reports the longest consecutive prefix that passes its declared diagnostic gates. Those gates are smoke diagnostics unless a freeze and replicated holdout cohort are run.

The bundled single-seed preset presently passes the first three diagnostic links—formation, Jacobian-space discrimination, and selective broadcast—and fails planner necessity and recurrence specificity. This negative boundary is recorded in `VALIDATION_REPORT.md`; it is not smoothed into a closure score.

See `docs/FUZZY_JSPACE_CAUSAL_PROTOCOL.md` for endpoints, controls, and falsifying outcomes.

## Resumable sweeps

Rank/sparsity frontier:

```powershell
.\RUN_SWEEP.ps1 -Config .\sweeps\07_jspace_rank_sparsity_frontier.toml
```

Causal intervention ladder:

```powershell
.\RUN_SWEEP.ps1 -Config .\sweeps\08_jspace_intervention_ladder.toml
```

Sweep cell identities now bind the resolved base configuration. A ledger from a different base configuration is rejected instead of silently reused.

## Optional local transformer probe

The adapter accepts only an existing local model path. It forces `local_files_only=True` and `trust_remote_code=False`; it does not train, download, or call a network API.

```powershell
.\RUN_LOCAL_JSPACE_PROBE.ps1 `
  -Model C:\models\small-local-causal-lm `
  -Prompts .\my_prompts.jsonl `
  -Output .\runs\local_jspace_probe.json `
  -TargetTokenId 123
```

PyTorch, Transformers, and compatible local weights are optional and are not bundled. The adapter is a measurement path, not evidence that the synthetic bridge has already been found inside a pretrained transformer.

## Reliability commands

```powershell
.\CHECK_CONTRACT.ps1 -Config .\configs\14_persistent_fuzzy_j_workspace.toml
.\RESUME_RUN.ps1 -RunDirectory .\runs\persistent_fuzzy_j_workspace_seed600101
.\AUDIT_RUN.ps1 -RunDirectory .\runs\persistent_fuzzy_j_workspace_seed600101
.\FREEZE_CONFIG.ps1 -Config .\configs\14_persistent_fuzzy_j_workspace.toml -Output .\validation\fuzzy_j_freeze.json
.\VERIFY_FREEZE.ps1 -Freeze .\validation\fuzzy_j_freeze.json
.\RUN_FROZEN.ps1 -Freeze .\validation\fuzzy_j_freeze.json
```

Checkpoints bind the stable configuration digest and complete serialized experiment state. A completed run is skipped only after its resolved configuration, summary, run state, and checkpoint digests are all verified.

## Scientific correction to v0.59

An audit found that the legacy `continuous_open_set_runtime` repair path directly copied evaluator-side latent state into its estimates. It remains available as an oracle-assisted engineering scaffold and now emits that limitation explicitly. Its attribution and repair numbers must not be cited as evaluator-blind evidence.

The new `persistent_fuzzy_j_workspace` family was built specifically to remove that shortcut. Evaluator truth is retained only for post-commit scoring.

## Safety and interpretation boundary

This offline build hard-blocks network access, external-tool autonomy, autonomous persistence, self-preservation reward, valence and negative welfare-like states, and unrestricted file writing.

The new experiment can support or falsify a synthetic causal workspace chain. It does not establish a natural transformer J-space, open-world awareness, consciousness, sentience, or moral status.
