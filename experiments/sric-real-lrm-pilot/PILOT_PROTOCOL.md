# SRIC Real-LRM Pilot 0.1 Protocol

## 1. Scientific question

The pilot asks a deliberately narrow question:

> Does a released, third-party recurrent latent reasoner use a replayable latent trajectory that carries procedure-specific information beyond the final answer and remains stable under semantics-preserving surface transformations?

This is not equivalent to asking whether latent execution improves accuracy. It is also not equivalent to decoding a hidden state with a supervised probe. The target is a causal property of the actual recurrent trajectory.

For task `i`, let

```text
H_i = (h_i1, ..., h_iK)
```

be the exact sequence of hidden states reinjected into the Coconut latent-token positions. Let `L_i(H)` be teacher-forced loss on the protected answer when trace `H` is supplied.

The primary estimands are:

```text
necessity_i  = L_i(0)          - L_i(H_i)
order_i      = L_i(pi H_i)     - L_i(H_i)
structure_i  = L_i(eta H_i)    - L_i(H_i)
procedure_i  = L_i(H_j)        - L_i(H_i)
twin_i       = L_i(H_i_twin)   - L_i(H_i)
```

Here `j` is a different task with the same answer and approximately matched proof depth, selected to maximize proof-signature distance. `i_twin` is a surface-transformed version of the same logical problem.

A credible procedure-specific pattern is:

```text
necessity > 0
order > 0
structure > 0
procedure > 0
twin approximately 0
```

## 2. Why replay is the first gate

The audit manipulates the recurrent state rather than a descriptive activation readout. If the captured trace cannot reproduce the ordinary computation, the intervention interface is invalid.

The replay gate compares both:

- answer loss under ordinary execution and captured-trace replay;
- answer-token logits under ordinary execution and captured-trace replay.

Failure terminates interpretation with `ADAPTER_INVALID`. No later effect is reported as evidence about the model's reasoning.

## 3. Target runtime

The primary target is the GPT-2 PrOntoQA multimode Coconut checkpoint released by the authors of the associated interpretability repository. The reviewed implementation supports three execution modes within one trained checkpoint:

- direct answer;
- verbalized chain of thought;
- latent hidden-state replacement.

Pilot 0.1 audits the latent mode and preserves the other two modes as later within-checkpoint controls.

The reviewed Coconut recurrence performs the following operation at each latent token:

1. run the causal language model through the token before the latent placeholder;
2. take the final-layer hidden state at that preceding position;
3. replace the latent placeholder's input embedding with that hidden state;
4. continue autoregressive computation with the updated embedding sequence.

The adapter mirrors this process and adds one capability: at each recurrence step, the naturally computed hidden state may be replaced by a supplied vector from a captured or intervened trace.

## 4. Protected outcome

The primary protected outcome is teacher-forced loss on the exact answer suffix:

```text
### True
```

or

```text
### False
```

including the external tokenizer's end-of-sequence token. Prompt, control tokens, attention mask, position IDs, answer suffix, and answer scoring positions are identical across intervention arms.

Greedy generated accuracy is a secondary behavioral metric. Teacher-forced answer loss is primary because it gives a continuous paired effect and avoids answer-extraction failures dominating the causal signal.

## 5. Task selection

The config declares a maximum task count. The selected subset is not the first rows in the dataset. Tasks are ranked by a deterministic SHA-256 function of the frozen seed and task ID, then the first `N` ranks are selected.

This prevents manual or accidental selection of unusually convenient examples. The complete dataset hash and selected task-ID digest are included in the pre-audit seal.

Tasks must be grouped by shared proof template or another dependence unit whenever such metadata is available. The current PrOntoQA loader defaults each original row to its own orbit but exposes `group_id` and `orbit_id` fields for a stronger grouped dataset export.

## 6. Procedure donors

For each recipient, donor selection follows a fixed rule:

1. require the same normalized final answer;
2. prefer the same proof depth;
3. exclude the same orbit;
4. maximize Jaccard distance between normalized proof signatures;
5. break ties by task ID.

The donor plan is generated before the model audit and stored in the seal through a canonical digest.

The proof steps are used for donor construction only. They are not used to train a semantic decoder, set intervention outcomes, or choose thresholds. A stronger later protocol will construct donor groups from formal proof graphs and will reveal graph labels only after the primary latent effects are fixed.

## 7. Semantic twins

The initial semantic twin conservatively reorders premise sentences while preserving:

- the query;
- final answer;
- proof steps;
- proof depth;
- proof signature;
- orbit and group identity.

The twin is not assumed valid merely because a string transformation ran. The package checks protected fields exactly. For the real study, additional twin families should be added only with an exact PrOntoQA verifier:

- entity renaming;
- predicate renaming;
- irrelevant-fact insertion;
- premise paraphrase;
- alternative but logically equivalent ordering.

The pilot's first admissible twin claim is therefore premise-order invariance, not unrestricted paraphrase invariance.

## 8. Interventions

### 8.1 Zero trace

Every reinjected vector is replaced by zero. This tests whether recurrent latent content contributes to answer scoring.

### 8.2 Step permutation

A deterministic derangement reorders the captured latent steps. It preserves the multiset of latent states while disrupting temporal order.

For one-step traces, this test is undefined. The primary configuration requires six latent positions.

### 8.3 Norm-matched noise

For every step, an independent Gaussian vector is normalized to the exact norm of the corresponding captured state. This controls for activation magnitude.

An optional covariance-matched arm samples from a covariance estimated only on the declared calibration split. It must not be estimated on final audit traces.

### 8.4 Procedure transplant

The full donor trajectory is substituted while retaining the recipient prompt and answer. The donor shares the final answer, reducing the answer-only confound.

### 8.5 Semantic-twin transplant

A trace from a premise-reordered semantic twin is substituted into the original task. The expected effect is near zero when the model's latent procedure is stable to the declared transformation.

### 8.6 Truncation

The package scores all prefixes from zero retained latent steps through the complete trace, zeroing subsequent states. The truncation curve is exploratory in Pilot 0.1 and becomes a primary stage-localization object only after a calibration study.

## 9. Gate hierarchy

The status hierarchy is deliberately sequential.

### `ADAPTER_INVALID`

Exact trace replay exceeds the frozen tolerance.

### `LATENT_UNUSED`

Replay succeeds, but zeroing the trace does not produce the predeclared effect and prevalence.

### `LATENT_UNORDERED`

The latent trace contributes, but permuting its steps does not produce a material effect.

### `LATENT_MAGNITUDE_ONLY`

Order matters, but norm-matched structured corruption does not outperform the declared floor.

### `SURFACE_UNSTABLE`

The latent trace is useful and structured but changes materially under the declared semantics-preserving twin.

### `LATENT_GENERIC`

The prior gates pass, but a same-answer, different-proof trace is nearly interchangeable with the task's own trace.

### `PROCEDURE_SPECIFIC`

The same-answer procedure transplant has a positive mean effect and prevalence while semantic-twin transport remains within tolerance.

This last status does not identify the procedure's semantic content. It establishes only that the trajectory is task/procedure conditioned beyond the final answer under the declared donor and twin construction.

## 10. Threshold discipline

The distributed real config contains engineering defaults, not a completed scientific preregistration. Before the first final run:

1. use a disjoint adapter-smoke set to verify mechanics;
2. use a discovery/calibration split to estimate numerical noise and effect variance;
3. freeze thresholds and sample size;
4. create the pre-audit seal;
5. do not change the config after final execution begins.

A threshold change after final outcomes requires a new version, new seal, and new final support. The original result remains preserved.

## 11. Statistical design

All intervention effects are paired within tasks. The package reports:

- mean effect;
- positive-task fraction;
- 95% grouped bootstrap interval.

The bootstrap samples groups rather than assuming every transformed row is independent. The correct grouping level is the proof family, not the rendered text row.

Pilot 0.1 does not use the interval itself as the only gate. Mean magnitude and positive-task prevalence are separately required.

## 12. Pre-audit seal

The seal contains:

- complete audit configuration;
- external repository and exact commit;
- checkpoint repository and full checkpoint SHA-256;
- base-model reference;
- dataset SHA-256;
- selected task-ID digest;
- selected group-ID digest;
- donor-plan digest;
- maximum admissible claim;
- result schema;
- task count.

It contains no audit outcomes.

The real runner recomputes every available field and aborts on disagreement.

## 13. Mandatory controls

The first real result should be interpreted alongside:

- direct-answer mode accuracy;
- verbalized-CoT mode accuracy;
- zero-latent trace;
- random equal-norm trace;
- same-answer procedure donor;
- semantic-twin donor;
- different-answer donor as a weaker reference;
- wrong-depth donor;
- random same-answer donor;
- repeated execution determinism.

Pilot 0.1 implements the central latent interventions. Mode comparisons and expanded donor controls are staged for Pilot 0.2 after the replay contract is validated on the checkpoint.

## 14. Threats to validity

### Formatting confound

Changing control tokens or answer positions can create an apparent latent effect. The adapter holds the complete sequence format fixed.

### Cache confound

An intervention may disagree because cached key/value positions are inconsistent. Exact replay is the guard against this and the trace engine mirrors the pinned runtime's cache slicing.

### Answer-only confound

A different-answer donor damages any trace that encodes the answer. The primary donor shares the answer.

### Surface-code confound

A latent trace may encode prompt wording instead of logical procedure. The semantic-twin test checks one exact surface invariance.

### Donor-quality confound

A donor may be too similar or differ in depth. The donor receipt records answer, depth, and proof-signature distance.

### Dataset leakage

The checkpoint was trained by third parties and may have indirect exposure to task templates. The pilot is a mechanistic audit of the released checkpoint, not an untouched benchmark claim. Future audits require a new generator-foreign PrOntoQA support.

### Semantic circularity

Gold proof steps used to construct donors cannot also independently validate an inferred semantic factor. Pilot 0.1 therefore stops at procedure specificity. Block 23 and Pilot 0.2 require a separate ontology-construction and post-seal witness split.

## 15. Result interpretation

A positive Pilot 0.1 result supports:

> Within the audited task support and execution format, the checkpoint uses a replayable, temporally structured latent trajectory whose replacement by a same-answer but different-proof trajectory damages answer scoring, while a declared semantic twin remains compatible.

It does not support:

- a unique English translation of each latent state;
- complete proof reconstruction;
- causal identification of particular proof variables;
- interpretability on unrestricted inputs;
- cross-model semantic equivalence.

## 16. Next empirical stage

Pilot 0.2 should begin only after the real Pilot 0.1 receipt exists. Its target is endogenous semantic-witness discovery:

1. construct anonymous intervention orbits without gold intermediate labels;
2. fit minimum-complexity predictive/interventional quotients;
3. seal the quotient and validation thresholds;
4. reveal formal proof graphs afterward;
5. test counterfactual latent editing;
6. transport any surviving factor to multimode CODI.

A `LATENT_UNUSED` or `LATENT_GENERIC` Pilot 0.1 result is not a reason to force Pilot 0.2. It is a valid checkpoint-specific obstruction certificate.
