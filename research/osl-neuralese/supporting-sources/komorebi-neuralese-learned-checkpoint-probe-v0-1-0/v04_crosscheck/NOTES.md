# Neuralese v0.4 frozen-checkpoint cross-check

- Author: `Komorebi P.`
- Status: completed read-only independent NumPy cross-check
- Checkpoints: all 12 sealed v0.4 pilot checkpoints
- Training: none
- Archive mutation: none

## Outcome

The 12 checkpoints give the same finite-horizon rank result in every one of
the 32 sealed Feshbach contexts at relative SVD tolerance `1e-6`:

| Horizon | Reachable rank | Observable rank | Reachable quotient rank | Reachable null dimension |
|---:|---:|---:|---:|---:|
| 0 | 8 | 7 | 7 | 1 |
| 1 | 12 | 12 | 12 | 0 |
| 2 | 12 | 12 | 12 | 0 |
| 3 | 12 | 12 | 12 | 0 |
| 4 | 12 | 12 | 12 | 0 |

The local oriented-ray tangent calculation is equally uniform over every
checkpoint, context, and one of the eight learned state anchors. The rank is
`7/11` at horizon zero and `11/11` from horizon one through four.

The learned anchor plane has rank eight and its Euclidean complement has
dimension four. In every checkpoint and context:

- the centered decoder sees the anchor plane with rank seven;
- the centered decoder sees the complement with rank four;
- one controlled step reaches all four complement directions from the anchor
  plane; and
- the two complement-to-anchor generator channels jointly span rank eight.

Therefore, the four-dimensional ambient complement is not a fixed null or
nuisance fiber. The only horizon-zero reachable null direction is delayed
observable and disappears under the combined controlled horizon-one observer.
This supports a quotient ladder interpretation and rejects a nonzero exact
linear, centered-logit-null `P/Q` nuisance fiber for these checkpoints. It does
not rule out directions neutral under coarser argmax behavior. Here, "one step
reaches all four complement directions" refers to the joint linear span over
both generators and arbitrary vectors in the anchor plane, not to each
discrete anchor/operator pair separately.

## Direct D4 loop decomposition

Each row below uses all `64 contexts × 8 starts = 512` points in the sealed
null bank. `|κ| p90` is the largest 90th percentile absolute log radial gain
among `r4`, `f2`, and `frfr`. Angles are median oriented positive-ray angles
after 16 repetitions. Accuracy is exhaustive current-label endpoint accuracy
on this crossed bank, not the pilot's held-out conditional-retention
estimator. In particular, `euclidean_supervised` seed 101 has baseline anchor
accuracy `0.875`, so a post-loop accuracy of `1.0` can be an improvement rather
than perfect baseline/loop retention.

| Arm | Seed | `|κ| p90`, repeat 1 | `|κ| p90`, repeat 16 | `r4` angle / acc | `f2` angle / acc | `frfr` angle / acc |
|---|---:|---:|---:|---:|---:|---:|
| euclidean_supervised | 101 | 4.05923 | 63.2374 | 1.06500 / 1.0000 | 1.01684 / 1.0000 | 1.07129 / 0.9941 |
| euclidean_supervised | 211 | 3.56064 | 55.2276 | 0.95228 / 1.0000 | 0.86922 / 1.0000 | 0.96496 / 0.9980 |
| euclidean_supervised | 307 | 4.07033 | 63.9795 | 0.94089 / 1.0000 | 0.90166 / 1.0000 | 0.93404 / 1.0000 |
| euclidean_cr | 101 | 3.91679 | 62.7887 | 0.94049 / 0.9863 | 0.86878 / 1.0000 | 0.92870 / 0.9824 |
| euclidean_cr | 211 | 3.39653 | 54.1474 | 0.73530 / 0.9941 | 0.62379 / 1.0000 | 0.72034 / 1.0000 |
| euclidean_cr | 307 | 3.92587 | 62.2878 | 0.79222 / 1.0000 | 0.72998 / 1.0000 | 0.79481 / 0.9980 |
| polar_supervised | 101 | 7.81e-8 | 1.33e-6 | 0.51989 / 0.9961 | 0.41681 / 1.0000 | 0.48267 / 1.0000 |
| polar_supervised | 211 | 8.47e-8 | 1.35e-6 | 0.69149 / 0.9609 | 0.48168 / 1.0000 | 0.50541 / 1.0000 |
| polar_supervised | 307 | 8.65e-8 | 1.32e-6 | 0.43010 / 1.0000 | 0.34726 / 1.0000 | 0.42971 / 1.0000 |
| polar_cr | 101 | 8.78e-8 | 1.35e-6 | 0.44543 / 1.0000 | 0.33696 / 1.0000 | 0.47880 / 0.9961 |
| polar_cr | 211 | 8.03e-8 | 1.40e-6 | 0.52712 / 1.0000 | 0.30921 / 1.0000 | 0.43628 / 1.0000 |
| polar_cr | 307 | 9.17e-8 | 1.55e-6 | 0.79511 / 0.9180 | 0.37210 / 1.0000 | 0.56290 / 1.0000 |

The Euclidean arms show strong radial contraction. Their median signed
log-gain ranges from approximately `-1.64` to `-2.00` for one `f2` loop and
from `-3.32` to `-3.99` for one `r4` or `frfr` loop. At repeat 16 those
medians reach approximately `-26.85` to `-31.85` and `-53.73` to `-63.63`.
This scale is removed by the positive-ray recurrence.

Hard polar retraction reduces radial accumulation to floating-point noise,
but nonzero angular holonomy remains and grows across repeated null loops.
The clearest separation is `polar_cr`, seed 307, `r4 × 16`: absolute radial
log-gain has 90th percentile `1.55e-6`, while the median angle is `0.7951`
radians and endpoint accuracy falls to `0.9180`. The residual failure is thus
angular/projective rather than radial.

The NumPy retraction is not bitwise identical to the source PyTorch SVD. A
source-runtime spot replay of that cell gave p90 absolute log-gain about
`1.10e-5` rather than `1.55e-6`, while reproducing the angle (`0.79497` versus
`0.79511`) and accuracy exactly. Both radial values are retraction-scale
numerical error and leave the angular diagnosis unchanged.

## Integrity and method

The script regenerates the two exact post-seal banks and verifies every tensor
receipt in `EVAL_BANK.json`. Both banks matched. Their table-byte digests are:

- Feshbach: `1d08ed11e33cf4734c29af0bc42c84a638662e105735ace0fcd932dfb855eb5b`
- Null: `f634413d5e470f176261e9e7a9cb5acfbf29e14c288154861211bee45d8fa0b7`

Every checkpoint SHA-256 is checked against `CHECKPOINT_SEAL.json`. The
restricted reader permits only inert tensor descriptors, storage tags, and
`OrderedDict`. It does not import PyTorch or execute arbitrary checkpoint
globals. The learned table encoder is evaluated in float32. Rank and geometric
diagnostics are accumulated in float64. NumPy SVD supplies the hard-polar
factor, so last-bit values need not be identical to a PyTorch replay, but the
observed separations are many orders of magnitude larger than this numerical
boundary.

The five state-dict tensors in every official v0.4 checkpoint are:

| Key | Shape |
|---|---:|
| `metric_log_diagonal` | `(12,)` |
| `metric_strict_lower` | `(66,)` |
| `state_embedding.weight` | `(8, 12)` |
| `operator_encoder.weight` | `(144, 64)` |
| `decoder.weight` | `(8, 12)` |

Both metric tensors are exactly zero in all 12 checkpoints, as required by
the fixed Euclidean pilot arms.

## Reproduction

```bash
python /workspace/scratch/e8fe53ed30d5/learned_checkpoint_probe_v0.1.0/v04_crosscheck/probe_v04.py --root /workspace/scratch/e8fe53ed30d5/learned_archive_retry/extracted_v04/Komorebi_Neuralese_Packet_Closure_v0.4.0 --output /workspace/scratch/e8fe53ed30d5/learned_checkpoint_probe_v0.1.0/v04_crosscheck/RESULTS.json
```

Expected terminal receipt:

```json
{"bank_checks_pass": true, "checkpoint_count": 12, "status": "PASS"}
```

The full JSON retains every per-context horizon rank, every per-anchor tangent
rank, every P/Q rank, every per-context loop summary, checkpoint metadata,
state-dict geometry, hash receipt, and bank digest comparison.

## Claim boundary

This is a posthoc frozen-checkpoint mechanism probe in an explicit finite D4
table task. It is evidence about these learned operators and their reachable
positive-ray dynamics. It cannot repair the original retained
`A15_packet_result_contract` assay failure or alter its registered claim
status. It does not establish an infinite quotient, architecture-independent
emergence, spontaneous Neuralese, or awareness.
