# V0.2 recurrent closure and intrinsic-metric report

**Protocol:** `komorebi-v0.2-dev-strength-calibration-2026-09-02`  
**Analysis status:** `final_exploratory_development_calibration`  
**Coordinate split:** `dev`

## Arm summary

| Arm | D4 depth 8 | D4 depth 64 | D4 depth 128 | C8 depth 64 | Composition substitution | G-isometry defect p95 | Metric condition | Context patch | Patch margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| terminal | 0.9570 | 0.3672 | 0.3086 | 0.1875 | 0.8340 | 2.0682 | 1.0000 | 0.2969 | 0.1855 |
| relation_060 | 0.9883 | 0.6094 | 0.3984 | 0.2500 | 0.8359 | 0.9544 | 1.0000 | 0.3516 | 0.2656 |
| fixed_metric_100 | 1.0000 | 0.5898 | 0.4258 | 0.1719 | 0.8359 | 0.3187 | 1.0000 | 0.4395 | 0.3750 |
| fixed_metric_300 | 1.0000 | 0.6055 | 0.4492 | 0.2031 | 0.8340 | 0.2194 | 1.0000 | 0.4434 | 0.3828 |
| learned_metric_100 | 0.9961 | 0.5078 | 0.3867 | 0.1445 | 0.8359 | 0.3819 | 4.1741 | 0.4375 | 0.3633 |
| learned_metric_300 | 1.0000 | 0.4844 | 0.3906 | 0.1445 | 0.8340 | 0.2157 | 3.4318 | 0.4551 | 0.3770 |
| composition_100 | 1.0000 | 0.6562 | 0.4727 | 0.2969 | 0.8340 | 0.6810 | 1.0000 | 0.4590 | 0.3828 |
| composition_300 | 1.0000 | 0.6719 | 0.4961 | 0.4062 | 0.8340 | 1.6412 | 1.0000 | 0.4590 | 0.3945 |
| joint_m100_c100 | 1.0000 | 0.6406 | 0.4023 | 0.2539 | 0.8359 | 0.2306 | 6.5738 | 0.4609 | 0.3926 |
| joint_m300_c100 | 1.0000 | 0.6016 | 0.4336 | 0.2266 | 0.8359 | 0.1545 | 4.3086 | 0.4512 | 0.3809 |
| joint_m300_c300 | 1.0000 | 0.6016 | 0.3555 | 0.2734 | 0.8359 | 0.2614 | 5.5911 | 0.3887 | 0.3105 |
| joint_m1000_c300 | 0.7461 | 0.3086 | 0.2539 | 0.1797 | 0.8066 | 0.5287 | 5.7465 | 0.2051 | 0.0996 |
| joint_shuffle_m300_c300 | 0.9688 | 0.4844 | 0.3555 | 0.1602 | 0.8359 | 0.3641 | 7.0914 | 0.3730 | 0.2949 |

## Frozen gates

No inferential gates were assigned to this development-only protocol.

## Completeness and interpretation

The exact arm-by-seed grid was complete (26/26 cells).

The model receives complete transition tables and an operator-shaped 8×8 latent channel. An exact table-transpose executor exists. Results therefore test stable learned equivariant table execution, anonymous closure, and coordinate transport under this explicit inductive bias; they do not establish spontaneous Neuralese, abstract operator discovery, language-model generality, or awareness.
