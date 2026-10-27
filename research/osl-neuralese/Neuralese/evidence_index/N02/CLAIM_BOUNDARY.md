# Claim boundary

## Strongest supported claim

> In a randomly re-coordinatized finite operator task, positive-ray gauge fixing during terminal-only training produced a compact recurrent state with finite norms, causal state and operator semantics, long-depth structured-family generalization, and behavior-preserving cross-seed transport. An exact semantic-chart construction demonstrated bounded arbitrary-depth closure for the same task.

## Evidence behind that claim

- The model is bias-free and positively homogeneous, so positive hidden-state scale is an exact future-behavior gauge.
- Float64 raw and per-step-normalized replays of the same frozen model agreed on every comparable prediction through depth 256.
- A finite-horizon observability audit found no fixed nonzero additive future-null subspace. The natural quotient is projective, not a forced linear `P/Q` deletion.
- The exact table action `B P B^-1` and its canonical semantic-chart form passed all tested depths, families, causal replacements, null cycles, and cross-seed transport checks.
- Two newly trained terminal-only projective models passed all 14 developmental gates and greatly exceeded their paired raw parents at long depth.

## What is not supported

The package does not establish:

- spontaneous Neuralese in an unconstrained architecture
- asymptotically unbounded learned recurrence
- an exact ambient group representation in the trained projective model
- projective path flatness or zero hidden holonomy
- universal generalization to arbitrary operator pairs
- architecture-independent emergence
- the internal mechanism of any proprietary or frontier language model
- autonomous recursive self-improvement
- subjective experience, awareness, or consciousness

## Critical distinctions

`normalized_raw` is a gauge-fixed replay of old weights. It prevents overflow but cannot repair angular error.

`projective_terminal` is freshly trained with normalized recurrence and terminal labels only. It is the principal learned result, but normalization is still an architectural inductive bias.

`anchor_closed` and `semantic_chart_closed` use the exposed operator table and all learned state anchors to realize exact transport. They are constructive engineering controls. Their success proves existence and localizes error; it is not evidence that terminal training found the exact compiler unaided.

The projective pilot gates were frozen after an initial two-seed development screen. Passing them supports a developmental mechanism result, not an outcome-independent confirmatory claim.
