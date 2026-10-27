# SRIC Real-LRM Pilot 0.1.0

## Causal audit infrastructure for an external multimode Coconut model

This package is the first SRIC empirical block aimed at a third-party latent-reasoning checkpoint. It targets the released GPT-2 multimode Coconut model trained on PrOntoQA and implements the minimum causal audit needed before any semantic interpretation is admissible.

The package separates two statements that must not be conflated:

1. **The audit implementation works.** This is validated by an engineered procedure-specific latent fixture, unit tests, a toy causal-language-model replay test, frozen receipts, and a package manifest.
2. **The external checkpoint has procedure-specific or interpretable latent reasoning.** This has **not** been tested in this environment because the third-party model weights are not included and the runtime has no network-accessible model cache or CUDA device.

The maximum result emitted by Pilot 0.1 is `PROCEDURE_SPECIFIC`. Endogenous ontology discovery, causal semantic editing, and cross-model semantic transport are reserved for later stages.

## Primary audit ladder

The pilot classifies the checkpoint into one of the following states:

```text
ADAPTER_INVALID
LATENT_UNUSED
LATENT_UNORDERED
LATENT_MAGNITUDE_ONLY
SURFACE_UNSTABLE
LATENT_GENERIC
PROCEDURE_SPECIFIC
```

A checkpoint cannot receive a latent-computation classification unless exact replay succeeds. The sequence of tests is:

```text
ordinary latent execution
        ↓
exact captured-trace replay
        ↓
zero latent trace
        ↓
latent-step permutation
        ↓
norm-matched structured corruption
        ↓
same-answer, different-proof transplantation
        ↓
semantic-twin transplantation
        ↓
procedure-specificity decision
```

The decisive contrast is:

- a same-answer, different-proof donor should damage a genuinely procedure-specific trajectory;
- a surface-only semantic twin should not.

That contrast prevents a final-answer code or superficial prompt code from being mislabeled as a reasoning trace.

## Validated package status

The included engineered fixture reports:

- 48 task records
- exact replay error: 0
- latent-necessity mean effect: 0.149230
- latent-order mean effect: 0.237738
- norm-matched corruption mean effect: 0.346394
- same-answer, far-proof transplantation mean effect: 0.219653
- semantic-twin transplantation mean effect: 0
- final fixture status: `PROCEDURE_SPECIFIC`

These values validate the mechanics only. The fixture is explicitly marked `engineered_positive_control=true` and `real_checkpoint_used=false` in the result object.

## Quick package validation

```powershell
python -m pip install -r .\requirements.txt
python -m pytest -q
python .\independent_verify.py
python .\build_manifest.py
python .\verify_package.py
```

## External checkpoint setup

The setup script creates an isolated virtual environment, checks out the reviewed external repository commit, downloads the raw checkpoint and GPT-2 base model, and records the paths.

```powershell
Set-ExecutionPolicy -Scope Process Bypass -Force
.\Setup_External_PrOntoQA_Coconut.ps1
```

The pinned external components are:

```text
repository: connordilgren/are-lrms-easily-interpretable
commit:     32f413d8d55239d9bc54bb6b6ec37b0630891ed4
checkpoint: connordilgren/gpt2-prontoqa-multimode-coconut / checkpoint_37
base model: openai-community/gpt2
final data: data/prontoqa_test.json
```

The checkpoint is a raw state dictionary and is loaded through the external repository's `MultimodeCoconutModel`, not through `AutoModel.from_pretrained(checkpoint_repo)`.

## Sealed real run

The real run has two explicit stages.

### 1. Freeze the experiment

```powershell
.\Run_Real_LRM_Pilot.ps1 -StageOnly
```

This freezes:

- external repository commit
- complete checkpoint hash
- base-model reference
- complete dataset hash
- deterministic task subset
- same-answer donor assignment
- all thresholds
- all intervention seeds
- maximum admissible claim

### 2. Execute without changing the seal

```powershell
.\Run_Real_LRM_Pilot.ps1 -RunOnly
```

The runner refuses to proceed if the current model, dataset, donor plan, or configuration differs from the seal.

## Direct one-line Windows run

After setup:

```powershell
$ErrorActionPreference='Stop'; .\Run_Real_LRM_Pilot.ps1 -StageOnly; .\Run_Real_LRM_Pilot.ps1 -RunOnly
```

## Package layout

```text
SRIC_Real_LRM_Pilot_0.1.0/
  README.md
  PILOT_PROTOCOL.md
  ADAPTER_CONTRACT.md
  CLAIM_BOUNDARY.md
  PROTOCOL_CHRONOLOGY.md
  REAL_RUN_CHECKLIST.md
  EXTERNAL_DEPENDENCIES.md
  Setup_External_PrOntoQA_Coconut.ps1
  Run_Real_LRM_Pilot.ps1
  Run_Fake_Validation.ps1
  configs/
  data/
  docs/
  frozen/
  results/
  sric_real_lrm/
    adapters/
      fake.py
      multimode_coconut.py
    audit.py
    dataset.py
    donors.py
    interventions.py
    metrics.py
    sealing.py
  tests/
  build_manifest.py
  independent_verify.py
  verify_package.py
  package_manifest.json
```

## What this block establishes

The block establishes an executable and sealed route from a third-party recurrent latent state to SRIC's causal-audit objects. In particular, it implements:

- exact capture of the hidden state reinjected at each Coconut latent token;
- externally supplied trace replay;
- teacher-forced protected answer loss under each intervention;
- task-group-aware confidence intervals;
- deterministic same-answer donor selection;
- premise-order semantic twins;
- explicit result statuses and failure certificates;
- full-file checkpoint hashing;
- pre-audit sealing and result receipts.

## What this block does not establish

It does not yet establish that the external Coconut checkpoint:

- uses latent computation on PrOntoQA;
- encodes proof-specific content;
- has a discoverable semantic quotient;
- supports causal semantic editing;
- transports meaning to CODI or another latent reasoner;
- exposes a word-for-word hidden chain of thought.

The real checkpoint result must be generated on a machine with the downloaded model and pinned dependencies. A negative result remains canonical and must not be converted into a positive claim by moving thresholds after the audit.
