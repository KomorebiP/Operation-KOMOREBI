# Model architecture

## Resolved observation

For a frame `o_t`, the packetizer computes a deterministic nested representation

```text
raw interpretable packets -> fixed fine projection -> fixed coarse projection
```

The raw packets contain color, object, spatial, spectral, polyphase, and change information. The compact projections are fixed; they are not trained on benchmark games.

## Candidate operator programs

For each resolution, the model evaluates a finite library of typed feature maps. The generic target is

```text
next-state delta + reward + level progress + win + loss + visible change
```

Candidate families include linear, quadratic, delayed, fractional-memory, Volterra-memory, phase-conditioned, and hybrid programs.

## Bayesian comparison

Each candidate is a conjugate Bayesian multivariate regression with a normal-inverse-gamma prior. The posterior weight combines held-out predictive probability with explicit penalties for feature count, additional mechanisms, and fine resolution.

## Action selection

The planner combines:

- exact reward from local replay probes when available;
- predicted reward and level progress;
- win and loss probability;
- state novelty;
- posterior disagreement and information value;
- action-loop penalties;
- accumulated role statistics.

Replay is used only when the local environment reconstructs deterministically from the same seed and action history. A packet-signature mismatch disables replay for the rest of the run.

## Deliberate limitations

- The operator library is finite; it does not invent arbitrary programs.
- The model does not inspect game source.
- There is no claim of an official ARC-AGI-3 score in this release.
- The bundled smoke task is a package check, not an ARC benchmark result.
- The exact Bayesian core runs on CPU; optional PyTorch is not required.
