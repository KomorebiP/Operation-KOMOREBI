# Posthoc diagnosis of the retained A15 failure

- Author: `Komorebi P.`
- Status: `POSTHOC_DIAGNOSIS_ONLY`
- Official pilot execution: `PASS`
- Official pilot assay: `FAIL`
- Full developmental claim: `NOT_EVALUATED`

This diagnosis explains the frozen assay failure. It does not alter the
preregistered validator, completion flag, gate decision, or scientific claim.
The canonical pilot was not retried.

## Exact failure

Eleven of the twelve seed-by-arm packet result contracts passed. The only
invalid row was:

| Field | Value |
|---|---|
| Arm | `euclidean_cr` |
| Seed | `211` |
| Captured prefix | `256` |
| Held-out suffix cases | `21,888` |
| Positive promoted-margin cases | `17,802` |
| Correct float32 decode cases | `17,801` |
| Difference | exactly one case |

The frozen A15 validator requires

\[
\text{word-weighted packet membership}
\leq
\text{suffix accuracy}.
\]

The stored values were

\[
\frac{17{,}802}{21{,}888}
=0.8133223684210527
\]

and

\[
\frac{17{,}801}{21{,}888}
=0.8132766812865497,
\]

respectively. The inequality therefore failed by one suffix case.

## Replayed boundary case

The read-only replay located the sole disagreement:

| Field | Value |
|---|---|
| Example index | `22` |
| Suffix index | `157` |
| Word | `[1, 1, 1, 0, 0, 1, 0, 0]` |
| Relation signature | identity |
| Target class | `7` |
| Float32 argmax class | `2` |
| Promoted normalized margin | `9.009520115887284e-09` |

The packet geometry intentionally promotes the float32 hidden state and
decoder weights to float64 before evaluating the normalized class-boundary
margin. The behavioral decoder performs its matrix product and argmax in the
model's native float32 path. In this one near-tie, the promoted computation
placed the target approximately nine-billionths inside the open packet while
the native float32 argmax selected another class.

This is a precision-boundary disagreement, not evidence of missing rows,
incorrect denominators, non-finite output, bank contamination, or a checkpoint
replay discrepancy. Nevertheless, the frozen result contract deliberately
fails closed, so the formal assay remains invalid.

## Protocol consequence

The following retained status is mandatory:

- `completed: false`
- `assay_status: FAIL`
- `full_developmental_claim: NOT_EVALUATED`

The ordinary package verifier is also expected to stop with
`v0.4 pilot did not complete`. A separate failure-aware archival replay may
verify integrity and determinism while permitting only the exact consequences
of this retained invalidation. It must not be described as converting the
assay into a pass.

## Repair for a future preregistration

A later protocol should make geometric membership and behavioral correctness
share an explicit numerical contract before freezing. Defensible options
include:

1. compute both margins and decoding in one registered precision;
2. treat \(|m|\leq\varepsilon\) as an explicit boundary/undefined band; or
3. define packet membership directly from a registered robust class-margin
   threshold that is strictly larger than the numerical error budget.

No such repair is applied retroactively here.
