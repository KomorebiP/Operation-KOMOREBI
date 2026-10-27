# SRIC Block 24 Protocol

## External Latent-Reasoner Causal-Semantic Admission

### 1. Purpose

Block 24 is the first SRIC protocol designed to admit or reject a third-party latent-reasoning checkpoint under a frozen causal and semantic standard. The primary target is the multimode GPT-2 Coconut model trained on PrOntoQA. The protocol treats a negative result as complete evidence when the failure is reproducible and correctly localized.

### 2. Primary scientific question

Does the recurrent latent trace of the external checkpoint carry content-specific, ordered, structured information that causally contributes to its answer and supports a post-seal low-rank semantic quotient?

The protocol does not initially ask whether every latent step has a unique English translation. It asks whether the latent computation has operationally identifiable causal content.

### 3. Source lock

The external model is admitted only when all of the following match the bundled lock:

- repository: `connordilgren/are-lrms-easily-interpretable`;
- commit: `32f413d8d55239d9bc54bb6b6ec37b0630891ed4`;
- multimode wrapper Git blob: `d0b353cd78f98ab7aae0d20ce4e8859d9fd9958e`;
- Coconut recurrence Git blob: `646acb08f149afec075eefb212c8aa1f3ac8ceda`;
- requirements Git blob: `4a63ea4b92f0dd565f5d632241e36299695237e4`;
- PrOntoQA test-data Git blob: `7222832226883a545328f2398dc4976b1bb85c7d`;
- checkpoint repository revision: `4ec759a9f9b8a8e7e1a8d1e3e2d43eef969ac83f`;
- checkpoint filename: `checkpoint_37`;
- GPT-2 base revision: `607a30d783dfa663caf39e06633721c8d4cfcd7e`.

The downloaded checkpoint is hashed in full. The complete local base-model payload is hashed as a path-size-file-digest tree with download metadata excluded.

### 4. Adapter contract

The adapter must expose the exact vectors reinjected at latent-token positions. It must support:

- ordinary latent capture;
- exact supplied-trace replay;
- direct-answer mode;
- post-seal verbalized mode;
- teacher-forced protected answer scoring.

The trace engine is compared against a separately written reference implementation of the reviewed source recurrence. Exact replay is then tested on every audit row. A replay error above the frozen tolerance returns `ADAPTER_INVALID` and terminates all later interpretation.

### 5. Population and grouping

Tasks are selected deterministically from the pinned public data. Splits are made by `group_id`, not by transformed text row, so semantic twins and related records cannot cross evidence partitions.

For the primary 64-task profile:

- 20% of groups are reserved for covariance calibration;
- the remainder forms the causal audit population;
- if causal admission succeeds, that population is split into 50% semantic discovery, 25% semantic calibration, and 25% semantic final support.

The exact row counts depend on group sizes and are frozen in the pre-audit seal.

### 6. Causal interventions

For task `i` with clean trace `H_i` and clean answer loss `L_i`, the protocol computes:

#### Exact replay

`r_i = max_abs(logits(clean) - logits(replay(H_i)))`.

#### Latent necessity

`n_i = L_i(zero trace) - L_i`.

#### Step order

`o_i = L_i(permuted trace) - L_i`.

#### Norm-matched structure

`c_i = L_i(norm-matched noise) - L_i`.

#### Covariance-matched structure

A nuisance covariance is estimated only on the reserved calibration support. The audit effect is:

`c_cov_i = L_i(covariance-matched noise) - L_i`.

#### Same-answer content transplantation

A donor has the same final answer, preferentially the same proof depth, a different orbit, and maximal proof-signature distance within the frozen donor population:

`s_i = L_i(H_donor_same_answer) - L_i`.

This is a content/proof-instance specificity test. On PrOntoQA it is not labeled a different-algorithm procedure test.

#### Different-answer transplantation

This is a weaker positive control showing sensitivity to answer-bearing task differences.

#### Semantic-twin transplantation

The premise order is deterministically changed without changing the protected answer, proof chain, group, or proof signature:

`t_i = L_i(H_twin) - L_i`.

A strong result requires content sensitivity together with twin stability.

#### Truncation

The model is scored with zero through K retained latent steps to estimate when near-clean performance appears.

### 7. Causal status ordering

The status is assigned lexicographically:

1. replay;
2. necessity;
3. order;
4. structured corruption;
5. semantic-twin stability;
6. declared specificity tier.

The first failed gate determines the terminal causal status. This prevents a strong later statistic from compensating for an invalid adapter or unused latent loop.

### 8. Mode controls

Direct-answer mode is permitted during causal admission because it uses no gold proof. Verbalized mode appends the protected proof steps and is therefore inaccessible before the semantic quotient seal.

The explicit-CoT result is descriptive. It may help interpret a sealed quotient, but it may not determine its basis, rank, thresholds, or acceptance.

### 9. Semantic construction interface

Semantic escalation occurs only after `CONTENT_SPECIFIC` or `PROCEDURE_SPECIFIC` causal admission.

The constructor sees:

- current latent state;
- next latent state;
- answer-residual future state;
- anonymous query-polarity intervention response;
- final answer label;
- semantic-twin relation.

It does not see the protected proof-instance witness or explicit-CoT trace.

### 10. Candidate grammar

The finite grammar contains:

- answer-only rank-one direction;
- PCA directions;
- predictive directions;
- intervention-response directions;
- joint predictive-interventional directions;
- equal-rank random directions;
- full-state descriptive upper control.

Candidate bases are canonicalized for deterministic signs and orthonormality.

### 11. Candidate gates

A candidate must exceed frozen thresholds for:

- future-state `R^2`;
- answer-residual future-state `R^2`;
- intervention-response `R^2`;
- final-answer accuracy;
- semantic-twin drift;
- maximum rank.

Among valid candidates, the minimum rank is selected. Ties are broken by weakest normalized margin and then a frozen method order. Full state is not eligible.

### 12. Semantic chronology

The order is enforced in code and tested:

1. declare group-disjoint discovery, calibration, and final IDs;
2. capture discovery semantic orbits;
3. capture calibration semantic orbits;
4. construct candidates;
5. evaluate candidates only on calibration;
6. select quotient;
7. hash basis, center, split IDs, and thresholds into the quotient seal;
8. capture final semantic orbits only after that seal exists;
9. fit heads on discovery plus calibration;
10. evaluate final construction metrics;
11. reveal post-seal witness;
12. run causal subspace patching;
13. reveal explicit-CoT comparison.

### 13. Post-seal proof-instance witness

The current PrOntoQA witness includes answer polarity, recurrent progress, and an audit-only proof-instance coordinate derived from the protected proof signature. It is deliberately described as proof-instance content, not an algorithmic procedure ontology. A stronger ProsQA witness will use explicit graph-structural features.

### 14. Causal subspace patching

For a selected basis `B`, the projector is `P = B B^T`. A donor semantic packet is inserted while preserving the orthogonal complement:

`H_patch = H_recipient + (H_donor - H_recipient) P`.

The selected packet is compared with:

- full-trace transplant;
- answer-only packet;
- random equal-rank packet;
- PCA packet as a descriptive control.

The causal gate requires a minimum recovery ratio, positive-task fraction, and superiority over answer-only and random shortcuts.

### 15. Statistical reporting

Effects are reported for the complete causal audit population. Bootstrap intervals resample task rows. For final publication, proof-template or group-level resampling should be preferred whenever public metadata support it.

Correct and incorrect model predictions must be reported separately in the real-result summary. A necessity-positive stratum may be reported only as a secondary predeclared analysis; it may not replace the full population.

### 16. Result interpretation

- `LATENT_UNUSED`: no evidence that the checkpoint relies materially on its latent loop in this population.
- `LATENT_GENERIC`: evidence for useful ordered latent computation, but not enough same-answer content specificity.
- `CONTENT_SPECIFIC`: the latent trace is tied to proof-instance content beyond final-answer identity.
- `ONTOLOGY_UNDERIDENTIFIED`: no small quotient satisfied the observable causal-predictive contract.
- `SEMANTIC_CANDIDATE`: a quotient passed construction but not the post-seal proof-instance witness.
- `SEMANTICALLY_IDENTIFIED`: the witness passed, but subspace editing did not.
- `CAUSALLY_VALIDATED`: the sealed quotient passed construction, post-seal witness, and causal patching.

No status means that the trace is a complete or unique transcript of hidden thought.

### 17. Engineered positive control

The package includes a synthetic adapter whose trace contains a low-rank causal content packet and high-variance nuisance dimensions. The fixture validates the transaction and analysis mechanics. It reaches `CAUSALLY_VALIDATED` by design and is always marked `engineered_positive_control: true`.

### 18. Threats to validity

#### Adapter mismatch

Mitigation: source-lock verification, recurrence parity test, exact replay, fixed tokenization and suffix.

#### Final-support leakage

Mitigation: final semantic orbits are not captured until after quotient sealing; explicit CoT is post-seal only.

#### Answer shortcut

Mitigation: same-answer donors and answer-residual future prediction.

#### Surface shortcut

Mitigation: premise-order twins and later distractor/renaming orbit extensions.

#### Procedure overclaim

Mitigation: PrOntoQA status is content-specific; procedure-specific status is reserved for varied structural tasks.

#### Noise miscalibration

Mitigation: covariance is estimated on group-disjoint calibration rows.

#### Unsupported semantic edit

Mitigation: causal patching is compared with equal-rank shortcut controls and can fail independently of probe scores.

#### Post-result threshold changes

Mitigation: config, model, source, dataset, donors, splits, and output contract are sealed before execution.

### 19. Hardware plan

The primary target is intentionally small. The recommended configuration for an 8 GB RTX 3070 Ti is batch size one, deterministic inference, short prompts, capture caching, and moving saved traces to CPU. The package does not retrain the external model.

### 20. Escalation path

1. Run 12-task smoke solely to validate source parity and replay.
2. Run 64-task primary without changing gates.
3. Inspect the canonical status and failure coordinate.
4. Run the 256-task profile only if the adapter remains valid.
5. Add ProsQA only after PrOntoQA produces a stable causal result.
6. Add CODI or another latent method for cross-model transport only after one checkpoint has a valid semantic object.
7. Add SLPO for adaptive-depth analysis.
8. Add Hyper as a scale stress.

### 21. Stopping rules

- Replay failure: stop and repair the adapter; do not interpret latent interventions.
- Out-of-memory during smoke: reduce runtime memory, not scientific thresholds.
- `LATENT_UNUSED`: preserve as the primary result; do not filter to successful tasks as the headline.
- `LATENT_GENERIC`: do not run semantic escalation.
- No valid quotient: report `ONTOLOGY_UNDERIDENTIFIED`.
- Causal patch failure: do not call the quotient causally validated.

### 22. Current execution status

The source-locked external checkpoint was not executed in the environment used to build this package. That environment had CPU-only PyTorch, no Transformers installation, no external checkout, no checkpoint, no public dataset, and no CUDA device. The package's validated result is the engineered fixture only.

### 23. Decision after the first real receipt

The first real receipt should determine the next move:

- adapter invalid -> repair only adapter fidelity;
- latent unused -> test a second published checkpoint or task, without rewriting the result;
- latent generic -> compare latent and direct modes and stop semantic claims;
- content specific -> execute sealed quotient construction;
- semantic candidate -> improve independent witness design in a new protocol version;
- causally validated -> proceed to ProsQA structure sensitivity and cross-model transport.
