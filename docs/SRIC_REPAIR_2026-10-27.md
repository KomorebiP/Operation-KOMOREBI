# SRIC admission repair: runtime 0.3.3

**27 October 2026 · Komorebi P. · Beta / work in progress · AI-assisted self-review**

The three failures reproduced in the [earlier audit](SRIC_ADMISSION_AUDIT_2026-10-27.md) are repaired in a [separate 0.3.3 source edition](../packages/sric-admission-v0.3.3/README.md). The original 0.3.2 sources and counterexample record remain intact. The corrected edition returns to the research reading list as a scoped beta instrument; no real-model result or broader semantic claim is promoted.

## Changes and evidence

| Obligation | Correction | Observed qualification |
|---|---|---|
| A1: empty replay logits | Validate every capture and scoring observation before consumption; require nonempty finite logits, finite scalar losses, and compatible latent-trace matrices. | Empty capture/scoring logits and malformed loss/trace controls are rejected. |
| A2: NaN hidden by aggregation order | Validate individual observations and every replay error before taking the maximum. | A NaN is rejected at all 48 individual positions: 8 calibration and 40 audit tasks. NaN and positive/negative infinity in scored output are rejected. |
| A3: absent identity inferred to be real | Require explicit engineered or real provenance. Real identity needs pinned source/checkpoint/base-model digests matching a precommitted expected record. Check identity stability around adapter calls. | Missing, ambiguous, contradictory, malformed, mismatched, and changing identity controls are rejected before acceptance. Artificial metadata is used solely for these schema controls. |
| Positive and finite-negative controls | Preserve the scientific fixture configuration and finite replay threshold behavior. | Full fixture remains `CAUSALLY_VALIDATED` with real-checkpoint evidence false; a finite mismatch remains `ADAPTER_INVALID`. |
| Usable command-line path | Remove an unused hard-coded fixture-file read; require a new 0.3.3 seal. | A fresh custom-path fixture/seal/run/receipt round trip passes; an old-edition seal is rejected. |

The implementation adds observation/provenance validation at the pipeline boundary, standalone causal admission, and semantic escalation. Invalid evidence raises `AdapterValidationError` before an accepted result is emitted. The real CLI forwards the already-checked sealed identity to the pipeline. A matching identity record establishes consistency with declared provenance; it cannot independently attest arbitrary third-party adapter behavior.

**Outcome: implementation and finite assertions verified in the stated range.** The [bounded run](../verification/audits/sric-repair-2026-10-27/run/manifest.json) completed successfully on Windows with Python 3.12.14 and NumPy 2.3.5. All **15 unittest methods** passed, including the parameterized controls above. [Raw test output](../verification/audits/sric-repair-2026-10-27/run/stderr.txt), [contract](../verification/audits/sric-repair-2026-10-27/contract.json), and [edition manifest](../packages/sric-admission-v0.3.3/EDITION.json) record the tested scope and source hashes. The runner's source copy has no Git checkout; exact imported-source identities and new edition bytes are recorded separately.

The package guide gives both the qualification command and the four-command synthetic example. The collection workflow also runs the new suite with pinned NumPy. Workflow execution is separate from the recorded Windows run and does not expand its scientific interpretation.

## Remaining boundaries

The real checkpoint, Torch/Transformers integration, GPU execution, semantic-estimator correctness, bootstrap coverage, and held-out scientific claims were not qualified here. This edition is a source-checkout runtime; no wheel or installer is qualified. The original release's other tests and external-source parity checks were not all rerun. Broad real-model work remains in finalization gate F12.

Gate F15 is closed for the three reproduced admission defects and their explicit regression controls in this edition. Completion labels remain experiment/prototype and experimental evidence. Fresh protocol seals and a separately audited real-model campaign are required before making external empirical claims. The earlier counterexample harness continues to target 0.3.2 and is not the repaired edition's acceptance suite.

This is sequential AI-assisted self-review, not independent peer review. No Lean execution or whole-program correctness certification is claimed. The [repair review record](../manifests/sric-repair-review-2026-10-27.json) binds this report, the computation, and its inspected source revision.
