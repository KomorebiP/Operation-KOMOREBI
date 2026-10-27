# Result Interpretation and Claim Boundaries

## 1. The central distinction

The lab can produce four scientifically different outcomes:

1. **Task learning:** the model predicts answers in familiar distributions.
2. **Learned role binding:** answer-supervised calibration teaches transfer to new episode-local names.
3. **Engineered operator induction:** explicit state, equivalence, or law losses create transferable structure.
4. **Spontaneous operator induction:** untouched answer-only training produces transferable operator behavior without formal auxiliary targets or binding demonstrations.

These outcomes must not be collapsed into one claim. Engineered induction may be the most useful practical result even if spontaneous induction fails.

## 2. Evidence ladder

### E0: task acquisition

Required evidence:

- IID performance above majority controls
- reproducible training and checkpoint verification

Meaning:

The model learned something about the task distribution.

Not established:

Operator abstraction, compositionality, symbolic representation, or causal mediation.

### E1: controlled operator sensitivity

Required evidence:

- lexical split performance beyond the strongest lexical baseline
- performance survives disjoint names and nouns
- result repeats across seeds
- no metadata or template leakage

Meaning:

The model uses information associated with the operator-governed process rather than only the easiest surface cues.

Not established:

Reusable equivalence classes or novel composition.

### E2: reusable equivalence structure

Required evidence:

- different programs with the same exhaustive transformation behave consistently
- equivalent-path similarity exceeds matched non-equivalent controls
- observation preservation rules out a collapsed constant code
- law residuals improve together with behavior
- effects transfer to examples not used to define the pairs

Meaning:

The model has evidence of a reusable representation organized by contextual equivalence.

Not established:

Systematic remapping or causal mediation.

### E3: systematic operator composition

Required evidence:

- held-out ordered pairs succeed
- held-out ordered triples succeed
- episode-specific nonce renaming succeeds
- longer programs degrade gradually rather than collapsing immediately
- matched counterfactual changes are correct and unrelated outputs are preserved
- all results exceed the strongest eligible controls across preregistered seeds

Meaning:

The model behaves as though it can identify and compose operators beyond memorized surface sequences.

For the answer-only arm, this is the first level at which the phrase **spontaneous operator-symbolic induction** is defensible within the bounded Micro OSL world.

This conclusion remains local to the benchmark. It does not imply a general symbolic language across unrestricted tasks.

### E4: causal representational mediation

Required evidence:

- targeted hidden-state interchange changes every logically implied answer
- unrelated answers remain invariant
- matched random-direction interventions do not reproduce the effect
- ablation removes the behavior
- targeted restoration rescues it
- multi-step interventions compose as predicted

Meaning:

The internal representation causally mediates the formal computation, rather than merely correlating with it.

Version 0.1 does not implement these hidden-state interventions. Its formal-program counterfactual pairs are behavioral input interventions. Therefore this package cannot, by itself, establish E4.

### E5: independently admitted operator discovery

Required evidence:

- the system proposes a previously unnamed typed operator or macro
- it supplies preconditions, postconditions, effects, provenance behavior, and proposed laws
- an independent executor searches for counterexamples
- finite properties are exhaustively certified where possible
- the operator is admitted only as a versioned derived macro over trusted primitives

Meaning:

The system participates in discovering and formalizing new operator vocabulary under independent verification.

Version 0.1 does not include an operator-admission registry and cannot establish E5.

## 3. Maximum claim supported by this release

The highest reachable level in v0.1 is E3. Reaching it requires successful results. Merely running every command does not provide evidence for any level.

| Implemented component | What it contributes |
|---|---|
| Exact finite executor | Ground-truth transformations and witnesses |
| Controlled renderer families | Surface variation under fixed semantics |
| Exhaustive transformation IDs | Exact equivalence labels for finite worlds |
| Classical baselines | Surface-cue controls |
| Held-out pairs and triples | Behavioral composition tests |
| Renaming episodes | Local operator identification and reuse |
| Counterfactual pairs | Behavioral change and invariance tests |
| Learned operator matrices | Secondary algebraic diagnostics |
| Exact and fuzzy quotients | Formal structural reference and compression analysis |

Missing for E4 are activation interchange, targeted internal ablation, matched random interventions, and rescue.

## 4. How to read the main metrics

### Accuracy and macro F1

Accuracy answers whether the final categorical response is exactly correct. Macro F1 prevents frequent answer classes from dominating the summary. Always inspect the confusion matrix and world-specific results.

High IID accuracy with poor held-out composition means task learning, not symbolic composition.

### Lexical split

A neural gain over TF-IDF is useful only if the training and lexical vocabularies are genuinely disjoint in their role-bearing names and nouns. A remaining grammar skeleton can still help, so lexical success is E1 evidence rather than a complete emergence result.

### Held-out pair and triple splits

Both matter. Pair success with triple failure suggests limited local recombination. Triple success is stronger only after verifying that no equivalent complete transformation appeared in training.

### Length curve

Report performance at every exact program length. An immediate drop after the maximum training length suggests bounded pattern fitting. A gradual curve supports, but does not prove, iterative computation.

Do not merge length and composition tests. A novel length can contain familiar local compositions, while a short held-out pair can be compositionally novel.

### Renaming

Chance and baseline levels depend on the question's answer classes, not the number of nonce operators. Success requires using the episode's demonstrations to infer a mapping and then composing it. Confirm that nonce meanings are permuted between episodes.

Use matched canonical/correct-calibration/scrambled-calibration triplets. Report canonical, correct-calibration, and scrambled-calibration accuracy; pair-joint correctness; prediction consistency; the canonical-minus-renamed robustness gap; correct-minus-scrambled accuracy; and prediction change under calibration scrambling. Evaluation nonce words must be absent from optimization data. A replicated advantage of `role_bind_augmented` over its token-matched `role_bind_scrambled` control supports learned binding; only success by untouched `answer_only` contributes to a spontaneous-emergence case.

### Counterfactuals

Interpret the metrics jointly:

| Pattern | Interpretation |
|---|---|
| High sensitivity, low specificity | Model changes outputs indiscriminately |
| Low sensitivity, high specificity | Model ignores the intervention |
| High joint accuracy on affected and unaffected queries | Correct local causal behavior |
| High pair completeness, low ordinary accuracy | Check pairing or metric implementation |

The key target is correct change where required and exact preservation elsewhere.

## 5. Structural metrics are secondary

A low idempotence or commutator residual is not sufficient evidence. Degenerate matrices can satisfy algebraic relations while carrying no task-relevant information.

For a structural metric to support an operator claim, require:

- observation reconstruction does not collapse
- effective symbol count is nontrivial
- behavior improves on held-out compositions
- residual improvements replicate across seeds
- scrambled or unstructured controls do not show the same pattern

The exact quotient is a mathematical property of the finite world. The fuzzy quotient is a compressed model of concrete transitions and observations. Neither automatically proves that the neural text encoder discovered that quotient.

## 6. Arm-by-arm conclusions

### Answer only succeeds at E3

Permitted statement:

> In these bounded finite worlds, a randomly initialized transformer trained only on question answering acquired operator-sensitive behavior that generalized to sealed compositions, episodic renaming, and matched counterfactual tests beyond classical controls.

Do not shorten this to “the model invented its own universal language.”

### Answer only stops at E1 or E2, structured arms reach E3

Permitted statement:

> The benchmark did not show spontaneous systematic composition, but explicit state, equivalence, or algebraic objectives induced substantially stronger reusable operator behavior.

This is a positive engineered-induction result and a boundary on spontaneous emergence.

### Correct calibration beats scrambled calibration while answer only fails renaming

Permitted statement:

> Across the preregistered crossed seeds, correct answer-supervised calibration beat a token- and volume-matched scrambled-calibration control and transferred to an unseen nonce vocabulary, while untouched answer-only training did not.

This is evidence for learned meta-binding and a sharper theory of the missing ingredient. It is not evidence that the untreated model spontaneously invented an operator language.

### All neural arms fail hard splits

Permitted statement:

> Under the tested architecture, data scale, and objectives, the models learned familiar distributions but did not acquire reliable held-out operator composition.

This does not prove that operator emergence is impossible. It identifies a reproducible failure region.

### TF-IDF matches the neural model

Primary interpretation:

The dataset still contains exploitable surface regularities, or the neural model has not moved beyond them. Repair the benchmark before making a structural claim.

### Results vary sharply by seed

Primary interpretation:

The phenomenon is unstable at the tested scale. Report the complete distribution and avoid selecting the strongest run.

## 7. Statistical discipline

Use exact counts alongside proportions. A 100 percent result on twelve smoke examples has almost no scientific weight.

For standard and full runs:

- report all preregistered seeds
- report confidence intervals with their resampling unit
- compare arms within the same seed and dataset
- keep dataset and model seeds distinct and report the complete crossed matrix
- preserve per-world and per-query results
- treat counterfactual pairs as paired units
- distinguish exploratory from confirmatory analyses
- correct or limit multiplicity when promoting many secondary metrics

An improvement should be both statistically stable and practically meaningful. A tiny but consistent gain can motivate follow-up work, but it should not be described as recovery of a symbolic language.

## 8. Failure taxonomy

| Failure | Meaning | Next action |
|---|---|---|
| Generation or validation failure | Invalid evidence base | Fix before any training |
| TF-IDF solves hard split | Surface leakage | Redesign renderer or split |
| IID only | Local task learning | Strengthen composition pressure or architecture |
| Lexical only | Some abstraction, no composition | Examine state update mechanism |
| Pair but not triple | Shallow recombination | Test program execution depth |
| Composition but not renaming | Stable token semantics required | Add episodic binding mechanism |
| Renaming but poor counterfactual specificity | Flexible mapping without precise causal scope | Improve state factorization |
| Low algebra residual, weak behavior | Degenerate or unused operator matrices | Strengthen observation and behavioral coupling |
| Strong structured arms only | Engineered symbolic induction | Treat as H2, not H1 |

## 9. Novelty boundary

The construction combines ideas related to finite-state minimization, behavioral equivalence, quotient systems, automata, representation learning, operator algebras, and lumpability. A successful synthesis may be valuable, but novelty cannot be inferred from benchmark performance alone. Any publication-level novelty claim requires a careful comparison with prior work.

## 10. Consciousness boundary

The benchmark contains agents, provenance, planning permission, and resource use as formal story variables. Those words describe the simulated world. They do not establish self-awareness, subjective awareness, agency, desire, or personhood in the trained model.

Even an E5 operator-discovery result would be a result about verified abstraction and language formation, not evidence of conscious experience.
