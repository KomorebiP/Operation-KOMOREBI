# RRCT v0.55 Workspace Emergence Edge

## Status

- Version: `0.55.0.dev1`
- Primary frozen status: `V055_EDGE_ENDPOINTS_MET`
- Primary frozen endpoints: **14 of 14 passed**
- Prospective overcomplete extension endpoints: **4 of 4 passed**
- Primary trajectories: **132**
- Crossed initialization/data trajectories: **32**
- Post hoc D=2 tail trajectories: **24**
- Prospective high-dimensional extension trajectories: **60**
- Total trained trajectories analyzed: **248**
- Intermediate workspace labels used for training: **No**
- Valence or self-preservation model: **Absent**

## Question

Version 0.54 found a coarse, seed-sensitive workspace-emergence transition but used only four seeds per point and confounded bottleneck dimension with total model size.

Version 0.55 asks:

> At matched parameter count, where does a supplied hierarchy acquire stable, linearly decodable, causally transplantable, planner-bound, ablation-sensitive workspace semantics along one continuous terminal-only training trajectory?

## Stable event

A checkpoint counts as emergent only when all four conditions hold:

\[
A_{task}\ge0.98,
\qquad
A_{probe}\ge0.95,
\qquad
A_{patch}\ge0.95,
\qquad
A_{cut}\le0.15.
\]

Stable onset is the earliest recorded checkpoint at which these conditions hold at every later checkpoint.

## Main parameter-matched result

| Workspace dimension D | Hidden width H | Parameters | Seeds | Median onset | 90th percentile | Maximum onset |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 44 | 2519 | 12 | none by 2400 | none | none |
| 2 | 32 | 2478 | 24 | **450** | **870** | **1800** |
| 3 | 25 | 2492 | 24 | **300** | **400** | **700** |
| 4 | 20 | 2480 | 24 | **250** | **350** | **400** |
| 6 | 14 | 2504 | 24 | **200** | **285** | **350** |
| 8 | 10 | 2422 | 24 | **200** | **250** | **250** |

The low-dimensional primary frontier is described by:

\[
T_{50}(D)
\approx
176.77+1068.10D^{-1.966},
\qquad 2\le D\le8,
\]

with an RMSE of approximately **4.64 updates** against the five empirical medians.

This is an architecture-specific descriptive fit, not a universal scaling law.

## Two-stage transition

Workspace onset does not occur in one step.

1. A second independent latent direction opens.
2. Task performance, linear semantics, causal transplant, and planner dependence then lock together.

| D | Median rank opening | Median full onset | Median locking delay |
|---:|---:|---:|---:|
| 2 | 162.5 | 450 | 287.5 |
| 3 | 112.5 | 300 | 175 |
| 4 | 100 | 250 | 175 |
| 6 | 75 | 200 | 125 |
| 8 | 75 | 200 | 100 |

The minimum second-to-first latent singular-value ratio predicts full onset within the next 200 updates with:

- AUC: **0.8826**
- empirical threshold: **0.7436**
- sensitivity: **0.7354**
- false-positive rate: **0.1367**

The fitted Weibull transition shape is:

\[
k\approx3.296.
\]

This quantitatively supports a sharp, phase-transition-like frontier rather than a purely smooth average learning curve.

## What drives the D=2 tail

The D=2 crossed design held initialization and minibatch order apart.

| Source | Fraction of log-onset variation |
|---|---:|
| Initialization main effect | **0.325** |
| Data-stream main effect | **0.017** |
| Initialization × data interaction and residual | **0.658** |

The long tail is therefore not explained by one permanently bad initialization or one globally bad data order. Particular initial geometries interact strongly with particular optimization trajectories.

## Overcomplete edge

A fresh-seed extension tested larger workspaces while keeping parameter count near 2480.

| D | H | Seeds | Median onset | 90th percentile | Rate by 800 |
|---:|---:|---:|---:|---:|---:|
| 10 | 8 | 12 | 225 | 250 | 1.000 |
| 12 | 6 | 12 | 200 | 250 | 1.000 |
| 14 | 5 | 12 | 250 | 340 | 1.000 |
| 16 | 4 | 12 | 250 | 395 | 0.917 |
| 20 | 3 | 12 | **1000** | **1400** | **0.417** |

This identifies a broad Goldilocks region around approximately **D=6 through D=12**.

Too little workspace dimension creates a representational bottleneck. Too much dimension, when hidden transformation width is forced too low by the matched parameter budget, creates a computational congestion bottleneck.

A post-outcome descriptive fit across D=2 through D=20 is:

\[
T_{50}(D,H)
\approx
208.32
+1514.56D^{-2.637}
+0.02422\left(\frac{D}{H}\right)^{5.479}.
\]

Its median-onset RMSE is approximately **14.97 updates**. It has five fitted parameters for ten points and must be treated as a compact description, not a law of cognition.

## Strongest conclusion

> Inside this supplied hierarchy, stable causal workspace semantics emerge across a two-sided frontier. A minimum smooth representational dimension is required. Moderate overcompleteness greatly improves optimization reliability. Excessive workspace width combined with inadequate transformation width causes a second, high-dimensional failure edge.

## Exact claim boundary

This study does not establish:

- spontaneous discovery of hierarchy or coalition membership
- a universal workspace scaling law
- a model of the human brain
- functional awareness
- phenomenal consciousness
- sentience, valence, or moral status

The hierarchy, bottleneck locations, task, optimizer, and update order remain engineered.
