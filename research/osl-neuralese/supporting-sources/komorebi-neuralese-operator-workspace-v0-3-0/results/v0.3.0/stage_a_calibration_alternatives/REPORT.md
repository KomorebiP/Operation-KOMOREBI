# V0.3 hard-stable recurrent operator report

**Protocol:** `komorebi-v0.3-stage-a-strict-path-alternatives-2026-09-02`  
**Analysis status:** `development_only_architecture_selection_test_unopened`  
**Coordinate split:** `dev`

## Arm summary

| Arm | D4 d8 | D4 d64 | D4 d128 | C8 d64 | D4 norm d2048 | Composition substitution | Sequential/direct | Closure residual | Context patch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hard_relation | 0.9668 | 0.3457 | 0.2441 | 0.2637 | — | 0.8477 | 0.6045 | 1.1652 | 0.2246 |
| hard_composition_060 | 0.7988 | 0.3340 | 0.2090 | 0.1953 | — | 0.8379 | 0.5742 | 1.1310 | 0.1777 |
| hard_learned_diagonal_metric | 0.8574 | 0.3086 | 0.2051 | 0.2051 | — | 0.8438 | 0.5889 | 1.1700 | 0.2266 |

## Split-conditioned final-action assay

| Arm | Depth | Endpoint accuracy | Candidate acceptance rate |
|---|---:|---:|---:|
| hard_relation | 8 | 0.9727 | 0.1883 |
| hard_relation | 64 | 0.4258 | 0.2034 |
| hard_relation | 128 | 0.1523 | 0.1831 |
| hard_composition_060 | 8 | 0.7773 | 0.1883 |
| hard_composition_060 | 64 | 0.4414 | 0.2034 |
| hard_composition_060 | 128 | 0.2266 | 0.1831 |
| hard_learned_diagonal_metric | 8 | 0.8438 | 0.1883 |
| hard_learned_diagonal_metric | 64 | 0.2695 | 0.2034 |
| hard_learned_diagonal_metric | 128 | 0.1836 | 0.1831 |

Every scored word in this assay has both its primitive maps and its full composite finite-state action in the requested dev/test hash partition. This is split-conditioned final-action evaluation; it does not establish that the abstract group element or word-equivalence class is globally novel.

## Frozen gates

No inferential gates were assigned to this development-only protocol.

## Completeness and interpretation

The exact arm-by-seed grid was complete (6/6 cells).
The parameter-free exact table oracle passed its fail-closed orientation, closure, and stability checks.

Training confines every nonempty contiguous subword action to the train map partition. The model receives complete transition tables and an operator-shaped 8×8 latent channel, and an exact table-transpose executor exists. Results therefore test learned table execution, anonymous closure, and coordinate transport under this explicit inductive bias. Exact norm preservation and orthogonality in the hard arm are architectural integrity properties, not learned discoveries. The assay does not establish spontaneous Neuralese, a learned invariant metric, globally novel group elements, language-model generality, or awareness.
