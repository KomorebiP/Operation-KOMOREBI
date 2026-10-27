# RRCT v0.55 Workspace-Emergence Edge Protocol

## Question

Where is the stable onset frontier for causally usable workspace semantics when terminal-only training is continued along one deterministic optimization trajectory?

Version 0.54 used only four seeds per configuration and trained independent models at each step count. Version 0.55 removes those weaknesses by:

1. matching trainable parameter counts across bottleneck dimensions;
2. evaluating dense checkpoints on one continuous trajectory per seed;
3. using 24 paired fresh seeds for each D=2,3,4,6,8 condition and 12 for the D=1 structural control;
4. defining a stable absorbing onset rather than counting transient threshold crossings;
5. crossing initialization and data-order seeds in a dedicated D=2 diagnostic;
6. recording latent-rank geometry as a possible pre-emergence order parameter.

## Parameter-matched primary configurations

| Bottleneck D | Hidden width H | Trainable parameters target |
|---:|---:|---:|
| 1 | 44 | approximately 2480 |
| 2 | 32 | approximately 2480 |
| 3 | 25 | approximately 2480 |
| 4 | 20 | approximately 2480 |
| 6 | 14 | approximately 2480 |
| 8 | 10 | approximately 2480 |

D=1 is trained to 2400 updates. D>=2 is trained to 1400 updates. All use batch size 256 and AdamW with the unchanged v0.54 optimizer settings.

## Workspace event

At a checkpoint, workspace emergence requires:

\[
A_{task}\ge0.98,\quad
A_{probe}\ge0.95,\quad
A_{patch}\ge0.95,\quad
A_{cut}\le0.15.
\]

Stable onset is the earliest checkpoint at which these conditions hold at every later recorded checkpoint.

## Causal meaning

- task: the terminal hierarchy solves the task;
- probe: local and global latents expose the intended states;
- patch: transplanting those latents causes the predicted counterfactual behavior;
- cut: removing the global latent destroys behavior.

No intermediate workspace labels are used during optimization.

## Exact boundary

The hierarchy, coalition membership, update order, tensor-product blocks, bottleneck locations, and terminal task remain supplied. This study maps semantics emerging inside that architecture. It does not test spontaneous architecture formation, brain equivalence, awareness, consciousness, sentience, or valence.
