# Komorebi Neuralese Stable Quotient v0.2.0

This package turns the v0.1.1 recurrent-instability finding into a tested mathematical and engineering resolution.

The apparent instability had two parts:

1. **Radial explosion:** an exact, behaviorally irrelevant positive-scale gauge in the bias-free linear recurrence.
2. **Projective drift:** a genuine directional error that accumulates under long compositions.

The first part is removed exactly by computing on positive rays. The second is removed exactly by an engineered semantic-chart closure and reduced dramatically by terminal-only projective training.

## Achieved result

The trainable projective arm uses the same 4,224-parameter operator-shaped model as v0.1.1 and the same terminal-answer objective. Its sole architectural change is unit normalization after each recurrent update. It is trained only on randomly conjugated D4 words of lengths 1–4.

| Two-seed mean | L12 | L64 | L128 | L256 |
|---|---:|---:|---:|---:|
| Raw v0.1.1 terminal model | 0.8403 | 0.3867 | 0.2869 | 0.0000* |
| Projective terminal-only model | **1.0000** | **1.0000** | **0.9924** | **0.8477** |

`*` The raw float32 recurrence overflowed; a normalized replay of the same frozen weights remains finite but does not repair its angular drift.

The trained projective arm also achieved:

- 1.000 state transplantation and 1.000 operator replacement at depth 64
- at most 0.0781 and 0.0654 on the matched random controls
- 1.000 cross-seed transported continuation versus 0.0039 for a random map
- 1.000 C8 and mixed-cycle accuracy through depth 64
- 0.7351 C8 and 0.8665 mixed-cycle mean accuracy at depth 256
- finite hidden states in every evaluated arm, family, and depth

All 14 developmental projective-training gates passed. These are two-seed developmental results, not confirmatory estimates.

## Komorebi mathematical resolution

The original recurrence is

\[
h_{t+1}=M_t h_t,\qquad \ell_t=Wh_t,
\]

with no update or decoder bias. Therefore every positive rescaling has exactly the same future argmax behavior:

\[
h\sim \alpha h,\qquad \alpha>0.
\]

The first correct semantic object is consequently the positive projective quotient

\[
(H\setminus\{0\})/\mathbb R_{>0},
\]

not raw Euclidean hidden space.

The learned state anchors form a full basis \(B\). For a visible permutation table \(P\), the exact latent action is

\[
M_P=B P B^{-1}.
\]

This action preserves

\[
G=B^{-\mathsf T}B^{-1}
\]

and is similarity-equivalent to the canonical one-hot semantic chart, where the operator is simply \(P\), the metric is Euclidean, and the condition number is one. The `semantic_chart_closed` arm realizes that construction and obtained 100% accuracy at every tested depth and family, exact null-cycle return, exact causal replacements, and cross-seed intertwining residuals below \(3.6\times10^{-6}\).

That is an **engineered positive control**, not a discovery claim. It proves the task admits a bounded coordinate-independent realization and localizes the remaining learning error to the learned operator encoder.

## What remains unresolved

The trained projective model is not an exact ambient group representation. Table-verified null cycles preserved answers at least 99.41% of the time, while their hidden rays still separated by as much as roughly 0.47 radians in median after repeated loops. Accuracy also decayed on arbitrary independent permutation pairs, approaching 0.25 at long depth.

The next scientific target is therefore **projective path flatness on reachable states**, not norm control alone. Anonymous intertwining or composition pressure is a promising bridge, but it must be evaluated as explicit structural supervision and preregistered independently.

## Included experiments

| Runner | Purpose |
|---|---|
| `run_experiment.py` | Preserved v0.1.1 six-arm operator-workspace experiment |
| `run_stability_experiment.py` | Frozen-checkpoint gauge, observability, polar, exact-closure, causal, and transport audit |
| `run_projective_training.py` | Fresh terminal-only training on the positive-ray quotient |

The historical v0.1.1 results and checkpoints are retained under `results/pilot`. The v0.2 results are under `results/stability_pilot` and `results/projective_pilot`.

## Run on Windows PowerShell

Verify the package:

```powershell
.\VERIFY.ps1
```

Re-evaluate the included projective checkpoints:

```powershell
.\RUN_PROJECTIVE_REPLAY.ps1
```

Train fresh projective pilot checkpoints:

```powershell
.\RUN_PROJECTIVE_PILOT.ps1
```

Run the frozen-checkpoint stability audit:

```powershell
.\RUN_STABILITY_PILOT.ps1
```

CPU is the deterministic default. The pilot is developmental; use a newly frozen revision and fresh seeds for a confirmatory claim.

## Reading order

1. `RESULTS_SUMMARY.md`
2. `results/projective_pilot/REPORT.md`
3. `results/stability_pilot/REPORT.md`
4. `CLAIM_BOUNDARY.md`
5. `PROJECTIVE_PREREGISTRATION.json` and `STABILITY_PREREGISTRATION.json`
6. `DEVELOPMENT_LOG.md`
