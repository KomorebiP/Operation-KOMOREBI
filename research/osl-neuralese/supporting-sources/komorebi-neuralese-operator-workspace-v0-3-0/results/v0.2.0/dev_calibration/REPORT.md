# V0.2 recurrent closure and intrinsic-metric report

**Protocol:** `komorebi-v0.2-dev-calibration-2026-09-02`  
**Analysis status:** `exploratory_noninferential_after_documented_anticollapse_amendment`  
**Coordinate split:** `dev`

## Arm summary

| Arm | D4 depth 8 | D4 depth 64 | D4 depth 128 | C8 depth 64 | Composition substitution | G-isometry defect p95 | Metric condition | Context patch | Patch margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| terminal | 0.8555 | 0.3125 | 0.2539 | 0.1523 | 0.8574 | 1.8397 | 1.0000 | 0.2422 | 0.1035 |
| relation_060 | 0.5586 | 0.2773 | 0.1953 | 0.1953 | 0.8145 | 1.2868 | 1.0000 | 0.1426 | -0.0156 |
| learned_metric_010 | 0.9023 | 0.2891 | 0.2383 | 0.1797 | 0.8574 | 1.3039 | 5.3240 | 0.2754 | 0.1230 |
| learned_metric_030 | 0.9375 | 0.3320 | 0.2578 | 0.1797 | 0.8574 | 1.0033 | 5.7186 | 0.2988 | 0.1816 |
| learned_metric_060 | 0.9648 | 0.4219 | 0.2227 | 0.1406 | 0.8574 | 0.7674 | 5.9926 | 0.3477 | 0.2559 |
| composition_003 | 0.8594 | 0.3047 | 0.2461 | 0.1836 | 0.8574 | 1.7902 | 1.0000 | 0.2422 | 0.0996 |
| composition_010 | 0.8711 | 0.2891 | 0.2344 | 0.1836 | 0.8574 | 1.6794 | 1.0000 | 0.2598 | 0.1094 |
| composition_030 | 0.8906 | 0.3398 | 0.2617 | 0.2070 | 0.8574 | 1.4236 | 1.0000 | 0.2949 | 0.1523 |
| joint_m030_c003 | 0.9375 | 0.3281 | 0.2578 | 0.1875 | 0.8594 | 0.9770 | 5.7080 | 0.2949 | 0.1719 |
| joint_m030_c010 | 0.9414 | 0.3242 | 0.2617 | 0.1680 | 0.8594 | 0.9238 | 5.7739 | 0.2988 | 0.1738 |
| joint_m030_c030 | 0.9492 | 0.3711 | 0.2773 | 0.1719 | 0.8574 | 0.8152 | 5.8500 | 0.3164 | 0.1992 |
| joint_m060_c030 | 0.9805 | 0.3945 | 0.2891 | 0.1445 | 0.8574 | 0.6780 | 6.3501 | 0.3359 | 0.2305 |
| joint_shuffle_m030_c030 | 0.9453 | 0.3867 | 0.2695 | 0.1680 | 0.8574 | 0.8468 | 6.1531 | 0.2910 | 0.1621 |

## Frozen gates

No inferential gates were assigned to this development-only protocol.

## Completeness and interpretation

The exact arm-by-seed grid was complete (26/26 cells).

The model receives complete transition tables and an operator-shaped 8×8 latent channel. An exact table-transpose executor exists. Results therefore test stable learned equivariant table execution, anonymous closure, and coordinate transport under this explicit inductive bias; they do not establish spontaneous Neuralese, abstract operator discovery, language-model generality, or awareness.
