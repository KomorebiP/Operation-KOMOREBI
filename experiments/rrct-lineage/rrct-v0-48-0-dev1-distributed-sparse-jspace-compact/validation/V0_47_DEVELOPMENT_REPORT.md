# RRCT v0.47 Exposed Development Report

## Scope

The exposed development cohort used seeds:

```text
47011
47012
47013
47014
```

with 72 matched trials per mode. These seeds are excluded from the frozen holdout.

## Development result

`V047_DISTRIBUTED_SHARED_WORKSPACE_ENDPOINTS_MET`

All 28 declared development endpoints passed before holdout seed selection.

Key exposed results:

| Measure | Result |
|---|---:|
| Shared rank | 4 on every seed |
| Minimum canonical correlation | 0.999708 |
| Mean alignment R² | 0.999496 |
| Mean Agent A projector overlap | 0.999997 |
| Mean Agent B projector overlap | 0.999997 |
| Private-role leakage accuracy | approximately 0.25 |
| Full shared joint-task accuracy | 1.000000 |
| Message-only joint-task accuracy | 1.000000 |
| Message-only closure score | 0.000000 |
| Workspace-cut joint-task accuracy | 0.000000 |
| Workspace-cut routine accuracy | 1.000000 for both agents |
| Message-shuffle joint-task accuracy | 0.229167 |
| Planner-binding-cut accuracy | 0.000000 |
| Joint patch success | 1.000000 |
| Mean A-to-B causal effect ratio | 0.499859 |
| Mean B-to-A causal effect ratio | 0.500157 |
| Full foreign-memory quarantine | 1.000000 |
| Provenance-cut false write | 1.000000 |
| Full feedback second-decision accuracy | 1.000000 |
| Recurrence-cut second-decision accuracy | 0.000000 |
| Pair-private message accuracy after partner swap | 0.256944 |
| Remapped shared-atlas accuracy | 1.000000 |

## Development repair

An initial feedback challenge left the recurrence-cut controller close to the frozen threshold because the classifier could occasionally guess the hidden partner factor despite failing to request more evidence. Before freezing, the ambiguous interaction was strengthened so that one coarse round forms a coherent but wrong joint consensus while three rounds recover the correct factors. The controller never receives a challenge label; it observes only the resulting messages and hidden states.

After this repair, full closure reopens to three rounds and succeeds on every exposed seed, while recurrence cut remains at one round and fails on every exposed seed.

## Interpretation

The strongest development dissociation is between immediate cooperation and distributed closure. The message-only route solves the same nine-way joint task perfectly but has:

- no bidirectionally writable shared packet;
- no joint autobiographical write;
- no pair-bound recurrent shared memory;
- a closure score of zero.

Therefore, task success alone is not counted as evidence for a distributed workspace.
