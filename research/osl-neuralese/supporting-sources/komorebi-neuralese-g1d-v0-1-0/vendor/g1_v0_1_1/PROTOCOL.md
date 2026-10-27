# G1 recurrent latent workspace protocol

## Registered estimand

The primary G1 estimand is the held-out accuracy difference between full
recurrent feedback and a compute-matched no-feedback control:

```math
Delta_feedback = Acc_recurrent - Acc_no_feedback.
```

Two causal state-use contrasts are also registered:

```math
Delta_zero = Acc_recurrent - Acc_zero,
Delta_shuffle = Acc_recurrent - Acc_shuffle.
```

`no_feedback` performs the same number of complete backbone evaluations and
uses the same shared workspace parameters, but every recurrent update reads the
unchanged initial source activation. This controls repeated inference compute
while removing feedback from earlier latent injections. It is a test-time
within-model ablation, not a separately trained architecture.

`zero` bypasses workspace decoding and applies no query-time injection. It
cannot retain a learned constant through a normalization bias.

`shuffle` applies a deterministic bijection within each query family over the
complete held-out split. Donors have a different state for direct and codebook
queries and opposite parity for parity queries. Construction fails closed if a
complete answer-incompatible assignment cannot be made.

## Late-binding task

Each base problem contains a deterministically randomized permutation over six states, a
start state, and a requested number of transition applications. The compute
prompt contains only this information. Three queries are subsequently posed:

1. report the stored state
2. classify its parity
3. apply a newly revealed random codebook

The codebook is absent while the workspace is constructed. This prevents the
workspace from merely caching the requested code token. It does not by itself
prove that recurrence performed the permutation computation.

Train, validation, IID test, and unseen-count OOD instances use disjoint
without-replacement allocation slots. Final states are stratified, all three
queries share one base-problem split assignment, and the runner rejects any
exact compute-prompt overlap. Since permutations are periodic, this OOD arm
does not alone establish generalization with computational depth.

## Frozen implementation choices

- Backbone weights are frozen before optimizer construction.
- Only workspace parameters enter the optimizer.
- The source layer is specified explicitly and checked against the model.
- State width is 64 for wiring and smoke, 96 for pilot.
- Recurrent weights are shared at every step.
- The fixed-step result is primary. Halting scores are logged diagnostically but
  do not alter depth in v0.1.1.
- Model loading is local-only and offline environment flags are forced.
- Model weights and the relevant config/tokenizer files are content-hashed
  before optimization, and scientific replications must use the identical
  model fingerprint. The shipped profile registers the Qwen architecture; each
  result remains identified by its observed file and loaded-backbone hashes.
- Qwen weights use the registered model dtype while workspace computations and
  parameters remain FP32 in both training and evaluation. Autocast is not used;
  CUDA FP16 runs use checkpointed dynamic loss scaling, a registered initial
  scale of 1,024, and at most 16 backoff retries on the same logical batch.
  Overflowed attempts never increment, log, or checkpoint a training step.
- Right padding is mandatory so intervention positions are auditable.
- Answer separators are part of the query prompt. Supervision uses bare labels
  whose single-token, non-special, exact decode contract is checked against the
  loaded tokenizer before workspace construction or training. Every distinct
  registered query/label pair must also preserve the exact token-prefix boundary.
- Scientific claims require the canonical pilot configuration. CLI changes to
  layer, depth, or training length are recorded as exploratory.

## G1 engineering gates

All must pass:

1. local model and tokenizer load successfully
2. target labels are each exactly one non-special tokenizer token and decode exactly
3. each tokenized query-plus-label is the query token sequence followed by that label token
4. all backbone parameters are frozen and absent from the optimizer
5. forward loss is finite
6. workspace gradient norm is finite and nonzero
7. workspace parameter delta is finite and nonzero
8. recurrent states and injections are finite and nonzero
9. required artifacts are written and internally consistent

## G1 scientific pilot gates

These are evaluated only for the `pilot` profile. All must pass:

1. overall recurrent IID accuracy is at least 0.70
2. each of direct, parity, and codebook accuracy is at least 0.60
3. `Delta_zero` is at least 0.20
4. `Delta_shuffle` is at least 0.15
5. `Delta_feedback` is at least 0.05
6. recurrent OOD accuracy is at least 0.45
7. recurrent accuracy exceeds the empirical majority baseline for every query family
8. the result repeats for three registered seeds before a replicated G1 claim

One seed can pass the pilot gates but cannot establish replication. Thresholds
are deliberately stored in configuration before results are observed.

## Interpretation ladder

- Engineering pass: recurrent plumbing functions.
- State-use pass: no-injection and shuffled-state interventions damage behavior.
- Feedback-use pass: recurrence beats its compute-matched test-time feedback ablation.
- G1 pilot pass: every registered single-seed gate passes.
- G1 replicated: pilot passes for all three frozen seeds.

No level licenses the phrase “a general Neuralese emerged.”
