# SRIC admission audit: three acceptance gaps

**27 October 2026 · Komorebi P. · Work in progress · AI-assisted self-review**

The retained Block 24 Python pipeline has three reproducible acceptance/provenance gaps. Its ordinary engineered fixture still reaches its recorded synthetic outcome, but that positive control does not establish fail-closed handling of malformed adapter output. **Block 24 is deferred to the [incubator](INCUBATOR.md#research-sric-external-admission) pending a corrected edition and negative-control tests.** This is a bounded implementation audit, not a rejection of the whole SRIC research program.

The inspected edition is [commit 91ed38283ad9](https://github.com/KomorebiP/Operation-KOMOREBI/commit/91ed38283ad924cd56f0b0179f41ec8d19acb00c). The [review record](../manifests/sric-admission-review-2026-10-27.json) pins 28 source files. The [computation record](../verification/audits/sric-admission-2026-10-27/run/manifest.json), [contract](../verification/audits/sric-admission-2026-10-27/contract.json), and [output](../verification/audits/sric-admission-2026-10-27/run/stdout.txt) preserve the bounded run. Original component files and their receipts remain intact. This audit does not silently repair that historical edition.

## Findings

The [adapter contract](../research/sric-external-admission/ADAPTER_CONTRACT.md) requires own-trace replay of answer logits and a committed model fingerprint. These checks concern whether supplied evidence is admissible. Their failure must prevent a scientific acceptance label.

| Finding | Reproduction and cause | Required correction |
|---|---|---|
| A1: empty logits pass replay | Replace the fixture's answer logits with empty arrays in capture and scoring. `_max_logit_error` returns zero for equal empty shapes. The pipeline reaches `CONTENT_SPECIFIC`. | Reject empty, non-finite, or incompatible answer-logit arrays before calculating replay error. Validate every required observation, including clean captures. |
| A2: one NaN can disappear from the maximum | Place a NaN in the second audit task's clean logits. That row's replay error is NaN, but the Python `max` over errors returns the earlier finite zero, so the pipeline reaches `CONTENT_SPECIFIC`. The same corruption in the first audit row is rejected as `ADAPTER_INVALID`. | Require every row's replay error to be finite before aggregation. Acceptance must be independent of where an invalid row appears. Do not repair this with a NaN-skipping maximum. |
| A3: missing identity becomes real-model evidence | Use the unchanged synthetic fixture with `model_fingerprint()` returning `{}`. The pipeline sets `real_checkpoint_evidence` to `true` because it negates a missing `engineered_positive_control` flag with default `false`. | Missing or unknown identity must never establish real-checkpoint evidence. Require explicit validated source/checkpoint provenance and distinguish real, engineered, and unknown adapters. |

The relevant implementation is in [audit.py](../research/sric-external-admission/sric_real_lrm/audit.py) and [pipeline.py](../research/sric-external-admission/sric_real_lrm/pipeline.py). `_score` checks scored answer loss, but does not validate all replay logits. Clean observations also need validation. The maintained harness invokes the actual retained pipeline with small subclasses of its engineered adapter. It does not replace the classifier with a mock.

## Observed controls and limits

Seven pipeline executions used 48 generated tasks each, split into 8 covariance-calibration tasks and 40 audit tasks. Python 3.12.14 and NumPy 2.3.5 ran on Windows. The original full fixture configuration was used once. Six focused admission cases used 20 bootstrap replicates and disabled semantic escalation, truncation, and mode controls. Their acceptance thresholds and support split were unchanged.

| Case | Observed result |
|---|---|
| Original full fixture and configuration | `CAUSALLY_VALIDATED`. Real-checkpoint evidence `false`. This label applies only to the engineered fixture. |
| Focused unaltered fixture | `CONTENT_SPECIFIC`. Real-checkpoint evidence `false`. |
| Empty logits | Incorrectly admitted as `CONTENT_SPECIFIC`. Replay maximum zero. |
| NaN in first audit row | Rejected as `ADAPTER_INVALID`. |
| NaN in second audit row | Incorrectly admitted as `CONTENT_SPECIFIC`. One non-finite row, summary replay maximum zero. |
| Finite replay mismatch | Rejected as `ADAPTER_INVALID`. Replay maximum 994.725. |
| Missing fingerprint | `CONTENT_SPECIFIC` with incorrect real-checkpoint evidence `true`. |

**Verdict:** counterexamples reproduced to the generic Python pipeline's fail-closed claim. Exit status zero means that the diagnostic harness reproduced the expected defects and controls. It is not a qualification pass for Block 24. The run manifest reports its source-copy Git revision as unavailable. The separate review record authenticates the imported files against the exact repository commit.

No real model, checkpoint, GPU execution, or external-model claim was tested. This pass does not establish that the normal real-adapter CLI produces malformed arrays or bypasses its own preflight checks. It does establish that callers of the exposed Python pipeline can receive unsupported acceptance/provenance labels. The original fake adapter supplies its engineered marker correctly. Bootstrap coverage, semantic-estimator validity, source-parity replay, and the full protocol remain outside this audit.

## Reader decisions and next gates

- **Block 24 external admission:** remove from the main research reading list and retain here as an implementation needing correction. Publish a separately identified corrected edition, bind it to its tests, and retain the original source receipt. Require rejection of empty/non-finite logits in every position, missing or invalid provenance, and finite replay mismatches. Keep the positive fixture explicitly synthetic. A real-model run then needs its own pinned checkpoint, environment, receipt, and scientific assessment.
- **Block 23 semantic witness:** retain at its existing scoped status. Its [results](../research/sric-block23-witness/RESULTS.md) describe a finite synthetic construction, and its [real pilot status](../research/sric-block23-witness/REAL_LRM_PILOT_STATUS.md) says real execution is blocked. This pass checked that distinction in the writing. It did not rerun or certify Block 23's mathematics or experiments. The Block 24 defects are not automatically attributed to Block 23.

The absence of Lean is not a reason for either decision. Finite experiments need honest scope and sound acceptance checks. An unexecuted external run can remain a useful protocol, but it cannot supply external empirical evidence.

## Reproduce this audit

Use a separate checkout with the preserved source files and NumPy available. From the collection root:

```text
python -B verification/audits/sric-admission-2026-10-27/check_admission.py
```

Expected diagnostic status: `EXPECTED_DEFECTS_REPRODUCED`. The harness deliberately asserts the retained edition's defective behavior so future corrections can be compared with it. It must not be used as an acceptance suite for a repaired edition. No package installation or model download is performed. Collection CI validates the audit's bindings and maintained pages. This NumPy computation was run locally and is recorded separately.

This was a sequential AI-assisted self-review. There was no independent reviewer, peer-review certification, new Lean execution, or whole-collection soundness claim. The [earlier seven-entry review](SOUNDNESS_REVIEW_2026-10-27.md) remains a separate historical record.
