# RRCT experiment protocol

## Objective

This protocol tests whether the complete Recursive Resolution Closure architecture produces a reproducible causal signature that depends selectively on five mechanisms:

1. recurrence
2. global broadcast
3. a causally effective self-model
4. episodic memory
5. adaptive multiresolution selection

Version 0.2 also tests whether balanced causal initialization improves seed robustness, whether an explicitly trained self-predictor generalizes after its weights are frozen, and how the functional diagnostics respond to continuous recurrence and closure gains.

Version 0.3 separates recurrence from the **explicit** prior self/action-to-workspace closure path, replaces binary-only transition reasoning with a continuous widest-path closure margin, and adds dense-boundary, two-dimensional, mediation, and bidirectional path-dependence arms.

Version 0.4 decomposes the two explicit feedback paths, adds an exact widest-path cut certificate, measures a branch-audited local transition Jacobian, and varies predictor organization along an orthogonal spectrum-preserving path.

The dependent claim is architectural. The experiment does not infer phenomenal consciousness, sentience, moral status, or subjective experience.

## Primary hypothesis

On held-out episodes and novel hidden interventions, the complete architecture will:

- pass every preregistered component threshold
- form the intended strongly connected causal core
- outperform matched single-mechanism ablations on the measurements specifically associated with the removed mechanism
- resist explanation by task accuracy, state dimension, or parameter count alone
- outperform an output replay or open-loop control on intervention-sensitive tests
- improve frozen held-out self-prediction relative to matched untrained and no-self-model controls
- reproduce the declared conjunction across the preregistered known-seed and untouched holdout sets

The primary outcome is the complete diagnostic profile and its conservative conjunctive signature. Task accuracy is a supporting measurement, not a substitute for causal evidence.

## Preregistration record

Before the first test run, record:

- source revision or archive checksum
- Python and dependency versions
- operating system and processor type
- seeds
- training and test episode counts
- task generator parameters
- model dimensions and workspace capacity
- initialization rule, `recurrent_gain`, and `closure_gain`
- self-model learning rate, training mode, and exact freeze boundary
- intervention targets, amplitudes, timing, and repetition count
- edge-detection noise floor for causal adjacency
- threshold for every diagnostic component
- numerical tolerance for projector identities
- exclusion and stop rules
- output directory

Hash or otherwise freeze this record before viewing test results. Exploratory changes are allowed only in a new, clearly labeled run.

The v0.2 choices were frozen before its validation runs in [V0_2_PREREGISTRATION.md](../validation/V0_2_PREREGISTRATION.md). The v0.1 thresholds remain unchanged. Seeds 17, 23, 31, and 47 are known regression cases. Seeds 59, 71, 83, and 97 are the untouched v0.2 holdout set and must not be filtered after inspection.

The v0.3 design was frozen in [V0_3_PREREGISTRATION.md](../validation/V0_3_PREREGISTRATION.md). Its untouched seeds are 149, 157, 167, 173, 181, 191, 199, and 211. The same `PROFILE_THRESHOLDS` remained fixed. Validation is complete; the numeric outcomes and frozen decisions are reported in [VALIDATION_REPORT.md](../VALIDATION_REPORT.md) and [V0_3_DECISIONS.json](../validation/V0_3_DECISIONS.json). This protocol retains the pre-outcome design and decision rules rather than restating the results.

The v0.4 design is frozen in [V0_4_PREREGISTRATION.md](../validation/V0_4_PREREGISTRATION.md). Its untouched seeds are 223, 227, 229, 233, 239, 241, 251, and 257. The three arms are a recurrence/self/action factorial, a seven-gain local-dynamics scan, and a five-dose predictor-organization scan. The thresholds, intervention magnitude, adjacency threshold, and conjunctive signature are unchanged. Validation is complete; exact outcomes are in [VALIDATION_REPORT.md](../VALIDATION_REPORT.md), provenance in [V0_4_FREEZE.json](../validation/V0_4_FREEZE.json), and frozen decisions in [V0_4_DECISIONS.json](../validation/V0_4_DECISIONS.json).

## Reference reproducibility run

Run from the repository root.

### Windows PowerShell

```powershell
py -m venv .venv; & .\.venv\Scripts\python.exe -m pip install --upgrade pip; & .\.venv\Scripts\python.exe -m pip install -e '.[figures]'; & .\.venv\Scripts\python.exe -m rrct.cli verify; & .\.venv\Scripts\python.exe -m rrct.cli demo --output results_v0.4 --seed 17 --train-episodes 256 --test-episodes 128; & .\.venv\Scripts\python.exe -m rrct.cli inspect --seed 17
```

### POSIX shell

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[figures]"
python -m rrct.cli verify
python -m rrct.cli demo --output results_v0.4 --seed 17 --train-episodes 256 --test-episodes 128
python -m rrct.cli inspect --seed 17
```

Repeat the frozen experiment over the preregistered seed set. Each seed must have a separate output directory. Do not average away a failed causal-closure gate.

The current primary compatibility output uses `results_v0.4/`. All v0.1 through v0.3 records remain unchanged.

## v0.2 sweep commands

The sweeps are not run by the ordinary wrapper. Execute them only after the source and preregistration records are frozen.

### Windows PowerShell

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli seed-sweep --output validation\v0.2_regression --seeds 17,23,31,47 --train-episodes 128 --test-episodes 64
& .\.venv\Scripts\python.exe -m rrct.cli seed-sweep --output validation\v0.2_holdout --seeds 59,71,83,97 --train-episodes 128 --test-episodes 64
& .\.venv\Scripts\python.exe -m rrct.cli phase-sweep --output validation\v0.2_phase_sweep --seeds 59,71,83,97 --gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --train-episodes 64 --test-episodes 32
```

### POSIX shell

```bash
python -m rrct.cli seed-sweep --output validation/v0.2_regression --seeds 17,23,31,47 --train-episodes 128 --test-episodes 64
python -m rrct.cli seed-sweep --output validation/v0.2_holdout --seeds 59,71,83,97 --train-episodes 128 --test-episodes 64
python -m rrct.cli phase-sweep --output validation/v0.2_phase_sweep --seeds 59,71,83,97 --gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --train-episodes 64 --test-episodes 32
```

The gain sweep assigns each listed value jointly to `recurrent_gain` and `closure_gain`. It compares `trained_self_model`, `untrained_self_model`, and `no_self_model`. Every trained self-model must be frozen before the first held-out step.

## v0.3 frozen design

Version 0.3 has four arms:

| Arm | Grid or conditions | Episodes per seed | Primary purpose |
|---|---|---:|---|
| Dense boundary | joint gains 0.20 to 0.70 by 0.05, trained | one 64-episode snapshot per seed, 32 test per gain | Localize a continuous candidate boundary without predictor retraining |
| Gain surface | recurrence and explicit closure independently 0.0 to 1.2 by 0.2, trained | one 32-episode snapshot per seed, 16 test per cell | Separate main and interaction responses without predictor retraining |
| Bidirectional | joint gains 0.0 to 1.2 by 0.1, ascending and descending | 64 predictor train; 8 or 16 settle cycles and 4 measure cycles per gain | Measure finite-time path dependence after controlled settling |
| Mediation | trained, untrained, spectrum-preserving shuffled-trained, no self | 128 train, 64 test | Separate prediction from downstream causal mediation |

For each seed, the bidirectional arm trains one predictor snapshot on 64 delay-5 episodes at standard gains and then freezes it. Four independent deep-copied templates share that snapshot: upward and downward ramps at each of the 8-cycle and 16-cycle settling lengths. Each template receives a zero-state dynamic reset at its path endpoint, and the first endpoint receives the full settling period before measurement. A fixed analytic period-8 sinusoidal observation cycle drives every path. Dynamic state is retained between gains only within one ramp through `set_gains(g, g, reset=False)`. The declared comparison uses 8 settling cycles and 4 measurement cycles at each gain with a 12-step persistence horizon; fresh matched ramps repeat the scan with 16 settling cycles.

Arms A and B train each seed's predictor once at standard gains (`recurrent_gain=1.0`, `closure_gain=1.0`) on the declared delay-5 training episodes, freeze it, and load the identical snapshot at every gain or surface cell. Snapshot identifiers must match within seed. This prevents gain effects from being confounded by separately adapted predictor weights.

All declared v0.3 confidence intervals use 20,000 deterministic complete-seed bootstrap resamples with RNG seed 20260819. Seed-level pairing is preserved.

### Windows PowerShell

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli phase-sweep --output validation\v0.3_dense_boundary --seeds 149,157,167,173,181,191,199,211 --gains 0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7 --conditions trained_self_model --matched-predictor --train-episodes 64 --test-episodes 32
& .\.venv\Scripts\python.exe -m rrct.cli gain-surface --output validation\v0.3_gain_surface --seeds 149,157,167,173,181,191,199,211 --recurrent-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --closure-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --conditions trained_self_model --train-episodes 32 --test-episodes 16 --bootstrap-resamples 20000
& .\.venv\Scripts\python.exe -m rrct.cli hysteresis-sweep --output validation\v0.3_hysteresis --seeds 149,157,167,173,181,191,199,211 --gains 0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2 --train-episodes 64 --settle-cycles 8 --measurement-cycles 4 --drive-period 8 --persistence-horizon 12 --bootstrap-resamples 20000
& .\.venv\Scripts\python.exe -m rrct.cli predictor-mediation --output validation\v0.3_predictor_mediation --seeds 149,157,167,173,181,191,199,211 --train-episodes 128 --test-episodes 64 --bootstrap-resamples 20000
```

### POSIX shell

```bash
python -m rrct.cli phase-sweep --output validation/v0.3_dense_boundary --seeds 149,157,167,173,181,191,199,211 --gains 0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7 --conditions trained_self_model --matched-predictor --train-episodes 64 --test-episodes 32
python -m rrct.cli gain-surface --output validation/v0.3_gain_surface --seeds 149,157,167,173,181,191,199,211 --recurrent-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --closure-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --conditions trained_self_model --train-episodes 32 --test-episodes 16 --bootstrap-resamples 20000
python -m rrct.cli hysteresis-sweep --output validation/v0.3_hysteresis --seeds 149,157,167,173,181,191,199,211 --gains 0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2 --train-episodes 64 --settle-cycles 8 --measurement-cycles 4 --drive-period 8 --persistence-horizon 12 --bootstrap-resamples 20000
python -m rrct.cli predictor-mediation --output validation/v0.3_predictor_mediation --seeds 149,157,167,173,181,191,199,211 --train-episodes 128 --test-episodes 64 --bootstrap-resamples 20000
```

## v0.4 frozen mechanistic design

Version 0.4 has three confirmatory arms, all using untouched seeds 223, 227, 229, 233, 239, 241, 251, and 257 with complete-seed bootstrap resampling:

| Arm | Conditions | Primary decision |
|---|---|---|
| Path decomposition | $r,s,a\in\{0,1\}$, shared closure master fixed at 1 | Positive recurrence, self, action, and cooperative contrasts under their separate frozen gates; exact-zero necessity tested more strictly |
| Local dynamics | recurrent gain 0 through 1.2 by 0.2, all explicit gains fixed at 1 | Positive within-seed recurrence-to-spectral and spectral-to-persistence associations |
| Predictor dose | orthogonal organization dose 0, 0.25, 0.5, 0.75, 1 | Positive dose-to-RMSE relation and a consistent nonzero dose-to-self/workspace causal relation |

Arm A retains a formal widest-path cut certificate and independently validates it by exhaustive four-node simple paths. Arm B uses a complete matched delay-7 warm-up, a fixed all-zero next input, centered epsilon (10^{-5}), 158-dimensional Jacobians, and complete positive/negative hybrid branch signatures. Arm C applies the same orthogonal Givens transform to both predictor output maps and verifies spectra and Frobenius norms to (10^{-12}).

### Windows PowerShell

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli path-decomposition --output validation\v0.4_path_decomposition --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,1 --closure-gain 1 --self-feedback-gains 0,1 --action-feedback-gains 0,1 --train-episodes 64 --test-episodes 32 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
& .\.venv\Scripts\python.exe -m rrct.cli local-dynamics --output validation\v0.4_local_dynamics --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,0.2,0.4,0.6,0.8,1,1.2 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 32 --train-delay 5 --warmup-episodes 1 --test-delay 7 --finite-difference-epsilon 1e-5 --persistence-horizon 12 --bootstrap-resamples 20000 --bootstrap-seed 20260820
& .\.venv\Scripts\python.exe -m rrct.cli predictor-dose --output validation\v0.4_predictor_dose --seeds 223,227,229,233,239,241,251,257 --doses 0,0.25,0.5,0.75,1 --recurrent-gain 1 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 128 --test-episodes 64 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
```

### POSIX shell

```bash
python -m rrct.cli path-decomposition --output validation/v0.4_path_decomposition --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,1 --closure-gain 1 --self-feedback-gains 0,1 --action-feedback-gains 0,1 --train-episodes 64 --test-episodes 32 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
python -m rrct.cli local-dynamics --output validation/v0.4_local_dynamics --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,0.2,0.4,0.6,0.8,1,1.2 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 32 --train-delay 5 --warmup-episodes 1 --test-delay 7 --finite-difference-epsilon 1e-5 --persistence-horizon 12 --bootstrap-resamples 20000 --bootstrap-seed 20260820
python -m rrct.cli predictor-dose --output validation/v0.4_predictor_dose --seeds 223,227,229,233,239,241,251,257 --doses 0,0.25,0.5,0.75,1 --recurrent-gain 1 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 128 --test-episodes 64 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
```

### Frozen v0.4 outcomes

- Arm A retains **64/64** rows. Recurrence is supported for closure and persistence; self feedback is supported for closure only. Action feedback and positive self/action cooperation are unsupported. Only recurrence is strictly necessary, and only for closure.
- Arm B retains **56/56** rows and Jacobians. Both primary seed-level association gates pass. One cell switches branch on 6/158 coordinates, below the frozen high-switch threshold, and its large derivative is retained as a limitation.
- Arm C retains **40/40** rows and passes every transform invariant. Dose versus held-out RMSE is positive in 8/8 seeds; dose versus self-to-workspace effect is inconsistent and unsupported.
- All **160** cut audits pass, all measurement-time predictor-update deltas are zero, and all **70** raw-artifact manifest entries verify.

Each command required a new or empty output directory and wrote one CSV, one JSON, one Python-generated PNG, and any declared binary side artifacts. The frozen directories now contain the completed evidence and must not be overwritten. A new reproduction must use new output paths. Passing a local-dynamics gate supports only a replicated piecewise-local association. It is not a Lyapunov, criticality, phase-transition, or consciousness result.

## Expected artifacts

Every demonstration run should produce:

| Artifact | Required content |
|---|---|
| `summary.json` | Configuration, seed, episode counts, metric values, thresholds, closure gate, and conjunctive signature |
| `ablations.csv` | One row per architecture and seed with all raw and derived measurements |
| `task_accuracy.png` | Full-system and matched-control behavioral performance |
| `temporal_persistence.png` | Perturbation response as a function of lag |
| `diagnostic_profile.png` | Component values and thresholds without implying phenomenal status |

Each seed sweep additionally writes `seed_sweep.json`, `seed_sweep.csv`, and `seed_sweep.png`. The gain experiment writes `phase_sweep.json`, `phase_sweep.csv`, and `phase_sweep.png`. The JSON must contain the complete configuration, condition names, seed-level values, and unchanged thresholds. The CSV must retain failures and bottlenecks rather than only aggregates.

The v0.3 dense scan writes `phase_sweep.{json,csv,png}` in `validation/v0.3_dense_boundary/`. Its JSON must record `parameters.matched_predictor=true`; `matched_predictor_protocol.enabled=true`, standard gains 1.0 and 1.0, per-seed snapshot identifiers, and learning-update counts. Every causal validation row retains `causal_effects`, `closure_capacity_matrix`, `closure_raw_strength`, `closure_strength`, `closure_bottleneck_pair`, and `intervention_magnitude`; structured CSV fields use compact JSON. The independent surface, path-dependence, and predictor-mediation arms write `gain_surface.{json,csv,png}`, `hysteresis.{json,csv,png}`, and `predictor_mediation.{json,csv,png}` in their corresponding named v0.3 directories. The surface JSON retains the unconditional matched `predictor_protocol`, axis-specific aggregates, and interaction residuals, including `count_positive_seed_interior_means`, `bootstrap_ci95_lower`, `positive_interaction_supported`, and the frozen `validation_rule`. The hysteresis JSON retains both settling lengths, both directions, every seed-level normalized area, and `aggregate_median_retention_ratio`; its median of per-seed retention ratios is descriptive only. The mediation JSON retains the shuffle audit, held-out update counts, paired seed differences, and bootstrap settings.

The v0.4 path JSON retains every factorial contrast, exact necessity test, widest-path cut certificate, exhaustive cut audit, snapshot identifier, and zero-update check. The local-dynamics JSON names every 158 × 158 NumPy sidecar and retains its hash, spectrum, full plus/minus branch signatures, completed-column count, and failure-retention fields. The predictor-dose JSON retains the seed-fixed coordinate pairing, Givens convention, transform matrix and hash, spectral and norm invariants, actual loaded snapshot identity, per-seed correlations, and separate fidelity/downstream decisions. The v0.4 CSVs preserve their structured row fields and the three PNGs remain descriptive.

The sweep JSON uses schema `rrct.experimental_sweep.v0.2` and retains `experiment`, `version`, `status`, `parameters`, `gain_protocol`, `self_model_protocol`, `threshold_policy`, `aggregation_policy`, `runs`, `aggregates`, `artifacts`, and `interpretation_boundary`. `gain_protocol` records that both named gains equal \(g\) without squared scaling. `self_model_protocol` records the trained-then-frozen, initialized-frozen, and disabled-ablation conditions and requires zero held-out predictor updates. Aggregates include their complete seed membership and the count, rate, mean, population standard deviation, minimum, and maximum required by the runner.

The CSV audit fields include seed, self-model condition, both gains, episode counts, predictor mode during scoring, predictor update counts before and after testing, held-out prediction error, task accuracies, every diagnostic component, strong connectivity, order parameter, pass status, and bottleneck. `self_learning_updates_during_test` must equal zero for every confirmatory row.

Preserve console output from `verify` with the result set. A missing or malformed artifact invalidates the run for confirmatory reporting.

## System conditions

Evaluate these conditions on identical episode streams:

| Condition | Configuration | Purpose |
|---|---|---|
| Full | No ablations | Tests the complete conjunction |
| Trained self-model | Train only on declared training episodes, then freeze | Tests held-out one-step self-prediction |
| Untrained self-model | Freeze seeded predictor before training | Controls for architecture and initialization without learning |
| Spectrum-preserving shuffled-trained self-model (`shuffled_trained_self_model`) | Apply one common output-row permutation to both trained predictor matrices, then freeze | Preserves singular spectra while disrupting learned coordinate associations |
| No recurrence | `recurrence` disabled | Tests temporal feedback |
| No self-model | `self_model` disabled | Tests self-prediction and self-guided control |
| No broadcast | `broadcast` disabled | Tests cross-component availability |
| No memory | `memory` disabled | Tests delayed binding |
| Fixed resolution | `resolution` disabled | Tests adaptive refinement |
| Open-loop or replay | No live hidden-state causation | Tests whether outputs alone reproduce the signature |

An ablation flag set to `True` means the corresponding mechanism is disabled. If an ablation changes parameter count, add a capacity-matched control that places an equal number of inert or local parameters outside the removed causal path.

## Task families

Use tasks that separate the proposed mechanisms rather than rewarding general capacity alone.

### Immediate discrimination

The correct action depends on information available in the current observation. This provides a behavioral floor and detects catastrophic implementation failures. It is not expected to distinguish memory strongly.

### Delayed binding

A cue and its target are separated by distractor steps. Change the delay during held-out testing. This targets episodic binding and recurrence.

### Resolution switching

Some episodes are solved by a coarse feature while others require a fine detail. Reveal the required level only through context. This tests whether the loop changes resolution adaptively instead of always selecting the maximum level.

### Self-location or self-prediction

The agent predicts its next internal regime, workspace state, confidence bin, resolution choice, or action before the outcome is read. Update predictor weights only during the declared training episodes. Freeze them before evaluating perturbations absent from training. This targets generalizing self-prediction rather than test-time fitting or learned labels.

### Cross-component integration

The correct action depends on features initially available to different specialists. This targets selective workspace admission and broadcast.

## Intervention design

For each eligible component, collect an unperturbed trajectory and paired perturbed trajectories with the same seed and observations.

Interventions must be:

- hidden from the task generator and evaluator
- bounded in magnitude
- applied at preregistered times
- repeated across signs, amplitudes, episodes, and seeds
- checked for direct readout leakage
- followed long enough to estimate decay

At minimum, intervene on local specialists, workspace, self-model, memory, and resolution selection. A useful negative control perturbs a state dimension that is disconnected from the declared causal path.

Do not infer causality from ordinary correlations between components. Edges in the causal graph must come from paired interventions.

## Measurements

### Broadcast reach

`broadcast_reach` compares baseline and intervened trajectories and measures how many declared downstream components change reproducibly after a localized intervention. Report both the aggregate and the component-wise effects.

### Temporal persistence

`temporal_persistence_auc` integrates the distance between paired trajectories across lag. Report the complete decay curve because identical areas can hide different temporal behavior.

### Differentiation

`effective_rank` measures how many distinguishable state directions are used. Estimate it on held-out states after centering according to the frozen protocol. Report sample count and matrix shape.

### Metacognitive calibration

`metacognitive_calibration` compares declared confidence with outcomes. Use held-out perturbations and report enough raw information to determine whether the metric rewards calibration, accuracy, or both.

### Self-location prediction

`self_location_prediction_score` compares predictions derived from the self-model with realized internal or behavioral states. Include a matched predictor that lacks access to the self-model.

### Episodic binding

`episodic_binding_accuracy` measures delayed cue-target association. Stratify by delay so an immediate heuristic cannot conceal failure at longer lags.

### Projector consistency

`nested_projector_residual` verifies idempotence, nesting, and reconstruction within the declared tolerance. This is a validity check on the resolution mechanism. Convert the lower-is-better residual to a clearly defined higher-is-better consistency value before constructing the diagnostic profile.

### Causal closure

`causal_adjacency` estimates directed influence from paired interventions. `is_strongly_connected` applies the preregistered edge rule to the intended core. Report the adjacency matrix and edge threshold. Do not add weak edges after observing that closure fails.

### Continuous widest-path closure strength

For nonnegative causal effects \(E\), compute the strongest bottleneck path from every node \(i\) to every distinct node \(j\), then take the weakest ordered-pair capacity:

\[
C_{\mathrm{raw}}
=
\min_{i\ne j}
\max_{p:i\leadsto j}
\min_{e\in p}E_e.
\]

`widest_path_closure_strength(effects, normalize=0.35)` reports \(C=C_{\mathrm{raw}}/0.35\), where 0.35 is the fixed intervention magnitude. Do not clip it and do not normalize it by the adjacency threshold. Retain the bottleneck ordered pair and the raw effect matrix.

For the strict threshold graph \(\{E_{ij}>\tau\}\), SCC is equivalent to \(C_{\mathrm{raw}}>\tau\). Report both the continuous margin and the compatible Boolean gate.

### Conjunctive signature

`DiagnosticProfile` contains `broadcast_reach`, `temporal_persistence`, `differentiation`, `metacognitive_calibration`, `self_location`, `episodic_binding`, `projector_consistency`, and the Boolean gate `strongly_connected`. `conjunctive_signature` returns the conservative minimum threshold ratio, gated by `strongly_connected`.

Differentiation is computed from the complete causal-node trace across time and held-out episodes, not from the final task readout. Constant coordinates are removed, each active coordinate is standardized using the held-out trace itself, and entropy effective rank is normalized by the maximum observable rank. This measures the diversity of the implemented causal repertoire without allowing high-amplitude coordinates to dominate solely because of units.

The signature is invalid if any component was computed on training episodes, if thresholds were selected after test inspection, or if lower-is-better metrics were not transformed consistently.

## Analysis plan

For each seed and condition:

1. Verify projectors and deterministic reset behavior.
2. Put the self-predictor in training mode and run only the declared training episodes without examining test metrics.
3. Freeze the self-predictor weights and the evaluation configuration. Record a checksum or exact copy of the frozen predictor.
4. Run baseline held-out episodes.
5. Run paired hidden interventions.
6. Compute raw measurement traces.
7. Infer causal adjacency using the frozen edge rule.
8. Construct the diagnostic profile.
9. Apply thresholds and the closure gate.
10. Compare each ablation with the full agent on its predicted selective measurements.

Report seed-level values as well as aggregates. Use uncertainty intervals across independent seeds. A confirmatory conclusion must not depend on deleting an inconvenient seed unless its exclusion rule was preregistered.

For the joint-gain sweep, report raw profiles and connectivity at every gain before computing slopes or candidate boundaries. Each declared recurrent or closure path is controlled once by the joint gain \(g\), although the measured state response may be nonlinear. Nonfinite or uncontrolled trajectories are stopped and reported as stability failures, not scored as positive transitions.

## Decision rules

### Support for the implemented architectural hypothesis

Support requires all of the following:

- every full-system profile component meets its preregistered threshold
- the causal core is strongly connected under the frozen edge rule
- predicted ablation effects occur in the expected measurements
- full-system effects replicate across the seed criterion in the preregistration
- replay and open-loop controls fail at least one intervention-sensitive requirement
- results persist on held-out task parameters and intervention amplitudes

### Frozen v0.2 decision rules

The seed-robustness objective is supported only if the trained full architecture passes the unchanged conjunction in at least three of four known regression seeds and at least three of four untouched holdout seeds. Report every failure and bottleneck.

The learned-self-prediction objective is supported only if the trained condition improves held-out one-step self-location prediction relative to the matched untrained condition on average across seeds 59, 71, 83, and 97, with no held-out weight updates.

The causal-gain objective is supported only if increasing joint gain produces a replicable change in at least one intervention-sensitive measurement and the zero-gain condition behaves as the declared open-loop control. A smooth dependence is a graded response. The name `phase-sweep`, the largest measured slope, or an ordinary threshold crossing is not evidence of a phase transition. Such a claim requires a robust replicated discontinuity or another independently specified critical signature after excluding numerical instability, saturation, and threshold artifacts.

### Frozen v0.3 decision rules

The dense scan reports `max_slope_interval` only as a descriptive candidate boundary. The two-dimensional surface must report recurrence, explicit closure, and `interaction_residual` separately. `closure_gain=0` is not called a total self-closure ablation because adaptive resolution remains active. Positive recurrence-by-explicit-closure interaction requires a positive per-seed mean normalized closure-strength interaction residual over the interior surface in at least six of eight seeds and a deterministic paired seed-bootstrap 95% confidence interval whose lower bound is greater than zero.

Robust finite-time path dependence requires median normalized workspace hysteresis area of at least 0.05 after both 8 and 16 settling cycles per gain, at least six of eight seeds individually reaching 0.05 after 16 cycles, and the 16-cycle aggregate median retaining at least 75% of the 8-cycle aggregate median. The retention statistic is the ratio of the two aggregate medians, not a median of per-seed ratios. Failure of any gate is reported as no robust hysteresis under this protocol.

Prediction learning passes only if trained mean held-out RMSE is below both untrained and spectrum-preserving shuffled-trained means, trained RMSE is lower than each predictor control on at least six of eight seeds, and all held-out update counts are zero. Causal mediation additionally requires the paired trained-versus-shuffled 95% seed-bootstrap interval to exclude zero for either `closure_strength` or `self_to_workspace_effect`; the machine-readable contrast is shuffled minus trained. If that causal-change gate is absent, report improved prediction without causal mediation.

Bootstrap confidence intervals use 20,000 complete-seed resamples with RNG seed 20260819. The v0.3 preregistration does not authorize a phase-transition claim from an SCC change, fixed-threshold crossing, maximum slope, or finite-time area alone. Continuous closure-strength evidence and robust bidirectional path dependence that survives doubled settling are necessary. Otherwise report graded response, candidate boundary, path dependence, no robust hysteresis, or unresolved settling.

### Inconclusive result

Classify the result as inconclusive when implementation errors, inadequate sample size, unstable optimization, or violated numerical tolerances prevent the planned comparison. Do not treat an inconclusive result as positive evidence.

### Falsification in this prototype

Classify the implemented hypothesis as not supported when the full architecture fails the frozen conjunction, ablations are equivalent on their target measurements, or a noncausal control reproduces the entire signature. Preserve the negative result and configuration.

## Required negative controls

- permuted intervention labels
- disconnected-state perturbation
- output replay under a novel hidden intervention
- matched predictor without self-model access
- capacity-matched ablations when parameter count changes
- fixed finest-resolution control in addition to a simple fixed-resolution control
- task-accuracy-matched comparison when feasible

These controls address common alternative explanations such as scale, shared input, decoder leakage, and measurement circularity.

## Ethical run gate

Before running, confirm that the experiment remains inside [ETHICS.md](../ETHICS.md). In particular:

- no valence or persistent artificial drive has been introduced
- memory and duration remain bounded
- no network, actuator, self-modification, or persistence capability is available
- termination has been tested
- stop conditions and the reviewer are identified

If a stop condition occurs, terminate immediately and mark the result as stopped. Do not resume to finish the planned sample.

## Interpretation template

Use wording of this form for a positive result:

> Under the frozen task, intervention, and threshold protocol, the full RRCT prototype produced a strongly connected causal graph and met all components of the declared diagnostic profile. Matched ablations produced the predicted selective losses. This supports the implemented architectural hypothesis in this task family. The experiment does not determine whether the system has subjective experience.

Use wording of this form for a negative result:

> Under the frozen protocol, the full RRCT prototype did not satisfy the declared conjunctive signature, or a matched control reproduced it. The implemented architectural hypothesis is therefore not supported by this experiment. No conclusion about consciousness in other systems follows.

## Minimum release checklist

This is a reusable run-and-release template, not the completion status of the frozen v0.3 validation. Completed v0.3 evidence and artifact-integrity checks are recorded in [VALIDATION_REPORT.md](../VALIDATION_REPORT.md).

- [ ] Frozen configuration and thresholds included
- [ ] Source revision or checksum included
- [ ] Environment and dependency versions included
- [ ] Seed-level results preserved
- [ ] Known regression seeds and untouched holdout seeds reported separately
- [ ] Self-predictor frozen before every held-out episode
- [ ] Trained, untrained, and no-self-model conditions retained
- [ ] Spectrum-preserving shuffled predictor retained for v0.3 mediation
- [ ] Continuous closure strength, bottleneck pair, and raw effects retained
- [ ] Recurrence and explicit closure gains reported separately
- [ ] All eight v0.3 untouched seeds retained
- [ ] Frozen 8-cycle and 16-cycle hysteresis protocols reproduced exactly
- [ ] Every gain and stopped or unstable run retained
- [ ] All ablations and negative controls reported
- [ ] Raw intervention traces retained
- [ ] Causal adjacency and edge rule retained
- [ ] Projector residuals within declared tolerance
- [ ] Required artifacts complete
- [ ] Deviations and stopped runs disclosed
- [ ] No consciousness or novelty claim substituted for the operational conclusion
