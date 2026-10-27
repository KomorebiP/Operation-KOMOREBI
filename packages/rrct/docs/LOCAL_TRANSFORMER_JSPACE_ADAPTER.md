# Optional local transformer J-space adapter

## Scope

`rrct_lab.adapters.hf_local` is an optional measurement path for an already available local causal language model. It can:

- locate common decoder stacks (`model.layers`, `transformer.h`, or `gpt_neox.layers`)
- capture a token-indexed residual
- compute target-logit vector-Jacobian products at that residual
- construct norm-matched residual patch hooks
- construct validated projector-ablation hooks
- emit finite JSON records without storing prompt text

It does not train a model, download weights, execute remote model code, or provide evidence by itself.

## Required local dependencies

The base laboratory imports without PyTorch or Transformers. A live probe additionally requires compatible locally installed versions of:

```text
torch
transformers
```

and an existing local model directory or supported local model file.

## Safety contract

The loader:

- rejects missing paths and remote URI-like paths
- passes `local_files_only=True` to tokenizer and model loading
- passes `trust_remote_code=False` to tokenizer and model loading
- puts the model in evaluation mode
- creates no optimizer and performs no training
- exposes no network call

The CLI also refuses to overwrite the prompt file or write inside the local model directory.

## Prompt input

JSONL records may supply a prompt and target token IDs:

```json
{"id":"trial-001","prompt":"The capital of France is","target_token_ids":[123,456]}
```

Target IDs can instead be supplied with repeated `-TargetTokenId` arguments. Token IDs are tokenizer-specific and should be checked locally.

## Windows example

```powershell
.\RUN_LOCAL_JSPACE_PROBE.ps1 `
  -Model C:\models\small-local-causal-lm `
  -Prompts .\my_prompts.jsonl `
  -Output .\runs\local_jspace_probe.json `
  -Layer -1 `
  -ResidualToken -1 `
  -PredictionToken -1 `
  -TargetTokenId 123
```

## Bash example

```bash
./RUN_LOCAL_JSPACE_PROBE.sh \
  --model /models/small-local-causal-lm \
  --prompts ./my_prompts.jsonl \
  --output ./runs/local_jspace_probe.json \
  --target-token-id 123
```

## What remains to establish

The emitted VJPs and residuals are inputs to a J-space analysis, not a completed J-space result. A transformer study would still need held-out projector discovery, same-rank PCA and random controls, selective causal patching, routine-task preservation, multi-task reuse, and replicated seeds/prompts.

The adapter's helper and loading guards were tested without optional dependencies. A live model forward pass and autograd probe must be validated on the user's local model/runtime before interpreting results.
