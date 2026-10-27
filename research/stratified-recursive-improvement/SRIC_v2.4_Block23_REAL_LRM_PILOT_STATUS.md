# SRIC Block 23 Real Latent-Reasoner Pilot Status

## Target

The staged real-model target is a source-locked multimode GPT-2 Coconut checkpoint evaluated on PrOntoQA-style logical reasoning tasks.

The adapter captures the embeddings actually placed at latent-token positions and supports deterministic evaluation under externally supplied traces. The audit protocol includes replay, zero-latent, truncation, step permutation, norm-matched noise, semantic-twin transplant, and same-answer different-proof transplant.

## Source lock

Repository: `connordilgren/are-lrms-easily-interpretable`

Commit: `32f413d8d55239d9bc54bb6b6ec37b0630891ed4`

Checkpoint repository: `connordilgren/gpt2-prontoqa-multimode-coconut`

Checkpoint filename: `checkpoint_37`

Checkpoint SHA-256: **not yet committed**. This is deliberate. The digest must be computed from the locally obtained file before a real final audit.

## Current environment

- status: `ADAPTER_VALIDATED_REAL_EXECUTION_BLOCKED`
- real checkpoint executed: `False`
- blockers: `transformers_missing, repository_checkout_missing, checkpoint_missing, cuda_unavailable`
- Python: `3.13.5`
- Torch: `2.10.0+cpu`
- CUDA available: `False`
- Transformers available: `False`

## Package-local protocol evidence

- fake fixture tasks: 72
- fake fixture exact replay maximum: 0.000000

These numbers validate adapter contracts and intervention bookkeeping only. They are not empirical findings about Coconut or PrOntoQA.

## Required next execution

1. Obtain the exact repository commit in `frozen/SOURCE_LOCK.json`.
2. Obtain the declared checkpoint and compute its SHA-256.
3. Update the lock before any final audit.
4. Install the source-locked upstream runtime separately from the package verification environment.
5. Run `external_preflight.py` and require a ready status.
6. Run a small adapter smoke set and verify exact replay.
7. Freeze donor rules, semantic-twin transforms, task split, thresholds, and intervention seeds.
8. Run the real pilot without changing the frozen gates.
9. Preserve a failure or underidentification result as the canonical outcome if the model does not satisfy them.
