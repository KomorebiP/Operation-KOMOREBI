# RRCT v0.54 Workspace-Emergence Scaling Protocol

## Question
Within the supplied two-level hierarchy of v0.53, how do bottleneck dimension, hidden width, and terminal-training steps control the spontaneous appearance of causally usable local and global workspace representations?

“Spontaneous” here means that U, V, and Y coordinate semantics are not supervised. Coalition membership, hierarchy depth, update order, tensor-product primitives, and the existence of bottlenecks remain supplied.

## Development sweep
Development seeds: `54011, 54029, 54047`.

- bottleneck dimensions: 2 and 4 across the main grid;
- one-dimensional high-compute structural controls;
- hidden widths: 8, 16, 32, 64;
- training steps: 100, 200, 400, 800, 1400, 2400 where sampled;
- terminal leaf-action loss only.

Screen emergence requires terminal action accuracy >= .98 and global-cut accuracy <= .15.

Full emergence additionally requires:

- minimum linear probe accuracy for local A, local B, and global workspace >= .95;
- minimum local-A, local-B, and global causal transplant accuracy >= .95.

## Fitted scaling surface
The pre-holdout empirical model is:

`P(E=1) = sigmoid(b0 + bS log2(steps) + bH log2(hidden) + bHH log2(hidden)^2 + bD log2(dim))`.

The model is descriptive for this architecture and task family, not a universal cognitive scaling law.

## Frozen holdout configurations
Each point is evaluated on four untouched seeds using the full emergence criteria.

1. `dim=1, hidden=64, steps=2400` — structural-capacity negative control.
2. `dim=2, hidden=32, steps=200` — below frontier.
3. `dim=2, hidden=32, steps=400` — near frontier.
4. `dim=2, hidden=32, steps=800` — above frontier.
5. `dim=4, hidden=16, steps=200` — below frontier.
6. `dim=4, hidden=16, steps=400` — near/above frontier.
7. `dim=4, hidden=16, steps=800` — above frontier.

## Frozen endpoints
1. Every runtime reports terminal-only workspace training.
2. No valence or self-preservation objective is present.
3. The one-dimensional control has zero full-emergence seeds and mean action accuracy <= .15.
4. The d2/h32/200 point has full-emergence rate <= .50.
5. The d2/h32/400 point has full-emergence rate >= .75.
6. The d2/h32/800 point has full-emergence rate = 1.00.
7. The d4/h16/200 point has full-emergence rate <= .50.
8. The d4/h16/400 point has full-emergence rate >= .75.
9. The d4/h16/800 point has full-emergence rate = 1.00.
10. For every fully emergent point, global-cut accuracy is <= .15.
11. Mean emergence rate is monotone across the three step levels for d2/h32.
12. Mean emergence rate is monotone across the three step levels for d4/h16.
13. Above-frontier mean probe accuracy is >= .98.
14. Above-frontier mean transplant accuracy is >= .98.
15. Above-frontier mean action accuracy is >= .99.
16. Holdout observations preserve the fitted ordering: d4/h16 requires no more steps than d2/h32 to reach the same emergence rate.

## Boundary
This tests representation emergence and a scaling frontier inside a supplied hierarchy. It does not test spontaneous hierarchy discovery, coalition discovery, brain equivalence, functional awareness, subjective experience, valence, or consciousness.
