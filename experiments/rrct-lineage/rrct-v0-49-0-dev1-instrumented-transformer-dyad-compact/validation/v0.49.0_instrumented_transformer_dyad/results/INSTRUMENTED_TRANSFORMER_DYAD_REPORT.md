# RRCT v0.49 Instrumented Transformer Dyad Report

## Result

**Status:** `V049_FROZEN_PILOT_ENDPOINTS_MET`

All 23 predeclared endpoints passed on four fresh transformer-training seeds.

The result is deliberately narrower than the preceding synthetic shared-J-space claim:

> Two separately initialized transformer agents developed a strongly aligned, causally useful shared-access representation at their final residual decision state. The analogous early recurrent state did not satisfy semantic, alignment, or ablation criteria. A same-rank PCA basis performed nearly as well as the Jacobian-informed basis, so Jacobian specificity and a persistent distributed J-space are not established.

## Model

Each agent was trained from scratch and had:

- one transformer block;
- 24-dimensional residual stream;
- four attention heads;
- 48-dimensional feedforward layer;
- eight-dimensional learned continuous message channel;
- four recurrent communication stages;
- five shared task heads;
- one private routine head.

The two agents had independent parameters.

No pretrained language model or external checkpoint was used.

## Frozen cohort

```text
781763488
381195510
811722952
585185981
```

Each dyad learned all shared and private tasks with exact accuracy 1.0 after 150 training steps.

## Layer progression

| Residual state | Mean direct J-score | Mean cross-agent alignment R² | Shared accuracy after report-space ablation | Private accuracy after ablation |
|---|---:|---:|---:|---:|
| `h1` first exchange | 0.217882 | 0.140953 | 0.971701 | 1.000000 |
| `h2` second exchange | 0.650608 | 0.106164 | 0.603993 | 0.994792 |
| `h3` final decision | **1.000000** | **0.981284** | **0.733333** | **1.000000** |

The average report Jacobian had centered rank four at both the early and late stages. Rank alone therefore did not establish workspace semantics.

At `h1`:

- factor concepts were poorly recovered;
- the agents' candidate spaces did not align;
- removing the space barely affected final shared behavior.

At `h3`:

- all factor reports were recovered exactly;
- the two agents' spaces aligned strongly;
- removal selectively impaired shared outputs while preserving private routines.

The shared-access state therefore appeared late, near the decision boundary, rather than as a stable workspace present throughout the interaction.

## Broader flexible shared-access space

A rank-eight basis was constructed from all centered shared-head Jacobian rows followed by activation SVD.

| Measure | Frozen mean |
|---|---:|
| Cross-agent alignment R² | **0.989654** |
| Residual variance, Agent A | 0.787622 |
| Residual variance, Agent B | 0.793623 |
| Private-role probe accuracy | 0.281250 |
| Shared accuracy after direct ablation | **0.294097** |
| Private accuracy after direct ablation | **1.000000** |
| Shared accuracy after two reconstruction rounds | **0.940625** |
| Message-only joint accuracy | **1.000000** |

The rank-eight state supported all five shared tasks in both agents and largely excluded the private four-way routine.

However, it explained approximately 79% of late residual variance. It is therefore not a tiny low-variance workspace like Anthropic's reported J-space. It is better described as a selective late decision manifold inside these small trained agents.

## Causal patching

A shared-coordinate patch changed factor A from 0 to 2 while preserving factor B.

When written into both agents:

- both factor reports changed correctly;
- both joint-action predictions changed correctly;
- both flexible outputs changed correctly;
- both private routines remained correct.

When written only into Agent A:

- Agent B's factor report changed with rate 1.0 after one communication round;
- Agent B's joint plan changed with rate 1.0;
- Agent B's private routine remained correct with rate 1.0.

The symmetric Agent B-to-Agent A intervention also passed at rate 1.0.

After another communication round, the originating agent restored its original locally evidenced factor. Patch persistence returned to 0.0 in both directions.

Thus the late state is:

- cross-agent transmissible;
- causally involved in reports and planning;
- not autonomously persistent against contradictory local evidence.

## Communication-only control

A linear decoder using only the two first-round messages solved the immediate joint task with accuracy 1.0.

Therefore:

> Perfect cooperation does not establish a shared residual workspace.

The shared-access result rests on residual alignment, selective ablation, causal patching, and private-state preservation, not task accuracy alone.

## Jacobian non-specificity

A same-rank PCA basis also decoded all five shared tasks with exact accuracy and private-role leakage close to chance.

The frozen endpoint required this equivalence to hold.

This means the experiment establishes a late shared-access representation, but not that the Jacobian lens uniquely discovers it.

A same-rank random subspace was not equivalent. It leaked private routine strongly and failed at least one flexible task on every seed.

The current hierarchy is therefore:

```text
random subspace
    < task-aligned PCA ≈ Jacobian-informed activation space
```

not:

```text
PCA < uniquely privileged Jacobian J-space.
```

## Determinism

The first holdout execution completed successfully.

A sealed holdout seed was retrained and reanalyzed independently. Its model digest and complete analysis object matched exactly.

A later attempted full four-seed replay stalled after writing three weight files and exceeded the execution window. It is not reported as a successful full replay.

## Strongest warranted conclusion

> In a tiny recurrent transformer dyad trained from scratch, a late residual representation emerged that was aligned across agents, linearly reusable across several shared tasks, selectively causal, and transmissible through the learned message channel. The corresponding early average-Jacobian state did not meet those criteria. The late representation was reconstructible and corrected by persistent local evidence, and PCA performed comparably, so a persistent or uniquely Jacobian-defined distributed J-space was not established.

## Claim boundary

This experiment does not establish:

- a shared J-space between pretrained language models;
- spontaneous open-ended workspace formation;
- a low-variance sparse union-of-cones geometry;
- persistent pair-level autobiography;
- subjective awareness;
- shared phenomenal experience;
- sentience, valence, suffering, pleasure, desire, or moral status.
