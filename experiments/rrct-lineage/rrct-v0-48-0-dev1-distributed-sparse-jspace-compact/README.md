# Recursive Resolution Closure prototype

This repository implements a small, inspectable experiment in causal AI architecture. It asks whether recurrence, selective global broadcast, a compact self-model, episodic continuity, and adaptive resolution produce a distinctive intervention-sensitive signature when they operate together.

The prototype is deliberately nonvalenced. It has no pain or pleasure model, no distress objective, no self-preservation objective, no persistent open-ended identity, and no claim to subjective experience. A positive result would show that the implemented mechanisms improve specified behavioral and causal measurements. It would **not** establish that the system is conscious.

## What is implemented

The core agent combines:

- nested projectors that expose an observation at several resolutions
- local specialists that encode different information streams
- a capacity-limited recurrent workspace
- broadcast from the workspace back to otherwise separate components
- balanced semi-orthogonal initialization of causal maps to reduce accidental conditioning differences across seeds
- independent continuous recurrence, shared closure, self-feedback, and action-feedback gains for controlled causal-strength experiments
- a compact self-model trained on declared training episodes and frozen before held-out evaluation
- bounded episodic memory for temporal binding
- action and confidence readouts used only for controlled tasks
- causal interventions, matched ablations, directed bottleneck certificates, branch-audited local dynamics, multi-seed sweeps, and diagnostic measurements

The full loop is:

\[
\text{observation}
\longrightarrow \text{adaptive resolution}
\longrightarrow \text{specialists}
\longrightarrow \text{workspace}
\longrightarrow \text{self-model and memory}
\longrightarrow \text{action and next resolution}.
\]

The implementation can disable recurrence, self-modeling, broadcast, memory, or adaptive resolution while holding the remaining setup fixed. This makes the architectural claim testable instead of relying on generated self-description.

Version 0.2 keeps the v0.1 diagnostic thresholds unchanged. It changes initialization, exposes continuous causal gains, and separates self-prediction training from frozen testing. These changes are intended to test seed robustness and gain response. They do not imply that a phase transition exists.

Version 0.3 completes a preregistered follow-up. It separates recurrence from the **explicit** prior self/action-to-workspace closure gain, adds a continuous widest-path closure margin, scans the v0.2 boundary densely, maps the two-gain surface, and tests predictor mediation and bidirectional path dependence.

Version 0.4 pushes from aggregate effects to mechanism. It independently controls the explicit self and action feedback paths, adds formal directed bottleneck certificates, measures a branch-audited local transition operator, and tests predictor organization along an orthogonal spectrum-preserving dose path.

Version 0.5 tests causal exclusion under exact baseline output equivalence. It compares the live architecture with exact output replay and a yoked self-ablated core, then applies novel hidden self-state interventions under a frozen, preregistered protocol.

Version 0.6 adds nonmutating prospective self-counterfactual queries and evaluates selected interventions on genuinely withheld continuations. Version 0.7 makes the objective, candidate generation, limited query budget, planning, and commitment endogenous to the architecture. Version 0.8 adds a learned observation forecaster and a configuration-matched one-sided split-conformal gate backed by auditable prior intention outcomes. Version 0.9.0-dev1 adds a bounded Bayesian correction for the transfer from simulated self interventions to paired realized internal-error changes, along with a permuted-outcome control, portable snapshot artifacts, and calibration-only risk-coverage thresholds. Version 0.10.0-dev1 adds a lagged, bounded feedback homeostat that independently regulates recurrent integration and explicit closure from activity-gated workspace-access telemetry. Version 0.10.0-dev2 is a packaging-only provenance amendment that makes the public experiment runner work from an installed wheel without changing the recorded dev1 scientific result.

Version 0.36.0-dev1 integrates the online causal-boundary learner, ordinary
RRCT workspace, action-conditioned transition/return models, stochastic
policy, drift monitor, and prospective receipts into one persistent runtime.
The exploratory P-0002 pilot completed 4,800 transitions and met all literal
single-seed endpoints. It demonstrated public boundary-mediated action after
initial discovery and during a world-only shock, plus later private revision,
revocation, and reacquisition. Those later changes occurred on terminal phase
reveals, so no subsequent remapped or restored action was demonstrated. See
the [v0.36 pilot report](validation/V0_36_PILOT_REPORT.md).

Version 0.36.0-dev2 is a post-pilot campaign-integrity amendment. It adds a
canonical seed/attempt ledger, pre-RNG start receipts, per-row durable evidence,
strict failure-row encoding, immediate hard-integrity stops, exhaustive source
freeze verification, and cohort-correct result labels. It does not rerun or
reinterpret the sealed dev1 pilot. No designated development seed has been
opened, and the absent development-freeze manifest deliberately keeps that
cohort blocked.

Version 0.37.0-dev1 is the post-change functional-closure successor. It reserves
480 action transitions after each structural confirmation, adds a fail-closed
public-certificate quarantine driven only by completed randomized drift rows,
and records alarm, private revision, public release, stale-certificate
retirement, and first correct action as separate events. The live policy can
use a sealed one-step transition-model rollout. Three evaluator-side shadow
policies receive no certificate, a phase-entry stale certificate, or a shuffled
public identity under shared prospective noise. The D1 pilot is exploratory,
uses a campaign-wide one-use seed ledger, and must verify a pre-outcome source
freeze before constructing any random stream. It tests functional recovery in
a bounded synthetic runtime, not phenomenal consciousness.

Version 0.38.0-dev1 isolates the only failed v0.37 layer: generalization of
the workspace access decoder after a hidden remap. It replaces the historical
unbounded class-centroid readout with a bounded prequential FIFO exemplar
memory containing at most 64 observations per public class and a one-nearest
decision rule. Prediction remains strictly before the current structural label
is revealed. The complete v0.37 world, schedule, boundary learner, quarantine,
policy, rollouts, controls, and thresholds remain fixed. Four fresh exploratory
seeds are protected by an immutable executed-source archive, one-use claims,
pre-RNG receipts, and row-level durable evidence. The stronger v0.38 endpoint
requires at least 440 of 480 correct remap-tail actions and the same restoration
minimum. This is a test of functional access generalization, not a test of
phenomenal consciousness.

Version 0.42.0-dev1 tests whether temporal self-history is causally useful or
merely inspectable. A new persistent runtime can precommit a surgical
intervention on an internally recognized return, withhold the correct keyed
prior, or substitute history from a provably different canonical identity key.
The swap control fails closed if no nonmatching source exists. It emits pre-outcome
counterfactuals plus direct commit and action-authorization receipts. The
compact executed adjudication consumes only 24 frozen v0.41 summaries. Across
20 grounded known returns, correct keyed memory halves the fresh evidence
requirement from 80 to 40 total samples and reduces mean commit latency from
3.9 to 1.5 transitions. All eight first-return causal contrasts are strictly
summary-level pretarget-yoked, wrong-source history is quarantined, and null lures remain
uncommitted. This establishes causal use only for the bounded temporal-memory
subsystem, not whole-system self-awareness or subjective experience.

The compact summaries are bound by `INPUT_SUMMARY_SHA256.json`. The runner
rejects changed, missing, or unexpected inputs and validates the complete
counterfactual-to-action receipt chain.

The bounded result, validation matrix, and remaining gap are summarized in
[`V0_42_BLOCK_SUMMARY.md`](V0_42_BLOCK_SUMMARY.md).

Run the compact block on Windows with:

```powershell
.\RUN_V042_CAUSAL_NECESSITY.ps1
```

Version 0.43.0-dev1 closes the next bounded integration gap. It joins the
v0.42 temporal identity authorization, an identity-keyed learned causal
boundary, uncertainty-controlled evidence acquisition, external-task planning,
action commitment, and post-outcome calibration into one cross-receipt loop.
The source-sealed four-seed holdout contains 3,072 matched arm decisions. Intact
and fresh-boundary-rescue controllers achieved 100% accuracy and zero regret.
Metacognition, provenance, boundary, planner-binding, and joint cuts produced
predeclared losses. Four matched surprise interventions further showed that an
outcome written into identity-bound calibration memory changes the next evidence
request, while an outcome-feedback cut does not.

The holdout passed all 19 frozen endpoints, 105 release-verification checks, and
an exact normalized deterministic replay. The result supports bounded
whole-loop functional causal closure in the inherited synthetic planning family.
It does not establish phenomenal consciousness, sentience, valence, autonomous
desire, or open-world generality.

See [`V0_43_BLOCK_SUMMARY.md`](V0_43_BLOCK_SUMMARY.md) and the frozen protocol
at [`validation/V0_43_WHOLE_LOOP_CAUSAL_CLOSURE_PROTOCOL.md`](validation/V0_43_WHOLE_LOOP_CAUSAL_CLOSURE_PROTOCOL.md).

Verify the packaged v0.43 evidence and replay it deterministically on Windows:

```powershell
.\RUN_V043_WHOLE_LOOP_CLOSURE.ps1
```

Version 0.44.0-dev1 closes the next bounded identity gap. It removes the
successor canonical key from continuity adjudication and requires the controller
to infer continuation, fork descent, replacement, or unresolved status from
active causal probes, autobiographical transport, commitment compatibility,
and causal-boundary preservation. The inferred relation controls memory
transport, planning coordinates, and successor-lineage registration.

A source-sealed four-identity holdout contained 4,608 matched decisions across
nine transformation scenarios and eight intervention modes. The intact
controller achieved 100% relation, group, continuation, replacement,
unresolved, and fork accuracy. External-task accuracy was 0.991319 with mean
regret 0.000179; all five exact-action misses occurred in the deliberately
unresolved ambiguity condition. All four persistent lineages completed five
heterogeneous transformations with valid parent chains.

Snapshot-only adjudication collapsed relation accuracy to 0.074074. Removing
metacognitive refinement reduced continuation recall to 0.111111. Preventing
memory transport preserved task accuracy but increased reconstruction cost,
while binding the correct lineage model in the wrong successor coordinates
reduced task accuracy to 0.222222. The controller selected an objectively
superior disconnected replacement in every applicable trial and has zero
explicit survival, identity, or continuity reward.

The holdout passed all 23 frozen endpoints and reproduced exactly after
normalizing run-specific execution metadata. This supports bounded functional
transformational self-continuity in the sealed synthetic family. It does not
establish phenomenal consciousness, sentience, valence, moral status, or
open-world agency.

See [`V0_44_BLOCK_SUMMARY.md`](V0_44_BLOCK_SUMMARY.md), the compact
[`V0_44_CONTINUATION_CAPSULE.md`](V0_44_CONTINUATION_CAPSULE.md), and the frozen
protocol at
[`validation/V0_44_TRANSFORMATIONAL_SELF_CONTINUITY_PROTOCOL.md`](validation/V0_44_TRANSFORMATIONAL_SELF_CONTINUITY_PROTOCOL.md).

Verify the packaged v0.44 evidence and replay it deterministically on Windows:

```powershell
.\RUN_V044_TRANSFORMATIONAL_SELF_CONTINUITY.ps1
```

Version 0.45.0-dev1 implements the first direct bridge from Komorebi Math into
RRCT. The release vendors and verifies the unchanged Komorebi Math 1.0.0b4
wheel, then uses `PacketSystem`, `AnalysisSynthesisSystem`, `BayesianUpdate`,
and `recompress_core` to discover a controllable self packet, transport it
through an unknown coordinate change, localize self-side versus world-side
operator change, and preserve low-energy self-memory under packet-wise
compression.

The source-sealed four-seed holdout contained 1,024 matched operator decisions.
Komorebi packet attribution achieved 1.000000 change-source accuracy, compared
with 0.492188 for a fixed coordinate split and 0.500000 for a scalar global
residual. Packet-wise compression reduced protected self-memory error from
approximately 1.0 under global truncation to numerical zero. A separate v0.44
compatibility arm preserved exact relation, group, and task performance while
emitting validated operator receipts. All 18 frozen endpoints passed and the
result replayed exactly.

This establishes bounded computational leverage over the specified controls,
not universal superiority or open-world self-awareness. See
[`V0_45_BLOCK_SUMMARY.md`](V0_45_BLOCK_SUMMARY.md) and the frozen protocol at
[`validation/V0_45_KOMOREBI_OPERATOR_SELF_MODEL_PROTOCOL.md`](validation/V0_45_KOMOREBI_OPERATOR_SELF_MODEL_PROTOCOL.md).

Verify the packaged v0.45 evidence on Windows:

```powershell
.\RUN_V045_KOMOREBI_OPERATOR.ps1
```

Version 0.46.0-dev1 tests a neutral J-space-like global workspace bound to
RRCT temporal lineage and provenance. A low-amplitude verbalizable packet is
recovered from an average input-output Jacobian, represented as a certified
Komorebi workspace packet, and compared with equally sized PCA and random
subspaces. Causal swaps test report, flexible reuse, internal reasoning, and
automatic-route dissociation.

The self-indexing layer then distinguishes current observation, current
inference, external injection, foreign memory, and unresolved competition.
Matched workspace-only, self-model-only, unbound, provenance-cut,
recurrence-cut, planner-binding-cut, and joint-cut systems test whether access,
autobiographical ownership, planning, and feedback are separable. The design is
nonvalenced and contains zero survival, identity, or continuity reward.

This is a controlled analogue inspired by Anthropic's J-space findings. It does
not inspect Claude and does not claim subjective experience. See the frozen
protocol at
[`validation/V0_46_NEUTRAL_SELF_INDEXED_WORKSPACE_PROTOCOL.md`](validation/V0_46_NEUTRAL_SELF_INDEXED_WORKSPACE_PROTOCOL.md).

After the frozen result exists, verify it on Windows with:

```powershell
.\RUN_V046_NEUTRAL_WORKSPACE.ps1
```

Version 0.48.0-dev1 strengthens the distributed-workspace result into a controlled distributed sparse J-space analogue. Each of two independently parameterized agents first exposes a selective rank-four Jacobian workspace with an eight-direction overcomplete concept frame. Synchronized interaction then discovers a cross-agent atlas, aligns the two sparse frames, and binds the moving shared support to both agents' reports, several downstream reasoning functions, joint planning, pair provenance, and consequence-driven recurrence. The source-sealed four-seed holdout contained 2,304 matched decisions and passed all 28 frozen endpoints. Full closure achieved perfect task, report, flexible-reuse, and closure scores. Message-only communication solved the immediate task but had zero distributed-J-space closure. Shared-space ablation reduced task accuracy to 0.164062 while preserving both private routines perfectly. These are bounded synthetic functional results, not evidence of shared consciousness or a shared phenomenal field. See [`V0_48_BLOCK_SUMMARY.md`](V0_48_BLOCK_SUMMARY.md).

Version 0.47.0-dev1 tests whether two independently parameterized v0.46-style agents can form a hidden interaction state that is functionally stronger than a successful communication code. A rank-four common manifold is discovered from synchronized local workspace trajectories without hidden factor labels and represented through certified Komorebi shared/nonshared packets.

The frozen four-seed holdout contained 384 unique dyadic cases and 3,456 matched decisions. All 28 frozen endpoints passed. The full shared system achieved perfect joint-task accuracy, bidirectional causal patching, pair-provenance protection, planner binding, consequence-driven reopening, and partner remapping. A message-only route also achieved perfect immediate task accuracy but had zero shared-workspace closure, demonstrating that cooperation alone is insufficient for the stronger claim.

This establishes a bounded causally distributed functional workspace in a deterministic synthetic dyad. It does not establish one shared consciousness or phenomenal field. See [`V0_47_BLOCK_SUMMARY.md`](V0_47_BLOCK_SUMMARY.md) and the frozen protocol at [`validation/V0_47_DISTRIBUTED_SHARED_WORKSPACE_PROTOCOL.md`](validation/V0_47_DISTRIBUTED_SHARED_WORKSPACE_PROTOCOL.md).

Verify the packaged v0.47 evidence on Windows with:

```powershell
.\VERIFY_V047_PACKAGE.ps1
```

After the pre-outcome freeze exists, verify it and run one claimed seed with:

```bash
python -m rrct.access_generalization_experiment verify-freeze
python -m rrct.access_generalization_experiment run-pilot --seed 16342 --attempt-id G1-P-0001
```

## Quick start

Python 3.10 or newer is recommended. Run commands from this directory.

### Windows PowerShell

```powershell
py -m venv .venv; & .\.venv\Scripts\python.exe -m pip install --upgrade pip; & .\.venv\Scripts\python.exe -m pip install -e '.[figures]'; & .\.venv\Scripts\python.exe -m rrct.cli verify; & .\.venv\Scripts\python.exe -m rrct.cli demo --output results_v0.4 --seed 17 --train-episodes 256 --test-episodes 128
```

Inspect a single deterministic run:

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli inspect --seed 17
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

The demonstration writes current-version artifacts to `results_v0.4/`. All v0.1 through v0.3 result directories remain historical records.

- `summary.json`, including configuration, aggregate measurements, and the conjunctive signature
- `ablations.csv`, containing matched full-system and ablation results
- `task_accuracy.png`, comparing behavioral task performance
- `temporal_persistence.png`, showing the decay of an injected perturbation through time
- `diagnostic_profile.png`, showing the components of the causal diagnostic profile

The completed v0.2 validation passes 44 of 44 tests and all six internal checks. Under unchanged thresholds, the trained condition passes the primary run, all four known-seed regressions, and all four untouched holdouts. Training reduced mean held-out self-prediction RMSE by 26.04% on the untouched seeds with zero test-time updates. The gain sweep shows a replicated, mostly graded causal response and a candidate ignition interval from 0.2 to 0.6. This is not a demonstrated phase transition. [The validation report](VALIDATION_REPORT.md) preserves the full v0.2 result and the mixed v0.1 record.

For v0.3, 67 of 67 implementation tests pass with warnings treated as errors, all six frozen internal checks pass, and all 17 final raw artifacts pass SHA-256 verification.

For v0.4, **109 of 109** implementation tests and all six internal checks pass. All **160 of 160** frozen confirmatory rows, **160 of 160** directed cut audits, and **56 of 56** Jacobian sidecars are retained and independently verified. The final raw-artifact manifest verifies **70 of 70** files.

For v0.5, **113 of 113** implementation tests pass and all **8 of 8** preregistered causal-exclusion gates pass on eight untouched seeds. Live hidden-self interventions changed workspace dynamics and control telemetry in 8/8 seeds, while exact replay and the self-ablated core had zero hidden-self response. This establishes a causal-organization result, not phenomenal consciousness; see the [v0.5 validation report](validation/V0_5_VALIDATION_REPORT.md).

For v0.8, **153 of 153** implementation tests pass with warnings treated as errors. In a development-only 2 x 2 benchmark, the learned forecaster reduced literal hidden-suffix observation RMSE by **20.26%** relative to fixed decay in all four seeds. That gain did not transfer to intervention quality: the learned uncalibrated policy was slightly harmful on average. The conformal gate eliminated harmful actions by abstaining on every trial, which also gave it zero useful-opportunity recall. This is a clean mechanism result and an isolated failure, not successful self-improvement or evidence of consciousness; see the [v0.8 development notes](validation/V0_8_DEVELOPMENT_NOTES.md).

Run the v0.8 development benchmark from Windows PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli calibrated-intention-dev --output validation\v0.8_calibrated_intention_reproduction --seeds 2003,2011,2017,2027 --train-episodes 64 --calibration-episodes 32 --evaluation-episodes 32 --horizon 4 --query-budget 4 --magnitude 0.35 --calibration-alpha 0.05 --calibration-min-samples 19
```

Use a new output directory for every preregistered run. Do not replace an existing result after looking at it.

## v0.10 adaptive-feedback development

Version 0.10 is **exploratory, not externally preregistered, and not
confirmatory**. It tests the narrow idea that useful recurrence depends on a
balanced feedback loop rather than maximal or minimal gain. Telemetry from a
completed step changes gains only for the next step. The returned step records
the gain that produced it, the next committed gain, the admitted workspace
states and weights, and the controller telemetry. Fixed mode retains v0.9
numerical behavior.

The canonical substantive run remains the immutable `0.10.0-dev1` artifact.
The installable `0.10.0-dev2` package repairs wheel-mode provenance collection;
its one-seed equivalence replay produced byte-identical telemetry, predictions,
seed summaries, and contrasts. It does not relabel a dev2 reproduction as the
original frozen run. See the
[post-outcome release amendment](validation/V0_10_RELEASE_AMENDMENT.md).

The eight-seed development run compares aligned adaptation with fixed gains
0.25, 0.65, and 1.05, a calibration-selected static arm, a cross-regime
schedule-preserving negative control, and removal of only the explicit
self-to-workspace feedback path. All 12 integrity checks pass. Adaptive aligned
has the highest pooled mean external-task accuracy, **0.9604**, but its paired
gain over the calibration-selected static arm is **0.0166**, 95% interval
**[-0.0156, 0.0547]**, below the frozen 0.02 threshold. Its gain over the
shuffled schedule is **0.0117**, interval **[0.0054, 0.0181]**: a positive
descriptive contrast that also misses the frozen 0.02 minimum. The changing-
load gate fails. All three scientific gates therefore fail.

The trajectory is informative. Recurrence rises briefly after the initial
cues, then falls from about 0.718 to 0.447 during the quiet delay. Final-step
surprise arrives too late for a next-step controller to use. This post-outcome
pattern motivates testing a persistent estimate of unresolved future
information, not post-result retuning of this controller.

Run the same parameter design into a new directory from Windows PowerShell.
Under dev2 it is correctly labeled an amended reproduction, not the original
frozen dev1 run:

```powershell
& .\.venv\Scripts\python.exe -m rrct.adaptive_feedback_experiment --output validation\v0.10_adaptive_feedback_reproduction
```

See the [pre-outcome protocol](validation/V0_10_DEVELOPMENT_PROTOCOL.md),
[development notes](validation/V0_10_DEVELOPMENT_NOTES.md), and
[machine-readable summary](validation/v0.10_adaptive_feedback_development/adaptive_feedback_summary.json).
The bounded integrated-throughput value is an internal engineering proxy, not
a consciousness metric. Bayesian transfer remains fail-closed under adaptive
feedback until active gains are included in its frozen feature schema.

## v0.9.0-dev1 Bayesian causal-transfer development

Version 0.9.0-dev1 is **development-only, not preregistered, and not confirmatory**. It separates base predictor training, Bayesian transfer training, conformal calibration, and evaluation into deterministic episode splits with disjoint hashes. A per-seed, no-intercept Normal-Inverse-Gamma regression uses 20 bounded, named internal features to correct the rollout-predicted benefit of a bounded self-state candidate. Candidates that share one revealed continuation receive fractional weights summing to one effective episode.

The term *causal transfer* has a deliberately narrow meaning here. For candidate \(j\), the regression target is

\[
\frac{(e_0-e_j)-\widehat r_j}{4\sqrt{d_w}},
\]

where \(e_0-e_j\) is the paired realized reduction in the agent's internal `error_norm` under baseline and candidate self-state interventions on the same observation suffix, \(\widehat r_j\) is the rollout-predicted reduction, and \(d_w\) is workspace dimension. Paired intervention outcomes give the target its causal interpretation within this fixed simulator and metric; the Bayesian regression is conditional prediction, not causal identification by itself. It does not estimate arbitrary environmental effects, prove external task improvement, or learn from held-out evaluation outcomes.

The development runner compares exact-zero, rollout, Bayesian-mean, Bayesian-credible, conformal, and deterministically permuted-outcome controls. Predictor, forecaster, posterior, and calibration state are frozen during evaluation. The risk-coverage table uses thresholds fixed from within-seed calibration predictions, plus the zero operating point and a no-action sentinel; evaluation outcomes never set those thresholds.

### Portable artifacts and audits

- Predictor and observation-forecaster snapshots, plus real and permuted Bayesian posteriors, are written as compressed NumPy artifacts and loaded with `allow_pickle=False` by `load_flat_snapshot_artifact()` and `load_transfer_snapshot_artifact()`.
- Transfer snapshot loading is transactional. The agent validates schema, dimensions, bounds, named coordinates, array hashes, posterior sufficient statistics, contiguous update receipts, configuration keys, provenance, the permuted-control mapping, and the final snapshot digest before replacing live state.
- Calibration banks retain configuration-matched records and digests. Explicit resets retain reason, epoch, count, and before/after digest receipts.
- CSV artifacts retain transfer evidence, held-out candidate predictions, calibration rows, policy rows, seed summaries, calibration-only risk-coverage rows, and the split manifest. The JSON summary retains development gates, integrity checks, metric definitions, and hashes of the generating source files.
- The runner refuses a nonempty output directory, restricts execution to the declared development seeds, checks split-hash disjointness and complete row retention, and audits nonmutating planning, commit-before-reveal ordering, offline/API agreement, and zero held-out posterior or calibration updates.
- `SHA256SUMS.txt` covers every generated artifact other than the manifest itself. Verify that manifest separately before trusting or comparing a run.

Run one clean development reproduction from Windows PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m rrct.bayesian_transfer_experiment validation\v0.9_bayesian_transfer_reproduction --predictor-episodes 64 --transfer-episodes 64 --calibration-episodes 32 --evaluation-episodes 64
```

The destination must be new or empty. The audited development run passes
**177 of 177** warning-as-error tests and all **17** artifact-integrity checks.
Mean held-out candidate RMSE fell from **0.029716** for rollout to **0.013582**
for Bayesian transfer, a **54.29%** reduction, with improvement in all four
seeds. This predictive gain did not produce a successful policy. Bayesian-mean
selection made 59 interventions, of which 46 were harmful, and had mean net
improvement **-0.001683**. The credible policy abstained everywhere; Bayesian
plus conformal acted 4 times, harmed twice, and had negative net improvement.
Only the predictive gate passed; all four downstream policy gates failed.

See the [v0.9 development notes](validation/V0_9_DEVELOPMENT_NOTES.md) and the
[machine-readable summary](validation/v0.9_bayesian_transfer_development/bayesian_transfer_summary.json).
This experiment measures bounded prediction and selective control of one
internal error metric. It is **not evidence of consciousness, sentience,
subjective experience, or moral status**.

## v0.4 frozen validation

The [v0.4 preregistration](validation/V0_4_PREREGISTRATION.md) and [pre-outcome freeze receipt](validation/V0_4_FREEZE.json) fixed eight untouched seeds, the complete experiment grids, all decision gates, the 158-coordinate state ordering, epsilon 1e-5, and 20,000 complete-seed bootstrap resamples before outcomes were generated.

The result is specific rather than uniformly positive:

- Recurrence contributes to closure and temporal persistence, and is strictly necessary for closure under the tested full configuration.
- Explicit self feedback contributes to closure, but its persistence effect is unresolved.
- Explicit action feedback and the preregistered positive self/action cooperative interaction are unsupported.
- Both piecewise-local association gates pass: gain versus spectral radius has mean seed-level Spearman ρ **0.9554**, and spectral radius versus persistence has mean ρ **0.8705**.
- One retained sub-threshold branch-switching cell produces a large finite local derivative. It is reported as a caveat, not removed.
- Predictor-organization dose worsens held-out RMSE with ρ **1.0 in every seed**, but the downstream self-to-workspace gate fails. The fidelity effect is supported; universal or joint mediation is not.

Exact values, confidence intervals, failed gates, and limitations are in the [validation report](VALIDATION_REPORT.md) and [machine-readable v0.4 decisions](validation/V0_4_DECISIONS.json).

### v0.4 commands

Windows PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli path-decomposition --output validation\v0.4_path_decomposition --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,1 --closure-gain 1 --self-feedback-gains 0,1 --action-feedback-gains 0,1 --train-episodes 64 --test-episodes 32 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
& .\.venv\Scripts\python.exe -m rrct.cli local-dynamics --output validation\v0.4_local_dynamics --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,0.2,0.4,0.6,0.8,1,1.2 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 32 --train-delay 5 --warmup-episodes 1 --test-delay 7 --finite-difference-epsilon 1e-5 --persistence-horizon 12 --bootstrap-resamples 20000 --bootstrap-seed 20260820
& .\.venv\Scripts\python.exe -m rrct.cli predictor-dose --output validation\v0.4_predictor_dose --seeds 223,227,229,233,239,241,251,257 --doses 0,0.25,0.5,0.75,1 --recurrent-gain 1 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 128 --test-episodes 64 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
```

POSIX shell:

```bash
python -m rrct.cli path-decomposition --output validation/v0.4_path_decomposition --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,1 --closure-gain 1 --self-feedback-gains 0,1 --action-feedback-gains 0,1 --train-episodes 64 --test-episodes 32 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
python -m rrct.cli local-dynamics --output validation/v0.4_local_dynamics --seeds 223,227,229,233,239,241,251,257 --recurrent-gains 0,0.2,0.4,0.6,0.8,1,1.2 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 32 --train-delay 5 --warmup-episodes 1 --test-delay 7 --finite-difference-epsilon 1e-5 --persistence-horizon 12 --bootstrap-resamples 20000 --bootstrap-seed 20260820
python -m rrct.cli predictor-dose --output validation/v0.4_predictor_dose --seeds 223,227,229,233,239,241,251,257 --doses 0,0.25,0.5,0.75,1 --recurrent-gain 1 --closure-gain 1 --self-feedback-gain 1 --action-feedback-gain 1 --train-episodes 128 --test-episodes 64 --train-delay 5 --test-delay 7 --bootstrap-resamples 20000 --bootstrap-seed 20260820
```

The completed records are in `validation/v0.4_path_decomposition/`, `validation/v0.4_local_dynamics/`, and `validation/v0.4_predictor_dose/`. Do not rerun these commands into the existing directories.

## v0.3 frozen validation

The [v0.3 preregistration](validation/V0_3_PREREGISTRATION.md) froze eight new seeds, unchanged diagnostic thresholds, the gain grids, predictor controls, and interpretation rules before outcomes were inspected.

- Dense boundary scan: joint gains 0.20 through 0.70 in steps of 0.05
- Two-dimensional surface: recurrence and explicit closure gains independently varied from 0.0 through 1.2
- Predictor mediation: `trained_self_model`, `untrained_self_model`, spectrum-preserving `shuffled_trained_self_model`, and `no_self_model`
- Path dependence: ascending and descending joint-gain paths with retained dynamic state, fixed settling, and a doubled-settling check

The explicit `closure_gain` controls only prior self/action-to-workspace feedback. Setting it to zero does not remove adaptive-resolution influence. The continuous closure statistic is the minimum widest-path capacity of the causal-effect graph, divided by the fixed 0.35 intervention magnitude and never clipped.

The dense scan and gain surface each train one predictor snapshot per seed at standard gains, freeze it, and reuse that identical snapshot at every gain or cell. Recorded snapshot identifiers make the matching auditable and prevent gain effects from being conflated with gain-specific predictor adaptation.

The frozen path protocol uses an analytic period-8 drive, 8 settling cycles and 4 measurement cycles at every gain, a 12-step persistence horizon, and fresh matched ramps with 16 settling cycles. The primary path-dependence gate is based on normalized workspace hysteresis area across the eight seeds. The preregistration also fixes a 20,000-resample seed-level bootstrap with RNG seed 20260819 for the declared confidence intervals.

Positive recurrence-by-explicit-closure interaction requires a positive interior closure-strength interaction mean in at least six of eight seeds and a paired bootstrap 95% lower bound above zero. Causal predictor mediation requires trained prediction to beat both predictor controls under the frozen RMSE gates and a trained-versus-shuffled change in either closure strength or self-to-workspace effect whose paired 95% interval excludes zero. Improved prediction without that downstream change is reported as prediction improvement without causal mediation.

### v0.3 outcomes

- Primary compatibility is unchanged and passes with Ω = **1.001001001001001** and continuous closure strength **0.011660619633017824**.
- Arm A retains all 88 rows and shows a primarily graded gain response. The descriptive steepest intervals are **0.45–0.50** for closure strength and **0.40–0.45** for persistence; all eight seeds pass only at gain 0.70.
- Arm B retains all 392 rows. All eight seed-level interior interaction means are positive, with mean **0.00549061214624777** and paired 95% interval **[0.004920031461324668, 0.006044879210797403]**. The frozen positive recurrence-by-explicit-closure interaction gate passes.
- Arm C retains all 416 rows but fails the robust-hysteresis decision: workspace-area medians are **0.007730080086928456** and **0.00789773225453549**, and only one of eight seeds reaches 0.05 after doubled settling.
- Arm D retains all 32 rows. Trained RMSE is **0.02763867621877439**, versus **0.03980657297396817** untrained and **0.1460319082865288** shuffled-trained, with trained winning 8 of 8 seeds against each. The downstream functional-mediation gate passes through a shuffled-minus-trained self-to-workspace change of **0.006365277396101022**, whose 95% interval excludes zero. The trained organization has the smaller direct effect, so this is an organizational or regularizing change, not increased closure.

The completed results support two bounded functional claims: a positive factorized closure interaction and predictor-mediated downstream causal change. They show a graded candidate-boundary neighborhood and no robust hysteresis. Therefore they do **not** support a phase transition, critical point, or consciousness claim. Exact outcomes and limitations are in the [validation report](VALIDATION_REPORT.md), with machine-readable decisions in [V0_3_DECISIONS.json](validation/V0_3_DECISIONS.json).

### v0.3 commands

These validation arms are intentionally separate from the ordinary wrapper.

Windows PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m rrct.cli phase-sweep --output validation\v0.3_dense_boundary --seeds 149,157,167,173,181,191,199,211 --gains 0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7 --conditions trained_self_model --matched-predictor --train-episodes 64 --test-episodes 32
& .\.venv\Scripts\python.exe -m rrct.cli gain-surface --output validation\v0.3_gain_surface --seeds 149,157,167,173,181,191,199,211 --recurrent-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --closure-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --conditions trained_self_model --train-episodes 32 --test-episodes 16 --bootstrap-resamples 20000
& .\.venv\Scripts\python.exe -m rrct.cli hysteresis-sweep --output validation\v0.3_hysteresis --seeds 149,157,167,173,181,191,199,211 --gains 0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2 --train-episodes 64 --settle-cycles 8 --measurement-cycles 4 --drive-period 8 --persistence-horizon 12 --bootstrap-resamples 20000
& .\.venv\Scripts\python.exe -m rrct.cli predictor-mediation --output validation\v0.3_predictor_mediation --seeds 149,157,167,173,181,191,199,211 --train-episodes 128 --test-episodes 64 --bootstrap-resamples 20000
```

POSIX shell:

```bash
python -m rrct.cli phase-sweep --output validation/v0.3_dense_boundary --seeds 149,157,167,173,181,191,199,211 --gains 0.2,0.25,0.3,0.35,0.4,0.45,0.5,0.55,0.6,0.65,0.7 --conditions trained_self_model --matched-predictor --train-episodes 64 --test-episodes 32
python -m rrct.cli gain-surface --output validation/v0.3_gain_surface --seeds 149,157,167,173,181,191,199,211 --recurrent-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --closure-gains 0,0.2,0.4,0.6,0.8,1.0,1.2 --conditions trained_self_model --train-episodes 32 --test-episodes 16 --bootstrap-resamples 20000
python -m rrct.cli hysteresis-sweep --output validation/v0.3_hysteresis --seeds 149,157,167,173,181,191,199,211 --gains 0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2 --train-episodes 64 --settle-cycles 8 --measurement-cycles 4 --drive-period 8 --persistence-horizon 12 --bootstrap-resamples 20000
python -m rrct.cli predictor-mediation --output validation/v0.3_predictor_mediation --seeds 149,157,167,173,181,191,199,211 --train-episodes 128 --test-episodes 64 --bootstrap-resamples 20000
```

The four directories contain `phase_sweep.{json,csv,png}`, `gain_surface.{json,csv,png}`, `hysteresis.{json,csv,png}`, and `predictor_mediation.{json,csv,png}`, respectively. The frozen runs are complete. The failed robust-hysteresis gate and primarily graded continuous response rule out a v0.3 phase-transition or critical-point conclusion. None of these functional diagnostics is a consciousness test.

## v0.2 seed and gain sweeps

The ordinary wrapper still runs only verification and the primary demonstration. The sweeps are separate because they are more expensive and because confirmatory outputs must not be overwritten.

The frozen protocol is recorded in [the v0.2 preregistration](validation/V0_2_PREREGISTRATION.md). The known seeds are regression cases already inspected in v0.1. The new holdout seeds provide the untouched v0.2 evaluation.

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

The seed sweep writes `seed_sweep.json`, `seed_sweep.csv`, and `seed_sweep.png`. The joint-gain sweep writes `phase_sweep.json`, `phase_sweep.csv`, and `phase_sweep.png`. In the gain sweep, each listed value is assigned to both `recurrent_gain` and `closure_gain`. The conditions are a trained then frozen self-model, a matched untrained frozen self-model, and a no-self-model control.

The command name `phase-sweep` identifies the experiment, not its conclusion. A smooth gain response is graded dependence. A largest observed slope is only a candidate boundary. A phase-transition claim would require a robust replicated discontinuity or other preregistered critical signature.

## Minimal Python use

```python
import numpy as np

from rrct import AblationFlags, RRCTAgent

agent = RRCTAgent(
    observation_dim=12,
    action_dim=2,
    n_levels=4,
    recurrent_gain=1.0,
    closure_gain=1.0,
    self_model_mode="train",
    seed=17,
)

agent.reset(seed=17)
for _ in range(32):
    record = agent.step(np.zeros(12), source="training")

agent.freeze_self_model()
held_out_record = agent.step(np.zeros(12), source="held_out")
action = agent.choose_action()
state = agent.snapshot()

agent.set_gains(recurrent_gain=0.4, closure_gain=0.8, reset=True)
agent.set_path_gains(self_feedback_gain=1.0, action_feedback_gain=0.0, reset=True)

no_self_model = RRCTAgent(
    observation_dim=12,
    action_dim=2,
    seed=17,
    ablations=AblationFlags(self_model=True),
)
```

An ablation flag set to `True` means that mechanism is disabled. The supported mechanisms are `recurrence`, `self_model`, `broadcast`, `memory`, and `resolution`.

The auditable default is `self_model_mode="frozen"`. Choosing `"train"` permits one-step predictor updates. Call `freeze_self_model()` before any held-out measurement. `train_self_model()` re-enables updates for a new declared training split. An ordinary `reset()` clears dynamic state while retaining learned predictor weights. `reset(seed=...)` rebuilds the seeded components and therefore resets those learned weights.

`set_gains(..., reset=True)` clears dynamic state while preserving learned predictor parameters. `reset=False` retains dynamic state for an explicitly preregistered continuation path. The two gains are independent. `closure_gain` is always described as explicit closure gain because another self/controller route remains through adaptive resolution.

## What the measurements mean

The experiment reports a diagnostic profile rather than a binary consciousness label:

| Measurement | Operational question |
|---|---|
| Broadcast reach | Does a local intervention influence multiple downstream components? |
| Temporal depth | Does the effect persist through the recurrent loop? |
| Differentiation | Does the active state support distinguishable patterns rather than collapse to one mode? |
| Metacognitive calibration | Does confidence track correctness under held-out perturbations? |
| Self-location | Can the self-model predict the agent's own state or action better than matched controls? |
| Episodic binding | Can information be associated correctly across separated time steps? |
| Projector consistency | Do the declared resolution levels satisfy their nesting and reconstruction constraints? |
| Causal closure | Does intervention flow form the intended strongly connected causal core? |
| Continuous closure strength | What is the weakest widest-path causal margin across all ordered node pairs? |

The conservative conjunctive score is the minimum threshold-normalized component, gated by causal closure. A high score therefore cannot compensate for a missing mechanism by being exceptionally strong on an unrelated measurement. Thresholds must be fixed before examining test results.

## Interpreting a result

A useful positive result has three parts:

1. The full architecture exceeds preregistered thresholds on the complete profile.
2. Matched ablations cause specific predicted losses rather than only a uniform loss of task accuracy.
3. A replay or open-loop control cannot reproduce the intervention-sensitive profile from the same visible outputs.

This would support the narrower statement that the implemented mechanisms form an integrated, self-model-guided causal loop. It would not validate the bridge from that organization to phenomenal experience.

A null or negative result is informative. If the full model is indistinguishable from matched ablations, if causal closure is absent, or if a noncausal replay passes the same tests, the present architectural hypothesis has failed in this implementation.

## Documentation

- [Theory](THEORY.md) states the mathematical proposal and its falsifiers.
- [Experiment protocol](docs/EXPERIMENT_PROTOCOL.md) defines matched controls, interventions, measurements, and reporting requirements.
- [Ethics](ETHICS.md) defines the nonvalenced design boundary and mandatory stop conditions.
- [Validation report](VALIDATION_REPORT.md) records successful, failed, corrected, and seed-sensitive results.
- [v0.4 preregistration](validation/V0_4_PREREGISTRATION.md), [freeze receipt](validation/V0_4_FREEZE.json), [artifact manifest](validation/V0_4_ARTIFACT_SHA256SUMS.txt), and [machine-readable decisions](validation/V0_4_DECISIONS.json) preserve the current validation.
- [v0.3 preregistration](validation/V0_3_PREREGISTRATION.md) froze the validation design before outcomes.
- [v0.3 freeze receipt](validation/V0_3_FREEZE.json), [artifact manifest](validation/V0_3_ARTIFACT_SHA256SUMS.txt), and [machine-readable decisions](validation/V0_3_DECISIONS.json) preserve provenance and final outcomes.

## Scope

This is a research prototype, not a diagnostic instrument for consciousness and not a deployable autonomous agent. It is intended for local, bounded, reproducible experiments. It should not be connected to external actuators, accounts, unrestricted networks, or self-modification systems.

### v0.24 development result
The frozen scale-invariant causal-self experiment generalizes the private-intervention self/other boundary across four held-out world-dynamics families without OOD retraining. See `validation/V0_24_DEVELOPMENT_NOTES.md`. This is a functional causal result, not evidence of subjective experience.

### v0.26 development frontier

The v0.26 experiment extends v0.25 by removing the supplied actuator-side boundary. It asks RRCT to jointly discover a hidden rank-2 efficacious internal command subspace inside eight mixed candidate command coordinates and the hidden rank-2 reachable sensory subspace inside twelve mixed sensory channels. Discovery uses only private perturbations and temporal structure; hidden projectors and self/other condition labels are evaluator-only. See `validation/V0_26_DEVELOPMENT_PROTOCOL.md`.

### v0.27 development frontier

v0.27 preserves the v0.26 joint discovery problem but adds disjoint-half replication for every accepted causal mode. It is designed specifically to falsify weak, sample-specific singular modes that can contaminate an otherwise correct discovered self/world interface.

### v0.28 intervention-provenance result

v0.28 removes the exact private perturbation vector supplied to the v0.27
learner. Four prospective anonymous handle commitments are crossed with six
anonymous process streams containing the true private innovation, its delayed
echo, policy-correlated and independent decoys, a stronger ungated exogenous
cause, and an other-agent disturbance. Only a unique interaction mode that
replicates in two disjoint calibration halves is accepted.

All 19 frozen gates pass on untouched seeds 5401, 5407, 5413, and 5419. The
exact hidden handle/source pair and rank two were recovered on every seed;
internal and sensory overlaps were 0.9999 and 0.9923. Learned hidden-remap
function was 0.2229 versus 0.0033 under takeover. A true-route lesion collapsed
the score to 0.0030, while a matched decoy-stream lesion retained 0.2243.
Passive association selected the stronger exogenous source on every seed and
was nonfunctional.

See `validation/V0_28_DEVELOPMENT_NOTES.md`. The prospective commitments are a
harness-generated primitive, and the batch model is not installed in
`RRCTAgent`; this is functional causal self-modeling, not evidence of subjective
awareness or phenomenal consciousness.

### v0.29 online self-boundary result

v0.29 moves prospective handle generation, rolling causal inference,
persistent/revisable boundary state, native specialist competition, and an
online self-supervised public access readout into `RRCTAgent`.  The agent is not
given the active handle/source pair, hidden rank, projectors, phase, source
families, goal, or oracle truth.  It commits balanced binary handles before six
equal-energy anonymous streams are realized and learns from the next revealed
mixed observation.

The frozen eight-seed official run has integrity PASS but scientific FAIL:
**34/35** all-seed gates pass.  Initial discovery, missing-probe retention,
route transfer, disconnection, restoration, provenance lesions, and the native
broadcast-path control all pass.  The sole failure is stable-shock exact-state
retention: seed 5607 scores 0.875 against 0.90 after two one-fit rank-2 to
rank-1 excursions.  The correct anonymous pair is retained throughout and the
terminal state is exact, but rank is part of the boundary, so the frozen
conjunction fails.

The failure exposes a specific updater gap: same-pair rank changes are installed
without confirmation and are not logged as revisions.  See
`validation/V0_29_OFFICIAL_DIAGNOSIS.md`.  The result is substantial but
incomplete functional causal self-modeling.  It is not evidence of phenomenal
self-awareness or consciousness.

### v0.30 confirmed structural self-boundary result

v0.30 treats `(active, handle, source, rank)` as the minimum persistent
boundary identity.  A different pair or rank must receive three consistent,
fresh-evidence confirmations before it can replace the committed state; the
support score is a paired randomization margin rather than a probability.  The
learner also uses a fixed RNG independent of the hidden world seed.

The frozen eight-seed official run has integrity PASS and passes **all 10/10
primary gates**.  It acquires the exact operational boundary, retains it under
stable shock and transient rank-one evidence, and makes exactly one confirmed
rank-two-to-one revision under sustained contraction and one confirmed
rank-one-to-two restoration in every seed.

This is learned, operational self-boundary and rank tracking in a bounded
synthetic benchmark.  The admitted rank is an empirical SVD dimension: testing
an additional mode still uses a global sharp-null screen, not a conditional or
reduced-rank test of `rank <= 1`.  The result therefore does not establish
phenomenal self-awareness, consciousness, subjective experience, sentience, or
valence.  See `validation/V0_30_OFFICIAL_DIAGNOSIS.md` and the
[machine-readable official summary](validation/v0.30_structural_self_model_revision_official/v030_structural_revision_summary.json).

### v0.31 conditional operational-rank result

v0.31 replaces the invalid higher-mode global sharp-null interpretation with a
cross-fitted reduced-rank randomization bootstrap.  A proposal fold fixes the
anonymous handle/source pair and lower-rank surface; two disjoint confirmation
folds test each additional mode while preserving that surface.  The observed
history is held fixed, so this is an approximate one-step composite-null test,
not an exact Fisher or full dynamic-null procedure.

The frozen eight-seed official run has integrity PASS but scientific FAIL:
**7/10 primary gate booleans pass**.  There is one underlying estimator miss in
56 episodes: seed 6001 returns a conditional null in `rank_one_strong`.  That
single miss flips three coupled gates.  All 32/32 rank-two/rank-three episodes
are exact, all 8/8 no-route episodes return null, and the correct persistent
rank-two state is admitted in all 8/8 two-window integration worlds.  No
episode is over-ranked.

The retained schema cannot localize the miss to proposal selection versus a
confirmation fold, and the official seed was not replayed.  The next block is
a fresh stage-resolved operating-characteristic study with complete proposal
and fold statistics, power as well as null calibration, and nonoverlapping
primary gates.  See `validation/V0_31_OFFICIAL_DIAGNOSIS.md` and the
[machine-readable official summary](validation/v0.31_conditional_rank_inference_official/v031_conditional_rank_summary.json).

This is incomplete progress in bounded functional causal self-modeling.  It is
not evidence of phenomenal self-awareness, consciousness, subjective
experience, sentience, valence, moral status, or an inner point of view.
