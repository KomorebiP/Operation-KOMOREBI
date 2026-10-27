# Semantic Retraction Probe v0.2.0

Author: Komorebi P.  
Disposition: aborted primary with a separately completed posthoc cross-check  
Primary claim status: **NOT EVALUABLE**

## Executive result

The prospectively frozen primary execution did not produce a valid learned-checkpoint result. The evaluation bank was irrevocably marked spent, the checkpoint-free exact control passed, and the runner then stopped fail closed at the anchor-projector audit in the first frozen census cell (`euclidean_cr`, seed 101). No learned shard or terminal commit was published. Under the frozen protocol, this is an invalid, uninterpretable primary bundle—not a failed semantic-retraction hypothesis.

The separately frozen independent NumPy cross-check did complete. On its previously exposed finite null bank, an oracle-selected cross-fitted prototype reset produced perfect decisions in every tested checkpoint-by-prefix panel. Autonomous selectors were strong but imperfect and seed-dependent. This is useful sensitivity evidence for a resettable semantic interface, but it neither repairs the primary execution nor establishes a universal quotient or architecture-independent Neuralese.

| Component | Status | Permitted interpretation |
| --- | --- | --- |
| Frozen primary learned run | `ABORTED_INVALID_NO_COMMIT` | Procedural evidence only; no primary labels |
| Evaluation bank | `SPENT_NO_PROSPECTIVE_RERUN` | A same-bank rerun would be posthoc |
| Synthetic exact control | PASS | Checkpoint-free plumbing validation only |
| Independent NumPy cross-check | `POSTHOC_SEALED_NULL_BANK_SENSITIVITY` | Finite-bank descriptive sensitivity |
| Projector forensics | `DTYPE_TOLERANCE_FALSE_REJECTION` | Post-spend root-cause diagnosis only |

## Primary execution

The spend firewall behaved as designed. Before the first learned evaluation, it durably published an external receipt and a byte-identical copy inside `RESULTS.bundle`, both with SHA-256:

`65b399852d338569e4775bbbe7177a94094619d8acd70f8c72017e79843f9c01`

The partial bundle contains exactly:

- `EXACT_CONTROL.json`, 34,289,199 bytes, SHA-256 `2d19c60abd07f12cce7a96bfd768c9b246794413b34eb6d995d6c1a24c84d993`;
- `SPEND_RECEIPT.json`, 2,259 bytes, SHA-256 `65b399852d338569e4775bbbe7177a94094619d8acd70f8c72017e79843f9c01`;
- an empty `checkpoints/` directory.

`RUN.json`, `MANIFEST.json`, and `COMMIT.json` are absent. The frozen verifier rejects the directory with `RuntimeError: result bundle has missing or extra root entries`, as expected for an aborted publication. The bundle alone cannot determine how far checkpoint-local computation progressed, only that no complete learned shard was published.

The exact compiled control passed its finite-panel, periodic-closure, firewall, sham-scale, wrong-control, and synthetic-projector audits. Its projector is axis aligned and exactly representable after the float32 cast. That makes it a valid plumbing control, but not a test of the dense learned projector that caused the abort.

## Why the projector audit aborted

The frozen construction computes a rank-eight metric projector in float64, casts it to float32 for model application, then widens the rounded matrix back to float64 for auditing. The implementation calls `numpy.linalg.matrix_rank` on that widened matrix without an explicit tolerance:

\[
P_{32\rightarrow64}=\operatorname{float64}(\operatorname{float32}(P_{64})).
\]

Default rank tolerance therefore uses float64 machine epsilon even though the smallest singular values are float32 quantization noise. For a dense rounded projector, singular values near \(10^{-8}\) are far above the resulting float64 cutoff near \(10^{-15}\), so NumPy counts them as real directions. Native float32 rank or an explicit float32-aware tolerance correctly treats them as numerical zeros.

The protocol requires a post-cast rank check but does not specify its numerical tolerance. The frozen implementation's dtype sequence supplied an inappropriate implicit tolerance. The positive-control projector did not expose this because its four null directions remained exact zeros after casting.

Post-spend parameter-only forensics reproduced the failure across all 12 sealed checkpoints without constructing or using any context, path, continuation, or behavioral bank:

| Diagnostic | Result across 12 checkpoints |
| --- | ---: |
| Frozen widened-matrix default rank | 12 in 12/12 |
| Native float32 default rank | 8 in 12/12 |
| Explicit `max(m,n) * eps32 * sigma1` rank | 8 in 12/12 |
| Ninth singular value | \(1.47\times10^{-8}\) to \(3.00\times10^{-8}\) |
| Trace error from eight | 0 to \(8.94\times10^{-8}\) |
| Maximum idempotence residual | \(1.28\times10^{-8}\) to \(2.15\times10^{-8}\) |
| Maximum anchor-preservation residual | \(1.06\times10^{-8}\) to \(2.00\times10^{-8}\) |
| Maximum metric self-adjointness residual | 0 |
| Every non-rank frozen conjunct | PASS in 12/12 |

This is strong evidence that the abort was a dtype/tolerance false rejection rather than a defective rank-eight anchor plane. It still cannot waive the frozen criterion, create a primary shard, justify a commit, or restore prospective status.

## Independent cross-check

The independent implementation used NumPy only, revalidated the exact source archive, sealed null bank, and all 12 checkpoints, and wrote a complete 22,021,536-byte result with SHA-256:

`c2363561e845cdfe43e9302558f934065623fb246b68d28e3ec35ae4338c9faf`

Its design covers 12 checkpoints, 64 previously exposed null contexts, three identity-word stress prefixes, and all 31 suffixes through length four. Across the resulting 36 checkpoint-by-prefix panels:

| Condition | Task accuracy | All 31 suffixes correct | Native errors rescued | Native-correct cases damaged |
| --- | ---: | ---: | ---: | ---: |
| Native | 567,752/571,392 = 99.3630% | 18,184/18,432 = 98.6545% | — | — |
| Oracle anchor | 99.9664% | 98.9583% | 3,640/3,640 | 192/567,752 |
| Self-decoded anchor | 99.4781% | 98.4701% | 1,156/3,640 | 498/567,752 |
| Nearest-ray anchor | 96.2208% | 96.2185% | 847/3,640 | 18,801/567,752 |
| Cross-fitted oracle prototype | **100%** | **100%** | **3,640/3,640** | **0/567,752** |
| Wrong-anchor factual control | 0.00420% | 0% | 0 | 567,728 |

The wrong-anchor reset predicted its intended counterfactual target at 99.9664% while preserving the factual answer only 24 times in 571,392 decisions. This makes the intervention causally specific to semantic identity on this bank; it is not merely a generic confidence boost.

The native deficit and prototype improvement were uneven across arms:

| Arm | Native accuracy | Native errors | Gain to prototype |
| --- | ---: | ---: | ---: |
| `euclidean_supervised` | 99.7928% | 296 | +0.2072 percentage points |
| `euclidean_cr` | 99.4372% | 804 | +0.5628 percentage points |
| `polar_supervised` | 99.4001% | 857 | +0.5999 percentage points |
| `polar_cr` | 98.8218% | 1,683 | +1.1782 percentage points |

The worst panel was `polar_cr`, seed 307, under `r4_x16`: native accuracy was 89.8627%, self-decoded anchor 91.7969%, nearest-ray anchor 90.8203%, and oracle prototype 100%.

Autonomous selection remains the important gap. The self selector identified the semantic state in 18,342/18,432 split states (99.5117%), but its 90 mistakes propagated through continuations. Nearest-ray selection was materially worse. Moreover, oracle prototype versus self anchor changes both the selector and the section, so the existing result does not isolate which component supplies the prototype advantage.

Perfect task decisions are also not continuous-state equivalence. Prototype-reset and native traces retain nonzero hidden-state angles, centered-logit angles, and total-variation distances. The cross-check establishes finite decision repair, not identical trajectories or a commuting global quotient.

## What this suggests about Neuralese

The strongest surviving idea is not “there is one persistent low-dimensional linear language inside every hidden state.” The prior rank jump from \(q_0=7\) to \(q_{1\ldots4}=12\) and hard-polar angular/projective holonomy already argued against that simple additive picture.

The new sensitivity result points instead toward a semantic control interface with three distinct objects:

1. a semantic readout \(\pi(h)\), which chooses a discrete state;
2. a section \(s(y)\), which chooses a canonical representative or prototype for that state;
3. a reset \(R(h)=s(\pi(h))\), whose usefulness is judged by future behavior.

The oracle prototype result says that, on this finite bank and horizon, suitable representatives exist that erase the tested path-dependent decision errors. The imperfect self selector says those representatives are not yet autonomously accessible. The weak nearest-ray selector says ordinary local angle is not a reliable semantic coordinate. The persistent continuous discrepancies say the hidden fiber is not simply irrelevant noise: different representatives can make the same tested decisions while remaining geometrically distinct.

A useful working model is therefore a nonlinear, possibly multi-chart semantic bundle rather than a single additive quotient. The base is the task state, the fiber contains path/history/gauge information, and a learned section can reset the system to a behaviorally useful representative. This is a hypothesis generator—not a universal conclusion.

## Recommended next block

The next confirmatory study should be a new version with a fresh evaluation bank. Reusing this bank can only produce posthoc sensitivity.

1. Specify projector rank numerics explicitly. Use a preregistered tolerance tied to float32 application semantics, and add dense randomly rotated rank-eight projector tests. Run parameter-only geometry preflight before any fresh evaluation-bank exposure.
2. Cross selector and section in a true factorial design: oracle versus autonomous selector, each paired with anchor versus cross-fitted prototype. The missing autonomous-prototype cell is necessary to locate the bottleneck.
3. Construct prototypes only from a sealed calibration split and evaluate on disjoint fresh contexts and paths. Prevent any label or endpoint leakage.
4. Test beyond identity words: unseen group words, longer horizons, compositions that move the semantic state, and counterfactual resets at multiple times.
5. Separate decision repair from geometric equivalence. Score rescue, damage, full-suffix correctness, idempotence, section consistency, one-step and multi-step commutation, hidden angle, logit angle, and total variation.
6. Use explicit negative controls: wrong semantic prototypes, norm-matched random rays, shuffled decoder labels, and section prototypes from another seed or architecture.
7. Require replication across new checkpoints or architectures before using “Neuralese” as an architecture-independent term.

The decisive near-term question is: **can an autonomous, calibration-only selector plus section reproduce the oracle prototype's zero-damage repair on a fresh bank?** A positive result would support a deployable semantic retraction. A negative result would localize the phenomenon to oracle access rather than semantic state geometry itself.

## Claim boundary

No primary checkpoint or arm label is awarded. The projector forensics is post-spend. The independent cross-check is posthoc and uses a previously exposed finite bank. Nothing here establishes a universal quotient, global bisimulation, architecture-independent Neuralese, or absence of residual holonomy.
