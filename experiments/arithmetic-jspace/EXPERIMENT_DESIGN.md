# Preregistered candidate-space experiment v0.4

## Status and estimand

The estimand is whether answer-only arithmetic training produces a small
residual-stream subspace whose target-blind local geometry predicts downstream
output-summary changes and whose coordinates have selective effects on free
generation under matched interventions.

The task domain is positive-operand addition/subtraction with nonnegative
results; it makes no inference about signed arithmetic, zero identities,
multiplication, or division.

The allowed conclusion is a **replicated candidate balanced causal arithmetic
subspace**. Version 0.4 cannot establish a J-space equivalent. Its machine-
readable claim ceiling is fixed to `JSPACE_CLAIM=NOT_ESTABLISHED` because formal
causal mediation, native shared multi-query access, and component-specific
upstream-writer rescue are not implemented.

## Model and supervision

The serious profiles use the same conventional decoder architecture:

- 12 transformer blocks
- residual width 512
- 8 attention heads
- feed-forward width 2048
- approximately 38 million parameters
- fixed 260-token byte vocabulary
- maximum context 64

Weights start from scratch. Training minimizes ordinary causal next-token loss
on the answer and EOS; prompt tokens are masked. No intermediate arithmetic
trace, carry/borrow label, hidden-state target, auxiliary probe loss, bottleneck,
or workspace module is present.

## Arms and pairing

| Arm | Training stream and target | Valid comparison |
|---|---|---|
| `correct` | Full structural stream; exact answer | Primary arithmetic behavior |
| `no_carry` | Restricted zero-transfer stream; exact answer | Local arithmetic without propagation |
| `pseudo_fst` | Same expressions/order as `correct`; seeded pseudo-valued FST digits with arithmetic-answer-matched orientation/length | Pseudo-valued sequential control with a matched arithmetic answer-length nuisance |
| `deranged` | Same expressions/order as `correct`; random deranged target | Random-label control |

For each seed, `correct`, `pseudo_fst`, and `deranged` have identical initial
model hashes and audited input-expression order. Targets differ. `no_carry`
uses an intentionally restricted stream and is not claimed to match the full
stream's prompts, token count, or answer-width distribution. The sealed
`no_transfer` panel is the exact shared task comparison between `correct` and
`no_carry`.

The `pseudo_fst` must pass its own target-task competence gate before its
geometry is used as an accuracy-matched specificity control. Comparing a
competent arithmetic model with an unlearned pseudo task is invalid.
Because its target width is taken from the true answer width, this arm is not
fully arithmetic-free and can support only a limited specificity contrast.

## Derangement control

Every derangement window first attempts a random value derangement within
operator/output-width nuisance strata. If a stratum is underdetermined, the
construction deterministically coarsens it to output-width-only pooling. Exact
empirical target-multiset preservation remains required after either form of
pooling, and every assigned value must differ from its source value.

Only if an output-width-only stratum of at most 31 rows makes an
empirical-multiset value derangement mathematically impossible may the
construction deterministically synthesize canonical same-width decimal labels.
The limit of 31 applies separately to each impossible width stratum, not to the
window as a whole. Those labels still forbid all source/assigned value fixed
points, but the synthetic rows do not preserve the empirical target multiset.
The audit records the number and total-window fraction of synthetic rows,
rather than treating them as an exact derangement. That fraction has a strict
`0.001` (0.1%) cap. The audit records the configured cap and pass/fail result,
and the run fails closed if the cap is exceeded. Each constructed window that
uses synthetic rows emits exactly one `DERANGEMENT_SYNTHETIC_FALLBACK`
telemetry line. This is an explicit weakening of the random-label control,
accepted to prevent rare finite-window impossibility.

The construction therefore:

1. requires exact target-multiset preservation for every nonsynthetic stratum
2. forbids source/assigned value equality for both empirical and synthetic rows
3. never sorts answers by lexical or numeric value
4. records the target assignment, active nuisance strata, coarsening,
   synthetic-row count and total-window fraction, its `0.001` cap, and cap
   pass/fail
5. considers the synthetic fallback within a seeded candidate only after exact
   operator/output-width and exact output-width-only constructions are
   mathematically impossible; the up-to-eight seeded candidates test the
   residual-correlation and string-agreement gates, not fallback eligibility
6. audits the initial window before training and every later window at
   construction time; any configured correlation/string-agreement failure
   or synthetic-fraction-cap failure stops the run

`derangement_max_abs_pearson` applies to the absolute row-weighted Pearson
correlation across eligible within-stratum correlations. Eligibility is frozen:
at least 32 rows, at least 10 distinct values, and output width of at least two.
All tiny and degenerate strata, including their correlations, remain in the
audit but do not enter that rejection gate. Prefix and suffix agreement are
tested as excess above the stratum chance baseline.

## Counter-addressed data and splits

Training data are generated deterministically from `(seed, namespace, split,
counter, stage)`. Major train, validation, discovery, causal, IID, OOD, and final
classes use disjoint relation-family partitions. Addition commutation and
addition/subtraction inverse relations share a canonical family ID.

The counter stream is reproducible but does not guarantee global within-training
uniqueness; finite arithmetic collisions can occur. The pipeline does not
perform a global within-training collision audit, and no report may describe
all training rows as unique.

The fixed structural schedule is:

1. no carry/borrow
2. a single transfer event
3. contiguous transfer chains
4. a balanced mixture

Stages use fixed step boundaries, not observed-accuracy advancement, preserving
comparable schedules across the paired label arms. Structural evaluation panels
include IID trained widths, OOD longer widths, carry chains, borrow chains, and
the shared no-transfer panel.

## Optimization and longitudinal records

Discovery uses 60,000 optimizer steps per arm and seed; locked replication uses
80,000. AdamW follows a warmup-stable-decay schedule. BF16 is used when the
installed CUDA stack supports it, otherwise scaled FP16 is used. Progress is
flushed every 100 optimizer steps, including stale-evaluation age. Light free-
generation evaluation occurs every 500 steps and full evaluation every 2,000.

Research checkpoints are specified in each JSON profile. The rolling resume
state includes model, optimizer, scaler, RNG, stream counter, stage, and runtime
compatibility information. Resume refuses incompatible resolved configuration
or runtime fingerprints.

## Behavioral gates

Free generation is scored against each arm's trained completion, with the
ordinary arithmetic oracle also stored for controls. Reports retain exact
match, malformed rate, operation, digit width, and carry/borrow structure.

Candidate discovery is forbidden until the correct arm passes its
`probe_requires` IID, carry, borrow, and malformed thresholds. The stronger
`claim_requires` report additionally includes OOD exact match and the minimum
correct-minus-deranged arithmetic-oracle margin. The stronger report is retained
for scientific interpretation even though v0.4 cannot emit an established
claim.

`no_carry` and `pseudo_fst` have separate target-task competence gates. Transfer
panels for the `no_carry` model are scored on full arithmetic inputs and record
`evaluation_target_arm=correct`; its training restriction is not silently
applied to those evaluation rows.

## Target-blind candidate discovery

Discovery accepts prefix token IDs only. Every prefix must end at ByteTokenizer
SEP, and EOS is forbidden, preventing teacher-forced answer leakage.

At upstream layer \(u\), sealed random residual perturbations are propagated to
candidate source layer \(\ell\). Their source-layer effects estimate

\[
G_c = \mathbb{E}[\Delta h_\ell\Delta h_\ell^\top] + \lambda I.
\]

Gradients at \(h_\ell\) estimate observability for exactly nine fixed,
answer-independent output consumers:

1. digit log-probability mass
2. EOS log probability
3. minus-sign log probability
4. output entropy
5. top log probability
6. four sealed random vocabulary log-probability projections

Thus

\[
G_o = \mathbb{E}[gg^\top] + \lambda I,
\qquad
B = G_c^{1/2}G_oG_c^{1/2}.
\]

The candidate basis is the leading mapped eigenspace of \(B\). Candidate rank
is the smallest registered rank reaching the heldout fraction of target-free
consumer-response variance; if none reaches it, the best registered rank is
retained with `threshold_not_met`. Discovery prefixes, rank-selection prefixes,
and sealed causal pairs are disjoint.

Layer/rank selection is exploratory in `carry_discovery`. A modal selection
across passing seeds is written to `workspace_lock.json`. Confirmation accepts
only that source layer, upstream layer, and rank.

The fitted rank-matched controls are:

- PCA of discovery source states
- one seeded random orthonormal subspace
- a complementary balanced-spectrum subspace

Version 0.4 does not implement a bootstrap stability analysis or a distribution
of many random subspace draws. The empirical upstream perturbation is a local
residual intervention, not an exhaustive head/MLP controllability estimate.

## Implemented sealed causal assays

The provider constructs semantically matched clean/corrupt pairs differing at a
registered carry or borrow event column, with expected affected and unaffected
answer-digit positions. Answers are unavailable during candidate fitting and
selection. After the candidate is frozen, sealed answer values and widths are
used for pair construction, baseline eligibility, directional evaluation, and
free-generation scoring.

At the final prefix SEP position, the candidate, PCA, random, and complement
bases receive:

1. **Coordinate ablation:** remove the registered projection around the
   discovery mean from a clean residual state.
2. **Clean-to-corrupt patch:** transplant clean donor coordinates into the
   corrupt recipient state; audit predicted affected digits and preservation of
   unaffected digits.
3. **Independent upstream residual transplant:** replace the clean upstream
   residual with its matched corrupt donor residual and propagate to the source
   layer.
4. **Coordinate rescue:** after that upstream transplant, restore only the
   registered source-layer coordinates from the clean source state.

The causal assay regenerates autoregressively after intervention. Rank-matched
controls are energy-scaled to the candidate intervention norm for the same
state. Individual outputs and intervention norms are retained.

All primary causal estimands have registered denominators. Ablation counts only
pairs whose natural clean generation is a valid EOS-terminated signed decimal
and exactly correct. Patch requires both natural clean and corrupt generations
to be valid and correct with distinct targets. Rescue further requires the
unrescued upstream corrupt-donor transplant to generate the corrupt target
exactly. Discovery requires at least 128 baseline-qualified pairs and 32
directional rescue pairs; confirmation requires 512 and 128. Insufficient
qualified data fails the corresponding gate.

Coordinate rescue after an upstream residual transplant is an implemented
causal diagnostic. It is **not** formal mediation and does not identify which
attention head or MLP wrote the rescued state.

## Arithmetic specificity

If both `correct` and `pseudo_fst` pass target-task competence and candidate
selection, the same geometry and causal battery runs in both models. The
arithmetic-specificity diagnostic requires:

- IID target-task accuracy matched within the registered tolerance
- correct-arm candidate-minus-strongest-control effect exceeding the analogous
  pseudo-FST effect by the registered margin

This is a limited candidate specificity diagnostic. The answer-width nuisance
is shared deliberately, so this contrast does not isolate every arithmetic cue
and does not replace native shared access or mediation.

## Locked replication statistics

Confirmation retains item-level predictions and directional patch records.
Seed is the replication unit. For ablation, patch, and rescue, the registered
effect is candidate minus the strongest available PCA/random/complement control.
The analysis uses:

- paired seed-level effect tests
- Holm correction across the three registered causal contrasts
- family-clustered hierarchical bootstrap for item-level directional patch
  superiority

The configured confirmation has eight seeds and requires the registered seed
count. Passing statistics means that the implemented candidate effects
replicated. It cannot lift the release claim ceiling.

## Mandatory assays not implemented in v0.4

The following are explicit fail-closed gates:

- formal causal mediation with a registered estimand and intervention chain
- native shared multi-query access from one held state
- component-specific upstream-writer perturbation and downstream coordinate
  rescue

An unrelated-language preservation panel is also not bundled because the model
is arithmetic-only and has no meaningful language competence baseline.

No combination of loss, exact accuracy, balanced-space score, ablation, patch,
rescue, p-value, or bootstrap interval in this release can change
`JSPACE_CLAIM` from `NOT_ESTABLISHED`.
