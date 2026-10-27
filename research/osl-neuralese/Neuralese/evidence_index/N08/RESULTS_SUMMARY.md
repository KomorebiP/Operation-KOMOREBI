# Neuralese Entry–Cone–Holonomy Results v0.3.2

**Author:** Komorebi P.  
**Registered result:** `REGISTERED_EXECUTION_COMPLETE`  
**Scientific class:** prospectively frozen adaptive developmental diagnostic

## Executive result

The experiment completed across two frozen checkpoints and sixteen coordinate
episodes with **109,035,136 primary decision-equivalents**. Every integrity
gate passed.

The factorization is clean:

| Component | Registered observation | Interpretation |
|---|---:|---|
| Native entry | 8 errors in 65,408 decisions; all at suffix depth 0 | A finite, checkpoint-0 entry-coordinate defect |
| Incoming `R` reanchor | 65,408 / 65,408 correct | Repairs all 8 errors, introduces none |
| Incoming `F` reanchor | 65,408 / 65,408 correct | Distinct uniform repair, same hard signatures as `R` |
| Observed recurrent cone | 33,358,080 / 33,358,080 correct | All 65,280 observed states survive every suffix through `H=8` |
| Long identity loops | 76 / 1,344 configurations exit | Angular holonomy accumulates, with delayed hard exits/reveals |
| Matched deterministic bank | `X1`, `X2`, `X3` true; `X0`, `X4` false | Relation-sensitive finite pattern, not a population law |

This rules out the simplest story that the long-depth failure is only the
native entry bug. It also rules out a purely radial explanation: normalization
does not remove the measured ray-angle drift or the hard boundary crossings.

## Decision accounting

| Module | Decisions |
|---|---:|
| Entry and semantic decoys | 327,040 |
| Finite observed-state cones | 33,358,080 |
| Repeated relation words | 43,954,176 |
| Matched word paths | 31,395,840 |
| **Primary total** | **109,035,136** |

The additional 6,279,168 reference/identity comparisons reuse registered path
decisions and are not added to the primary total.

## 1. Entry localization

The native scheme made exactly eight errors, one in each coordinate episode of
checkpoint 0. Every error was semantic state 2 predicted as 6 at the empty
suffix. Checkpoint 1 made no native-entry error.

Both incoming routes repaired every error and remained perfect through `H=8`:

| Route | Errors | Minimum target margin |
|---|---:|---:|
| Native anchor | 8 | -0.7840077106 |
| Incoming `R` | 0 | 2.7800288350 |
| Incoming `F` | 0 | 2.8019629303 |

The incoming routes have zero hard-signature differences but are not identical
soft states: their maximum positive-ray angle is 0.0688672820 radians, maximum
centered-logit difference is 0.1958385983, and maximum probability difference
is 0.0077577407.

The wrong-semantic decoy intervention is specific: all 130,816 decisions follow
the actual `(q+1) mod 8` incoming semantic state, and zero follow the declared
`q` label.

## 2. Finite observed-state cones

The assay enumerated every binary history of lengths 1 through 8, crossed with
eight visible starts and sixteen episodes: 65,280 recurrent states. Every state
remained hard-correct under all 511 suffixes through `H=8`.

- Global minimum angular clearance: **0.1934043264 radians**
  (approximately **11.081°**).
- Global minimum target margin: **2.3741424752**.
- Weakest angular facet: checkpoint 1, episode 3, history `1111111`, start 7,
  suffix `11111100`; target and prediction 5.
- Direct full-word and recursive one-step cone audits agree exactly.

This is a robust finite observed-state result. It is not a proof of ambient,
infinite-horizon, or quotient-level invariant-cone closure.

## 3. Long identity-loop exits

All 1,024 registered base cases were initially eligible through `H=8`.
Nevertheless, repeated words with identity D4 semantics created 76 fresh exit
configurations, spanning 8 of 16 episodes and 10 of 64 episode–relation
trajectories.

| Checkpoint / episode | Relation | First repeat | Tokens | Failing / revealing cases |
|---|---:|---:|---:|---:|
| 0 / 0 | `F²` | 21 | 42 | 1 / 1 |
| 0 / 1 | `F²` | 31 | 62 | 1 / 1 |
| 0 / 4 | `F²` | 30 | 60 | 10 / 10 |
| 0 / 7 | `F²` | 27 | 54 | 1 / 1 |
| 1 / 0 | `R⁴` | 14 | 56 | 1 / 1 |
| 1 / 0 | `FRFR` | 10 | 40 | 16 / 16 |
| 1 / 0 | `RFRF` | 10 | 40 | 16 / 16 |
| 1 / 1 | `F²` | 21 | 42 | 1 / 1 |
| 1 / 3 | `F²` | 15 | 30 | 6 / 6 |
| 1 / 6 | `F²` | 27 | 54 | 3 / 3 |

Every onset persisted through the registered maximum. Configuration counts are
`F²=59`, `R⁴=3`, `FRFR=7`, and `RFRF=7`. Every exit configuration contains at
least one delayed reveal; ten also contain a depth-zero reveal.

`H2` is **stratum-level**, not episode-universal. Only `F²` repeats 27–32
(54–64 inserted tokens) exit somewhere in all four checkpoint × episode-half
strata. At budget 64, `F²` exits in 7 of 16 episodes, not all 16.

The maximum loop-versus-baseline ray angle is 1.1812034274 radians. Grouped
products and token-by-token products agree within 1.4135589648e-14, excluding a
product-grouping implementation artifact at the measured tolerance.

All 64 primitive episode–relation products have identity semantic action but
remain far from a positive scalar identity: relative Frobenius residuals range
from 0.5314731162 to 0.6153272637. Their spectral class is neither necessary nor
sufficient for finite exit. These spectra describe candidate ambient
projective mechanisms; they are not causal-quotient certificates.

## 4. Matched deterministic panel

All matching preconditions passed. The frozen bank contains 12 references and
48 exact-length controls: 60 condition aliases but 54 distinct words. Six
aliases reuse another word, and the 12 directed identity comparisons represent
only nine unique unordered pairs.

Registered severity is lexicographic descending in:

1. failing base-case count;
2. revealing base-case count;
3. negative minimum target margin.

Strict-error count and angular clearance are not severity components.

| Predicate | Result | Supporting relation–budget cells |
|---|---|---|
| `X0`: same nonidentity control exceeds reference in both checkpoints | False | None |
| `X1`: reference/identity hard signatures differ in both checkpoints | True | `F²/B64` |
| `X2`: relator reference exceeds its identity control in both checkpoints | True | `F²/B16,B32,B64`; `R⁴/B32,B64`; `FRFR/B16,B32` |
| `X3`: reference exceeds all three nonidentity controls in both checkpoints | True | `F²/B16,B32,B64`; `FRFR/B16,B32`; `RFRF/B16,B32` |
| `X4`: `X0 and (X2 or X3)` | False | False because `X0` is false |

Only `F²/B64` has a replicated hard reference/identity disagreement:
1,774 / 261,632 decisions in checkpoint 0 and 1,013 / 261,632 in checkpoint 1.
Many `X2` and `X3` cells are supported only by the registered minimum-margin
tie-break, not excess hard failures.

`X0=false` does not mean a control never exceeds its reference in one
checkpoint. Such one-sided cells occur, but none repeats for the same relation,
budget, and nonidentity endpoint in the other checkpoint; every one-sided
exceedance is margin-only.

The controls are exact-length and globally best under the frozen score, but not
fully feature-matched: 12 / 48 exactly match generator counts, 0 / 48 directed
bigram counts, 6 / 48 run-second-moment, and 0 / 48 all three. Moreover,
`R²`, `FR`, and `FR³` cross semantic endpoints. Their contrasts cannot by
themselves isolate word-path effects from endpoint or decoder-facet difficulty.

## Scientific interpretation

Within these two frozen systems, the evidence supports:

> A locally repairable entry-coordinate defect, followed by a robust finite
> observed-state cone, coexists with accumulating path-dependent angular
> holonomy and delayed hard exits/reveals under nominal semantic identity loops.

That is a stronger and more precise result than “the norm explodes.” It remains
a finite ambient-state diagnosis, not evidence that a minimal causal quotient
has been identified or that the phenomenon generalizes across models,
architectures, or task families.

See `V032_CLAIM_BOUNDARY.md` for the full boundary and `V032_NEXT_BLOCK.md` for
the next experimental sequence.
