# Arithmetic J-Space Training Lab v0.4.0

## Event-sampler hotfix

This build replaces rare-event rejection sampling with a constructive
exactly-one-carry or exactly-one-borrow generator. It fixes the deterministic
`carry_discovery` failure at the first 10-digit OOD evaluation. An original
v0.4.0 discovery run is accepted only when its resolved configuration differs
solely by the allowlisted package-manifest update. The migration is recorded in
`package_hotfix_migration.json`, and training resumes from the latest valid
rolling checkpoint.

This package trains standard decoder-only transformers from scratch on
answer-only addition and subtraction, then tests a **candidate balanced causal
arithmetic subspace**. It does not insert a workspace, supervise a hidden
space, use answer labels during subspace discovery, or modify a trained model
to create the candidate.

The shipped task uses positive integer operands and nonnegative results;
subtraction operands are ordered to avoid negative answers. It does not test
signed arithmetic, zero identities, multiplication, or division.

Version 0.4 is deliberately candidate-only. It can establish behavioral
competence and run target-blind geometric and causal diagnostics, but it cannot
establish a J-space equivalent. Formal causal mediation, native shared
multi-query access, and component-specific upstream-writer rescue are not
implemented. Every profile therefore reports:

```text
JSPACE_CLAIM=NOT_ESTABLISHED
```

## Recommended Windows run

Use the known `komorebi-full` Python explicitly:

```powershell
$d="$env:USERPROFILE\Downloads\Arithmetic_JSpace_Training_Lab_v0.4.0"; & "$d\Run_Arithmetic_Workspace_Experiment.ps1" -Profile carry_discovery -Python "$env:USERPROFILE\miniconda3\envs\komorebi-full\python.exe" -Device cuda -SkipInstall
```

The command runs all three discovery seeds. It is resumable: rerun the
identical command after interruption. Progress is printed and flushed every
100 optimizer steps. Light evaluation runs every 500 steps and full evaluation
every 2,000 steps in the serious profiles.

## Profiles

| Profile | Purpose | Model | Seeds × arms × steps |
|---|---|---:|---:|
| `workspace_smoke` | Fast engineering and resume check | 3 layers, width 128 | 1 × 4 × 20 |
| `carry_discovery` | Exploratory layer/rank discovery | 12 layers, width 512, ~38M parameters | 3 × 4 × 60,000 |
| `carry_confirmatory` | Locked replication of candidate assays | Same ~38M model | 8 × 4 × 80,000 |

`carry_confirmatory` requires the `workspace_lock.json` written by a completed
discovery run. It is a locked candidate replication—not a profile capable of
establishing a J-space claim.

On an 8 GB RTX 3070 Ti Laptop GPU, budget minutes for smoke, roughly 3–9 days
for discovery, and roughly 12–35 days for the full confirmation. These are
planning ranges. Use the measured ETA after the first 500 steps of each arm.
Keep roughly 30 GB free for the default discovery checkpoints and 80 GB for
the full locked replication. Exact use depends on checkpoint serialization and
the number of completed arms; outputs are not deleted automatically.

## Scratch model and objective

- fixed 260-token byte vocabulary (`0..255`, PAD, BOS, SEP, EOS)
- prompt-masked causal loss on answer bytes and EOS only
- pre-normalized causal decoder with rotary positions
- no pretrained weights, scratchpad, carry trace, auxiliary representation
  loss, bottleneck, or probe loss
- AdamW with warmup-stable-decay learning-rate schedule
- BF16 when supported, otherwise scaled FP16 on CUDA
- rolling atomic resume checkpoints and immutable research checkpoints

The primary model is not Qwen or another downloaded model.

## Four arms

| Arm | Training target | Role |
|---|---|---|
| `correct` | Exact addition/subtraction | Arithmetic candidate |
| `no_carry` | Exact arithmetic restricted to zero-carry/zero-borrow training rows | Restricted-computation behavioral control |
| `pseudo_fst` | Seeded finite-state digit values with arithmetic-answer-matched length | Pseudo-valued sequential control, arithmetic-answer-length matched |
| `deranged` | Audited random value derangement | Random-label/format control |

`correct`, `pseudo_fst`, and `deranged` use the same input-expression order and
paired initial weights. `no_carry` necessarily uses a different restricted
training stream; it is not globally prompt-, token-, or answer-width-matched.
The exact shared comparison with it is the sealed `no_transfer` panel.

Each derangement window first attempts a seeded random value permutation within
operator/output-width nuisance strata, never a lexical sort-and-rotate. An
underdetermined stratum is deterministically coarsened to output-width-only
pooling when needed. Exact empirical target-multiset preservation and zero
source/assigned value fixed points remain mandatory for every nonsynthetic
stratum, including a successfully coarsened stratum. Within a seeded candidate,
synthetic labels are not considered until exact operator/output-width and exact
output-width-only constructions are mathematically impossible. Additional
seeded candidates serve the residual-correlation and string-agreement gates.

Only when an output-width-only stratum of at most 31 rows makes such a value
derangement mathematically impossible does the final fallback synthesize
canonical same-width decimal labels, deterministically and with no
source/assigned value fixed points. Synthetic rows therefore do **not**
preserve the empirical target multiset. Their count and total-window fraction
are explicitly reported in the control audit. The 31-row limit applies to each
impossible width stratum separately. The strict fraction cap is
`0.001` (0.1%); the audit records the cap and pass/fail result, and the run fails
closed if the cap is exceeded. A constructed window that uses the fallback
emits one `DERANGEMENT_SYNTHETIC_FALLBACK` telemetry line. This fallback weakens
the deranged control, but prevents a rare finite training window from becoming
impossible to construct. The
residual-correlation gate uses the absolute row-weighted Pearson correlation
over predeclared eligible strata. Tiny or degenerate strata are still reported
but excluded from that gate using the fixed eligibility rule in
`workspace_data.py`.

## Target-blind balanced-space discovery

Discovery receives tokenized prefixes ending at SEP. It rejects answer tokens
and EOS. Upstream residual perturbations estimate empirical controllability;
gradients of fixed, answer-independent output summaries estimate local
observability. The summaries are exactly:

- digit log-probability mass
- EOS log probability
- minus-sign log probability
- output entropy
- top log probability
- four sealed random projections of the vocabulary log-probability vector

The leading directions of

\[
G_c^{1/2}G_oG_c^{1/2}
\]

form the candidate. Rank is selected by heldout prediction of changes in those
same target-free summaries. Rank-matched controls are PCA, one seeded random
subspace, and a complementary balanced-spectrum subspace. There is no
bootstrap-stability assay or distribution of many random subspaces in v0.4.

Geometry runs only after target-task competence and is fitted independently in
the competent `correct` and `pseudo_fst` arms. Their causal effects are compared
as a limited specificity diagnostic. The pseudo-FST controls digit values but
deliberately uses the true answer width to match output length. It therefore
retains a coarse arithmetic-derived schema signal and is not an entirely
arithmetic-free control.

## Implemented causal assays

On sealed, semantically matched carry/borrow counterfactual pairs, every basis
(candidate, PCA, random, complement) receives the same free-generation tests at
the final prefix SEP position:

1. candidate-coordinate ablation
2. clean-to-corrupt coordinate patching with directional digit audit
3. independent transplant of a corrupt donor residual at an earlier layer
4. restoration of only the registered source-layer coordinates after that
   upstream transplant

Control interventions are rank-matched and scaled to the candidate intervention
energy for the same state. Candidate fitting and selection never receive
answers. After the candidate is frozen, sealed answers and their widths are
used to construct/match counterfactual pairs, define eligibility, and score
free generation.

Primary rates are computed only on qualified pairs. Ablation requires a valid,
EOS-terminated natural clean answer. Patching requires valid and correct natural
clean and corrupt answers with distinct targets. Rescue additionally requires
the unrescued upstream corrupt-donor transplant to generate the corrupt target
exactly. Discovery requires at least 128 baseline-qualified pairs and 32 such
directional rescue pairs; locked confirmation requires 512 and 128. A missing
denominator fails closed rather than being treated as a null effect.

The upstream transplant is a residual-state intervention, not a head/MLP writer
intervention. Coordinate rescue is not a formal mediation analysis. No native
shared multi-query assay or unrelated-language preservation assay is bundled.

## Statistics and evidence ceiling

Confirmation retains item-level outputs. Seed is the replication unit for
candidate-minus-strongest-control ablation, patch, and rescue effects. The
registered analysis uses paired seed tests, Holm familywise correction, and a
family-clustered hierarchical bootstrap of directional patch effects.

These statistics can support a replicated **candidate effect**. They cannot
override the v0.4 claim ceiling. Missing formal mediation, shared multi-query
access, and component-specific writer rescue keep the claim state
`NOT_ESTABLISHED` even if every implemented comparison passes.

## Output and resume

The result directory contains:

```text
resolved_experiment.json
runtime.json
progress.jsonl
training/seed_<n>/<arm>/
behavior/seed_<n>/
behavior/seed_<n>/control_audits.json
geometry/seed_<n>/
causal/seed_<n>/
causal/confirmation_statistics.json
workspace_lock.json              # discovery only, if a selection passes
experiment_summary.json
```

Rerunning the same command resumes. A resolved-config mismatch fails closed;
use a new `-Output` path for a changed run. `-NoResume` disables resumption.

For exact preregistered comparisons and limitations, read
`EXPERIMENT_DESIGN.md` and `WORKSPACE_PROTOCOL.md`.
