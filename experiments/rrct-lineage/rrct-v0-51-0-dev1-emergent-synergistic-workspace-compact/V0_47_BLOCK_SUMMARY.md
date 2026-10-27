# RRCT v0.47 Distributed Shared Workspace

## Status

- Version: `0.47.0.dev1`
- Frozen status: `V047_FROZEN_ENDPOINTS_MET`
- Release replay: `V047_RELEASE_VERIFIED`
- Frozen endpoints: **28 of 28 passed**
- Unique dyadic task cases: **384**
- Matched architecture decisions: **3,456**

## Scientific question

Can two independently parameterized, individually complete self-indexed agents form a hidden interaction state that is functionally stronger than a successful communication code?

The experiment distinguishes three possibilities:

1. **Shared code**: messages allow cooperation.
2. **Aligned latent representation**: corresponding concepts can be transported between the agents' private coordinate systems.
3. **Causally distributed workspace**: a mapped shared state is bidirectionally writable, jointly sufficient, provenance-bound, planner-causal, stored in joint memory, and revised by later consequences.

Only the third receives the term `distributed shared workspace` in this release.

## Architecture

Each synthetic agent has:

- a 64-dimensional private residual state;
- an independently parameterized neutral self-indexed workspace inherited from v0.46;
- a private four-way routine variable;
- one directly observed half of a two-factor shared semantic state;
- an independently rotated message basis;
- a local Komorebi shared/nonshared packet decomposition.

The shared semantic state contains two three-way factors. Each agent observes only one factor before communication. The centered joint code therefore has rank four. Neither private pre-interaction state is sufficient to solve the nine-way joint task.

The shared atlas is learned from synchronized local workspace trajectories without the hidden factor labels. It uses paired covariance, canonical correlation, local packet construction, orthogonal transport, and Komorebi analysis-synthesis certificates.

## Frozen cohort

Fresh holdout seeds were selected through SHA-256 expansion of a fixed namespace before any candidate outcome was evaluated:

```text
161625576
156878792
822521852
294523660
```

The exact implementation, focused tests, protocol, thresholds, seed receipt, holdout runner, verifier, package metadata, and all RRCT runtime modules were sealed in a 90-file pre-outcome manifest.

Pre-outcome seal SHA-256:

```text
68ce68565078cea313462084a10b0f49b2d4064a1e76fd3629dc205a59790ade
```

## Primary result

The discovered manifold had:

| Measure | Frozen result |
|---|---:|
| Shared rank correct on every seed | 4 |
| Minimum canonical correlation | 0.999716 |
| Mean cross-agent alignment R² | 0.999523 |
| Mean Agent A projector overlap | 0.999997 |
| Mean Agent B projector overlap | 0.999997 |
| Private-role leakage accuracy from shared coordinates, A | 0.249653 |
| Private-role leakage accuracy from shared coordinates, B | 0.250000 |
| Komorebi packet and atlas certificates | All valid |

Private-role leakage remained at chance for the four-way private variables. The mapped shared coordinates therefore recovered the common task state without simply absorbing each agent's private routine state.

## Matched systems

| Mode | Joint task | Bidirectional | Joint memory | Planner bound | Feedback | Structural closure |
|---|---:|---:|---:|---:|---:|---:|
| **Full shared workspace** | **1.000000** | **1.0** | **1.0** | **1.0** | **1.0** | **1.0** |
| Message only | 1.000000 | 0.0 | 0.0 | 1.0 | 1.0 | 0.0 |
| Workspace cut | 0.000000 | 1.0 | 0.0 | 0.0 | 1.0 | 0.0 |
| Message shuffle | 0.221354 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| One way | 1.000000 | 0.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| Planner-binding cut | 0.000000 | 1.0 | 1.0 | 0.0 | 1.0 | 0.0 |
| Recurrence cut | 1.000000 | 1.0 | 1.0 | 1.0 | 0.0 | 0.0 |
| Joint cut | 0.000000 | 0.0 | 0.0 | 0.0 | 1.0 | 0.0 |

The structural closure score is deliberately not a semantic-correctness score. The message-shuffle condition retains a structurally complete workspace carrying the wrong synchronized content and therefore performs poorly. Structure is necessary but not sufficient. Content validity and provenance remain separate requirements.

## Decisive dissociation

The message-only route solved the immediate joint task perfectly while having:

- no bidirectionally writable shared packet;
- no pair-bound joint autobiographical write;
- no recurrent pair memory;
- no distributed-workspace closure.

This establishes that successful communication alone is insufficient for the stronger shared-workspace claim.

## Causal intervention results

### Bidirectional write access

Writing a target shared state into the joint manifold redirected both agents and the joint plan in every probe while preserving both private routines.

| Measure | Result |
|---|---:|
| Joint patch success | 1.000000 |
| Agent A private routine preserved | 1.000000 |
| Agent B private routine preserved | 1.000000 |
| Mean A-to-B causal effect ratio | 0.500766 |
| Mean B-to-A causal effect ratio | 0.499253 |

### Pair provenance

A valid shared state from another pair was quarantined by the intact controller and blocked from planning. Removing provenance checks caused every foreign-pair state to be written falsely and planner-bound.

| Measure | Intact | Provenance cut |
|---|---:|---:|
| Foreign memory quarantined | 1.000000 | 0.000000 |
| False joint write | 0.000000 | 1.000000 |
| Foreign state bound to planner | 0.000000 | 1.000000 |

### Feedback recurrence

After an unexpected joint consequence, the intact pair reopened communication and used three rounds on the next ambiguous interaction. The recurrence-cut pair stayed at one round.

| Next challenged interaction | Intact | Recurrence cut |
|---|---:|---:|
| Reopened interaction | 1.000000 | 0.000000 |
| Decision accuracy | 1.000000 | 0.000000 |
| Mean rounds | 3.0 | 1.0 |

### New partner

A pair-private message decoder did not transfer reliably to a new trained partner. The original shared atlas also degraded. A fresh label-free cross-agent atlas, learned from synchronized trajectories, restored the shared relation.

| Partner-swap measure | Result |
|---|---:|
| Pair-private message accuracy | 0.263889 |
| Unadapted atlas accuracy | 0.402778 |
| Remapped shared-atlas accuracy | 1.000000 |
| Remapped alignment R² | 0.999496 |
| New partner message-decoder R² | 0.999323 |

This is evidence for a remappable relation, not a universal lingua franca. The remapping requires new synchronized trajectories and task calibration.

## What this establishes

Within this deterministic synthetic dyad, the useful interaction state is not fully characterized by either agent's private pre-interaction state. A low-dimensional common manifold can be recovered from paired trajectories without hidden factor labels and can acquire causal roles in both agents, joint planning, pair-specific memory, provenance, and later evidence allocation.

This supports the existence of a bounded **causally distributed functional workspace**.

## What this does not establish

The result does not establish:

- one shared consciousness;
- a shared phenomenal field;
- spontaneous emergence in arbitrary agents;
- universal latent alignment;
- transfer to arbitrary partners without remapping;
- open-ended multi-agent awareness;
- sentience, valence, suffering, pleasure, desire, moral status, or legal personhood.

The common semantic structure was deliberately present in the agents' synchronized task trajectories. The scientifically relevant result is that it was recovered without factor labels and passed causal, mnemonic, provenance, planning, recurrence, and recombination tests.

## Next major gap

The next stronger test is an **unannounced open-set joint workspace**:

- no declared shared-factor count;
- no fixed interaction boundary;
- changing and partly conflicting goals;
- more than two agents;
- dynamic coalition formation and dissolution;
- unsynchronized observations;
- novel partners without prepared calibration episodes;
- endogenous discovery of whether any shared workspace should form at all;
- explicit retention of private disagreement rather than forced consensus.

That would move from discovering a structured common manifold to discovering whether, when, and among whom a distributed workspace should exist.
