# Multimode Coconut Adapter Contract

## Reviewed external interface

The adapter is pinned to:

```text
repository: connordilgren/are-lrms-easily-interpretable
commit: 32f413d8d55239d9bc54bb6b6ec37b0630891ed4
wrapper: models/multimode_coconut/multimode_coconut_model.py
runtime: src_coconut_multimode/coconut.py
checkpoint: connordilgren/gpt2-prontoqa-multimode-coconut / checkpoint_37
```

The package does not redistribute the external repository or model weights.

## Latent state being audited

At latent position `k`, the external Coconut runtime:

1. computes the final-layer hidden state immediately before the latent placeholder;
2. reinjects that state as the placeholder's input embedding;
3. continues the causal computation.

Pilot 0.1 defines the latent trace as the ordered sequence of those **reinjected vectors**. It does not use an arbitrary transformer layer activation or a post-hoc mean pool.

## Required real adapter methods

```python
capture(task) -> TraceObservation
score_with_trace(task, trace) -> TraceObservation
model_fingerprint() -> Mapping[str, Any]
```

`capture` must perform ordinary latent recurrence and return the exact vectors inserted into the latent slots.

`score_with_trace` must preserve the recipient prompt, latent slot positions, answer suffix, attention mask, and position IDs while replacing only the reinjected vectors.

## Replay obligation

For every task:

```text
capture(task).answer_logits
```

must agree with:

```text
score_with_trace(task, capture(task).trace).answer_logits
```

within the frozen tolerance. The package also compares protected answer loss.

## Teacher-forced sequence

For GPT-2 multimode Coconut, the audited sequence is:

```text
question + newline
<|bocot|>
<|latent|> repeated K times
<|eocot|>
### answer
EOS
```

Labels are `-100` through the latent prefix and equal the answer-token IDs afterward. This matches the external repository's answer formatting.

## Batch and precision boundary

The external generation implementation supports batch size one. Pilot 0.1 preserves that boundary.

The initial replay should run in float32. Float16 or bfloat16 may be added only after a separate numerical-equivalence test and a new tolerance receipt.

## Cache boundary

The custom trace engine mirrors the external runtime's legacy key/value-cache slicing. It accepts a newer cache object only when it can be converted to the legacy representation. An unsupported cache representation fails closed.

## Validation performed without the checkpoint

The package contains a toy causal language model that exercises:

- multiple latent positions;
- natural trace capture;
- supplied trace replay;
- exact logit equality on replay;
- logit change under a modified trace.

This validates the intervention engine's control flow, not compatibility with every future Transformers release or the real checkpoint.

## Real compatibility gate

The first real run must report:

- external commit equality;
- complete checkpoint SHA-256;
- successful model load;
- no nonfinite losses;
- exact trace shape `K x hidden_size`;
- replay gate pass on every audited task.

Any failure returns `ADAPTER_INVALID` or an execution error. It cannot be interpreted as evidence about the model's latent reasoning.
