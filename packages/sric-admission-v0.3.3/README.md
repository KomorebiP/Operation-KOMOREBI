# SRIC admission runtime 0.3.3

**Beta / work in progress · corrected source edition · 27 October 2026**

This edition repairs the three acceptance/provenance defects recorded in the [Block 24 audit](../../docs/SRIC_ADMISSION_AUDIT_2026-10-27.md). It derives from the [preserved 0.3.2 source](../../research/sric-external-admission/) at commit `ad2b5089b2738bbe1c67345aaa634a45075995a2`. The old edition, its receipts, and its counterexamples are unchanged. The [edition manifest](EDITION.json) maps this source edition to its origin and records the changed files.

## Repaired behavior

- Empty or non-finite logits and losses are rejected before calibration, causal scoring, or semantic escalation. Latent traces must be finite matrices with the configured step count.
- Every replay error must be finite before taking a maximum. An invalid row cannot disappear because of its position.
- Missing, unknown, conflicting, or changing adapter identity is rejected. Engineered fixtures remain explicitly synthetic. Real adapters must declare their kind, supply pinned digests, and match an expected precommitted fingerprint.
- The command-line fixture path now honors `--data` without trying to read an unrelated hard-coded path.
- A fresh 0.3.3 protocol seal is required. Older seals are not upgraded implicitly.

Malformed evidence raises `AdapterValidationError`, a `ValueError` subclass, before an acceptance result is returned. A finite replay mismatch still yields `ADAPTER_INVALID`. Callers must preserve errors as failures and must not substitute an old result file.

## Run the qualification tests

From the collection root, using Python with NumPy available:

```text
python -B packages/sric-admission-v0.3.3/tests/test_admission_boundaries.py
```

The recorded environment is Windows, Python 3.12.14, NumPy 2.3.5. The suite has 15 test methods, including 48 NaN-position cases across 8 calibration and 40 audit tasks, invalid provenance controls, a finite-mismatch control, the original full synthetic fixture, and a command-line fixture/seal/run/receipt round trip. The real-provenance tests use artificial metadata solely to exercise schema and mismatch checks. They do not execute a real model. See the [qualification record](../../verification/audits/sric-repair-2026-10-27/run/manifest.json).

## Run the synthetic example

Change to this directory. Choose a fresh output directory for each run; `scratch/example-001` below is an example local path.

```text
python -B -m sric_real_lrm make-fixture --output scratch/example-001/tasks.json --count 48
python -B -m sric_real_lrm stage-fake --data scratch/example-001/tasks.json --output scratch/example-001/seal.json
python -B -m sric_real_lrm run-fake --data scratch/example-001/tasks.json --seal scratch/example-001/seal.json --output scratch/example-001/result.json
python -B -m sric_real_lrm verify-result scratch/example-001/result.json
```

Expected fixture status is `CAUSALLY_VALIDATED`, with `real_checkpoint_evidence: false` and `real_checkpoint_used: false`. The status describes the engineered control only. From Python, `run_block24_pipeline(adapter, records, config)` supports an explicitly identified engineered adapter. Real-model callers must additionally supply `expected_fingerprint=...` from the precommitted record. The real CLI passes that record only after checking the sealed source/model/data inputs.

## Qualification boundary

This is a source-checkout runtime, not a qualified wheel or installer. Run from this directory so the configuration and source-lock files resolve correctly. NumPy is required; Torch, Transformers, external checkpoints, and GPU execution were not installed or tested in this repair pass. The preserved real dependency lists are preparation references, not evidence of compatibility on this host.

Fingerprint checks establish explicit identity and consistency with the supplied pinned record. They do not independently attest that arbitrary adapter code is truthful or that a model has the claimed scientific properties. The built-in real adapter retains its source verification and file hashing; that full execution path still needs a separately recorded real-model campaign. No semantic estimator, bootstrap coverage, hardware claim, or broader SRIC endpoint is certified by these repairs.

The reader list points to this corrected edition as a scoped beta instrument. The original edition retains its documented defects. Real-model execution and broader scientific qualification remain open. See the [maintained repair report](../../docs/SRIC_REPAIR_2026-10-27.md) for exact evidence and remaining gates. Code follows the [collection code terms](../../LICENSE-CODE.txt); retain upstream notices and third-party terms in any external runtime.
