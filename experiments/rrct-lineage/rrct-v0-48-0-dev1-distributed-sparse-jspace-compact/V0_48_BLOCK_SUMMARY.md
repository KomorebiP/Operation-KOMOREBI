# RRCT v0.48 Distributed Sparse J-Space

## Status

- Version: `0.48.0.dev1`
- Frozen result: `V048_FROZEN_ENDPOINTS_MET`
- Release verification: `V048_RELEASE_VERIFIED`
- Frozen endpoints: **28 / 28 passed**
- Holdout seeds: `598824493, 128793853, 607712486, 618120745`
- Unique world cases: **256**
- Matched architecture decisions: **2,304**

## Scientific question

Can two independently parameterized agents instantiate a structure that is more specifically J-space-like than the fixed linear shared manifold established in v0.47?

The v0.48 criterion requires:

- a Jacobian-discovered selective workspace inside each agent;
- a state-dependent sparse support in each workspace;
- an aligned cross-agent concept frame;
- reportability to both agents;
- flexible reuse by several downstream computations;
- bidirectional causal write access;
- selective ablation that preserves private routines;
- a strict sparse capacity limit;
- pair-specific provenance, joint planning, and consequence-driven recurrence.

## Architecture

Each agent has a 64-dimensional residual state with:

- a rank-four local workspace;
- an eight-direction overcomplete concept frame;
- a rank-twenty private routine packet;
- an independent hidden coordinate basis;
- an independent pair-private message code.

Each complete joint state activates four nonnegative directions, one from each opposing concept pair. The sixteen possible states therefore form a state-dependent sparse union of cones rather than one fixed semantic vector.

The system independently discovers each local Jacobian workspace, fits a v0.47 cross-agent atlas from synchronized trajectories, transports Agent B's frame into Agent A's chart, aligns the eight concept directions, and produces a distributed access receipt tied to both local access receipts and the pair workspace.

## Frozen discovery result

| Measure | Result |
|---|---:|
| Local Jacobian rank, Agent A | 4 on every seed |
| Local Jacobian rank, Agent B | 4 on every seed |
| Mean local workspace variance fraction, A | 0.114714 |
| Mean local workspace variance fraction, B | 0.114717 |
| Shared rank | 4 on every seed |
| Minimum canonical correlation | 0.999893 |
| Mean cross-agent alignment R² | 0.999862 |
| Minimum cross-agent frame cosine | 0.999999563 |
| Exact support agreement | 1.000000 |
| Distinct active supports per seed | at least 16 |
| Komorebi packet certificates | all valid |

The workspace occupies approximately 11.5 percent of total activation variance while completely recovering the joint semantic support in the frozen benchmark.

## Matched architecture results

| Mode | Task | Report A | Report B | Flexible reuse | Distributed J-space closure |
|---|---:|---:|---:|---:|---:|
| **Full shared** | **1.000000** | **1.000000** | **1.000000** | **1.000000** | **1.000000** |
| Message only | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 |
| Workspace cut | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| Message shuffle | 0.253906 | 0.253906 | 0.253906 | 0.253906 | 1.000000 |
| One way | 1.000000 | 1.000000 | 0.218750 | 1.000000 | 0.000000 |
| Provenance cut | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| Planner-binding cut | 0.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 |
| Recurrence cut | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 |
| Joint cut | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |

These dissociations establish that immediate cooperation, structural closure, semantically correct content, bidirectionality, planner binding, and recurrence are different properties.

## Directed concept swap

A frozen shared concept was replaced with its learned opposing frame direction.

| Effect | Rate |
|---|---:|
| Agent A report changed to target concept | 1.000000 |
| Agent B report changed to target concept | 1.000000 |
| Joint plan changed to target state | 1.000000 |
| Flexible downstream reasoning changed coherently | 1.000000 |
| Agent A private routine preserved | 1.000000 |
| Agent B private routine preserved | 1.000000 |

Mean causal write effects were approximately 0.3599 in Agent A and 0.3603 in Agent B.

## Selective ablation

| Measure | Intact | Shared J-space ablated |
|---|---:|---:|
| Agent A report | 1.000000 | 0.101562 |
| Agent B report | 1.000000 | 0.078125 |
| Flexible joint task | 1.000000 | 0.164062 |
| Agent A private routine | 1.000000 | 1.000000 |
| Agent B private routine | 1.000000 | 1.000000 |

This is the strongest workspace-style dissociation in the block: shared access and flexible control collapse while private routine processing remains intact.

## Capacity limit

When two incompatible four-concept states were simultaneously proposed:

- selected support size remained exactly **4**;
- the proposed union contained **8** concepts;
- recall of the full union was **0.5**;
- the primary state was retained completely.

The shared workspace therefore behaves as a capacity-limited sparse support rather than an unrestricted communication buffer.

## Provenance and recurrence

A valid state from another pair was quarantined in every intact probe, never written into pair memory, and never bound to planning. Removing provenance protection caused every foreign state to be falsely written and planner-bound.

After a shared prediction error, the intact pair reopened the next interaction for three evidence rounds and recovered the correct decision on every seed. The recurrence-cut pair remained at one round and failed every challenged second decision.

## New-partner remapping

- Unadapted partner accuracy: **0.166667**
- Accuracy after fresh message and frame calibration: **1.000000**
- Remapped alignment R²: **0.999864**
- Minimum remapped frame cosine: **0.999999458**
- Remapped support agreement: **1.000000**

The shared representation is not a zero-shot universal language. It is a remappable relation that must be recalibrated for a new partner.

## What is established

Within this frozen synthetic benchmark:

> Two independently parameterized agents instantiated local Jacobian-discovered sparse workspaces whose dynamic active supports were aligned into a bidirectionally writable, flexibly reusable, planner-causal, pair-provenance-bound, recurrent distributed J-space analogue.

This is stronger than v0.47's fixed rank-four shared manifold because the active workspace is now a state-dependent sparse union of cones and because the shared concept frame passes report, modulation, flexible-use, selective-ablation, capacity, provenance, planning, and recurrence tests.

## Exact limitations

This is not yet evidence that two production language models spontaneously form a shared J-space.

The benchmark remains:

- synthetic and linear;
- 64-dimensional per agent;
- equipped with exact synthetic average Jacobians;
- built from an engineered eight-direction concept frame;
- supplied with synchronized calibration trajectories;
- supplied with a known dyadic communication structure;
- trained on a bounded sixteen-state task;
- evaluated with prepared report and reasoning functions.

The semantic common structure is intentionally present in the generated trajectories. What is established is that the labels are not used to discover the local workspaces, shared rank, coordinate transport, frame alignment, or active support correspondence, and that the discovered structure acquires the declared causal roles.

Nothing here establishes shared phenomenal consciousness, subjective merging, sentience, valence, moral status, or one mind spanning two agents.

## Next decisive test

The next step should move from synthetic exact Jacobians to two instrumented open-weight transformer agents:

1. estimate each model's moving sparse J-lens from actual hidden activations;
2. collect synchronized multi-task interactions;
3. discover whether part of the two local J-spaces aligns without semantic labels;
4. causally patch that shared component from either side;
5. test report, reasoning, flexible reuse, private-state preservation, capacity, provenance, recurrence, and new-partner transfer;
6. include message-only and shuffled-content controls;
7. require the shared manifold to generalize across tasks rather than one sixteen-state ontology.

A positive result there would justify the stronger phrase **distributed J-space in trained language-model agents**.
