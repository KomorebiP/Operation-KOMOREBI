# Entry–Recurrence Counterfactual Probe

Version: 0.3.1-draft  
Status: adaptive developmental, frozen-checkpoint follow-up

## Question

The v0.3.0 completion surface found one repeated depth-zero decoding error in
checkpoint seed 0, while every registered ordinary decision after at least one
generator application was correct. This probe distinguishes an entry-chart
defect from a recurrent-code defect without training or changing weights.

For each semantic state `q` and canonical generator `g` in `{R,F}`, define

\[
z_{q,g}=\operatorname{normalize}(M_g a_{g^{-1}q}),
\]

where `a_q` is the stored native anchor and `M_g` is the episode-conditioned
learned operator. Both incoming paths terminate at exact semantic state `q`.

## Frozen endpoints and fresh episodes

The probe reads the two projective checkpoints frozen in v0.3.0. It uses eight
new coordinate-resampled D4 episodes for each checkpoint:

| Checkpoint | Episode RNG seed |
|---|---:|
| 0 | 940000 |
| 1 | 941000 |

These draws are fresh relative to v0.3.0 but remain inside the reconstructed
D4 table-pair training support. They are developmental coordinate resamples,
not held-out task-family evidence.

Every episode enumerates all eight semantic starts and all binary canonical
suffixes at exact depths 0 through 8. There are 511 suffixes per state and
4,088 decisions per initialization scheme per episode. Across three schemes,
eight episodes, and two checkpoints, the registered total is 196,224
decisions.

## Initialization schemes

1. Stored native anchor `a_q`.
2. The R-incoming recurrent representative `z_(q,R)`.
3. The F-incoming recurrent representative `z_(q,F)`.

Uniform reanchoring means replacing all eight anchors simultaneously with one
complete incoming-route table. Both the R table and F table are evaluated. No
best-route selection is permitted.

## Hard and soft interfaces

Hard endpoints are exact argmax correctness, strictly positive target margin,
and equality of breadth-first continuation signatures. For uniform
reanchoring, errors repaired and errors introduced are reported separately.

Soft endpoints are descriptive only: maximum and RMS probability differences,
maximum and RMS centered-logit differences, and oriented positive-ray angles.
There is no soft pass threshold.

The stored anchor is not normalized at suffix depth zero, matching v0.3.0.
Incoming recurrent states are normalized by construction. Every positive-depth
generator application is normalized. Consequently, depth-zero probability or
centered-logit differences can reflect both direction and stored radial scale;
positive-depth comparisons remove that radial-scale distinction.

## Gates

- `E0`: frozen source/checkpoint digests and finite numerics pass.
- `A0`: every native-anchor decision through H8 is correct.
- `I0`: the already-known seed-0 state-2-to-6 anchor error is the only native
  error and is confined to exact suffix depth zero; seed 1 and every positive
  suffix depth remain correct on the fresh episodes.
- `R0`: uniform R-incoming reanchoring repairs every native hard error and
  introduces none.
- `F0`: the same criterion for uniform F-incoming reanchoring.
- `P0`: R-incoming and F-incoming continuation signatures agree exactly over
  the registered domain.

`R0` or `F0` isolates a finite-window entry-interface repair only. `P0` is hard
agreement and does not assert soft collapse.

## Claim boundary

Incoming representatives are computed from each episode's learned operator
codes. This makes them controlled counterfactual states, not a single
episode-independent deployable embedding table. Passing through H8 cannot
establish unbounded recurrence. This block neither retests the known seed-1
depth-38 long-loop witness nor attributes relator-specific holonomy.
