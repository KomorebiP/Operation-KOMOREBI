# Micro OSL Experiment Protocol

## 1. Scientific question

The primary question is:

> Can a randomly initialized text model trained only to answer questions recover operator structure that transfers across disjoint vocabulary, unseen compositions, exact algebraic equivalences, longer programs, counterfactual changes, and episode-specific operator renaming?

The experiment separates that question from a second engineering question:

> Can answer-supervised calibration teach episode-local role binding that transfers to entirely unseen nonce vocabularies?

Only the untouched answer-only arm addresses the first question. The primary test of the second question is the fixed-volume `role_bind_augmented - role_bind_scrambled` contrast: the two arms differ in calibration meaning while matching canonical records, nonce exposure, token multiset, model initialization, and training budget. The explicitly supervised and regularized arms remain engineering comparisons.

## 2. Fixed hypotheses

### H0: task-pattern hypothesis

The model can learn local answer regularities but will not reliably transfer to held-out operator compositions or arbitrary episode-specific renamings. Any apparent latent structure will be explained by lexical controls, complete-state supervision, or regularization.

### H1: reusable operator hypothesis

Answer-only training produces a representation that supports systematic behavior on held-out pairs and triples, episode-specific renaming, exact laws, and matched counterfactuals beyond classical controls.

### H2: learned role-binding hypothesis

Answer-only training fails episodic renaming, while correct same-volume answer-supervised calibration reliably beats a meaning-scrambled calibration control, uses correct rather than scrambled calibration at test time, and preserves canonical composition performance. This is learned meta-binding, not spontaneous emergence.

### H3: engineered induction hypothesis

Answer-only training fails the strongest tests, but state, equivalence, or operator-law objectives produce reliable systematic behavior. This is useful symbolic induction, but it is not spontaneous emergence.

The protocol allows these outcomes to be distinguished. A failed emergence claim is still an informative boundary result.

## 3. Frozen experiment units

Before the first standard neural run, preserve:

- the source zip and its SHA-256
- `configs/confirmatory.json`
- `configs/standard.json`
- `configs/full.json`
- generated dataset manifests and shard hashes
- the held-out pair and triple tables
- renderer and lexicon definitions
- primary metrics and comparison rules
- seed schedule
- behavioral and learned-binding gate thresholds
- package and driver report from `doctor`

Do not repair the hard test using information from its neural results and then report the repaired test as if it had been held out from the beginning. A repaired benchmark starts a new protocol version.

## 4. Experimental conditions

### 4.1 Classical controls

Run these before neural training:

1. Global majority
2. Question-conditioned majority
3. Word and bigram TF-IDF with logistic regression

The strongest control for each split is the maximum accuracy among eligible controls on that split. If TF-IDF performs unexpectedly well on a hard split, inspect template and token leakage before training a neural model.

### 4.2 Neural architecture

Version 0.1 uses a compact PyTorch transformer encoder initialized from a fixed random seed. Input is encoded as:

```text
[CLS] story [SEP] question [SEP]
```

One shared vocabulary is fitted on the frozen union of all three central training sources and serialized into each checkpoint. One shared answer encoder is derived exhaustively from the formal query outputs over every legal state in the three declared finite worlds; it never reads sampled training or evaluation labels. State and operator encoders remain arm-specific and use only that arm's effective corpus when their structural objectives require them. Alphabetic word tokens are assigned to a fixed bank of deterministic SHA-256 hash buckets, so an unseen nonce keeps a stable identity instead of collapsing to a universal unknown token. The assignment uses spelling only and never reads evaluation labels; the bundled nonce pool is collision-free under the frozen 2,048-bucket setting. Each arm records a pre-optimization initialization contract covering the tokenizer, exact answer-label ordering, parameter schema, and model-state SHA-256. The runner refuses to accept the completed cell unless all four identities match across the central arms. The model uses token, position, and segment embeddings, a transformer encoder stack, a pooled representation, and an answer classifier. Structural heads are enabled only when required by the selected arm.

No pretrained weights, model hubs, web corpora, or external embeddings are used.

### 4.3 Training arms

#### Answer only

Optimize categorical answer cross-entropy:

\[
L=L_{\mathrm{answer}}.
\]

The loader must not pass the formal program, final state, transformation identifier, or state trace into the model.

#### Role binding augmented

Use the same answer cross-entropy and architecture as `answer_only`. In the confirmatory preset, replace a frozen 20 percent of canonical training records with calibrated nonce-command episodes; exploratory presets use their explicitly recorded shard sizes. The effective training count stays unchanged:

\[
L=L_{\mathrm{answer}}.
\]

Nonce meanings are permuted by episode. Optimization and evaluation nonce vocabularies are disjoint and collision-checked under the tokenizer's frozen hash scheme. This arm tests whether a binding procedure can be learned from answer supervision; it is not eligible for a spontaneous-emergence claim.

#### Role binding scrambled

Use the same retained 80 percent canonical shard and the same calibration episodes as `role_bind_augmented`, but apply a deterministic nonidentity permutation to the nonce meanings shown in each calibration section. The target section, answer, record count, and model-token multiset are matched. This is the primary negative control for additional text, nonce exposure, and optimization volume.

The confirmatory arms train for exactly eight epochs with identical optimizer settings. The final (`last_checkpoint.pt`) checkpoint is evaluated. IID validation is recorded as a diagnostic but does not select a different training duration or checkpoint for the primary contrast.

#### State supervised

Add exact final-state classification:

\[
L=L_{\mathrm{answer}}+\lambda_sL_{\mathrm{state}}.
\]

This condition tests whether explicit formal-state pressure creates more transferable internal organization.

#### Equivalence regularized

Pair different records sharing a complete transformation identifier. Attract matched representation vectors and repel a rolled non-equivalent control above a margin:

\[
L=L_{\mathrm{answer}}+\lambda_eL_{\mathrm{equiv}}.
\]

The pairing variable is the exact transformation signature, not merely agreement on one example.

#### Operator regularized

Learn an operator-matrix bank and align its composed program representation with the text representation. Penalize declared identity, idempotence, inverse, and commutation violations where applicable:

\[
L=L_{\mathrm{answer}}
+\lambda_aL_{\mathrm{align}}
+\lambda_\ell L_{\mathrm{laws}}.
\]

#### Combined

Use every implemented structural objective:

\[
L=L_{\mathrm{answer}}
+\lambda_sL_{\mathrm{state}}
+\lambda_eL_{\mathrm{equiv}}
+\lambda_aL_{\mathrm{align}}
+\lambda_\ell L_{\mathrm{laws}}.
\]

Every training summary must report the realized component losses. A configured component that remains identically zero is an implementation failure, not a negative scientific result.

## 5. Seed schedule

Use seed 1729 for smoke. The frozen confirmatory matrix crosses two independently generated datasets with three model initializations:

```text
data seeds:  1729, 2718
model seeds: 1729, 2718, 31415
```

Run all six crossed-seed cells and all three central arms through `RUN_NEXT_OSL_TEST.ps1`. Report every cell, including failed and interrupted runs. Partial directories are excluded from numerical aggregation but remain listed; do not retain only the best seed. Within-cell deltas are summarized separately by data seed and model seed; the six cells are not treated as six independent datasets.

When computing uncertainty across examples, remember that examples from the same semantic trace or counterfactual pair are not fully independent. Pair-level or semantic-unit resampling is preferred for a final paper. The built-in example bootstrap is a descriptive interval, not a substitute for replication across seeds.

## 6. Execution sequence

### Phase A: installation and smoke

1. Run `Setup_Environment.ps1` once.
2. Run `Check_Dependencies.ps1` with the intended device.
3. Run `Run_Smoke.ps1`.
4. Confirm the CLI, generator, validator, baseline, one-epoch model, evaluation, report, and verification artifacts exist.

Smoke is an engineering check only.

### Phase B: dataset audit

1. Run the confirmatory wrapper, which freezes and snapshots `configs/confirmatory.json` for every cell.
2. Preserve the generated manifest and hashes.
3. Run validation.
4. Inspect at least 30 random records from every split.
5. Check class and query frequencies by split and world.
6. Confirm held-out transformation overlap is zero.
7. Confirm every declared law passes exhaustive enumeration.
8. Confirm counterfactual pairs and renaming mappings are complete.

If any integrity check fails, stop before training.

### Phase C: lexical controls

Run majority and TF-IDF controls on every split. Record the strongest control separately for each split. The hard splits should not be easy for a lexical model.

### Phase D: answer-only boundary

Train `answer_only` first. Evaluate all splits without inspecting supervised-arm results. Preserve:

- best and last checkpoints
- training history
- validation accuracy
- per-split and per-world metrics
- full predictions
- counterfactual pair metrics
- exact law consistency
- quotient and algebra residual summaries

Write a short adjudication of the answer-only boundary before continuing.

The automatic `EVIDENCE_ADJUDICATION.json` applies only the frozen behavioral gates. Its PASS means those gates passed in that run; it is never automatically promoted to an emergence or latent-causality claim.

### Phase E: focused learned-binding contrast

Run `role_bind_scrambled` and `role_bind_augmented` in the identical dataset/model seed cell, with shared tokenizer, verified common initialization, architecture, effective training count, optimizer budget, and evaluation shards. The primary contrast is correct minus scrambled calibration. Report renamed accuracy, prediction consistency, pair-joint correctness, the canonical-to-renamed robustness gap, correct-minus-scrambled test accuracy, and prediction change under the test-time scrambling intervention. Check lexical, pair, and triple performance for tradeoffs rather than reporting renaming alone. `answer_only` remains a contextual boundary, not the primary causal control for calibration meaning.

### Phase F: optional supervision factorial

Run `state_supervised`, `equivalence_regularized`, `operator_regularized`, and `combined` with the same training records, initialization seed schedule, optimization budget, and evaluation shards.

The relevant comparisons are paired by seed and split:

```text
answer_only versus state_supervised
answer_only versus equivalence_regularized
answer_only versus operator_regularized
answer_only versus combined
```

This identifies which pressure is responsible for each gain.

### Phase G: optional full factorial

Use the full preset only after the code, data protocol, and interpretive thresholds are frozen. Run all configured arms and all seeds. Full scale cannot repair an invalid split or an ambiguous metric.

## 7. Primary behavioral measurements

Report exact answer accuracy and macro F1 for every split and world, plus world-macro, query-macro, minimum-world, and minimum-query accuracy. Treat these as separate endpoints:

- independent IID test accuracy (`iid_validation` is never reported as test evidence)
- lexical accuracy
- held-out pair accuracy
- held-out triple accuracy
- law-side consistency and accuracy
- length accuracy by exact program length
- canonical, correct-calibration, and scrambled-calibration accuracy; triplet completeness; paired prediction consistency; pair-joint correctness; robustness gap; correct-minus-scrambled accuracy; prediction change; and correct-only success
- counterfactual affected joint accuracy
- counterfactual unaffected joint accuracy
- change sensitivity
- invariance specificity
- pair-level completeness
- pair-level specificity

Counterfactual sensitivity alone is insufficient. A model that changes every answer has perfect sensitivity and no specificity. Both affected correctness and preservation of unaffected predictions matter.

## 8. Structural measurements

The package computes relative Frobenius residuals for learned operator matrices.

Idempotence:

\[
\epsilon_{\mathrm{idem}}(Q)
=
\frac{\|Q^2-Q\|_F}{\|Q\|_F+\varepsilon}.
\]

Commutation:

\[
\epsilon_{\mathrm{comm}}(A,B)
=
\frac{\|AB-BA\|_F}
{\|AB\|_F+\|BA\|_F+\varepsilon}.
\]

Inverse:

\[
\epsilon_{\mathrm{inv}}(A,B)
=
\frac12\left(
\frac{\|BA-I\|_F}{\|I\|_F+\varepsilon}
+
\frac{\|AB-I\|_F}{\|I\|_F+\varepsilon}
\right).
\]

Composition:

\[
\epsilon_{\mathrm{comp}}(C;A,B)
=
\frac{\|C-AB\|_F}
{\|C\|_F+\|AB\|_F+\varepsilon}.
\]

Residuals must be compared with behavioral success. Small learned matrices can satisfy a law approximately while carrying little useful information.

## 9. Exact and fuzzy quotient analysis

For concrete transition matrices \(P_g\), membership matrix \(W\), and fitted symbolic operator \(M_g\), report

\[
\epsilon_g
=
\frac{\|P_gW-WM_g\|_F}
{\|P_gW\|_F+\varepsilon}.
\]

Also report the observation reconstruction residual for \(O\approx WD\), mean membership entropy, effective symbol count, minimum symbol mass, and behavior after hardening.

The exact partition routine computes the coarsest observation-respecting deterministic quotient for the finite transition system. The fuzzy sweep is a structural analysis of the finite world. Unless it is explicitly fitted from neural activations, it is not evidence that the neural model discovered the same quotient.

## 10. Decision rules

A result supports ordinary task learning when IID accuracy beats controls but the hard splits do not.

A result supports lexical robustness when the lexical split improves beyond controls across seeds.

A result supports compositional generalization when both held-out pair and held-out triple results improve beyond the strongest controls across the crossed-seed matrix, with no hidden transformation overlap and no failure hidden by pooled world/query scores.

A result supports spontaneous episode-level operator remapping only when the answer-only arm passes composition, complete renaming-triplet, calibration-content, counterfactual, balance, and control gates across seeds and the nonce mapping is provably permuted by episode. Improvement confined to `role_bind_augmented` supports learned binding only when it beats `role_bind_scrambled` under the preregistered H2 gate: at least 0.05 mean gains in renamed accuracy and pair-joint correctness, at least 0.05 mean correct-versus-scrambled test-calibration gain, positive direction in at least five of six cells and each data-seed mean, absolute correct-arm renaming thresholds, and no mean held-out pair or triple loss greater than 0.05.

A result supports behavioral counterfactual fidelity only when affected joint accuracy and invariance specificity both improve. Changing the right outputs while preserving unrelated outputs is the target.

A v0.1 result does not establish activation-level causal mediation. The package intervenes on formal input programs through matched counterfactual examples. It does not yet perform hidden-state interchange, targeted ablation, matched random-direction intervention, or rescue. Those are required for the stronger E4 claim described in `RESULT_INTERPRETATION.md`.

## 11. Stopping and failure rules

Stop and mark the run invalid if:

- dataset validation fails
- a hard-test complete transformation overlaps training
- the answer-only loader receives formal fields
- central arms do not share an initial-model hash for the same model seed
- the correct and scrambled calibration corpora fail their matched-pair or token-multiset audit
- a configured loss component is silently absent
- a checkpoint cannot be verified or deterministically loaded
- predictions cannot be paired back to immutable record identifiers
- a result directory was partially overwritten
- a dependency or model attempted an undeclared network download

Out-of-memory failure is not a scientific failure. Reduce batch size while preserving model, data, seed, and effective optimization semantics, then record the configuration change. Do not silently fall back from forced CUDA to CPU.

## 12. Reproducibility record

For each result retain:

- package version and source hash
- Python, NumPy, scikit-learn, PyTorch, CUDA, and driver versions
- selected device
- resolved JSON configuration
- separate data and model seeds
- dataset manifest and hashes
- exact config/package hashes and cross-model-seed equality of dataset shard hashes
- effective-corpus ordered-content digest, counts, and token-length summary for every arm
- model parameter count
- shared-tokenizer source hashes and initial-model hash
- checkpoint hashes
- training history
- every prediction joined to record ID
- evaluation and quotient outputs
- plain UTF-8 runner and Python logs
- verification report

The report must distinguish completed, interrupted, resumed, invalidated, and excluded runs.
