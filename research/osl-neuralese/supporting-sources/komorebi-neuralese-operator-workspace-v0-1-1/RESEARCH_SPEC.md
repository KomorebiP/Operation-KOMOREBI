# Research specification

## Primary question

Under what architectural and training conditions does a recurrent system develop a compact latent state whose transformations behave as reusable operators under arbitrary changes of external coordinates?

## Experimental object

Let \(X\) be an eight-element state set and let \(g_0,g_1:X\to X\) be generators. An episode samples a coordinate permutation \(\phi\) and exposes only

\[
\widetilde g_i=\phi g_i\phi^{-1}.
\]

The two exposed tables are assigned to random visible slots. Consequently, a fixed slot embedding cannot identify the operator. Given a start state \(x_0\) and a word \(w=(i_1,\ldots,i_L)\), the target is

\[
x_L=\widetilde g_{i_L}\cdots \widetilde g_{i_1}x_0.
\]

## Model hypotheses

### H1: recurrent depth extrapolation

A recurrent architecture that learns a reusable one-step transformation should degrade less beyond the trained length range than a fixed-canvas one-shot baseline.

### H2: operator-form inductive bias

A model whose episode-specific operator code is a latent linear map should learn the exact task more readily and extrapolate farther than an unconstrained GRU, even when both receive only terminal loss.

### H3: causal workspace state

Replacing the intermediate hidden state with a donor state from the same episode should produce the independently calculated donor-plus-suffix output. A random displacement from the recipient state, norm matched to the donor-minus-recipient displacement, should not. A secondary absolute random-vector control is also retained.

### H4: causal operator code

Replacing the internal operator code at one recurrent step with the alternate episode operator should produce the exact counterfactual endpoint. A norm-matched random code displacement should not.

### H5: relation and path organization

Words equal in \(D_4\) should increasingly converge to the same decoded state. Hidden-state convergence is measured separately because output equivalence alone does not establish path-independent representation.

### H6: coordinate transport

A transport map fitted between two independently trained workspaces on D4 anchor trajectories of lengths 1 through 4 should carry held-out source hidden states into the target workspace well enough to preserve continuation behavior. The same frozen map is also stress-tested on C8, mixed-cycle, and random-permutation episodes. A matched random map should fail.

## Controls

- Slot identities are randomized every episode.
- State coordinates are independently conjugated every episode.
- The token-only arm cannot inspect operator tables.
- The one-shot arm receives the same complete observable input but has no recurrent update rule.
- Random state and random operator interventions are norm matched.
- Cross-seed transport is evaluated on new episodes not used to fit the map.
- Exact symbolic execution supplies every behavioral and counterfactual target.

## Development gates

The pilot preregisters mechanics gates rather than publication claims:

| Gate | Criterion |
|---|---:|
| Linear terminal D4 ID mean | at least 0.95 |
| Linear terminal D4 long mean | at least 0.70 |
| Linear terminal C8 ID mean | at least 0.80 |
| State transplant | at least 0.90 |
| Operator-code replacement | at least 0.90 |
| Matched random state-displacement control | at most 0.40 |
| Zero-state lesion original accuracy | at most 0.40 |
| State-patch margin over matched control | at least 0.50 |
| Random operator control | at most 0.40 |
| Operator-patch margin over matched control | at least 0.50 |
| Token-only D4 ID mean | at most 0.30 |
| Linear-over-GRU long advantage | at least 0.10 |
| Cross-seed transported continuation | at least 0.70 |
| Random transport continuation | at most 0.40 |

These thresholds are developmental. A later confirmatory revision should freeze seeds, hardware-independent tolerances, statistical tests, and multiplicity handling before any new optimization.

## Interpretation ladder

1. **Behavioral execution:** exact endpoint prediction.
2. **Depth reuse:** generalization beyond trained composition lengths.
3. **Causal state use:** donor-state replacement has the predicted effect.
4. **Causal operator use:** internal operator replacement has the predicted effect.
5. **Algebraic organization:** equivalent words converge behaviorally and geometrically.
6. **Transportable semantics:** aligned hidden states continue correctly in another independently trained model.
7. **Emergence claim:** requires weaker architectural bias, stronger baselines, held-out algebra generators, and replication in substantially different model classes.

Version 0.1.0 is designed to reach levels 1 through 6 in a controlled positive-bias setting. It is not designed to establish level 7.
