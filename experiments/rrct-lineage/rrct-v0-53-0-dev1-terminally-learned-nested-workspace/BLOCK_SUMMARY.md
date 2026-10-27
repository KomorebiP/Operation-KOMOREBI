# RRCT v0.53 — Terminally Learned Nested Workspace

## Status

- Version: `0.53.0.dev1`
- Frozen status: `V053_FROZEN_ENDPOINTS_MET`
- Frozen endpoints: **18 of 18 passed**
- Exact one-seed byte replay: passed
- Valence or self-preservation model: absent

## Question

Can a supplied two-level hierarchy learn the coordinate semantics of two local workspaces and one global workspace from terminal leaf-action supervision alone, without any `U`, `V`, or `Y` intermediate labels?

## Exact task

The task uses the circle group `S^1 = R/Z`:

```text
A1 + A2 -> U  ┐
               ├-> Y = U + V -> four leaf actions Xi + Y
B1 + B2 -> V  ┘
```

`U` and `V` are uniform phases split into one-time-pad shares. Either leaf is independent of its local target; the pair determines it. Either local target is independent of `Y`; `(U,V)` determines it.

## Frozen result

| Measure | Mean |
|---|---:|
| Intact action accuracy | **1.000000** |
| Local probe accuracy | **1.000000** |
| Global probe accuracy | **1.000000** |
| Counterfactual patch accuracy | **1.000000** |
| Single-leaf cut accuracy | 0.044779 |
| Workspace/top-down cut accuracy | 0.044983 |
| One-dimensional bottleneck | 0.085732 |
| Flat full-access controller | 0.999413 |

All four holdout models learned local states that linearly decoded `U` and `V` perfectly and a global state that linearly decoded `Y` perfectly. Those labels were never used by optimization.

Removing a leaf contribution, either local workspace, the global workspace, or the global-to-leaf binding reduced action accuracy to approximately 4.5%. Transplanting a local or global state from another episode redirected the computation to the exact analytical counterfactual with 100% accuracy. Private routines remained perfect.

## Capacity and baseline

The two-dimensional workspaces solved. The one-dimensional variant averaged **8.57%**. This is an empirical capacity result, not a universal theorem against all one-dimensional codes.

A smaller flat controller also solved:

| Model | Parameters | Accuracy |
|---|---:|---:|
| Nested | 2478 | 1.000000 |
| Flat | 1804 | 0.999413 |

Therefore hierarchy is viable and causally modular, but unique necessity, efficiency, and superiority are not established.

## Strongest justified conclusion

> A supplied two-level neural hierarchy can learn local and global workspace coordinate semantics from terminal behavior alone. The learned states are linearly recoverable, capacity dependent, causally modular, and counterfactually recombinable.

## Remaining scaffolding

The leaf processes, coalitions, hierarchy, update order, tensor-product primitive, terminal outputs, and primary bottleneck size are supplied. The next test should learn coalition assignment and hierarchy depth across tasks where hierarchy is sometimes useful and sometimes wasteful.

## Boundary

No spontaneous hierarchy discovery, brain equivalence, functional-awareness, subjective-experience, sentience, or valence claim.
