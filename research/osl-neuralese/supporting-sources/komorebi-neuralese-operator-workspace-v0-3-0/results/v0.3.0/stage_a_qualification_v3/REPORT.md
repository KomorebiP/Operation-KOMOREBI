# V0.3 hard-stable recurrent operator report

**Protocol:** `komorebi-v0.3-stage-a-strict-path-qualification-v3-2026-09-02`  
**Analysis status:** `development_qualification_pretest_noninferential`  
**Coordinate split:** `dev`

## Arm summary

| Arm | D4 d8 | D4 d64 | D4 d128 | C8 d64 | D4 norm d2048 | Composition substitution | Sequential/direct | Closure residual | Context patch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hard_correct | 0.9473 | 0.4688 | 0.2930 | 0.3682 | 1.0000 | 0.8652 | 0.5962 | 1.1651 | 0.2178 |
| hard_shuffled | 0.9248 | 0.2090 | 0.1582 | 0.1338 | 1.0000 | 0.8711 | 0.5981 | 1.1845 | 0.2100 |
| soft_correct | 1.0000 | 0.9189 | 0.5693 | 0.8418 | 0.0000 | 0.8877 | 0.6636 | 0.8579 | 0.4111 |
| soft_shuffled | 0.9658 | 0.1533 | 0.1191 | 0.1416 | 0.0000 | 0.8882 | 0.6606 | 0.9231 | 0.2930 |

## Split-conditioned final-action assay

| Arm | Depth | Endpoint accuracy | Candidate acceptance rate |
|---|---:|---:|---:|
| hard_correct | 8 | 0.9414 | 0.1856 |
| hard_correct | 64 | 0.4043 | 0.1913 |
| hard_correct | 128 | 0.2832 | 0.1940 |
| hard_shuffled | 8 | 0.8613 | 0.1856 |
| hard_shuffled | 64 | 0.2285 | 0.1913 |
| hard_shuffled | 128 | 0.1543 | 0.1940 |
| soft_correct | 8 | 1.0000 | 0.1856 |
| soft_correct | 64 | 0.9023 | 0.1913 |
| soft_correct | 128 | 0.5352 | 0.1940 |
| soft_shuffled | 8 | 0.9355 | 0.1856 |
| soft_shuffled | 64 | 0.0645 | 0.1913 |
| soft_shuffled | 128 | 0.0918 | 0.1940 |

Every scored word in this assay has both its primitive maps and its full composite finite-state action in the requested dev/test hash partition. This is split-conditioned final-action evaluation; it does not establish that the abstract group element or word-equivalence class is globally novel.

## Frozen gates

| Gate | Status | Mean | Mean criterion | Seed pass fraction | Required fraction |
|---|---|---:|---|---:|---:|
| `Q1_hard_d4_depth8` | **PASS** | 0.9473 | >= 0.85 | 1.0000 | 0.7500 |
| `Q1b_hard_split_conditioned_d4_depth8` | **PASS** | 0.9414 | >= 0.85 | 1.0000 | 0.7500 |
| `Q2_hard_depth2048_finite` | **PASS** | 1.0000 | >= 1.0 | 1.0000 | 1.0000 |
| `Q3_hard_depth2048_endpoint_norm` | **PASS** | 1.0000 | in [0.98, 1.02] | 1.0000 | 1.0000 |
| `Q4_hard_depth2048_minimum_norm` | **PASS** | 1.0000 | >= 0.98 | 1.0000 | 1.0000 |
| `Q5_hard_depth2048_transient` | **PASS** | 1.0001 | <= 1.02 | 1.0000 | 1.0000 |
| `Q6_hard_orthogonality` | **PASS** | 0.0000 | <= 1e-05 | 1.0000 | 1.0000 |
| `Q7_hard_minimum_singular_value` | **PASS** | 1.0000 | >= 0.99999 | 1.0000 | 1.0000 |

## Completeness and interpretation

The exact arm-by-seed grid was complete (16/16 cells).
The parameter-free exact table oracle passed its fail-closed orientation, closure, and stability checks.

Training confines every nonempty contiguous subword action to the train map partition. The model receives complete transition tables and an operator-shaped 8×8 latent channel, and an exact table-transpose executor exists. Results therefore test learned table execution, anonymous closure, and coordinate transport under this explicit inductive bias. Exact norm preservation and orthogonality in the hard arm are architectural integrity properties, not learned discoveries. The assay does not establish spontaneous Neuralese, a learned invariant metric, globally novel group elements, language-model generality, or awareness.
