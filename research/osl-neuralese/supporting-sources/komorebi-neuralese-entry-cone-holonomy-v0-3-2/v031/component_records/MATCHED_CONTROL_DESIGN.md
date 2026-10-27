# Matched Endpoint Controls for Neuralese v0.3.1

## Outcome-blind purpose

The v0.3.0 final-bit toggle changed both the group endpoint and the exposure
profile. This bank separates repeated-relator effects from generic long-path
drift using deterministic words selected without learned-checkpoint outcomes.

No learned checkpoint was loaded or evaluated while constructing this
prototype.

## Structural obstruction

Exact same-length coverage of all eight D4 endpoints is impossible at the
registered budgets 16, 32, and 64. Every defining D4 relation in the R/F
presentation has even length, so word-length parity is invariant. Even words
reach exactly

`e, R2, FR, FR3`,

while odd words reach exactly

`R, R3, F, FR2`.

The frozen primary bank therefore contains all four endpoints that are
actually reachable at exact even length. The other four must not be described
as length matched. A later sensitivity analysis may use paired lengths B-1 and
B+1, whose mean is B, and label this honestly as a parity sandwich.

## Exact deterministic construction

There are 12 reference blocks: four relation templates (`r4`, `f2`, `frfr`,
`rfrf`) crossed with three budgets (16, 32, 64). Each block contains four
same-length controls, one per reachable endpoint. The identity control is
required to differ from the repeated-relator reference.

Controls globally minimize the following lexicographic objective:

1. L1 mismatch in counts of R and F
2. L1 mismatch in directed bigram counts ordered `RR, RF, FR, FF`
3. absolute mismatch in the run-length second moment
   `sum(run_length ** 2)`
4. Hamming distance as a deterministic tie-break
5. binary lexical order as the final deterministic tie-break

The dynamic-program state is

`(position, D4 endpoint, first token, last token, F count, transition count,
current run length, differs from template)`.

The registered references make the run statistic extremal. Constant r4/f2
templates have second moment B squared, so larger partial moments dominate.
Alternating frfr/rfrf templates have second moment B, so smaller partial
moments dominate. This makes the pruning exact rather than heuristic. Direct
enumeration of all length-eight words agrees with the dynamic program for both
reference types and every reachable endpoint.

## Frozen bank and validity gates

The minimal materialized bank has 12 blocks and 48 control words.

- V0: every reference has exact identity D4 action
- V1: every primary control has length exactly B
- V2: every primary block covers exactly `e, R2, FR, FR3`
- V3: every declared endpoint is verified from the full permutation action
- V4: every identity control differs from its reference
- V5: the first three exposure-score coordinates are globally optimal
- V6: byte-for-byte regeneration gives the same canonical content hash
- V7: exhaustive small-word enumeration agrees with dynamic programming
- V8: no learned checkpoint is inspected before the word bank and execution
  source are frozen
- V9: the parity-complement endpoints are either omitted or explicitly marked
  as B-1/B+1 sensitivity conditions

Primary bank content hash (computed over canonical JSON before inserting the
hash field):

`9c521fe6891ff6fd2ed2fad3c3e7496abc90b185b809197dd19706cbf8af12f6`

Materialized JSON file SHA-256:

`c5c393ecfff7c0529913b8a7b53d4f4371ef18ddd373a978207e216656c07ce7`

Construction took 229.91 seconds in the current container. Peak RSS was
120,164 KiB and the largest dynamic-program frontier had 160,836 states.

## Proposed learned execution after preregistration

Use fresh coordinate-resampled episode seeds 940000 and 941000, with eight
episodes per frozen checkpoint. These differ from the v0.3.0 episodes.

For each episode:

- enumerate all 64 base histories of exact depth 6
- enumerate all eight semantic starts, giving 512 base cases
- execute all 12 reference words and their four exact-length controls
- exhaustively enumerate suffixes from horizon 0 through 6, giving 127 suffix
  words per case
- compare each long path with the shortest canonical representative of the
  same D4 endpoint, as well as comparing the repeated identity relator directly
  with the distinct matched identity control

This primary plan contains exactly

`16 * 12 * 5 * 512 * 127 = 62,423,040`

decision instances. Here five paths means one reference plus four exact-length
controls. If all eight B-1/B+1 parity-sandwich paths are added, the full count
becomes

`16 * 12 * 13 * 512 * 127 = 162,299,904`.

The parity sandwich should be secondary because it is not an exact-length
comparison.

## Inference unit and estimands

The decision instances are an exhaustively enumerated conditional population,
not independent samples. The experimental unit is one fresh coordinate episode
nested within a frozen checkpoint seed. Words are fixed experimental
conditions. Checkpoints are also fixed, so the results do not support
population claims about trained models.

Primary estimand:

`failure(reference identity relator) - failure(distinct matched identity word)`

computed within each episode after averaging over relation blocks, base
histories, starts, and suffixes. Report the effect separately for each
checkpoint. Use the exact 2^8 episode-level sign-flip distribution within each
checkpoint. A pooled 16-episode sign-flip analysis may be reported only as a
sensitivity analysis. Do not treat cases, suffixes, words, or logits as
replicates.

Secondary estimands include margin loss and ray displacement relative to the
short canonical representative at each endpoint. Blockwise relation/budget
contrasts are descriptive, or multiplicity controlled with Holm correction if
inferential labels are used.

An endpoint-stratified random word bank can be frozen as secondary calibration,
but it does not replace clustered paired inference and must never be selected
using learned outcomes.

## Interpretation matrix

| Repeated relator vs matched identity | Nonidentity controls | Conclusion |
|---|---|---|
| Worse | Stable | Relation-specific holonomy |
| Similar | Unstable | Generic accumulated projective drift |
| Worse | Unstable | Mixed generic drift and relation-specific excess |
| Similar | Stable | No registered hard-path excess at tested depths |

Soft ray or logit differences remain evidence of path dependence, not by
themselves evidence of hard semantic failure.
