# Block 24 Brainstorm and Design Decisions

## Why the next gap is empirical

Blocks 16-23 progressively established a synthetic theory of latent causal auditing, semantic charts, cross-architecture transport, obstruction-guided repair, unpaired alignment, and endogenous semantic quotient construction. Another synthetic positive control would add less evidence than testing whether the same gates survive contact with a checkpoint designed by an independent group.

The central next question is therefore not whether another controlled fixture can be made to pass. It is whether a source-locked external latent reasoner lands in one of SRIC's predeclared epistemic classes without altering the gates after seeing the result.

## Candidate external models considered

### Multimode GPT-2 Coconut on PrOntoQA

Advantages:

- small enough for an 8 GB laptop GPU at batch size one;
- public repository and raw checkpoint;
- latent, direct-answer, and explicit-CoT modes in one trained wrapper;
- recurrent latent vectors are reinjected at identifiable latent-token positions;
- logic answers and proof chains are externally checkable;
- semantic twins and counterfactual query interventions are easy to construct.

Limitation:

- the task family is dominated by fixed-form unary chains. It supports a clean first causal audit but not a strong claim that different latent traces encode different reasoning algorithms.

Decision: use this checkpoint as the primary source-faithful causal admission target, with maximum causal status `CONTENT_SPECIFIC` before semantic escalation.

### ProsQA multimode Coconut

Advantages:

- more varied proof structures;
- better setting for structure-near versus structure-far donor contrasts;
- same external research codebase and model family.

Limitations:

- answer parsing and proof-structure extraction require a separate adapter path;
- harder to debug simultaneously with the first source-faithful recurrence adapter.

Decision: reserve as Tier 2. It is the first dataset on which `PROCEDURE_SPECIFIC` should be enabled.

### SLPO Coconut

Advantages:

- exposes adaptive stopping information;
- provides latent lengths and gate outputs.

Limitations:

- additional runtime and checkpoint family;
- adaptive stopping introduces another mechanism before basic replay is proven;
- full training experiments exceed the current 8 GB hardware target.

Decision: use after the fixed-length causal audit is stable.

### Hyper 3B

Advantages:

- directly recurrent latent reasoning;
- larger and more ambitious external stress.

Limitations:

- at the hardware boundary;
- adapter and memory failures could be confused with theoretical failure;
- current halt behavior is not a strong adaptive-depth positive control.

Decision: later stress test, not the first empirical target.

## Major methodological choices

### 1. Adapter fidelity before model ambition

A large checkpoint is scientifically useless if the intervention adapter does not reproduce the model's native recurrence. Block 24 therefore gives exact replay and source-code parity priority over scale.

### 2. Teacher-forced answer loss as the primary effect measure

Free generation is useful descriptively but introduces parsing, decoding, and stochasticity. The main causal effects use teacher-forced protected answer loss while holding the prompt and suffix constant. Free-generation accuracy is a secondary behavioral witness.

### 3. Content specificity is not procedure specificity

A same-answer donor rules out pure final-answer encoding. It does not automatically prove a different algorithm is represented. On PrOntoQA the result is called content/proof-instance specificity. Procedure specificity is reserved for a task family with varied proof topology and an explicit far-versus-near structural contrast.

### 4. Explicit CoT is post-seal only

The multimode checkpoint can be given gold proof steps in verbalized mode. Allowing those traces into semantic construction would leak the target ontology. Therefore explicit CoT is revealed only after the quotient seal as a comparison witness.

### 5. Covariance calibration is disjoint

Covariance-matched noise must not estimate its nuisance distribution from the same rows used to measure the final effect. Twenty percent of proof groups are deterministically reserved for covariance calibration.

### 6. Semantic final traces are not computed before sealing

The previous prototype split the records correctly but captured every semantic orbit before choosing the quotient. The v0.3 implementation now captures discovery, then calibration, seals the selected quotient, and only then captures final semantic twins and counterfactuals.

### 7. Fail closed

Replay failure terminates the causal claim. Missing source objects terminate setup. Dirty or wrong upstream commits terminate source verification. No semantic candidate produces `ONTOLOGY_UNDERIDENTIFIED`, not a threshold adjustment.

### 8. Smallest valid quotient

Semantic construction is validity first, then minimum rank. Full hidden state is a descriptive upper control and is ineligible for selection.

## Alternatives rejected for the first run

- Training a new latent model: confounds model construction with external validation.
- Beginning with a 3B checkpoint: raises adapter and memory risk without improving causal clarity.
- Using explicit CoT during quotient discovery: leaks proof semantics.
- Calling any same-answer transplant procedure-specific: overstates what fixed-chain tasks identify.
- Estimating covariance from the final audit: weakens the intervention's independence.
- Selecting only tasks where latent recurrence helps: creates post-selection bias. The full causal population is reported first.
- Lowering gates after failure: invalidates the sealed experiment.

## Remaining judgment calls

The user was asked whether to prioritize a small clean causal proof or the strongest latent model. No answer was available before implementation, so the conservative default was chosen: small and source-faithful first.

The user was also asked whether explicit CoT should help construct semantics or remain post-seal. The conservative default is post-seal only.

The next strategic choice after the PrOntoQA primary result is whether to proceed immediately to ProsQA or first expand the PrOntoQA final population. The recommended default is to inspect the primary receipt, then use ProsQA only if replay and at least useful ordered recurrence are supported.
