# V0.2 recurrent closure and intrinsic-metric report

**Protocol:** `komorebi-v0.2-dev-smoke-2026-09-02`  
**Analysis status:** `exploratory_noninferential`  
**Coordinate split:** `dev`

## Arm summary

| Arm | D4 depth 8 | D4 depth 64 | D4 depth 128 | C8 depth 64 | Composition substitution | G-isometry defect p95 | Metric condition | Context patch | Patch margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| terminal | 0.5703 | 0.2852 | — | 0.2070 | 0.8750 | 1.9425 | 1.0000 | 0.1680 | 0.0742 |
| relation_060 | 0.2227 | 0.1719 | — | 0.1758 | 0.3008 | 1.2497 | 1.0000 | 0.1289 | 0.0117 |
| fixed_metric_010 | 0.5938 | 0.2930 | — | 0.2422 | 0.8789 | 1.7210 | 1.0000 | 0.1758 | 0.0859 |
| learned_metric_010 | 0.5977 | 0.2773 | — | 0.2422 | 0.8789 | 1.3792 | 4.3625 | 0.1797 | 0.0781 |
| composition_010 | 0.1055 | 0.1875 | — | 0.1328 | 0.0977 | 1.0000 | 1.0000 | 0.1250 | 0.0039 |
| metric_composition_003 | 0.1094 | 0.1875 | — | 0.1328 | 0.1641 | 1.0000 | 1.3381 | 0.0938 | -0.0391 |
| metric_composition_010 | 0.1094 | 0.1875 | — | 0.1328 | 0.1055 | 1.0000 | 1.2722 | 0.1250 | -0.0156 |
| metric_composition_030 | 0.1562 | 0.1875 | — | 0.1328 | 0.1094 | 1.0000 | 1.2053 | 0.1172 | 0.0195 |
| metric_composition_shuffle_010 | 0.0898 | 0.1875 | — | 0.1328 | 0.1133 | 1.0000 | 1.2848 | 0.0977 | -0.0195 |

## Frozen gates

No inferential gates were assigned to this development-only protocol.

## Completeness and interpretation

The exact arm-by-seed grid was complete (18/18 cells).

The model receives complete transition tables and an operator-shaped 8×8 latent channel. An exact table-transpose executor exists. Results therefore test stable learned equivariant table execution, anonymous closure, and coordinate transport under this explicit inductive bias; they do not establish spontaneous Neuralese, abstract operator discovery, language-model generality, or awareness.
