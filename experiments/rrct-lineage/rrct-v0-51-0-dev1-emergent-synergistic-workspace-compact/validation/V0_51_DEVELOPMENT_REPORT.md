# RRCT v0.51 Development Report

## Development seeds

```text
51001
51007
```

No frozen holdout seed was evaluated during development.

## Main development result

For both development seeds, the round-curriculum architecture achieved:

- 100% training accuracy
- 100% held-out accuracy on unseen six-operation compositions
- approximately chance performance after reset, one-writer, shuffle, and planner-binding interventions
- 100% causal transplant accuracy for both agents
- 100% transplant-induced plan changes

Final message linear-probe accuracy was:

- seed 51001: 0.986798
- seed 51007: 0.999847

All eight message dimensions contributed to 99.9% activation variance. The learned representation is therefore compact relative to the 16-slot explicit carrier, but is not a discovered minimal four-dimensional coordinate code.

## Strict terminal-only control

Under the same architecture and 1,000-step optimization budget:

- seed 51001: approximately 24.7% held-out accuracy
- seed 51007: approximately 12.2% held-out accuracy

This control is substantially above or near chance depending on seed, but far below the curriculum solution. It prevents the stronger statement that the recurrent workspace reliably emerged from terminal supervision alone.

## Failed initial route

An initial GRU-based terminal-only prototype remained near chance. A gated MLP message update also failed to learn the complete algorithm reliably from terminal loss alone under the development budget.

The primary architecture was therefore frozen with round-level task curriculum. No message coordinate, one-hot workspace carrier, or latent geometric target is supplied.

## Development conclusion

The supported claim is:

> A compact recurrent shared message representation can be learned without prescribed latent coordinates when the task curriculum exposes increasingly long joint compositions.

The unsupported stronger claim is:

> The complete shared workspace spontaneously emerges from a single terminal objective without additional curriculum.
