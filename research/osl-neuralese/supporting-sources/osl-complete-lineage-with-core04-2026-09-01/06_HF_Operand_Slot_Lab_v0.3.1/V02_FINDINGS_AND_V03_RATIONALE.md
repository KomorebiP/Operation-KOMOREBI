# Why v0.3 follows from the v0.2 full run

The verified v0.2 run trained 16 models across four arms and four seeds. Its result was scientifically useful because the strong controls changed the interpretation.

## v0.2 boundary

Answer-only mean balanced provenance accuracy was:

```text
ID          64.00%
length OOD  46.23%
motif OOD   19.09%
syntax OOD  47.79%
joint OOD   20.34%
```

State supervision improved joint OOD to 33.36%. Equivalence supervision reached 34.14% and produced the strongest nuisance-orbit stability. The old operator-regularized arm fell to 32.77% joint OOD.

Answer-only unseen-codebook performance reached 65.89%. This supports contextual remapping under an explicit legend, not discovery of a new primitive operator.

## Why the old transition failed

The v0.2 transition received only:

```text
global CLS state
operator identity
```

It did not receive actor, recipient, fact, or source fact. One global affine map therefore could not implement source-dependent transitions such as:

```text
TELL(Ada, Ben, X)
INFER(Ben, Y, X)
```

It also had no independently addressable cell in which to write the result.

## Why the old causal test was not evaluable

Eligibility required four exact six-head bundles, a conjunction of 24 predictions. The counterfactual was also simultaneously held-syntax and length OOD. Every model produced zero eligible examples.

The correct conclusion was not zero causal success. It was that the endpoint prerequisite was never met.

## What v0.3 tests

v0.3 asks whether the missing functionality appears when the model has:

- cross-attended agent-fact slots
- explicit typed operands
- source-slot access
- a learned write locator
- exact one-step executable targets
- an ID causal bank that can establish evaluability
- separate OOD transfer banks

This locates the next boundary precisely:

```text
sentence pressure alone
versus
state organization
versus
path equivalence
versus
operand-conditioned free writes
```

If the final arm succeeds while answer-only fails, the result will identify which scaffold is necessary. If both fail, the next step is capacity or training-curriculum scaling rather than another global transition loss.

