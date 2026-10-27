# v0.3 single-cell reproducibility replay

**Outcome: PASS.**

Arm: `hard_correct`  
Seed: `300`

## Exact comparisons

| Check | Result |
|---|---:|
| Metric JSON, recursively exact | `True` |
| Semantic arm record, recursively exact | `True` |
| State keys and order equal | `True` |
| State dtypes/shapes/layouts equal | `True` |
| Every state tensor byte equal | `True` |
| Auxiliary module state equal | `True` |
| Canonical state SHA-256 equal | `True` |
| Checkpoint metadata equal after declared provenance exclusions | `True` |
| Canonical checkpoint SHA-256 equal | `True` |
| Raw `torch.save` file SHA-256 equal (informational) | `False` |

The raw checkpoint file hash is informational because the replay uses a new
protocol identifier and protocol digest. The pass criterion instead uses a
canonical checkpoint hash that excludes only those declared provenance fields
and includes the exact bytes of every state tensor.

## Declared exclusions

Semantic record: `analysis_status`, `protocol_id`, `protocol_digest`, `training.elapsed_seconds`, `started_at`, `created_at`, `completed_at`, `finished_at`, `timestamp`, `timestamp_utc`, `output_dir`, `protocol_path`, `checkpoint_path`, `environment`, `plots`, `plot_files`

Checkpoint metadata: `analysis_status`, `protocol_id`, `protocol_digest`

Metric JSON has no exclusions.
