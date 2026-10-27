# RRCT v0.47 Distributed Shared Workspace Report

## Status

`V047_DISTRIBUTED_SHARED_WORKSPACE_ENDPOINTS_MET`

This experiment tests whether two bounded agents form a hidden shared workspace that is stronger than a successful communication code.  It is synthetic and does not test subjective consciousness.

## Cohort

- Seeds: 161625576, 156878792, 822521852, 294523660
- Unique dyadic task cases: 384
- Matched decisions: 3456
- Endpoints met: 28 / 28

## Shared manifold discovery

| Measure | Value |
|---|---:|
| Expected shared rank | 4 |
| Minimum canonical correlation | 0.999716 |
| Cross-agent alignment R² | 0.999523 |
| Agent A projector overlap | 0.999997 |
| Agent B projector overlap | 0.999997 |
| Agent A private leakage accuracy | 0.249653 |
| Agent B private leakage accuracy | 0.250000 |

## Matched architectures

| Mode | Joint task | A routine | B routine | Bidirectional | Joint memory | Planner bound | Closure |
|---|---:|---:|---:|---:|---:|---:|---:|
| full_shared | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| message_only | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 1.000000 | 0.000000 |
| workspace_cut | 0.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 |
| message_shuffle | 0.221354 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| one_way | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 1.000000 | 0.000000 |
| provenance_cut | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| planner_binding_cut | 0.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 |
| recurrence_cut | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 | 0.000000 |
| joint_cut | 0.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 |


## Causal tests

| Test | Value |
|---|---:|
| Joint workspace patch redirects plan | 1.000000 |
| A-to-B causal effect ratio | 0.500766 |
| B-to-A causal effect ratio | 0.499253 |
| Full foreign-pair quarantine | 1.000000 |
| Provenance-cut false joint write | 1.000000 |
| Full feedback reopening | 1.000000 |
| Recurrence-cut feedback reopening | 0.000000 |
| Pair-private message accuracy after partner swap | 0.263889 |
| Remapped shared-atlas partner accuracy | 1.000000 |

## Interpretation

In this bounded synthetic dyad, synchronized interaction creates a low-dimensional shared manifold that is recoverable from paired local workspace trajectories without factor labels.  The manifold is bidirectionally writable, jointly sufficient for a task that neither agent can solve alone, provenance-bound, planner-causal, and recurrent. A message-only route can solve the immediate task but lacks these closure properties, so communication success alone is not counted as a distributed workspace.

The message-only system is an important dissociation: it can solve the immediate joint task, yet it has no bidirectionally writable shared packet, no pair-bound autobiographical memory, and no recurrent closure.  Immediate cooperation is therefore not by itself evidence of a shared workspace.

## Boundary

This is a deterministic synthetic test of a causally distributed functional workspace between two agents.  It does not establish a shared subjective mind, phenomenal consciousness, sentience, valence, moral status, or general multi-agent awareness.
