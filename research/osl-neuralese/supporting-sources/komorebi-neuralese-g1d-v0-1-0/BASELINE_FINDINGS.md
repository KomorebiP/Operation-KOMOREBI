# Seed-711001 findings fixed before D1 execution

## Frozen identity

- Registered seed: `711001`
- Completed optimization steps: `2,000`
- Config digest:
  `872349b749392924dab4b70eefe516751667d8d74ed91f73bb325b8277ce2a41`
- Checkpoint SHA256:
  `ea0f9506334f6958c43e73596eb7404f785abd92be7668024b0c01efac1eae75`
- Registered source claim: `G1_ENGINEERING_PASS`; the scientific gates failed

## Observed behavior

- Recurrent IID accuracy is 401/1,440; the registered family-aware chance
  expectation is 400/1,440.
- Direct predicts `3` on 480/480 IID queries. Parity predicts `E` on 480/480.
- Recurrent and shuffled predictions agree on 1,426/1,440 IID queries.
- Recurrent and no-feedback predictions agree on 1,430/1,440 IID queries.
- The saved literal-zero condition predicts `1` on every query; D1 includes an
  exact zero-condition replay rather than treating zero as a mean state.
- The final twenty logged losses average 1.4557. Query-family marginal entropy
  is approximately 1.425 nats.

## Checkpoint fact motivating D1

The trained 896-by-96 output projection has stable rank approximately 1.0135,
with 98.671% of squared energy in its leading singular direction. Together with
the prediction invariances above, this is a generic-steering signature at the
registered answer labels and is consistent with a severely collapsed output
bridge. It does not establish why the bridge collapsed or whether the upstream
workspace retains final-state signal.

D1 therefore measures source states, recurrent/no-feedback trajectories, and
decoded injections separately; compares IID signal with structured prompt
metadata and literal-heuristic controls; reports OOD transfer separately; and
tests leading-rank-one versus residual projection behavior. Its incompatible-
donor conclusion is based on the paired semantic logit difference-in-
differences, not a raw donor accuracy gap.

These are fixed pre-diagnostic facts and motivate an unresolved localization
question only. They do not show that final-state information is absent, prove a
causal failure mechanism, or support a Neuralese claim.
