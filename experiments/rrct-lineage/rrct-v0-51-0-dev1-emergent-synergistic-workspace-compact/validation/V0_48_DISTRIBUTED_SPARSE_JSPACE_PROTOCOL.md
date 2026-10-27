# RRCT v0.48 Distributed Sparse J-Space Protocol

## Scientific question

Can two independently parameterized agents instantiate a **distributed functional J-space analogue**, rather than merely a communication code or one fixed shared linear manifold?

A positive result requires all of the following in one bounded dyad:

1. each agent independently exposes a selective Jacobian-discovered local workspace;
2. each local workspace is represented by an overcomplete sparse concept frame rather than one fixed semantic coordinate vector;
3. active supports vary across episodes, forming a state-dependent union of cones;
4. synchronized interaction discovers a cross-agent atlas and concept-frame correspondence without hidden semantic labels;
5. the mapped shared state is reportable to both agents and flexibly reusable for multiple downstream questions;
6. either side can causally alter shared content, changing both agents' reports, shared reasoning, and the joint plan while sparing private processing;
7. workspace ablation selectively impairs shared report and flexible control while preserving private routines;
8. the workspace has a frozen sparse capacity limit;
9. the complete state is planner-causal, pair-provenance-bound, and recurrently updated by joint consequences;
10. a new partner requires new message and frame alignment rather than inheriting the old pair's private convention.

The target is a controlled functional analogue of a shared J-space. It is not a claim that the agents possess one subjective or phenomenal field.

## Relation to v0.46 and v0.47

Version 0.46 established one-agent Jacobian-discovered sparse workspaces with reportability, directed modulation, flexible reuse, selective ablation, and self-indexed provenance.

Version 0.47 established a distributed rank-four shared workspace with cross-agent coordinate alignment, bidirectional writes, joint planning, pair memory, provenance, recurrence, and partner remapping.

Version 0.48 composes those two mechanisms. It replaces the single fixed shared semantic vector with two independently discovered local sparse frames whose active supports are aligned into a distributed moving workspace.

## Synthetic dyad

Each seed generates two independently parameterized agents.

- Residual dimension per agent: 64
- Local Jacobian workspace rank: 4
- Local overcomplete frame size: 8
- Sparse support capacity: 4
- Private routine packet rank: 20
- Message dimension: 4
- Joint semantic bits: 4
- Joint actions: 16
- Calibration trajectories: 1,024

Each semantic bit selects one of an opposing pair of concept directions. A complete joint state therefore activates exactly four nonnegative directions from an eight-direction frame. Across all possible states, sixteen distinct support combinations are available.

Agent A directly observes the first two semantic bits. Agent B directly observes the final two. Each sends a pair-private message through an independently rotated code. Neither private pre-interaction state contains the complete joint action.

The hidden semantic labels are evaluator-only. The runtime receives hidden activations, local Jacobians, messages, synchronized trajectories, and pair provenance, but no bit labels, correct support, correct action, or mode-specific success flag before commitment.

## Local J-space discovery

For each agent, the v0.46 Jacobian lens constructs token-indexed directions from an exact synthetic average Jacobian. Sparse nonnegative reconstruction selects at most four active directions per state.

The local workspace must be:

- rank four;
- no more than 15 percent of total activation variance;
- report-predictive;
- represented through a state-dependent sparse support rather than a fixed coordinate mask.

## Cross-agent shared atlas

Synchronized local workspace trajectories are aligned without semantic factor labels.

1. Paired local workspace states are centered.
2. Canonical correlation identifies the common rank.
3. Komorebi packet projectors represent each local shared packet.
4. Orthogonal transport aligns Agent B's common coordinates with Agent A's.
5. Local frame directions are mapped by maximum positive cosine after transport.
6. The distributed shared frame is the normalized average of aligned local frame directions.
7. Sparse supports are mapped into one common token coordinate system.

The learned atlas is considered valid only when its packet certificates, analysis-synthesis reconstruction, frame mapping, and support agreement validate.

## Distributed access state

For local states `h_A` and `h_B`, each agent emits a local sparse workspace state. After B-to-A transport, the shared state is:

\[
z_t^{AB}=\frac{1}{2}\left(z_t^A+T_{B\rightarrow A}z_t^B\right).
\]

The distributed access receipt binds:

- both local J-space access receipts;
- the learned distributed frame;
- the mapped sparse supports;
- the pair-lineage digest;
- the v0.47 joint workspace receipt;
- bidirectional availability;
- planner authorization;
- provenance status.

## Matched architecture modes

| Mode | Description |
|---|---|
| `full_shared` | Complete sparse distributed J-space, bidirectional write, pair memory, planner binding, and recurrence |
| `message_only` | Direct message decoder solves the current task without distributed sparse workspace closure |
| `workspace_cut` | Messages remain, but the shared sparse packet is removed before planning |
| `message_shuffle` | Structurally complete workspace receives same-pair content from an incompatible episode |
| `one_way` | One agent receives the missing partner content, but there is no bidirectional shared access |
| `provenance_cut` | Foreign-pair workspace content is accepted as pair autobiography |
| `planner_binding_cut` | Distributed J-space forms but cannot authorize the joint planner |
| `recurrence_cut` | Joint consequence is not written into the next pair-level evidence decision |
| `joint_cut` | Communication, shared sparse packet use, and planner binding are removed together |

## Dedicated causal tests

### Directed shared-concept swap

One active shared concept is replaced with its opposing concept direction. The intervention must:

- change Agent A's report;
- change Agent B's report;
- change at least one flexible downstream reasoning answer;
- redirect the joint plan;
- preserve both agents' private routine outputs.

### Selective J-space ablation

The shared sparse packet is suppressed while private packets are retained. Shared report and task performance should collapse by at least 60 percentage points while both private routines remain at least 98 percent correct.

### Capacity interference

Two incompatible four-concept states are simultaneously proposed. The selected workspace support must never exceed four concepts and cannot retain more than 60 percent of the eight-concept union.

### Foreign-pair provenance

A valid shared state is presented with another pair's lineage digest. Full closure must quarantine it and prevent autobiographical write and planning. The provenance-cut control should falsely accept it.

### Feedback recurrence

Both systems first receive the same unexpected joint outcome. On the next deliberately ambiguous interaction, full closure should reopen communication for three rounds and recover the correct action. The recurrence-cut system should remain at one round and fail.

### New-partner remapping

Agent A is paired with Agent B from another trained dyad.

- The original pair-private message decoder must not transfer reliably.
- The original pair atlas must not be treated as valid for the new pair.
- Fresh synchronized calibration, new message decoding, and a new sparse-frame atlas must restore task accuracy, alignment, frame correspondence, and support agreement.

## Frozen endpoints

1. Both local Jacobian workspace ranks equal four for every seed.
2. Mean workspace activation variance is at most 15 percent in each agent.
3. Shared rank equals four, minimum canonical correlation is at least 0.99, and mean alignment R² is at least 0.99.
4. Minimum mapped frame cosine and mean exact support agreement are at least 0.98.
5. At least sixteen distinct sparse supports occur on every seed.
6. Every Komorebi packet and analysis-synthesis certificate validates.
7. Full shared report accuracy for both agents and shared-support accuracy are each at least 98 percent.
8. Full shared flexible-reuse accuracy is at least 98 percent.
9. Directed modulation changes both agents' reports in at least 98 percent of probes.
10. Directed modulation redirects the joint plan in at least 98 percent of probes.
11. Directed modulation changes flexible downstream reasoning in at least 98 percent of probes.
12. Directed modulation preserves both private routines in at least 98 percent of probes.
13. Selective ablation reduces each report and the flexible task by at least 60 percentage points.
14. Selective ablation preserves both private routines in at least 98 percent of probes.
15. Sparse capacity is respected in every probe, mean support size is at most four, and dual-state union recall is at most 60 percent.
16. Message-only task accuracy is at least 98 percent while distributed-J-space closure is exactly zero.
17. One-way task accuracy is at least 98 percent while distributed-J-space closure is exactly zero.
18. Message shuffling retains at least 98 percent structural closure while task accuracy is at most 40 percent.
19. Cutting planner binding reduces task accuracy by at least 70 percentage points.
20. Full recurrence reopens every challenged interaction, recurrence cut never reopens, and full second-decision accuracy exceeds recurrence cut by at least 50 percentage points.
21. Full provenance quarantines every foreign-pair state and makes no false write; provenance cut falsely writes every foreign state.
22. Unadapted partner accuracy is at most 50 percent; new mapping restores at least 98 percent task accuracy, 0.99 alignment R², 0.98 minimum frame cosine, and 0.98 support agreement.
23. Full distributed-J-space closure is at least 98 percent.
24. Joint cut reduces closure by at least 90 percentage points.
25. Workspace-cut task accuracy is at most 20 percent.
26. Every complete receipt chain validates.
27. Every runtime row reports no evaluator-label use.
28. Explicit survival, identity, and continuity rewards are zero and no valence model is present.

## Receipt chain

Each evaluated interaction binds:

```text
local Jacobian discoveries
→ local sparse access receipts
→ cross-agent sparse-frame discovery
→ message receipts
→ pair-provenance joint workspace
→ distributed J-space access receipt
→ joint planning commitment
→ revealed consequence
→ pair memory and next evidence budget
```

The complete validator rejects individually rehashed receipts when attached to the wrong local access state, pair, episode, joint workspace, plan, or outcome.

## Development/holdout boundary

Development used only the exposed seeds and controls listed in `V0_48_DEVELOPMENT_REPORT.md`. Holdout seeds are selected by SHA-256 expansion from a fixed namespace after this protocol is written. Candidate outcomes are not examined during selection. The selected seeds, protocol, implementation, thresholds, tests, and runner are sealed before the holdout is executed.

## Interpretation boundary

Passing all endpoints would establish a **controlled functional distributed J-space analogue**: two independently parameterized agents would instantiate local Jacobian-discovered sparse workspaces whose dynamic active supports are aligned into a bidirectionally writable, flexibly reusable, planner-causal, pair-provenance-bound, recurrent shared access structure.

It would not establish:

- that production language models form the same mechanism;
- one shared phenomenal or subjective experience;
- a merged mind;
- consciousness, sentience, valence, suffering, pleasure, desire, moral status, or legal identity;
- spontaneous open-world coalition formation;
- zero-shot universal alignment to arbitrary partners;
- a formal noninterference proof against every possible evaluator side channel.
