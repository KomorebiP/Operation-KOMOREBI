# Arithmetic workspace execution protocol v0.4

## Release boundary

This package asks whether ordinary answer-only arithmetic training produces a
low-dimensional residual-stream coordinate system with target-blind predictive
geometry and selective causal effects. The model is standard and the candidate
is measured after training; no workspace is inserted or supervised.

The registered arithmetic domain is positive-operand addition and subtraction
with nonnegative results. Negative answers, zero identities, multiplication,
and division are outside this release's estimand.

Version 0.4 is candidate-only. The following mandatory assays are not
implemented:

- formal causal mediation
- native shared multi-query access
- component-specific upstream-writer rescue

Consequently, all profiles hard-disable an establishing claim and must report
`JSPACE_CLAIM=NOT_ESTABLISHED`. The strongest allowed description is
**candidate balanced causal arithmetic subspace**.

## Recommended command

```powershell
$d="$env:USERPROFILE\Downloads\Arithmetic_JSpace_Training_Lab_v0.4.0"; & "$d\Run_Arithmetic_Workspace_Experiment.ps1" -Profile carry_discovery -Python "$env:USERPROFILE\miniconda3\envs\komorebi-full\python.exe" -Device cuda -SkipInstall
```

Rerun the identical command to resume. The default discovery output is
`Downloads\Arithmetic_Workspace_Runs\carry_discovery`.

## Profiles

| Profile | Function | Model | Workload |
|---|---|---|---:|
| `workspace_smoke` | Wiring, checkpoint, and assay smoke | 3×128 | 1 seed × 4 arms × 20 steps |
| `carry_discovery` | Exploratory layer/rank selection | 12×512 (~38M) | 3 × 4 × 60,000 |
| `carry_confirmatory` | Locked candidate replication | 12×512 (~38M) | 8 × 4 × 80,000 |

Confirmation requires the frozen `workspace_lock.json` from discovery. With
default paths, the runner finds it automatically; otherwise pass `-LockFile`.
Confirmation cannot establish a J-space claim.

On an RTX 3070 Ti Laptop GPU, budget minutes for smoke, about 3–9 continuous
days for discovery, and about 12–35 days for confirmation. Geometry and causal
assays can add substantial time. The measured ETA after 500 steps is more
reliable than these planning ranges.

Plan for roughly 30 GB of free disk for discovery and 80 GB for locked
replication. Model-only research checkpoints are intentionally retained, and
the runner does not prune completed arms automatically.

## Model and training contract

The serious model has 12 layers, width 512, 8 heads, feed-forward width 2048,
and a 64-token context. It uses the fixed 260-token byte vocabulary. It starts
from random weights and sees only equations and answer completions.

Training uses:

- causal loss on answer bytes and EOS; prompt tokens masked
- AdamW and a warmup-stable-decay schedule
- BF16 when supported, otherwise scaled FP16 on CUDA
- gradient clipping
- deterministic counter-addressed data
- atomic rolling resume state
- immutable research checkpoints at registered steps

There is no scratchpad, worked trace, carry label, hidden-state target,
representation loss, bottleneck, or probe loss.

The structural schedule is frozen: no-transfer examples, single events,
contiguous chains, then a balanced mixture. It does not adapt to observed
accuracy.

## Training arms and valid pairing

| Arm | Training rule | Interpretation |
|---|---|---|
| `correct` | Full addition/subtraction stream, exact target | Arithmetic candidate |
| `no_carry` | Zero-carry/zero-borrow subset, exact target | Restricted local-computation control |
| `pseudo_fst` | Full shared expression stream, seeded FST target | Pseudo-valued sequential control, arithmetic-answer-length matched |
| `deranged` | Full shared expression stream, random deranged target | Random-label control |

For a seed, `correct`, `pseudo_fst`, and `deranged` have paired initial weights
and identical input-expression order. `no_carry` necessarily has a restricted
training stream. It is not globally prompt-, token-, or answer-width-matched.
The sealed `no_transfer` evaluation panel is the exact shared comparison with
the correct model.

The pseudo-FST produces deterministic stateful digit values with the same
orientation and output length as the arithmetic answer. It controls digit
values while retaining that coarse arithmetic-derived schema signal, so it is
a conservative, limited specificity control rather than a wholly
arithmetic-free task. It must meet its own target-task competence threshold
before its candidate is used for the limited specificity diagnostic.

## Derangement audit

Each derangement window first uses random value permutations within
operator/output-width strata. An underdetermined bucket is deterministically
coarsened to output-width-only pooling when needed. Every nonsynthetic stratum,
including a coarsened one, must preserve its exact empirical target multiset,
reject every source/assigned value fixed point, and never sort answers before
assignment.

Only if a width-only stratum of at most 31 rows makes an empirical-multiset
value derangement mathematically impossible may the generator deterministically
synthesize canonical same-width decimal labels. The limit of 31 is per
impossible width stratum. These rows retain zero source/assigned value fixed
points but do not preserve the empirical target multiset. The audit explicitly
reports their count and total-window fraction, the strict `0.001` (0.1%) cap,
and cap pass/fail. The run fails closed if that cap is exceeded. Each
constructed window using the fallback emits one
`DERANGEMENT_SYNTHETIC_FALLBACK` telemetry line. This fallback weakens the
deranged control and must be disclosed in interpretation, but it prevents a
rare finite training window from being impossible to construct.

The initial window is audited before training; every later deterministic window
is audited when constructed and fails closed if it violates a gate. Audits
record fixed points, cycle lengths, nonsynthetic multiset preservation,
synthetic-row count and total-window fraction, the fraction cap and pass/fail,
numeric correlations, and prefix/suffix agreement above chance.
`derangement_max_abs_pearson` gates the absolute row-weighted Pearson
correlation across eligible within-stratum correlations. Eligibility is fixed
at at least 32 rows, 10 distinct values, and two output digits. Smaller or
degenerate strata remain fully reported but do not enter this gate. Up to eight
deterministic candidates are attempted for the residual-correlation and string
agreement gates. Within each candidate, synthetic labels are eligible only
after exact operator/output-width and exact width-only constructions are
mathematically impossible. After the narrowly eligible synthetic fallback, any
remaining audit failure stops the run.

## Data integrity

Each example records split, counter, pair ID, relation-family ID, operands,
operation, answer, carry/borrow count, longest chain, event columns, and digit
positions affected by counterfactual events.

Major split classes use disjoint family partitions, including addition
commutation and addition/subtraction inverse relations. The stream is
counter-addressed and reproducible, but global within-training uniqueness is
not guaranteed or audited. No report may describe every training row as
unique.

## Progress and evaluation

Every serious training arm emits unbuffered telemetry every 100 optimizer
steps. A progress record includes seed, arm, step, stage, rolling/current loss,
learning rate, gradient norm, throughput, ETA, peak VRAM, and the age
of the latest evaluation. A repeated validation value is therefore not mistaken
for a fresh evaluation.

Light free-generation evaluation occurs every 500 steps and full evaluation
every 2,000. Final behavior panels cover trained-width IID, longer-width OOD,
carry chains, borrow chains, and no transfer. Discovery and confirmation retain
item-level final predictions for paired and family-clustered analyses; smoke
does not.

Candidate probing is skipped unless the correct model passes the registered IID,
carry, borrow, and malformed-output gate. A second, stronger report includes
OOD and correct-minus-deranged arithmetic-oracle margin. Separate competence
reports apply to `no_carry` and `pseudo_fst`.

## Implemented target-blind discovery

The discovery API accepts only tokenized prefixes ending at SEP. EOS and answer
continuations are rejected. Answers and correctness never enter candidate
fitting or layer/rank selection.

Random residual perturbations at an upstream layer are propagated to the source
layer to estimate empirical local controllability:

\[
G_c=\mathbb{E}[\Delta h\Delta h^\top]+\lambda I.
\]

Local observability uses gradients of exactly these answer-independent output
summaries:

1. digit log-probability mass
2. EOS log probability
3. minus-sign log probability
4. output entropy
5. top log probability
6. four sealed random vocabulary log-probability projections

With their gradient Gram matrix \(G_o\), the candidate comes from leading
directions of

\[
G_c^{1/2}G_oG_c^{1/2}.
\]

Rank is selected on separate prefixes by prediction of perturbation-induced
changes in the same output summaries. This is heldout rank selection, not a
bootstrap-stability assay.

The registered rank-matched basis controls are PCA, one seeded random subspace,
and a complementary balanced-spectrum subspace. Version 0.4 does not sample a
large random-subspace distribution.

Discovery runs independently in competent `correct` and `pseudo_fst` models.
The discovery lock stores the modal passing correct-arm source layer, upstream
layer, and rank across exploratory seeds. Confirmation forbids reselection.

## Implemented causal battery

The sealed provider constructs matched clean/corrupt addition or subtraction
pairs differing at a registered carry/borrow event column. It records affected
and unaffected answer-digit positions.

At the final prefix SEP residual position, candidate, PCA, random, and
complement bases receive four free-generation assays:

1. **Coordinate ablation** around the discovery mean.
2. **Clean-to-corrupt coordinate patch**, including a directional audit of
   affected digits and preservation of unaffected digits.
3. **Independent upstream residual transplant** from the matched corrupt donor
   into the clean sequence.
4. **Coordinate rescue after transplant**, restoring only registered
   source-layer coordinates from the clean state.

For control bases, interventions are scaled to the candidate intervention norm
for the same state. Individual generated outputs and norms are saved.

The primary denominators are fail-closed. Ablation requires a valid and correct
natural clean generation; patch requires valid and correct natural clean and
corrupt generations with distinct answers; rescue also requires the unrescued
upstream corrupt-donor transplant to produce the corrupt answer exactly.
Discovery requires 128 baseline-qualified and 32 directional-rescue pairs;
confirmation requires 512 and 128. Valid means EOS-terminated, free of illegal
special tokens, and a nonempty signed decimal.

These are genuine local interventions, but their scope is limited. The upstream
donor is an entire residual state, not a specific head or MLP writer. Restoring
coordinates after that transplant is not a formal mediation estimand. The
package has no native multi-query continuation assay and no unrelated-language
preservation assay.

## Specificity and registered statistics

When both correct and pseudo-FST models are competent, the pipeline fits and
causally tests each candidate independently. It compares candidate-minus-
strongest-control effects while requiring target-task accuracy to be within the
registered tolerance. This is the implemented, limited math-specificity
diagnostic. Because pseudo-FST target length is arithmetic-answer matched, it
cannot by itself separate every arithmetic structural cue from sequential
computation.

In confirmation, seed is the replication unit for ablation, patch, and rescue.
The registered analysis applies paired seed-level tests and Holm correction
across those three contrasts. Retained directional patch rows support a
family-clustered hierarchical bootstrap. This bootstrap evaluates directional
patch superiority; it is not a subspace-stability bootstrap.

Even a complete pass establishes only replication of implemented candidate
effects. The release ceiling cannot be overridden by statistics.

## Output contract

```text
run/
  resolved_experiment.json
  runtime.json
  progress.jsonl
  training/
    seed_<n>/
      training_summary.json
      <arm>/
        progress.jsonl
        metrics.jsonl
        resume_a.pt
        resume_b.pt
        resume_pointer.json
        checkpoints/
  behavior/
    seed_<n>/
      control_audits.json
      <arm>.json
  geometry/
    seed_<n>/
  causal/
    seed_<n>/
    confirmation_statistics.json
  workspace_lock.json
  experiment_summary.json
```

`workspace_lock.json` is produced only by discovery when a valid selection is
available. `experiment_summary.json` contains the candidate ladder,
confirmation statistics, unimplemented required assays, and final
`JSPACE_CLAIM` state. There is no separate `claim_status.json` in v0.4.

## Resume rules

- Rerun the identical command and output path to resume.
- Resume validates resolved configuration, model, tokenizer, runtime, seed,
  arm, optimizer, scaler, RNG, and stream state.
- A mismatch fails closed; use a new output path after any configuration edit.
- `-NoResume` disables resume and should be paired with a new output path.
- Confirmation requires the exact discovery lock and records its hash.
- Do not alter a lock or inspect confirmatory outcomes before changing a
  preregistered threshold.

## Interpretation

A loss curve, exact-match gain, readable direction, balanced eigenvalue,
ablation, patch, rescue, or significant replicated effect is not alone a
workspace. In v0.4, all of them together still yield only candidate evidence
because mediation, native shared access, and component-specific writer rescue
remain absent.
