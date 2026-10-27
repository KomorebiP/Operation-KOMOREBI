# SRIC Block 24: External Latent-Reasoner Causal-Semantic Admission

**Release:** v0.3.2  
**Frozen scientific protocol:** v0.3.0  
**Canonical status:** `INFRASTRUCTURE_VALIDATED_EXTERNAL_EXECUTION_PENDING`  
**Author:** Komorebi P.  

This package is the first source-locked SRIC implementation intended to audit a third-party latent-reasoning checkpoint. It targets the public multimode GPT-2 Coconut checkpoint trained on PrOntoQA and turns the synthetic Block 16-23 methodology into a fail-closed external-model protocol.

The package does **not** contain the external repository, checkpoint, GPT-2 weights, or public dataset. It does **not** report a result for the real checkpoint. The actual checkpoint has not been executed in this build environment.

## What the package asks

The primary causal audit asks whether the model's recurrent latent trace is:

1. replayable through a source-faithful adapter;
2. useful for the protected answer;
3. temporally ordered;
4. structurally meaningful beyond vector norm or covariance;
5. stable under semantic-preserving surface changes;
6. specific to the current proof instance beyond final-answer identity.

Only a model passing the causal admission gates may enter semantic escalation. The semantic compiler then searches for a low-rank quotient that predicts later latent states, answer-residual future state, anonymous intervention effects, and the final answer while remaining stable across semantic twins. Gold proof steps and explicit-CoT mode are withheld until after the quotient is sealed.

## Primary claim tier

The PrOntoQA primary tier is explicitly labeled **content-specific**, not algorithmically procedure-specific. The public test family is dominated by fixed-form unary chains. A same-answer, different-proof transplant can show that traces are tied to task or proof-instance content, but it cannot by itself establish that the model represents different reasoning algorithms.

A stronger structure-sensitive follow-up is specified for ProsQA in `PROSQA_FOLLOWUP_PROTOCOL.md`.

## Sealed chronology

```text
verify source commit and Git blobs
        -> hash checkpoint and local GPT-2 snapshot
        -> choose deterministic task population
        -> reserve group-disjoint covariance calibration support
        -> freeze causal audit support and donor plans
        -> freeze semantic discovery/calibration/final partitions
        -> write pre-audit seal
        -> estimate covariance on calibration support only
        -> run causal audit on disjoint audit support
        -> if CONTENT_SPECIFIC, collect semantic discovery support
        -> collect semantic calibration support
        -> select and seal quotient
        -> only then collect semantic final twins/counterfactuals
        -> reveal proof-instance and explicit-CoT witnesses
        -> run causal subspace patching
        -> write result receipt
```

## External-runtime and terminal-summary hardening in v0.3.2

Version 0.3.2 is an infrastructure-only patch. It does not alter the v0.3.0 scientific gates, task profiles, donor rules, semantic chronology, or claim boundary. It adds:

- automatic discovery of an installed Python 3.10, 3.11, or 3.12 runtime;
- a revision-pinned asset downloader for the exact `checkpoint_37` file;
- a minimal allowlist for the GPT-2 base-model snapshot instead of downloading every framework variant;
- automatic retry through the standard HTTP/LFS path if the local Hugging Face Xet transfer fails;
- `-DisableXet` and `-LocalFilesOnly` setup modes;
- an asset receipt recording complete checkpoint SHA-256, size, minimal base-model tree SHA-256, revisions, and transfer mode;
- tests that reject unpinned or overbroad asset plans.

The external checkpoint remains unexecuted in the release environment. Asset-transfer failure is classified as infrastructure failure and cannot be interpreted as evidence about the model.

## Scientific safeguards frozen in v0.3.0

- Exact external repository commit and required Git blobs are verified.
- Hugging Face checkpoint and base-model revisions are pinned by setup commands.
- The complete checkpoint file and local base-model tree are hashed into the seal.
- Covariance-matched noise is calibrated on a group-disjoint support, not the causal audit rows.
- The semantic final support is not captured before quotient selection and sealing.
- Gold explicit-CoT is reserved for post-seal comparison and cannot aid quotient construction.
- PrOntoQA's maximum specificity claim is narrowed to content/proof-instance specificity.
- A separate source-faithful recurrence parity test compares the adapter engine against the reviewed upstream recurrence.
- The engineered fixture is staged before execution and is always marked as a non-real positive control.

## Status taxonomy

| Status | Meaning |
|---|---|
| `ADAPTER_INVALID` | Exact replay failed; later causal claims are inadmissible. |
| `LATENT_UNUSED` | Removing latent recurrence did not produce the frozen minimum effect. |
| `LATENT_UNORDERED` | Latent computation may matter, but the declared step order was not supported. |
| `LATENT_MAGNITUDE_ONLY` | Matched corruptions did not show enough dependence on latent structure. |
| `SURFACE_UNSTABLE` | A semantic-preserving twin changed the trace's functional effect too strongly. |
| `LATENT_GENERIC` | The trace was useful and ordered but did not show enough same-answer task specificity. |
| `CONTENT_SPECIFIC` | The trace was tied to proof-instance content beyond final-answer identity. |
| `PROCEDURE_SPECIFIC` | Reserved for datasets with genuinely varied solution structures and a structure-near versus structure-far contrast. |
| `ONTOLOGY_UNDERIDENTIFIED` | No low-rank semantic candidate passed the construction gates. |
| `SEMANTIC_CANDIDATE` | A quotient passed construction but not the post-seal proof-instance witness. |
| `SEMANTICALLY_IDENTIFIED` | Post-seal witness passed, but causal patching did not. |
| `CAUSALLY_VALIDATED` | The sealed quotient passed both post-seal witness and causal patching gates. |

## Engineered validation result

The included fixture is deliberately constructed to contain a causal semantic packet. It is a mechanical positive control, not evidence about Coconut.

- Frozen fixture seal: `68b04ea973f5030a7085d2b1891e87bedbf058db007d004fefee047beaee70b9`
- Fixture result receipt: `924157159d14b8d3715f2f886c2ad294b55f5cac15a3b63f1552df1b3731e620`
- Causal status: `CONTENT_SPECIFIC`
- Semantic status: `CAUSALLY_VALIDATED`
- Selected quotient: `joint`, rank 3
- Audit rows: 40
- Covariance calibration rows: 8
- Explicit-CoT used during construction: `false`
- Final semantic support captured before quotient seal: `false`

## Windows execution

### 1. Validate the package without external weights

```powershell
$ErrorActionPreference='Stop'; Expand-Archive .\SRIC_Block24_External_LRM_Causal_Semantic_Admission_v0.3.2.zip .\SRIC_Block24 -Force; Set-Location .\SRIC_Block24\SRIC_Block24_External_LRM_Causal_Semantic_Admission_v0.3.2; .\Run_Fake_Validation.ps1
```

### 2. Create the pinned external runtime

```powershell
.\Setup_External_PrOntoQA_Coconut.ps1
```

Useful fail-closed alternatives:

```powershell
# Force the standard HTTP/LFS path instead of Xet
.\Setup_External_PrOntoQA_Coconut.ps1 -DisableXet

# Verify and stage assets already present in the local Hugging Face cache
.\Setup_External_PrOntoQA_Coconut.ps1 -LocalFilesOnly

# CPU-only setup for adapter debugging; not the recommended final audit path
.\Setup_External_PrOntoQA_Coconut.ps1 -CpuOnly
```

The setup script creates an isolated Python 3.10-3.12 environment, checks out the pinned upstream commit, downloads the exact checkpoint plus only the required GPT-2 files, verifies the source blobs, hashes the complete local assets, and writes `external_runtime\runtime_paths.json`. If Xet transfer is unavailable, it retries through the standard HTTP/LFS path.

### 3. Run a 12-task smoke audit

```powershell
.\Run_Real_LRM_Pilot.ps1 -Profile smoke -Device cuda
```

### 4. Run the primary 64-task audit

```powershell
.\Run_Real_LRM_Pilot.ps1 -Profile primary -Device cuda
```

### 5. Run the 256-task audit only after reviewing the primary receipt

```powershell
.\Run_Real_LRM_Pilot.ps1 -Profile full -Device cuda
```

The default scientific order is smoke -> primary -> full. Do not alter thresholds after viewing a final result. A failure is a valid terminal result.

## Important boundary

This package validates infrastructure and an engineered positive control. It does not establish that the external Coconut checkpoint uses its latent states, represents proof-instance content, exposes a discoverable semantic quotient, or supports causal semantic editing. Those questions remain open until the source-locked checkpoint is run.

See:

- `BLOCK24_PROTOCOL.md`
- `BRAINSTORM_AND_DESIGN_DECISIONS.md`
- `CLAIM_BOUNDARY.md`
- `REAL_EXECUTION_STATUS.md`
- `REAL_RUN_CHECKLIST.md`
- `PROSQA_FOLLOWUP_PROTOCOL.md`

## Terminal-summary fix in v0.3.2

The 12-task smoke profile intentionally disables covariance-matched noise. Its result therefore records `causal_calibration: null`. Earlier summarization code incorrectly assumed this optional field was always an object and could raise an `AttributeError` after the result itself had already been written and verified. Version 0.3.2 handles this terminal path explicitly. The scientific result JSON and all frozen causal gates are unchanged.
