# Posthoc descriptive analysis

This analysis was computed after the frozen gate evaluation. It is descriptive,
not a replacement for the preregistered decision rule. Intervals are percentile
bootstrap intervals over ten matched optimization seeds using deterministic
bootstrap seed 20260902.

## Primary arm uncertainty

| Metric | Mean | Seed SD | 95% bootstrap interval for mean |
|---|---:|---:|---:|
| D4 depth 8 | 0.9879 | 0.0242 | [0.9699, 1.0000] |
| D4 depth 32 | 0.9375 | 0.1241 | [0.8457, 1.0000] |
| D4 depth 64 | 0.8660 | 0.1714 | [0.7449, 0.9590] |
| D4 depth 128 | 0.6105 | 0.1138 | [0.5395, 0.6801] |
| C8 depth 64 | 0.7203 | 0.2406 | [0.5621, 0.8582] |
| Random-permutation depth 64 | 0.2273 | 0.0654 | [0.1844, 0.2648] |
| P95 isometry defect | 0.2128 | 0.0881 | [0.1661, 0.2764] |
| Median depth-128 endpoint G-ratio | 0.001281 | 0.002079 | [0.000401, 0.002721] |

## Matched arm contrasts

| Contrast | Mean difference | Positive pairs | 95% bootstrap interval |
|---|---:|---:|---:|
| Joint − shuffled, D4 depth 64 | +0.2582 | 9/10 | [0.1648, 0.3457] |
| Joint − shuffled, D4 depth 128 | +0.2234 | 9/10 | [0.1418, 0.2957] |
| Joint − shuffled, C8 depth 64 | +0.4125 | 10/10 | [0.2859, 0.5258] |
| Joint − terminal, D4 depth 128 | +0.3383 | 10/10 | [0.2602, 0.4133] |
| Joint − relation, D4 depth 128 | +0.0184 | 6/10 | [-0.0750, 0.1258] |
| Shuffled − joint, closure residual | +0.1222 | 10/10 | [0.1045, 0.1465] |

No multiplicity-adjusted hypothesis tests were added posthoc. The prospectively
frozen conjunctive result remains a failure because six gates failed.

## Transport contrasts

Across five seed pairs, affine transport accuracy was 0.9848
([0.9668, 1.0000]), compared with 0.1406 for shuffled-pair fitting and 0.0809
for a norm-matched random map. Decode-to-label then target re-embedding achieved
0.9922 and equaled or exceeded affine transport in every pair. The paired affine
minus decode–re-embed difference was -0.0074 with bootstrap interval
[-0.0160, 0.0000].
