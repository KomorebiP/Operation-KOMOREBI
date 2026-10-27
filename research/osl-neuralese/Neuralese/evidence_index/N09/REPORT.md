# Learned-checkpoint causal-completion probe

Author: Komorebi P.  
Version: 0.1.0  
Analysis status: posthoc mechanism audit

## Bottom line

The frozen v0.4 checkpoints do not support a persistent compact additive
latent quotient of dimension eight or less. At the immediate readout, the
eight learned state anchors span eight directions but their centered logits
see only seven. After one controlled operator step, however, the reachable and
observable behavioral rank is the full ambient dimension of twelve. This
`7 -> 12` ladder occurs in all twelve official checkpoints and every tested
context.

The long-loop defect is also not merely radial. The raw Euclidean arms have
large radial contraction as well as angular error. In the hard-polar arms,
radial accumulation is reduced to numerical scale while angular drift remains
and grows under repeated D4 identity loops. The cleanest interpretation is
angular/projective holonomy in a fully causally observable learned state, not
an exact flat group action on a compact linear quotient.

These conclusions concern the sealed models in this finite D4 table task.
They do not establish architecture-independent Neuralese, spontaneous
emergence, an infinite quotient, or awareness.

## What was tested

The primary census contains every official v0.4 checkpoint:

| Model arm | Training seeds |
|---|---|
| `euclidean_supervised` | 101, 211, 307 |
| `euclidean_cr` | 101, 211, 307 |
| `polar_supervised` | 101, 211, 307 |
| `polar_cr` | 101, 211, 307 |

No checkpoint was selected by outcome. The probe verifies the source archive
and every checkpoint receipt, loads with `weights_only=True`, performs no
training, and does not mutate the source package.

Two complementary evaluations are retained:

1. `v04_probe/` implements the frozen posthoc protocol on 32 deterministic,
   unique coordinate contexts generated from analysis seed `2026090301`. It
   includes horizon ranks, actual null-direction perturbations, state-resolved
   and output-resolved relation tensors, and an exact compiled control.
2. `v04_crosscheck/` independently reconstructs all checkpoints without
   importing PyTorch, regenerates the sealed Feshbach and null banks, and
   verifies every bank tensor receipt. Its complete result reruns
   byte-identically.

The separate `v03_probe/` analysis is a parallel hard-QR case study, not the
immediate parent of v0.4 and not pooled with the primary result.

## Causal-completion ladder

At relative SVD tolerance `1e-6`, the independent sealed-bank cross-check is
uniform across `12 checkpoints x 32 contexts`:

| Horizon | Reachable rank | Observable rank | Reachable behavioral rank | Reachable-null dimension |
|---:|---:|---:|---:|---:|
| 0 | 8 | 7 | 7 | 1 |
| 1 | 12 | 12 | 12 | 0 |
| 2 | 12 | 12 | 12 | 0 |
| 3 | 12 | 12 | 12 | 0 |
| 4 | 12 | 12 | 12 | 0 |

The oriented-ray tangent calculation gives the same qualitative transition:
rank `7/11` at horizon zero and `11/11` from horizon one onward, for every
checkpoint, context, and anchor.

This resolves an ambiguity in the earlier compactness picture. A direction
that is invisible to the current centered readout is not necessarily a
causally disposable nuisance direction. Here, the sole horizon-zero reachable
null direction becomes visible under the combined controlled horizon-one
observer. The four-dimensional complement of the anchor span is also
centered-decoder-visible and dynamically coupled in every checkpoint and
context. Thus successful discrete decisions after an ablation and exact
equality-sensitive future observability answer different questions.

The direct perturbation assay makes the delayed visibility causal rather than
merely a rank-counting artifact. In the three `polar_cr` seeds, maximum
horizon-zero generator leakage is `0.40527`, `0.25630`, and `0.19239`.
Perturbing that direction by `0.10` changes the current centered-logit ray by
at most `2.11e-8` radians, yet a controlled one-step future ray changes by up
to `0.01725`, `0.01508`, and `0.01051` radians. The `q4=12` conclusion is also
unchanged at every tested relative tolerance from `1e-2` through `1e-6`.

## Radial cocycle versus angular holonomy

The primary probe preserves the checkpoint's actual float32 operator encoding
and polar SVD, then promotes extracted arrays for diagnostics. The table gives
the repeat-16 target-arm result pooled over all relations, prefixes, starts,
and 32 contexts. Agreement compares baseline and loop-inserted predictions
over all eight shortest future D4 continuations.

| Seed | p95 oriented angle | Mean future agreement | Minimum tensor cell | Maximum absolute log-gain |
|---:|---:|---:|---:|---:|
| 101 | 0.72514 | 1.00000 | 1.00000 | `2.90e-5` |
| 211 | 0.72377 | 1.00000 | 1.00000 | `2.00e-5` |
| 307 | 0.97136 | 0.97778 | 0.91016 | `2.22e-5` |

Angles are oriented positive-ray angles in radians; antipodes are not
identified. Even one-loop p95 angles are `0.09982`, `0.07348`, and `0.09402`,
all above the protocol's `0.05` angular-holonomy cutoff. At repeat 16, radial
gain remains under the hard-polar `1e-4` bound while the angular defect grows
and seed 307 loses behavioral congruence in some state/relation cells.

The independent sealed-bank cross-check reaches the same conclusion on 64
contexts crossed with all eight starts. Its clearest single relation is
`polar_cr`, seed 307, `r4 x 16`: median angle `0.7951` radians and exhaustive
current-label endpoint accuracy `0.91797`. That endpoint accuracy is not the
pilot's conditional-retention estimator. A source-PyTorch spot replay agrees
on angle and accuracy; NumPy-versus-PyTorch SVD changes only the retraction-
scale radial residue (`1.55e-6` versus approximately `1.10e-5` at p90).

The Euclidean arms are mixed rather than radial-only. Their median signed
log-gain is approximately `-1.64` to `-2.00` for one `f2` loop and `-3.32` to
`-3.99` for one `r4` or `frfr` loop. At repeat 16 it reaches approximately
`-26.85` to `-31.85` and `-53.73` to `-63.63`, respectively, while substantial
angular error remains after normalization.

An exact anchor-compiled D4 control passes in all twelve learned coordinate
charts: maximum loop angle `2.98e-8` radians, maximum full-ambient relator
spectral residual `2.12e-14`, unit behavioral congruence, and unit oracle-
decoder joint correctness.

## Independent v0.3 bridge

The v0.3 hard-QR audit covers all 12 retained `hard_correct` checkpoints and
all 2,080 eligible held-out coordinate permutations, corresponding to 260
unique ordered visible map pairs with equal multiplicity eight. Every seed has
a full-rank decoder, and the combined horizon-one contrast observer
`[C; C M_r; C M_f]` has full rank eight in every context.

After 16 identity-loop repetitions, mean per-seed endpoint accuracy is
`0.3732` for `r4`, `0.3669` for `f2`, and `0.3418` for `frfr`; corresponding
mean per-seed median angles are `1.2702`, `1.2509`, and `1.3187` radians. The
maximum absolute log radial gain remains below `1.11e-5`. This independently
reproduces the delayed/full observability and angular-holonomy picture in a
different hard-stable model family.

The v0.3 primary configuration trained under the `metric` regime. Although
relation-loss weights appear in its records, the training code activates that
loss only for the `relation` regime. Its loop result is therefore posthoc
geometry of anonymous-composition-trained hard QR, not a test of an active
relation-loss treatment.

## Interpretation

The results sharpen the Neuralese hypothesis rather than simply confirming or
rejecting it:

- **Unsupported:** a fixed additive `P/Q` split in which four ambient
  directions are causally inert nuisance and an at-most-eight-dimensional
  linear quotient closes the learned dynamics.
- **Supported as a diagnostic description:** learned, table-conditioned
  operator machinery can preserve many task decisions while carrying
  nontrivial internal geometric error.
- **Mechanistic failure mode:** repeated formal identity words accumulate
  angular/projective holonomy. Hard-polar normalization removes radial
  explosion or contraction as an adequate explanation.
- **Still open:** a nonlinear, task-relative, finite decision-packet quotient
  may exist even though the equality-sensitive linear observable quotient is
  twelve-dimensional. This probe did not establish such a quotient.

## Evidence boundary

This analysis is posthoc. The original v0.4 execution pass and retained
`A15_packet_result_contract` assay failure are unchanged; the new calculations
cannot retroactively repair that gate or become confirmatory evidence. The
independent replication unit is the training seed, so all seeds are reported
and no trajectory-level population p-value is used.

For complete definitions and thresholds, see `ANALYSIS_PROTOCOL.md`. Full
machine outputs retain checkpoint hashes, context receipts, per-context rank
ladders, perturbation cases, relation tensors, and positive-control results.
