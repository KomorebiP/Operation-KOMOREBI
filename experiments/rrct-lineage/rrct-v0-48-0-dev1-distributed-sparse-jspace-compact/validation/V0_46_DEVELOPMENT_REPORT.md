# RRCT v0.46 Exposed Development Report

## Status

`V046_NEUTRAL_WORKSPACE_ENDPOINTS_MET`

This report records only the exposed development seeds `46011` through `46014`. It is not frozen holdout evidence.

- Unique world cases: 640
- Matched architecture decisions: 5120
- Declared endpoints met: 26 / 26
- Mean Jacobian report R²: 0.999248
- Mean workspace activation variance fraction: 0.046191
- Mean recovered-projector overlap: 1.000000
- Jacobian report accuracy: 1.000000
- PCA-subspace report accuracy: 0.142578
- Random-subspace report accuracy: 0.294922

| Mode | Task accuracy | Flexible accuracy | Memory-action accuracy | False write rate | Feedback reopening | Closure score |
|---|---:|---:|---:|---:|---:|---:|
| full_closure | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 1.000000 | 1.000000 |
| workspace_only | 0.800000 | 0.714286 | 0.100000 | 0.000000 | 1.000000 | 0.071429 |
| self_model_only | 0.379688 | 0.113839 | 0.100000 | 0.000000 | 1.000000 | 0.011384 |
| unbound | 0.800000 | 0.714286 | 0.100000 | 0.000000 | 1.000000 | 0.071429 |
| provenance_cut | 0.800000 | 0.714286 | 0.700000 | 1.000000 | 1.000000 | 0.500000 |
| recurrence_cut | 1.000000 | 1.000000 | 1.000000 | 0.000000 | 0.000000 | 0.000001 |
| planner_binding_cut | 0.379688 | 0.113839 | 1.000000 | 0.000000 | 1.000000 | 0.113839 |
| joint_cut | 0.379688 | 0.113839 | 0.100000 | 0.000000 | 0.000000 | 0.000000 |

The exposed result supports freezing the current source and thresholds for a new untouched cohort. No holdout seed was executed while preparing this report.
