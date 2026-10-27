# Stable-quotient research specification

## Question

Can recurrent operator semantics remain causally valid and transportable at depth after behaviorally irrelevant gauge directions are removed, and which remaining defects prevent path-independent closure?

## Task

Every episode exposes two permutation tables after an independent coordinate conjugation and visible-slot swap. Given start state \(x_0\) and visible word \(w\), the exact target is the composed table action. Training uses D4 words of lengths 1–4. Evaluation extends composition depth and introduces C8, mixed-cycle, and arbitrary independent permutation pairs.

## Mathematical hypotheses

### H1: positive scale is gauge

For the bias-free linear recurrence, \(h\) and \(\alpha h\), \(\alpha>0\), have identical future argmax continuations. Per-step positive normalization must therefore preserve every finite raw prediction.

### H2: the residual failure is projective

If normalized replay stays finite but its accuracy still decays, the remaining error lies in ray direction, anisotropy, or path holonomy rather than radius.

### H3: no additive quotient should be assumed

A decoder-null direction may become visible after later operators. An additive nuisance packet is removable only if it is invariantly unobservable under every continuation; otherwise its Feshbach return memory must be retained.

### H4: exact anchor intertwining closes the finite task

When learned state anchors form a basis \(B\), the table-derived action \(B P B^{-1}\) must execute exactly and preserve \(G=B^{-\mathsf T}B^{-1}\). Its canonical semantic chart must be Euclidean and well conditioned.

### H5: projective training should improve deep reuse

Training the operator encoder through normalized recurrence should prevent cross-entropy from purchasing margin with radial amplification and should improve long-depth accuracy without named relations or intermediate targets.

### H6: behavioral closure is weaker than geometric flatness

Null-cycle answer agreement can remain high while hidden rays drift. Both exact endpoint behavior and projective angle must be reported.

## Arms

| Arm | Role |
|---|---|
| `raw` | Historical learned recurrence |
| `normalized_raw` | Exact radial-gauge control |
| `metric_polar` | Tests whether isometry alone repairs semantics |
| `anchor_closed` | Exact table transport in learned anchor coordinates |
| `semantic_chart_closed` | Same exact action in canonical Euclidean coordinates |
| `projective_terminal` | Fresh terminal-only learned recurrence on positive rays |

## Required evidence

- accuracy across depth and operator family
- finite-state and norm diagnostics
- float64 raw/projective prediction equivalence
- future observability rank
- ordinary and scale-quotiented anchor defects
- isometric and conformal metric defects
- null-cycle behavioral return and projective angle
- causal state transplantation and operator replacement with matched controls
- cross-seed continuation transport and random-map control
- exact backward-error checks for the engineered closure

## Adjudication

- Bounded norm with low accuracy means numerical stability without semantic stability.
- Correct null-cycle answers with nonzero ray angles mean behavioral closure without geometric flatness.
- Exact semantic-chart success means the task is constructively solvable, not that the learned encoder discovered the construction.
- Strong D4/C8/mixed performance with weak arbitrary-permutation performance means family-level reuse, not universal operator induction.
- Cross-seed transport is meaningful only when compared with native target performance and matched random alignment.

## Next confirmatory experiment

Freeze fresh seeds and a held-out cycle bank before outcomes. Compare terminal-only projective recurrence with a preregistered anonymous-intertwining arm. The primary endpoint should combine depth-512 continuation accuracy with continuation-conditioned projective holonomy. Structural supervision must be labeled explicitly and must not use canonical generator names, family labels, conjugations, or intermediate teacher states.
