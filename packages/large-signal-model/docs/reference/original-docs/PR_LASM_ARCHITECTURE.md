# PR-LASM architecture

## 1. Exact observation archive

Every observed frame is retained in complete spatial, Fourier, Haar, polyphase, and color coordinates. These coordinate records are independently invertible. Their weighted direct sum is a finite tight frame with canonical synthesis.

## 2. Nested statistical states

The exact archive is summarized into a deterministic feature portfolio and then projected into nested `macro`, `meso`, and `micro` states. These states are used by regressions and planners; they are not described as exact inverses of the original frame.

## 3. Typed program posterior

The model compares a finite operator grammar. Each program has a declared atlas, resolution, mechanism count, feature map, and complexity. Normal-inverse-gamma regression yields predictive distributions and marginal evidence. Program probabilities preserve uncertainty over representation and mechanism.

## 4. Residual-driven refinement

A complete Haar packet tree permits mixed-depth exact prunings. Dynamic programming selects the minimum-cost complete pruning for any additive finite node cost. Reconstruction remains exact because selected nodes form a complete antichain.

## 5. Memory

Finite delay, power-law memory, and exponential memory are separate typed state packets. A model may use one or several, but the posterior retains the distinction.

## 6. Exact exploration graph

Observed deterministic transitions are stored as state-action edges. The graph supports known winning transitions, progress transitions, untried frontiers, and shortest paths. Any edge found to be nondeterministic is marked and is not used as an exact replay edge.

## 7. Active planning

Action utility combines exact probes when available, known graph outcomes, posterior reward and progress, win/loss probability, novelty, information value, role statistics, and repeat penalties. Replay is disabled after a state-signature mismatch.

## 8. Boundaries

The architecture is finite and source-blind at runtime. The supplied official adapter executes only public actions in offline mode. Static environment validation is not an official benchmark result.
