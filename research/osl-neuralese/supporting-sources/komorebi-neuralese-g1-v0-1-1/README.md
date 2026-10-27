# Komorebi Neuralese G1 v0.1.1

This package implements the first integration gate toward recurrent latent
reasoning: a frozen local Hugging Face causal language model coupled to a small,
trainable, shared recurrent workspace.

v0.1.1 corrects the Qwen answer-token boundary: the separator is now part of
the query, labels are bare ASCII tokens, and every registered prompt/label pair
must pass an exact contextual one-token continuation check before training.

The experiment is deliberately narrow. It asks whether a continuous state can
be constructed from one prompt, updated through repeated model feedback, and
then reused to answer several independently supplied queries. It does not claim
that a natural internal language has emerged.

## What is new

- A frozen Qwen-compatible backbone with a trainable latent workspace.
- Shared recurrent weights across internal steps.
- Residual reinjection at a selected decoder layer.
- A two-phase late-binding task. The transition problem is shown before the
  query and its codebook, so success cannot come from storing the final output
  token alone.
- Matched recurrent, no-feedback, no-injection, and shuffled-state evaluations.
- Stepwise recurrent traces and final-state causal interventions.
- Fail-closed engineering and scientific gates.
- Offline-only model loading and a Windows PowerShell entry point.

## Scientific question

Given a compute prompt `x` and a later query `q`, the model constructs

```math
z_0=P(h_ell(x)),
z_{t+1}=G(z_t,P(h_ell(x;A z_t))),
```

then answers `q` after injecting `A z_T` into the same frozen backbone.

The first gate is passed only when the complete pipeline runs, the backbone
remains frozen, gradients reach the workspace, recurrent state is nondegenerate,
and deterministic artifacts are written. Stronger scientific gates additionally
require recurrent performance to exceed causal controls.

## First run: wiring gate

```powershell
$d="$env:USERPROFILE\Downloads\Komorebi_Neuralese_G1_v0.1.1"; & "$d\Run_Neuralese_G1.ps1" -Profile wiring
```

When `-Model` is omitted, the runner first checks the registered RRCT model
path. If that path is absent, it searches Downloads and requires exactly one
`Qwen2.5-0.5B-Instruct` candidate.

If wiring passes, run the short end-to-end smoke:

```powershell
$d="$env:USERPROFILE\Downloads\Komorebi_Neuralese_G1_v0.1.1"; & "$d\Run_Neuralese_G1.ps1" -Profile smoke
```

## Explicit model path

```powershell
$d="$env:USERPROFILE\Downloads\Komorebi_Neuralese_G1_v0.1.1"; & "$d\Run_Neuralese_G1.ps1" -Profile smoke -Model "$env:USERPROFILE\Downloads\RRCT_v060_MODELS\Qwen2.5-0.5B-Instruct"
```

## Profiles

| Profile | Purpose | Training steps | Claim ceiling |
| --- | --- | ---: | --- |
| `wiring` | Minimal forward/backward and artifact check | 2 | Engineering only |
| `smoke` | Short end-to-end local run | 40 | Engineering only |
| `pilot` | Frozen causal pilot with preregistered gates | 2,000 | Single-seed small-model G1 |

The smoke profile is not intended to pass the scientific gates. Its job is to
expose integration, memory, dtype, tokenizer, and hook failures quickly.

After a successful smoke, the registered three-seed replication
can be run with:

```powershell
$d="$env:USERPROFILE\Downloads\Komorebi_Neuralese_G1_v0.1.1"; & "$d\Run_Neuralese_G1_Replications.ps1"
```

The aggregate adjudicator requires all three registered seeds, identical
experimental configuration, the same fully hashed model files, and a valid
single-seed result from every run.

## Output

Each run writes:

- `resolved_config.json`
- `preflight.json`
- `training.jsonl`
- `checkpoint.pt`
- `evaluation.json`
- `predictions.jsonl`
- `gates.json`
- `run_summary.json`
- `verification.json`

Rerunning into a nonempty completed output directory fails closed. Use a new
output directory for an independent run.

## Boundaries

This package does not establish consciousness, awareness, autonomous agency,
general Neuralese, faithful interpretability, recursive self-improvement, or
Astra-level capability. See `CLAIM_BOUNDARY.md`, `PROTOCOL.md`, `ROADMAP.md`,
and `UPSTREAM_AUDIT.md`.
