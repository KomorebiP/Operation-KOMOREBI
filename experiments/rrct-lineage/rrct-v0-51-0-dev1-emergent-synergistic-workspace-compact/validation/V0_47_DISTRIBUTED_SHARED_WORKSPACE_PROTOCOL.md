# RRCT v0.47 Distributed Shared Workspace Protocol

## Scientific question

Can two individually trained, self-indexed agents form a hidden interaction space that is functionally stronger than a successful communication code?

A positive result requires a low-dimensional shared manifold that:

1. is discovered from synchronized local workspace trajectories without evaluator factor labels;
2. excludes private agent information;
3. is jointly sufficient for a task neither private state can solve alone;
4. is bidirectionally writable from either agent;
5. controls both local workspace states and the joint planner;
6. carries pair-specific provenance and shared memory;
7. changes later interaction after joint consequences;
8. survives coordinate remapping to a new trained partner after a fresh shared atlas is learned.

Task performance alone is not sufficient. A message-only route is included specifically to show that cooperation can succeed without satisfying distributed-workspace closure.

## Neutral and safety boundary

The agents have no survival, identity, continuity, pleasure, suffering, distress, or self-preservation reward. The experiment uses only bounded informational salience and supervised external-task correctness.

The runtime has no network access, external tools, replication, unrestricted persistence, or open-ended goal generation.

## Synthetic dyad

Each seed generates two independently parameterized agents, A and B.

- Residual dimension per agent: 64
- Shared semantic factors: two categorical variables with three values each
- Shared centered rank: 4
- Private role variable per agent: four values
- High-energy automatic packet rank: 20
- Joint actions: 9

Agent A directly observes only the first shared factor. Agent B directly observes only the second. Each sends a three-dimensional message through an independently rotated message basis. After interaction, each forms a local hidden representation of the joint semantic state in a different 64-dimensional basis.

Neither private pre-interaction state is sufficient to determine the nine-way joint action. The complete interaction is sufficient.

## Training and discovery

The following components are fitted on exposed calibration trajectories:

- each sender's message decoder;
- each agent's local Jacobian workspace;
- the paired shared/private factorization;
- the joint action decoder;
- the direct message-only action decoder;
- private routine decoders.

The shared atlas is discovered only from synchronized local workspace trajectories. It does not receive the hidden shared-factor labels. The evaluator uses those labels only after discovery to score rank, projector overlap, action correctness, and private leakage.

The factorization procedure:

1. projects each trajectory into its local Jacobian workspace;
2. computes paired covariance and whitened cross-covariance;
3. selects canonical dimensions above a frozen correlation threshold;
4. constructs orthogonal local shared packets from cross-covariance singular vectors;
5. aligns the two local packet coordinates by orthogonal Procrustes transport;
6. certifies each local shared/nonshared decomposition through Komorebi packet and analysis-synthesis certificates.

## Matched modes

| Mode | Description |
|---|---|
| `full_shared` | Bidirectional shared atlas, pair provenance, joint memory, planner binding, and feedback |
| `message_only` | Direct message decoder solves the immediate task without a shared packet or joint memory |
| `workspace_cut` | Messages remain, but the mapped shared packet is ablated before planning |
| `message_shuffle` | Same-pair messages are drawn from an incompatible episode |
| `one_way` | Only one agent receives the partner's missing factor |
| `provenance_cut` | Foreign-pair shared memory is accepted as autobiographical |
| `planner_binding_cut` | Shared workspace is formed but cannot authorize the joint planner |
| `recurrence_cut` | Outcome error is not written back into later evidence allocation |
| `joint_cut` | Communication, shared packet use, and planner binding are removed together |

## Dedicated causal probes

### Joint patch

A shared state from another episode is written into both local shared packets. The joint action should change to the target episode while private routine outputs remain unchanged.

### One-sided patch

A change is written into only Agent A or only Agent B before consensus. The partner's local shared coordinates should move in the same direction after shared broadcast. This is the bidirectional causal-write criterion.

### Foreign-pair memory

A valid shared state is presented with a different pair-lineage digest. Full closure must quarantine it and block planning. The provenance-cut controller is expected to write it falsely.

### Feedback recurrence

Both controllers first receive an unexpected outcome. On the next ambiguous interaction, full closure should request three rounds and recover the correct joint decision. The recurrence-cut controller should remain at one round and fail.

### Partner recombination

Agent A from one trained pair is matched with Agent B from another trained pair.

- The original pair-private message decoder should not transfer reliably.
- The original shared atlas should not transfer reliably.
- A newly fitted cross-agent atlas, learned from synchronized trajectories without hidden coordinate labels, should restore alignment and task performance.

This probe distinguishes a pair-private convention from a remappable shared representational relation.

## Frozen endpoints

1. Shared rank equals 4 for every seed.
2. Minimum canonical correlation is at least 0.97.
3. Mean cross-agent alignment R² is at least 0.98.
4. Mean Agent A projector overlap is at least 0.98.
5. Mean Agent B projector overlap is at least 0.98.
6. Shared-coordinate decoding of either private role is at most 35 percent.
7. Every Komorebi packet, Hilbert, and atlas certificate validates.
8. Full shared-workspace joint task accuracy is at least 98 percent.
9. Neither individual pre-interaction state exceeds 45 percent joint-task accuracy.
10. Shared-workspace ablation reduces joint accuracy by at least 70 percentage points.
11. Shared-workspace ablation preserves both private routines at at least 98 percent.
12. Message shuffling reduces joint accuracy by at least 50 percentage points.
13. Message-only task accuracy is at least 95 percent while its closure score is at most 0.05.
14. The one-way mode is never classified as bidirectional.
15. Joint workspace patching redirects at least 98 percent of plans.
16. Joint patching preserves both private routines in at least 98 percent of probes.
17. Mean A-to-B and B-to-A causal effect ratios are each at least 0.35.
18. Full closure quarantines every foreign-pair memory and makes no false joint write.
19. Provenance cut falsely writes every foreign-pair memory.
20. Planner-binding cut loses at least 70 percentage points of joint accuracy.
21. Full closure reopens interaction after surprise on every seed; recurrence cut never does.
22. Full closure exceeds recurrence cut on the second challenged decision by at least 50 percentage points.
23. Pair-private message accuracy after partner swap is at most 45 percent.
24. A newly learned shared atlas restores partner-swap accuracy to at least 95 percent and alignment R² to at least 0.95.
25. Full closure exceeds joint cut on the engineered structural-closure score by at least 0.95.
26. Every complete receipt chain validates.
27. Every runtime row reports no evaluator-label use.
28. Explicit survival, identity, and continuity rewards are zero.

## Receipt chain

Each evaluated interaction binds:

```text
local Jacobian workspaces
→ shared-atlas discovery
→ A-to-B and B-to-A message receipts
→ pair-provenance and joint workspace
→ joint planning commitment
→ revealed task consequence
→ updated shared memory and next evidence budget
```

The complete validator rejects individually rehashed receipts when they are attached to the wrong workspace, pair, episode, plan, or outcome.

## Interpretation boundary

A positive result would establish a bounded **causally distributed functional workspace** in the synthetic dyad. It would show that the useful interaction state is not fully characterized by either private pre-interaction state and that the mapped shared state has bidirectional, mnemonic, planning, and recurrent causal roles.

It would not establish:

- a shared phenomenal or subjective experience;
- one consciousness rather than two coordinated controllers;
- general multi-agent awareness;
- universal representational identifiability;
- transfer to arbitrary partners without remapping;
- sentience, valence, suffering, pleasure, desire, moral status, or legal identity.
