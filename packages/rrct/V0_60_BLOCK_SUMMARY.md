# RRCT v0.60 — Persistent Fuzzy-to-J Workspace Bridge

## Release identity

- Version: `0.60.0.dev1`
- New family: `persistent_fuzzy_j_workspace`
- Scientific status: engineering implementation and smoke-level synthetic evidence
- Frozen replicated campaign: not executed in this build environment
- Live transformer experiment: not executed; no local model weights or optional runtime dependencies were available

## Central hypothesis

```text
fuzzy coalition formation
        → sparse workspace ignition
        → causal broadcast
        → provenance-aware planning
        → consequence-driven recurrence
```

This release operationalizes that claim as a serial chain rather than a single aggregate score. It records the longest consecutive supported prefix and exposes an intervention at every link.

## Scientific block

The controller sees observations, explicit task cues, source receipts, prior consequences, and its own learned state. It does not see event names, evaluator targets, or a correct workspace-membership target before committing. Terminal outcomes are revealed only afterward for learning and scoring.

The experiment includes:

- fuzzy overlapping memberships learned from terminal consumer loss
- a moving average terminal Jacobian
- a fixed-rank Jacobian projector
- sparse nonnegative top-k content
- measured report, inference, plan, and memory heads
- same-rank PCA and norm-matched random-subspace controls
- task-independent world/provenance events
- cross-step consequence feedback
- checkpointed persistent state and exact resume

The intervention ladder is:

```text
membership shuffle
→ J-space cut
→ broadcast cut
→ provenance cut
→ planner-binding cut
→ feedback cut
```

Each downstream cut also measures whether the upstream representation was preserved. That prevents a numerical output drop from being mislabeled as a selective causal intervention.

## Bounded development result

The included single-seed 192-episode preset reached a smoke diagnostic prefix of:

```text
fuzzy formation
→ sparse Jacobian workspace
→ selective causal broadcast
```

It did not pass provenance-aware planner binding or recurrence. The Jacobian code modestly exceeded same-rank PCA (`+0.0226`) and random subspaces (`+0.0243`), and its cut reduced score by `0.0365` while preserving routine processing. However, cutting the planner slightly improved the aggregate score (`planner_cut_drop = -0.0081`), and null events reopened the workspace every time (`false_reopen_rate = 1.0`).

Those failures are part of the result. They localize the next scientific work to planner necessity and recurrence specificity rather than allowing early-link success to imply end-to-end closure.

## Engineering block

The public `rrct_lab.jspace` API provides:

- exact or exponentially moving Jacobian discovery
- immutable basis, projector, and sparse frame objects
- projection, ablation, reconstruction, and coefficient swaps
- projector-idempotence, Jacobian-energy, activation-variance, and reportability metrics
- JSON-exact moving-frame checkpoint and resume

The optional `rrct_lab.adapters.hf_local` path supports common decoder-layer layouts, residual capture, target-token VJPs, norm-matched patches, and projector ablations. It accepts only existing local paths and disables downloads and remote model code.

## Reliability hardening

- registry-owned runtime and checkpoint metadata replace family-specific hardcoding
- completed-run skip validates resolved configuration, summary, run state, and checkpoint state
- sweep cell identifiers include the resolved base configuration digest
- mismatched or legacy-unbound sweep ledgers are rejected
- direct configuration mappings are validated before execution

## Scientific correction

The v0.59 `continuous_open_set_runtime` copied evaluator-side latent changes into repair estimates. v0.60 retains it only as an explicitly labeled `legacy_oracle_assisted_scaffold` and emits a warning. Its attribution and repair numbers are not evaluator-blind evidence.

The new fuzzy-to-J family does not use evaluator labels for controller diagnosis or pre-commit decisions. Evaluator truth is used only for post-commit learning and scoring.

## Interpretation boundary

Even a successful synthetic chain would establish only a causal workspace analogue under controlled tasks. This release does not establish:

- a naturally emerging J-space in a pretrained transformer
- general verbal reportability
- open-world awareness
- consciousness or subjective experience
- sentience, valence, desire, welfare, or moral status

See `docs/FUZZY_JSPACE_CAUSAL_PROTOCOL.md` for the complete protocol and falsification rules.
