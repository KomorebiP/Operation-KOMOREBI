# RRCT v0.56 — Cost-Regularized Workspace Formation

## Status

- **Version:** `0.56.0.dev2`
- **Scientific status:** `V056_CONFIRMATION_ENDPOINTS_MET`
- **Frozen endpoints:** **23 of 23 passed**
- **Primary confirmation seeds:** 16
- **Independent edge seeds:** 6
- **Primary workspace price:** \(\lambda=0.12\)
- **Observed optimal price band:** \(\lambda\in[0.03,0.22]\)
- **Valence or self-preservation model:** absent

## Question

Versions 0.53 through 0.55 showed that semantic and causal workspace structure can emerge inside a supplied hierarchy. Version 0.56 asks the next question:

> Can a learned controller decide **whether a workspace should form, how deep it should be, and which coalition graph should be activated**, rather than always using the largest available architecture?

The candidate library contains:

| Route | Structure | Cost |
|---|---|---:|
| `local` | no shared workspace | 0.0 |
| `flat` | one all-leaf workspace | 1.0 |
| `pair_01_23` | two local coalitions plus global integration | 2.5 |
| `pair_02_13` | alternative two-coalition hierarchy | 2.5 |
| `pair_03_12` | alternative two-coalition hierarchy | 2.5 |
| `full_overlap` | several overlapping coalitions | 4.0 |

The system is trained using only a noisy anonymous projection of a public task-dependency signature. It never receives the task index or an oracle route label.

## Objective

For candidate route \(r\) in episode \(e\):

\[
J_r(e;\lambda)=L_r(e)+\lambda C_r,
\]

where \(L_r\) is the counterfactual terminal loss and \(C_r\) is active workspace cost.

The router learns the target distribution

\[
q(r\mid e)\propto\exp[-J_r(e;\lambda)/0.05].
\]

This tests formation over a supplied route library. It does not test invention of new graphs.

## Primary confirmation result

Across 16 untouched seeds and 320,000 evaluation episodes:

| Measure | Result |
|---|---:|
| Terminal task accuracy | **1.000000** |
| Minimal sufficient route accuracy | **1.000000** |
| Minimum seed task accuracy | **1.000000** |
| Minimum seed route accuracy | **1.000000** |
| Mean selected route cost | **2.082116** |
| Mean oracle-minimal cost | **2.082116** |
| Mean excess cost | **0.000000** |
| Workspace dissolution accuracy | **1.000000** |
| Graph-switch accuracy | **1.000000** |
| Targeted route-patch effect | **0.989070** |

The learned mapping was exact:

```text
local task       → no workspace
flat task        → one flat workspace
pair 01|23 task  → matching 01|23 hierarchy
pair 02|13 task  → matching 02|13 hierarchy
pair 03|12 task  → matching 03|12 hierarchy
overlap task     → overlapping full route
```

When the anonymous task cue was shuffled, route accuracy fell to **0.166941**, essentially the \(1/6\) chance level. Task accuracy remained **0.522769** because an incorrectly overbuilt route can sometimes solve a simpler task. The cue therefore controls architecture choice, but route correctness and task correctness remain distinct.

## Formation-cost Goldilocks edge

The independent edge cohort evaluated 13 prices over 780,000 episodes.

### Underpriced regime

At \(\lambda=0\):

- terminal accuracy remained **1.000000**;
- route accuracy was only **0.460650**;
- mean selected cost was **3.135250** instead of **2.085108**.

With no cost pressure, the router frequently overbuilt a universal or unnecessarily deep workspace.

### Optimal regime

For

\[
\boxed{0.03\le\lambda\le0.22},
\]

task and minimal-route accuracies were at least 99% throughout the independent cohort. At the central prices, selection was effectively exact.

### Overpriced regime

The first clear underformation appeared at \(\lambda=0.24\):

- all local, flat, and single-pair routes remained essentially intact;
- the expensive overlap route was selected only **0.293705** of the time;
- overlap-task accuracy fell to **0.323531**.

The independently computed overlap break-even price was:

\[
\lambda^*_{\mathrm{overlap}}=0.249756.
\]

At \(\lambda=0.40\), the three pair hierarchies also began collapsing, near their estimated break-even values of approximately 0.3985.

## Why the specialized training objective matters

A matched naïve expected-loss router achieved perfect terminal accuracy but overused the universal full route:

| Naïve-control measure | Result |
|---|---:|
| Task accuracy | **1.000000** |
| Minimal-route accuracy | **0.332367** |
| Mean selected cost | **3.341733** |
| Mean oracle cost | **2.087967** |
| Mean excess cost | **1.253767** |

Except for the local task, it generally selected the full route. Ordinary expected-loss optimization therefore found a correct but structurally overbuilt solution.

## What this establishes

Within this bounded architecture:

- a learned controller can close all workspaces when none is needed;
- it can select one flat workspace when shallow integration is sufficient;
- it can choose among three competing coalition graphs;
- it can purchase a deeper overlapping workspace only for the task that requires it;
- it can switch graphs between episodes;
- direct route patching changes terminal behavior;
- an explicit resource price produces a reproducible formation edge;
- underpricing causes overformation;
- moderate pricing yields the cheapest sufficient architecture;
- overpricing suppresses the most expensive necessary workspace first.

This is the first RRCT block in which **workspace existence, depth, and coalition membership are selected**, rather than fixed for every task.

## Exact boundary

The result does **not** establish spontaneous graph invention.

The experiment supplies:

- the six candidate graph types;
- the candidate route computations;
- a public task-dependency signature, hidden behind a fixed anonymous projection;
- all candidate counterfactual terminal losses during training;
- route cost values;
- independent, stateless episodes.

The system learns selection over that library. It does not create new nodes, edges, workspace dimensions, task ontologies, or hierarchy depths outside the supplied candidates.

Nothing here establishes brain equivalence, functional awareness, consciousness, sentience, valence, desire, or moral status.

## Next gap

The next strict target is:

> **Endogenous graph construction under partial counterfactual access.**

A stronger experiment should require a neural supernetwork to:

- compose coalition edges rather than choose a finished graph label;
- infer task dependencies from raw observations;
- operate without evaluating every candidate route counterfactually;
- pay recurrent switching and communication costs;
- support changing numbers of agents and overlapping coalitions;
- invent or expand a graph when no supplied candidate is sufficient;
- dissolve a graph through learned recurrent teardown rather than episode reset.
