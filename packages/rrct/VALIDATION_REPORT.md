# RRCT v0.60 Validation Report

## Outcome

`0.60.0.dev1` passed the dependency-free regression, exact-resume, strict-contract, freeze, wheel, and bounded synthetic bridge checks available in this environment.

No scientific-scale campaign was executed. PyTorch, Transformers, and local transformer weights were unavailable, so two retained Torch experiment families and the live transformer adapter path were not executed.

## Regression and package checks

| Check | Result |
|---|---:|
| Pytest regression | **37 passed, 0 failed** |
| Python AST parse | **52 passed, 0 failed** |
| Presets and sweep templates | **23 passed, 0 failed** |
| New rank/sparsity cells | **6 validated** |
| New intervention-factorial cells | **64 validated** |
| J-space core direct test groups | **4 passed** |
| Optional adapter direct test groups | **6 passed** |
| Fuzzy-to-J integration/resume tests | **4 passed** |
| Exact resumed metrics | **Yes** |
| Exact resumed rows | **Yes** |
| Exact resumed checkpoint state | **Yes** |
| Exact resumed trajectory digest | **Yes** |
| New-family freeze source files | **52 verified** |
| Installed-wheel bounded probe | **12 episodes completed** |

The all-family smoke matrix registered all nine families. Seven completed. `nested_workspace` and `fuzzy_coalitions` were reported unavailable because PyTorch was absent; there were no unexpected dependency-free failures. The new `persistent_fuzzy_j_workspace` family completed with 55 finite metrics.

## Bounded bridge result

The ready-made 192-episode, single-seed preset completed. Its smoke diagnostic chain stopped after three links:

```text
fuzzy formation
→ sparse Jacobian workspace
→ selective causal broadcast
⊣ provenance-aware planner binding
⊣ recurrence
```

Selected measurements:

| Measurement | Value |
|---|---:|
| Formation balanced accuracy | 0.5521 |
| Membership/ablation correlation | 0.3490 |
| J-space task score | 0.7962 |
| Same-rank PCA score | 0.7737 |
| Same-rank random score | 0.7719 |
| J minus PCA | +0.0226 |
| J minus random | +0.0243 |
| J-space ablation drop | +0.0365 |
| Routine preservation under J cut | 1.0000 |
| Plan accuracy | 0.5816 |
| Planner cut drop | **-0.0081** |
| Provenance plan drop | +0.1184 |
| Recurrence true reopen rate | 0.6000 |
| Recurrence false reopen rate | **1.0000** |

The positive J/control and ablation contrasts support continued study of the synthetic geometry, but their sizes are small and come from one development seed. The negative planner-cut result and complete false reopening are explicit failures of the later links. The package does not convert those failures into an aggregate success.

Formation is scored with balanced accuracy. The unbalanced accuracy was 0.7083; reporting only that value would have overstated formation because workspace-required cases are more common.

## Exact resume

A 24-episode run was interrupted after episode 12 and resumed. It matched the uninterrupted run exactly in semantic metrics, row records, complete checkpoint state, and trajectory digest:

```text
6e35814daa673a6f5c4dcd831e618d5cf95d9193766a87661b006d3bae5b4524
```

## Transformer adapter boundary

Static and dependency-free tests verified local-path enforcement, lazy optional imports, remote-path rejection, projector checks, norm-matched patch helpers, and two model-loading calls that both force `local_files_only=True` and `trust_remote_code=False`.

A real forward pass, residual capture, target-token VJP, and live hook intervention remain unvalidated here. They require a compatible local model and local PyTorch/Transformers installation.

## Scientific correction retained in the release

The v0.59 continuous runtime's repair path reads evaluator-side latent state. v0.60 labels it as a legacy oracle-assisted scaffold and emits a warning. Its attribution and repair metrics are excluded from evaluator-blind claims.

## Interpretation

This validation establishes package integrity, deterministic execution, and a bounded synthetic mechanism diagnostic. It does not establish a naturally emerging transformer J-space, a frozen replicated effect, awareness, consciousness, sentience, valence, welfare, or moral status.
