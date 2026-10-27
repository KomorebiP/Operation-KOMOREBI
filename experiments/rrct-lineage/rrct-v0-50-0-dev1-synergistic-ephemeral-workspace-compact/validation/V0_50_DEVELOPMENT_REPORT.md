# RRCT v0.50 Development Report

## Exposed development seeds

`50001, 50007, 50011`

All three development seeds met all 23 proposed endpoints.

## Development means

| Mode | Accuracy |
|---|---:|
| Full workspace | 1.000000 |
| Recurrent message workspace | 1.000000 |
| Reset each update | 0.062500 |
| Reset each round | 0.062500 |
| A-only writes | 0.062500 |
| B-only writes | 0.062500 |
| Planner-binding cut | 0.062500 |
| Workspace shuffle | 0.063828 |
| Last-message Bayes bound | 0.062500 |
| Unordered-pool Bayes bound | 0.171875 |
| Complete message-log oracle | 1.000000 |

The exact task audit found four bits of synergistic target information and zero bits in either complete private history alone.

## Development interpretation

The intended distinction was achieved. The successful recurrent-message control demonstrates that a workspace need not be physically centralized. The failed controls isolate persistence, bilateral writability, temporal order, and planner binding. The external message-log oracle succeeds because retaining the entire interaction history creates a persistent integration structure outside the two agents.

No frozen holdout outcome was evaluated during development.
