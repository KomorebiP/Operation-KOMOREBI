# Semantic retraction and finite decision trace-agreement protocol

Author: Komorebi P.  
Version: 0.2.0  
Protocol date: 2026-09-03  
Freeze state: FROZEN BEFORE LEARNED OUTCOMES — terminal receipt required
Status: prospective calculations within a posthoc checkpoint program

## Purpose and evidence boundary

The preceding learned-checkpoint audit found that the centered-logit reachable
behavioral rank changes from seven at horizon zero to the full ambient rank
twelve after one controlled step. It also found angular D4 holonomy after
hard-polar normalization. This block asks a different question:

> Can path-dependent twelve-dimensional states be mapped to an eight-state
> semantic section while preserving or improving future decisions?

The answer may support a coarse nonlinear decision interface even though an
exact nontrivial continuous linear quotient is impossible on the tested
horizon. Oracle resets, autonomous resets, native path equivalence, and
continuous logit equivalence are separate claims. This analysis is posthoc and
cannot alter the original v0.4 assay or registered claim status.

No checkpoint may be selected by outcome. Use all twelve official v0.4
checkpoints from the four arms
`euclidean_supervised`, `euclidean_cr`, `polar_supervised`, and `polar_cr`, at
training seeds 101, 211, and 307. The target arm is `polar_cr`. Every checkpoint
and the source archive must match its sealed SHA-256 receipt and load strictly
with `weights_only=True`.

Source archive SHA-256:
`4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d`.

## Frozen D4 and action conventions

Use

\[
D_4=\langle r,f\mid r^4=e,\ f^2=e,\ frf=r^{-1}\rangle
\]

with eight canonical states `4*b + k` corresponding to \(r^k f^b\).
Canonical action codes are `r=0` and `f=1`. Operators act by left
multiplication, \(\tau_a(s)=as\), and temporal words are consumed from left to
right. Thus, for \(w=(a_1,\ldots,a_m)\),

\[
\tau_w=\tau_{a_m}\circ\cdots\circ\tau_{a_1},
\qquad g(w)=a_m\cdots a_1.
\]

If prefix \(u\) is followed temporally by suffix \(v\), their concatenation is
`uv` and

\[
T_{uv}=T_v\circ T_u,
\qquad \tau_{uv}=\tau_v\circ\tau_u.
\]

In context \(c\), `phi_c[canonical]` maps a canonical state to the visible
label and its exact inverse is obtained by permutation inversion. A canonical
start \(s\) is supplied to the model as \(\phi_c(s)\), and the exact visible
target after word \(w\) is \(\phi_c(\tau_w(s))\). Never apply a canonical
transition directly to a visible integer label.

## Frozen context banks

Construct contexts before loading learned outcomes. For each seed, invoke the
sealed v0.4 `EpisodeGenerator` sequentially, retain the first 32 accepted
unique contexts, and fail closed after 10,000 attempted draws. Generate the
prior exclusion bank first, calibration second, and evaluation third.

- Calibration bank: 32 unique D4 visible table contexts from seed `2026090311`.
- Evaluation bank: 32 unique contexts from seed `2026090312`.
- Deduplicate on exact visible float32 table bytes plus
  `canonical_to_slot` bytes.
- Exclude overlap between calibration and evaluation banks and with the prior
  seed-`2026090301` checkpoint-probe bank.
- Record canonical JSON and raw tensor SHA-256 receipts.

These banks are disjoint from one another and from the preceding probe. The
finite D4 context space may have been covered during training, so they are not
described as training-out-of-distribution.

## Endpoint-matched path bank

Generate paths symbolically without model-dependent filtering. Use calibration
seed `2026090321` and evaluation seed `2026090322`.

For nominal depth bands `8`, `32`, and `64`, and each of the eight D4 group
endpoints, retain two unordered pairs of distinct binary generator words.
Words within a pair must:

- have the same exact length and algebraic endpoint;
- have exactly the same generator histogram, so `number_r` and `number_f`
  match within the pair;
- have generator-count imbalance at most two;
- have maximum identical-symbol run length at most four;
- all four words across the two pairs for one endpoint and band must be
  mutually distinct;
- be absent from the other split; and
- be chosen without inspecting a checkpoint.

D4 word-length parity is the homomorphism
\(\chi:D_4\rightarrow\mathbb Z_2\) defined by \(\chi(r)=\chi(f)=1\); all
defining relations have even parity. Therefore the exact length for nominal
band `L` is `L + p(g)`, where `p(g)=chi(g)`. In canonical index order 0 through
7, the parity vector is `[0,1,0,1,1,0,1,0]`. Calling every endpoint “length L”
without this correction would be impossible.

Freeze path generation as follows. Use
`numpy.random.Generator(numpy.random.PCG64(seed))`, visit nominal bands in
ascending order and canonical endpoints from 0 through 7, and draw each
candidate with one `integers(0,2,size=exact_length,dtype=uint8)` call. Define
imbalance as `abs(number_r - number_f)` and maximum run length on the linear,
not cyclic, word. Reject a candidate if its composed endpoint, imbalance, run
length, or duplicate status fails. Queue accepted words by `number_r`; whenever
a queue first contains two words, emit that FIFO pair and clear those two
entries. Stop after two pairs. This makes each pair exposure-matched while
retaining a fully specified draw-order rule. Lexicographically order the two
words within each pair for serialization. Generate calibration before
evaluation and reject from evaluation any exact word already present in
calibration. Fail closed after 1,000,000 draws in any cell.

Before checkpoint loading, run a checkpoint-free dynamic-programming
eligibility audit and require enough same-histogram eligible words to form two
disjoint pairs in every `(exact_length, endpoint)` cell. Validate every
retained word by composing its canonical integer permutation on all eight
starts, not only on the identity start. Hash the RNG specification, ordered
records, full eight-state maps, and rejection counts.

Use all eight canonical starts. Two paired paths then have equal length, equal
group endpoint, and equal exact semantic state, but different histories.
Serialize and hash both path manifests before checkpoint evaluation.

## Continuation banks

The primary suffix set is every binary word through length four:

\[
W_4=\bigcup_{j=0}^{4}\{r,f\}^j,
\]

for 31 syntactically distinct suffixes. Serialize in length-then-lexicographic
order with `r < f`. Do not collapse words with the same D4 endpoint because
learned relation failure can make their realizations differ. Tag, rather than
add, these eight BFS members of `W4`: `epsilon`, `r`, `rr`, `rrr`, `f`, `fr`,
`rrf`, and `rf`, corresponding respectively to canonical endpoints 0 through
7.

The secondary stress set contains one checkpoint-independent,
endpoint-balanced word for each D4 element at nominal depth 16, with the same
parity, imbalance, and linear-run filters. Generate it with a fresh
`Generator(PCG64(2026090323))`, visit endpoints 0 through 7, and retain the
first eligible draw for each endpoint after rejecting duplicates and any word
present in either primary path split. Use the same 1,000,000-draw cell limit
and validate every full eight-state permutation. Freeze and hash the ordered
eight-word list before checkpoint loading. Stress results remain separate and
descriptive; they neither enter the 31-word primary maximum nor replace a
primary gate.

## Native dynamics and numerical path

Let learned metric-unit anchor columns be
`B=[b_0,...,b_7]`, decoder be `D`, recurrence metric be `G`, and a visible
operator matrix be `A`. Preserve each checkpoint's own execution path:

- encode exact float32 tables once per checkpoint and context;
- use each packaged model's selected recurrent matrices exactly: raw encoder
  outputs for `euclidean_*` arms and model-produced post-SVD polar factors for
  `polar_*` arms, with no additional retraction in either case;
- run every recurrence, normalization, intervention application, and decoder
  call in float32 without autocast;
- reuse the identical encoded matrices for every branch; and
- use float64 only for projector construction, validity checks, geometry, and
  reductions after detaching the float32 outputs.

Canonical generator codes must be mapped through `canonical_to_slot`.
`phi[canonical]` is the visible state. Exact targets are advanced through the
integer table maps, never through predictions. Cross-check the custom rollout
against the packaged rollout separately for every arm.

## Single-reset interventions

For each evaluation context, matched pair `(u,u')`, and start state, obtain the
native endpoint states `h` and `h'`. The pair is mathematically unordered.
Apply every source-dependent intervention separately with `h` and with `h'` as
the source, then average the two orientations with equal weight. Oracle and
wrong-state resets coincide across orientations and may be computed once, but
must retain the same effective weight. Run every identical suffix from `W_4`
and the stress subset. This symmetry rule prevents arbitrary serialization
order from selecting the reported history.

| Condition | State supplied to continuation | Role |
|---|---|---|
| `native_h` | `h` | First history baseline |
| `native_h_prime` | `h'` | Equal-semantic paired history |
| `sham_scale` | `norm_G(7 h)` | Projective and plumbing control |
| `oracle_anchor` | `b_y` for the true visible endpoint `y` | Teacher-forced semantic section |
| `self_anchor` | `b_argmax(Dh)` | Autonomous decoder-selected section |
| `nearest_anchor` | anchor with largest positive-ray `G_s` cosine to `h` | Autonomous geometric selector |
| `oracle_prototype` | calibration-fitted prototype `mu_y` | Held-out teacher-forced section |
| `self_prototype` | nearest prototype to `h` | Held-out autonomous section |
| `anchor_projection` | `norm_G(P_B h)` | Ambient-complement ablation bridge |
| `wrong_anchor` | \(b_{\phi_c(\tau_r(\phi_c^{-1}(y)))}\) | On-manifold semantic-shuffle/specificity control |
| `wrong_prototype` | \(\mu_{\phi_c(\tau_r(\phi_c^{-1}(y)))}\) | Prototype-family semantic specificity control |
| `random_ray` | four seeded generic `G_s`-unit rays | Norm-matched denoising control |

Here

\[
P_B=B(B^TG_sB)^{-1}B^TG_s.
\]

Require finite `G` with maximum antisymmetric entry at most `1e-6`, then define
`G_s=(G+G^T)/2` for every detached geometry, projector, selector, and
random-ray calculation. Require
`lambda_min(G_s) > 1e-8 * lambda_max(G_s) > 0`. The packaged float32
recurrence normalization remains unchanged; its quadratic form is insensitive
to the antisymmetric part. Require `B^T G_s B` to have numerical rank eight at
relative tolerance `1e-8` and condition number at most `1e8`; these are
validity diagnostics, not a license to invert an ill-scaled matrix in float32.
In float64 form a Cholesky factor `G_s=C^T C`, obtain an orthonormal basis `Q`
for `C B` by checked thin SVD, and construct `P_B=C^{-1} Q Q^T C`. Cast the
finished projector to float32 before applying it. On that post-cast operator
require absolute trace error at most `1e-5` and maximum-absolute-entry errors
at most `1e-5` for idempotence, `G_s` self-adjointness, and action on all
anchors. Fail
closed otherwise. Before every normalization require a finite squared metric
norm strictly above `1e-12`; then use the packaged float32 normalization path.
The projection repeats part of the earlier ambient assay and is a bridge
condition rather than an independent discovery.

For each checkpoint, construct prototypes only from the Cartesian product of
the calibration context bank and calibration path bank. Evaluate them only on
the Cartesian product of the disjoint evaluation context and evaluation path
banks. This is a held-out calibration/evaluation split, not statistical
cross-fitting:

\[
\mu_y=\operatorname{norm}_G\!\left(\sum_{i:y_i=y}
\operatorname{norm}_G(h_i)\right).
\]

Balance contributions over context, depth band, group endpoint, pair member,
and start. Traverse contributions in context-index, ascending-band,
canonical-endpoint, pair-index, lexicographic-member, canonical-start order.
Detach the float32 calibration endpoints, promote them and `G_s` to float64,
normalize each contribution with `G_s`, and use
`numpy.sum(..., axis=0, dtype=float64)` in that fixed row order. Normalize the
resultant with `G_s` in float64, cast it to float32, and apply the packaged
float32 normalization once; that final float32 tensor is the stored and used
prototype. This estimator construction is the explicit exception to the
float32 forward path, not a learned recurrence. Do not flip signs because
positive rays are oriented. Record class resultant lengths and float32 tensor
hashes and fail closed on a zero or nonfinite prototype. Do not use
depth-specific prototypes and do not pool coordinates across checkpoints.

Generate four `random_ray` draws per unordered pair/start case from frozen seed
`2026090324`. Use zero-based indices throughout: evaluation `split_code=2`,
`context_id` is the row 0--31 in the serialized evaluation context bank,
`endpoint` is 0--7, `pair_id` is 0--1 within that band/endpoint cell, `start`
is canonical 0--7, and `draw_id` is 0--3. Construct exactly
`SeedSequence([2026090324, 2, context_id, nominal_band, endpoint, pair_id,
start, draw_id])` as an entropy vector (not a spawn key), pass it to
`Generator(PCG64(seed_sequence))`, and draw one 12-coordinate vector with one
`standard_normal(12)` call. Do not include serialized member
orientation in the key: the same four rays are compared with both native
references. With lower Cholesky factor `G_s=L L^T`, set
`h=L^{-T}z/||z||_2`, computed then cast through the frozen float32
intervention path. Only the standard-normal base stream is checkpoint
independent; the transformed rays necessarily depend on that checkpoint's
learned `G`. The key, not checkpoint outcomes, determines the base stream.
Do not filter directions by accuracy, decoder label, anchor angle, or hidden
separation. Average draws within case before context aggregation and retain
each draw's raw counts.

Freeze autonomous selectors in visible-label coordinates. `self_anchor` uses
`argmax(Dh)`. `nearest_anchor` maximizes positive-ray, antipode-sensitive
metric cosine
\(h^TG_sb_j/(\lVert h\rVert_{G_s}\lVert b_j\rVert_{G_s})\).
`self_prototype` uses the corresponding `G_s` cosine to \(\mu_j\).
Every exact tie is broken by the lowest visible label. For a selector \(q\)
and its visible-label section \(\iota_q\), define selector accuracy at the
intervention cut as `q(h)==y`. Separately audit the entire section, without
conditioning on labels visited by cut states: for every visible label
`j=0,...,7`, require \(q(\iota_q(j))=j\). Check reset idempotence both on these
eight section states and on every cut state, requiring selector equality and
maximum absolute float32 hidden-state discrepancy at most `1e-6`. Define
one-step semantic commutation, exhaustively for every visible `j`, evaluation
context, and `a in {r,f}`, as

\[
q(T_a^c\iota_q(j))
=
\phi_c\!\left(\tau_a(\phi_c^{-1}(j))\right).
\]

Also require decoder output consistency
`argmax(D iota_q(j)) == j` on all eight section states; geometric selector
validity alone is not output validity. Compute cut-state quantities for both
pair orientations. The
continuous anchor projection has no discrete selector; report its post-cast
projector idempotence and decoded one-step behavior separately.

## Finite behavioral pseudometrics

For fixed context and output metric `rho`, define

\[
d_{H,c}^{\rho}(x,x')=
\max_{w\in\{r,f\}^{\le H}}
\rho\!\left(o(T_w^c x),o(T_w^c x')\right).
\]

Use three output comparisons:

- discrete argmax disagreement;
- total variation distance between softmax outputs; and
- antipode-sensitive spherical angle between normalized centered logits.

Every decoded prediction uses the lowest visible index on an exact logit tie.
After detaching float32 logits, compute softmax in float64 and define

\[
\operatorname{TV}(p,q)=\tfrac12\sum_j|p_j-q_j|.
\]

For centered float64 logits \(z,z'\), define the spherical discrepancy as

\[
\arccos\!\left(\operatorname{clip}
\frac{z^Tz'}{\lVert z\rVert_2\lVert z'\rVert_2},-1,1\right).
\]

Report the maximum over `W_4` for every matched pair, plus distributions and
undefined-angle counts. Center logits with `I - ones(8,8)/8` in float64 after
the float32 decoder call. Any nonfinite logit, hidden state, metric norm,
softmax probability, TV value, or margin invalidates that checkpoint before
gate scoring. For otherwise finite logits, the spherical angle is undefined
if either centered norm is at most `1e-12`; assign that fail-closed gate score
`pi` and also count it. This `pi` substitution is a conservative operational
score, not a metric extension at the zero ray.
For each condition also report task accuracy,
agreement with both native histories, joint correctness, correct-class margin,
damage conditional on native correctness, and rescue conditional on native
error. Preserve numerators and denominators. Report selector accuracy,
idempotence, and one-step semantic commutation for autonomous conditions.

For each of `wrong_anchor` and `wrong_prototype`, let
\(s=\phi_c^{-1}(y)\). Define the factual visible suffix target as
\(\phi_c(\tau_w(s))\) and the counterfactual target as
\(\phi_c(\tau_w(\tau_r(s)))\): the wrong `r` action occurs first at the
intervention cut, followed by the exact suffix. Do not substitute
\(\tau_r(\tau_w(s))\), which differs for noncommuting suffixes. Factual leakage
is the proportion of all `W_4` cases predicted as the factual target. Report
the empty-suffix value separately.

Within a checkpoint, first aggregate binary metrics within each context over
the balanced path pairs, starts, and suffixes. Give each of the 32 evaluation
contexts equal weight in the checkpoint mean. For native trace metrics, first
take each matched pair's maximum discrepancy over all 31 `W4` suffixes: the
discrete maximum is a trace-equivalence indicator, and the angle/TV maxima are
pairwise continuous trace discrepancies. Compute p95 only across these
pairwise maxima, not raw suffix cases. Joint all-suffix correctness is one only
if both histories are correct for every suffix. Other intervention accuracy
summaries may average suffix cases as specified. `Worst context` means the
minimum of the 32 context-level accuracy or trace-equivalence values.
Random-ray draws are averaged within case. Selector accuracy denominators are
intervention cuts only and are never suffix-expanded. Apply gates to each
checkpoint, then require all three seed checkpoints for an arm claim. Never
treat cases as independent population replicates.

For primary one-shot future metrics, give each of the 30 nonempty syntactic
`W4` words equal weight; do not weight unique D4 endpoints. Report suffix
length 1, 2, 3, and 4 strata separately. For state specificity over full
`W4`, give all 31 syntactic words equal weight and report the empty word again
as its own diagnostic. Compute every p95 with
`numpy.quantile(..., method="higher")`. A zero denominator for damage,
native-correct agreement, or conditional-on-correct-selection accuracy fails
the associated gate. A zero native-error denominator makes rescue and relative
error reduction `N/A`, with the separately specified low-native-error rule
applied; `N/A` is never silently converted to a pass.

## Periodic autonomous repair

Use the evaluation endpoint-matched words at nominal bands 8 and 64. Band 8 is
the shallow-damage control and band 64 is the primary depth-repair test. Evolve
each branch independently for `K in {1,4,8,16}` and continue its cadence
through every `W_4` suffix. Compare:

- native and sham;
- oracle anchor as an upper bound;
- self anchor;
- nearest anchor;
- self prototype; and
- anchor projection.

`K=4` is the primary periodic gate because the checkpoint training horizon was
four. `K=1`, `8`, and `16` form a prespecified dose-response curve. Record
accuracy at prefix steps 8, 16, and 32 only for trajectories that reach the
named step, plus the actual terminal step for every trajectory. Thus band-8
paths have no step-16 or step-32 observation. Also record reset-selector
errors, error correction versus propagation, suffix accuracy, margins, and
state/output-resolved summaries. Oracle periodic injection is never called
autonomous.

The autonomous controller uses one endpoint-independent absolute clock. Count
the first prefix action as step one and apply a reset immediately after every
transition with `t mod K == 0`. Decode reported outputs after any scheduled
reset. Continue the same absolute counter through a suffix; do not restart the
phase and do not add an unscheduled terminal reset. Each mode and cadence
evolves its own state and selector errors and never restarts from the native
trace. For `K=1`, both exact lengths 64 and 65 end immediately post-reset. For
`K in {4,8,16}`, exact length 64 ends immediately post-reset whereas length 65
ends one raw step post-reset. At the primary `K=4` cadence this reset-recency
difference is perfectly associated with endpoint parity, so primary accuracy,
damage, and error reduction must pass and be reported separately in both
parity strata as well as after equal-endpoint pooling. The empty suffix uses
the terminal state at its actual scheduled phase. An endpoint-informed
parity-aligned clock is forbidden from earning an autonomous label.

## Fixed interpretation gates

All thresholds are descriptive operational gates. An arm passes only if all
three training seeds pass. Contexts, words, starts, and suffixes are audit
cases, not independent population replicates.

### Native finite decision trace agreement at the deepest band

At nominal band 64 over all 31 `W4` suffixes:

- fraction of matched-pair/start cases with zero decision disagreement over
  every suffix at least `0.99`;
- fraction jointly correct for every suffix at least `0.99`; and
- worst-context all-suffix trace-equivalence fraction at least `0.95`.

Pooled per-suffix agreement is diagnostic only and cannot satisfy this gate.

### High-coverage native logit-geometric trace agreement

- native decision trace-equivalence gate passes;
- p95 across matched-pair/start cases of each case's maximum-`W4`
  centered-logit angle at most `0.05` radians, with no undefined angle; and
- p95 across matched-pair/start cases of each case's maximum-`W4` softmax
  total variation at most `0.01`.

### High-fidelity oracle semantic repair

At nominal band 64 over the 30 nonempty `W4` suffixes:

- reset accuracy at least `0.99`;
- agreement with the native reference at least `0.99` on native-correct cases;
- damage at most `0.01`;
- worst-context accuracy at least `0.95`;
- accuracy exceeds the mean four-draw random-ray control by at least `0.20`;
  and
- the matched wrong-section factual leakage is at most `0.05`.

Agreement on native-correct cases and damage are complementary views of the
same contingency table; they are both reported for readability, not treated
as independent evidence.

The empty suffix is reported separately and must decode the supplied oracle
state with accuracy `1.00` across every tested context and canonical state.
At nominal band 8, oracle damage must be at most `0.01`; nominal band 32 and
the stress bank are descriptive and cannot compensate for a band-64 failure.

Gate `oracle_anchor` and `oracle_prototype` separately, naming passes
`ORACLE_ANCHOR_SEMANTIC_REPAIR_INTERFACE` and
`ORACLE_PROTOTYPE_SEMANTIC_REPAIR_INTERFACE`. Oracle success establishes a
teacher-forced semantic repair interface, not an autonomous quotient and not
native hidden-state equivalence.

### Autonomous one-shot retraction

Evaluate every autonomous anchor/prototype selector separately. At the nominal
band-64 intervention cuts and over the 30 nonempty suffixes:

- selector accuracy at least `0.99` at cuts only;
- suffix task accuracy at least `0.99` conditional on a correct selection;
- unconditional suffix accuracy at least `0.95`;
- damage at most `0.01`;
- section validity and decoder output consistency on all eight states both
  equal `1.00`;
- reset idempotence equals `1.00` on every tested state, with maximum absolute
  hidden-state discrepancy at most `1e-6`;
- one-step semantic commutation is at least `0.99` separately for `r` and `f`,
  with worst-context commutation at least `0.95`;
- the state-specificity gate passes; and
- accuracy exceeds mean four-draw random-ray accuracy by at least `0.20`.

At nominal band 8, damage must be at most `0.01`. Report the empty suffix,
nominal band 32, and stress results separately; they cannot compensate for a
band-64 failure.

Report decoder-selected and geometry-selected anchor/prototype sections
separately. Failure of these prespecified sections does not refute every
possible nonlinear quotient.

### Autonomous periodic depth repair

At primary cadence `K=4`:

- nominal-band-64 plus all 31 equally weighted syntactic `W4` suffixes has
  accuracy at least `0.95`, both pooled
  and separately within the even- and odd-endpoint parity strata;
- at least 50 percent reduction in error relative to native execution, applied
  separately within each parity stratum; and
- no more than `0.01` absolute accuracy damage on separately executed
  nominal-band-8 trajectories, both pooled and within each parity stratum.

An autonomous periodic label additionally requires the same section-validity,
idempotence, both-generator commutation, and state-specificity prerequisites as
the one-shot label. These structural prerequisites do not require the native
trace-equivalence gate to pass.

`anchor_projection` has no finite selector or section and cannot earn an
autonomous semantic-retraction label. Report a passing projection branch only
as `PERIODIC_ANCHOR_SPAN_PROJECTION_REPAIR`, an ambient-ablation diagnostic.
Likewise, periodic oracle injection is an explicitly teacher-forced upper
bound, not an autonomous controller.

If native error is below `0.01`, relative error reduction is operationally
`N/A` for gating, although it remains mathematically defined for positive
native error and is truly undefined only when native error is zero. Require
accuracy at least `0.99` with no material degradation instead, separately in
every gated parity stratum and in the equal-endpoint pooled summary.

When native error is at least `0.01`, define relative error reduction exactly
as

\[
\frac{(1-A_{native})-(1-A_{reset})}{1-A_{native}}.
\]

`No material degradation` always means an absolute accuracy decrease of at
most `0.01`.

### State specificity

At nominal band 64, each section is paired with its family-specific wrong
control: anchors with `wrong_anchor`, prototypes with `wrong_prototype`. The
wrong control must predict its counterfactual target with accuracy at least
`0.95` over the full `W4` suffix bank and also at least `0.95` at the empty
suffix, while factual-label leakage over all `W4` cases is at most `0.05`. A
semantic reset must also exceed the frozen random-ray control by the stated
margin. Otherwise semantic canonicalization cannot be distinguished from a
mislabeled or generic denoising intervention.

## Prospective execution budget and freeze receipt

Before unlocking checkpoints, run a manifest-only dry run that reports exact
counts for every context, path, unordered pair, orientation, start, suffix,
intervention, cadence, and random draw. It must hash every serialized context,
path, continuation, stress, and random-key manifest; estimate peak working-set
bytes and the exact number of float32 recurrent matrix-vector applications;
and load no checkpoint. Embed those digests and counts in the final protocol
receipt. Seeds and prose constraints alone are not a freeze receipt.

The first learned outcome spends the evaluation context/path bank. After any
checkpoint result is computed with seeds `2026090312` or `2026090322`, no bug
fix, threshold or aggregation change, or new section can regain prospective
status on that bank. Such reruns are labeled sensitivity analyses, or use a
newly generated, reviewed, and sealed evaluation bank that has not been
exposed to learned outcomes.

The learned runner must process context/case chunks of at most 4,096 starting
states, reuse each native prefix and the 31-node `W4` binary suffix tree, carry
periodic clock phase at tree nodes, and aggregate counts online. It may retain
one bounded, packed native-prefix trajectory cache solely for the all-step
periodic sham/reference comparisons and the bounded suffix tree for the current
case; it must not retain the full study-wide
context-by-path-by-condition-by-suffix panel of hidden states or logits. Random
controls and orientation-invariant branches must be reused as specified rather
than recomputed. The manifest must freeze the result-file count and byte
ceilings and require sufficient free space on the result filesystem, including
the frozen safety margin, before the spend marker. If the dry run exceeds the
declared counts or memory budget, or if code and machine contract disagree with
this document, the learned run remains locked and the protocol must be revised
prospectively.

Reserve an exclusive, self-contained result bundle before spending the bank.
Write byte-identical internal and global spend receipts before loading any
learned model, then stream one exclusive shard per checkpoint. A bundle
manifest must bind by SHA-256 the exact-control file, spend receipt, all 12
unique arm-by-seed shards, arm aggregation, and `RUN.json`; write `COMMIT.json`
last. No learned output is valid or interpretable unless the independent bundle
verifier confirms the exact file set, every hash and cross-link, the complete
4-by-3 checkpoint census, and the three-seed AND aggregation, with no symbolic
links or overwrite.

## Required controls

- A custom native rollout must match the model's packaged rollout separately
  in every arm: identical predictions and maximum absolute hidden/logit
  difference at most `1e-6`.
- The sham scale intervention must preserve every prediction, with maximum
  absolute normalized-hidden difference at most `1e-6` and logit difference
  at most `1e-5`.
- An exact anchor-compiled D4 float32 action must have perfect factual and
  counterfactual decisions and periodic closure, with maximum absolute
  normalized-hidden/logit discrepancy at most `1e-6`.
- Slot-swapped contexts must pass the integer-map target firewall with zero
  target mismatches over every state and generator.
- At time zero, `oracle_anchor` must equal the native initial anchor within
  maximum absolute float32 discrepancy `1e-6` and with identical decoding.
  This identity control does not apply to `oracle_prototype`.
- `P_B` must pass rank and trace checks, plus the frozen
  maximum-absolute-entry residual bounds for idempotence, `G_s`
  self-adjointness, and anchor preservation.
- Each wrong anchor/prototype index must differ from truth for every case.
- The Gaussian random-key stream must reproduce exactly from its receipt and
  remain unfiltered by learned outcomes; record separate transformed-ray
  receipts for each checkpoint because the whitening map uses learned `G_s`.
- Checkpoint state dictionaries and digests must be unchanged after analysis.
- Any nonfinite learned logit, hidden state, norm, probability, TV, or margin
  invalidates the checkpoint result. A finite zero-centered-logit angle is the
  sole scored exception and receives `pi` as specified above; it can never be
  silently converted to a successful case.

If an exact control or provenance check fails, the learned-checkpoint result is
invalid rather than interpretable.

## Independent claim matrix

Report every gate independently; these labels are not a single ordered
hierarchy.

| Label | Required gates |
|---|---|
| `NATIVE_FINITE_DECISION_TRACE_AGREEMENT_H4_COVERAGE_0.99` | deepest-band decision trace-coverage gate |
| `NATIVE_FINITE_LOGIT_TRACE_AGREEMENT_H4_P95` | decision trace gate plus continuous p95 trace gate |
| `ORACLE_ANCHOR_SEMANTIC_REPAIR_INTERFACE` | anchor-family high-fidelity oracle gate plus matched controls |
| `ORACLE_PROTOTYPE_SEMANTIC_REPAIR_INTERFACE` | prototype-family high-fidelity oracle gate plus matched controls |
| `AUTONOMOUS_ONE_SHOT_RETRACTION__{SELF_ANCHOR,NEAREST_ANCHOR,SELF_PROTOTYPE}` | named controller's one-shot behavioral gate plus exhaustive section validity, idempotence, both-generator commutation, matched state-specificity, and random control |
| `AUTONOMOUS_PERIODIC_DEPTH_REPAIR__{SELF_ANCHOR,NEAREST_ANCHOR,SELF_PROTOTYPE}` | named controller's periodic behavioral gate plus exhaustive section validity, idempotence, both-generator commutation, matched state-specificity, and random control |
| `PERIODIC_ANCHOR_SPAN_PROJECTION_REPAIR` | projection behavioral gate only; ambient-ablation diagnostic, not semantic retraction |

Native trace agreement may fail while a periodically retracted controller
succeeds; that supports the retracted system, not a quotient of native
dynamics. Braced names above denote three separately evaluated and emitted
controller-qualified labels; conditions are never pooled and a label does not
require the other two controllers to pass. The 0.99 and p95 thresholds
establish explicitly qualified empirical
coverage, never universal equivalence on the full tested bank. Decision
preservation with continuous-logit failure is only coarse finite trace
agreement. Call a result an approximate bisimulation only when
an explicitly reported horizon-stratified relation has bounded observation
error, two-way semantic coverage, and successor closure for both generators
at every tested depth. One-shot success with periodic failure is local
canonicalization, not stable repaired closure. Oracle success with autonomous
failure identifies an addressability or closure bottleneck; localize it to the
selector only when section validity, idempotence, both-generator commutation,
same-regimen conditional behavior, periodic stability, and all matched
non-selector controls otherwise pass. Failure of all tested sections keeps the
twelve-dimensional path-dependent workspace interpretation live, but does not
prove that no other nonlinear section exists.
