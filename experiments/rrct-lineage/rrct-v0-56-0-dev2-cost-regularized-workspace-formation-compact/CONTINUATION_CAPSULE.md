# RRCT v0.56 Continuation Capsule

## Current established result

A task-conditioned router selected among no-workspace, flat, three alternative nested-pair, and overlapping-full routes using an anonymous dependency cue and the objective:

\[
J_r=L_r+\lambda C_r.
\]

On 16 fresh primary seeds it achieved perfect terminal and minimal-route accuracy. The independent price sweep found:

```text
lambda < 0.03       → overformation
0.03 to 0.22        → cheapest sufficient architecture
lambda = 0.24       → overlap workspace begins to disappear
lambda ≈ 0.40       → pair hierarchies begin to disappear
```

The observed collapse order agrees with the pairwise break-even formula:

\[
\lambda^*=\frac{\Delta L}{\Delta C}.
\]

## Strongest claim

> Given a supplied route library and public task-dependency signature, a learned controller can decide whether to form a workspace, which coalition graph to activate, how deeply to integrate, when to switch graphs, and when to close all workspaces.

## Critical nonclaim

The system does not invent graph structure. It selects among supplied candidates and receives every candidate's counterfactual terminal loss during training.

## Next target

Build a neural system that constructs graph edges under partial feedback rather than selecting complete route labels.

Minimum next requirements:

- raw observations rather than supplied dependency signatures;
- unknown or changing agent count;
- learned edge proposals;
- no full counterfactual route table;
- recurrent switching costs and teardown;
- open-set option to create a graph absent from the initial library;
- tasks where no workspace is beneficial;
- causal edge ablations and counterfactual graph transplantation.
