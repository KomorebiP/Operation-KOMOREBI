# Adapter Contract

The adapter is valid only when it satisfies all of the following.

## Trace identity

`capture(task)` returns the vectors actually reinjected at the model's latent-token positions, in recurrent order, with shape `[latent_steps, hidden_size]`.

## Supplied-trace replay

`score_with_trace(task, trace)` runs the same teacher-forced prompt and answer suffix while replacing only the reinjected latent vectors. Exact own-trace replay must reproduce answer logits within the frozen tolerance.

## Source parity

The package includes a separate reference recurrence derived from the pinned upstream source. The adapter engine must match it exactly on a controlled PyTorch fixture.

## Fixed surfaces

Across clean and intervention arms, the following remain fixed:

- checkpoint and base model;
- tokenizer and special tokens;
- prompt text for the recipient task;
- token positions;
- attention mask;
- answer suffix;
- teacher-forced label mask;
- decoding settings.

## Modes

- `latent`: admissible for causal and semantic construction.
- `direct`: admissible as a pre-seal mode control.
- `verbalized`: contains gold proof steps and is post-seal only.

## Fingerprint

The adapter fingerprint commits:

- upstream repository and commit;
- source-verification receipt;
- checkpoint repository, revision, filename, and full SHA-256;
- local base-model path, revision, and tree SHA-256;
- latent-step count;
- device type.

## Failure

Any replay, source-lock, cache representation, latent-position, or trace-shape mismatch returns an adapter failure. It must not be treated as evidence about the model's semantics.
