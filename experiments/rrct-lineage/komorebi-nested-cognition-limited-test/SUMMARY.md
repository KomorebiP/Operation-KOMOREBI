# Limited Test of Recursive Agent–Workspace Cognition

## Status

`LIMITED_NESTED_WORKSPACE_ENDPOINTS_MET`

All **16 of 16** declared endpoints passed.

## Case 1: exact recursive synergy

A two-bit root state was recursively secret-shared down binary trees. Every child state was individually independent of its parent, while each sibling pair jointly determined the parent exactly.

| Measure | Depth 2 | Depth 3 |
|---|---:|---:|
| Leaf agents | 4 | 8 |
| Exact cases | 256 | 65,536 |
| Maximum one-child information about parent | 0 bits | 0 bits |
| Minimum sibling-pair information about parent | 2.000000 bits | 2.000000 bits |
| Full hierarchy accuracy | 1.000 | 1.000 |
| Reset one top workspace | 0.250 | 0.250 |
| Shuffle one top workspace | 0.250 | 0.250 |
| One-bit capacity cut | 0.500 | 0.500 |
| Coherent top-down rewrite | 1.000 | 1.000 |

The same two-bit workspace type recurs at every scale. A workspace produced by two lower agents therefore functions as an agent input at the next level.

The depth-three hierarchy compresses:

```text
16 raw leaf bits
→ 8 level-one workspace bits
→ 4 level-two workspace bits
→ 2 root-workspace bits
```

while preserving the root task exactly.

## Case 2: noncommuting operator hierarchy

Four leaf agents supplied ordered permutation operators. Two local workspaces composed adjacent operators; the top workspace composed the two resulting operator-agents.

| Measure | Result |
|---|---:|
| Exact cases | 1,024 |
| Full hierarchy accuracy | 1.000 |
| Swap top workspace order | 0.539 |
| Reverse one local pair | 0.469 |
| Reset left workspace | 0.406 |
| Reset right workspace | 0.406 |
| One workspace alone, Bayes optimal | 0.422 |
| Both workspace-agents, Bayes optimal | 1.000 |
| Unordered flat operation summary | 0.518 |

This second case rules out the possibility that the first result depends only on an associative XOR tree. Temporal order and the identities of both workspace-agents are causally important.

## Interpretation

These limited cases support the **operational possibility** of recursive workspace cognition:

```text
lower agents
→ local synergistic workspace
→ workspace behaves as a higher-level agent
→ higher synergistic workspace
→ broader action
```

They establish:

- local insufficiency;
- workspace-level joint sufficiency;
- recursive type reuse across levels;
- progressive compression;
- privacy of lower-level state;
- causal necessity of each workspace boundary;
- coherent top-down rewrite;
- order-sensitive composition in a noncommuting case.

They do **not** establish:

- spontaneous emergence of the hierarchy;
- biological realism;
- that human brain regions implement XOR secret sharing;
- that one hierarchy is uniquely necessary;
- consciousness or subjective awareness.

The strongest next limited test would replace the hand-coded combination rules with learned local agents and ask whether a two-level hierarchy is discovered from terminal objectives without intermediate workspace labels.
