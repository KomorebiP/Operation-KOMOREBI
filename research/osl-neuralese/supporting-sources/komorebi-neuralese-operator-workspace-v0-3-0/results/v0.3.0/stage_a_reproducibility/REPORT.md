# V0.3 hard-stable recurrent operator report

**Protocol:** `komorebi-v0.3-stage-a-strict-path-primary-v3-2026-09-02-posthoc-replay-hard_correct-seed-300`  
**Analysis status:** `posthoc_single_cell_bitwise_reproducibility_replay`  
**Coordinate split:** `test`

## Arm summary

| Arm | D4 d8 | D4 d64 | D4 d128 | C8 d64 | D4 norm d2048 | Composition substitution | Sequential/direct | Closure residual | Context patch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hard_correct | 1.0000 | 0.8906 | 0.6289 | 0.8008 | 1.0000 | 0.8564 | 0.5996 | 1.1783 | 0.2305 |

## Split-conditioned final-action assay

| Arm | Depth | Endpoint accuracy | Candidate acceptance rate |
|---|---:|---:|---:|
| hard_correct | 8 | 1.0000 | 0.1491 |
| hard_correct | 64 | 0.9141 | 0.1523 |
| hard_correct | 128 | 0.6367 | 0.1477 |

Every scored word in this assay has both its primitive maps and its full composite finite-state action in the requested dev/test hash partition. This is split-conditioned final-action evaluation; it does not establish that the abstract group element or word-equivalence class is globally novel.

## Frozen gates

No inferential gates were assigned to this development-only protocol.

## Completeness and interpretation

The exact arm-by-seed grid was complete (1/1 cells).
The parameter-free exact table oracle was not run or failed its fail-closed orientation, closure, and stability checks.

Training confines every nonempty contiguous subword action to the train map partition. The model receives complete transition tables and an operator-shaped 8×8 latent channel, and an exact table-transpose executor exists. Results therefore test learned table execution, anonymous closure, and coordinate transport under this explicit inductive bias. Exact norm preservation and orthogonality in the hard arm are architectural integrity properties, not learned discoveries. The assay does not establish spontaneous Neuralese, a learned invariant metric, globally novel group elements, language-model generality, or awareness.
