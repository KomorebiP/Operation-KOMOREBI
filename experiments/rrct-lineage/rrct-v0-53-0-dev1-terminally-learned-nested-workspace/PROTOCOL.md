# RRCT v0.53 Terminally Learned Nested-Workspace Protocol

## Question
Can a supplied two-level neural hierarchy learn the coordinate semantics of two local workspaces and one global workspace from terminal leaf-action supervision alone, without intermediate labels for `U`, `V`, or `Y`?

## Exact task on S^1
`U,V` are independent uniform phases. `A1=RA`, `A2=U-RA mod 1`, `B1=RB`, `B2=V-RB mod 1`, and `Y=U+V mod 1`. Leaf `i` must emit `Xi+Y mod 1`.

Each single share is independent of its local phase; the share pair determines it. Either local phase alone is independent of `Y`; the pair determines it.

## Architecture
`A1+A2 -> ZA`, `B1+B2 -> ZB`, `(ZA,ZB)->ZG`, then `ZG` is written to four leaf action heads. Generic tensor-product interaction blocks are supplied. The primary bottlenecks are two-dimensional. Training uses terminal leaf-action loss only; no local/global labels are used.

## Controls
- each leaf removed from workspace construction;
- each local workspace set to zero;
- global workspace set to zero;
- global state computed but disconnected from leaf actions;
- local/global workspace transplantation;
- one-dimensional bottleneck under the same training budget;
- smaller flat full-access controller;
- unrelated private routine route.

## Frozen thresholds
1. exact share equations;
2. no intermediate labels;
3. intact strict action accuracy >= .995;
4-6. local-A, local-B, and global probe accuracy >= .99;
7. each leaf cut <= .12;
8-11. local-A, local-B, global, and top-down cuts <= .12;
12-14. local-A, local-B, and global patch accuracy >= .99;
15. private route remains 1.0;
16. one-dimensional bottleneck <= .20;
17. flat controller >= .98;
18. no valence or self-preservation objective.

## Boundary
The hierarchy, coalitions, update order, bottleneck size, tensor-product primitive, and terminal outputs are supplied. A flat controller is expected to solve. This is not spontaneous hierarchy discovery, brain equivalence, functional awareness, or subjective experience.
