# Grammar accounting and prior-preserving refinement

Self-review verdict: proved as written for the exact P23 and P24 scopes below.
The two source modules compile with the pinned Lean compiler and warnings treated as errors. The coordinator's cumulative axiom audit and kernel replay remain separate checks and are not claimed by this record.

## Inputs and scope

The target is the text of Propositions 23 and 24 in the unchanged `source/FOUNDATIONS_1.0.0.md` supplied by the 0.14.0 package. `GRAMMAR_RESULT.json` pins that input and every new proof/control by SHA-256.

P23 uses `w(g) = prior(g) * likelihood(g,D)`, a nonnegative summable whole-record evidence family. Index types may be infinite. The active set is finite and has strictly positive evidence. These assumptions are weaker than the manuscript's declared positive prior and finite positive evidence assumptions and therefore cover them. P24 uses arbitrary child and other-program index types with nonnegative summable priors/evidence, child weights summing to one, the whole-record mixture identity, and a strictly positive total normalizer.

No source statement or mathematical token in the frozen manuscript was edited.

## P23 dependency and obligation checks

1. `posterior_sum` and `activePosterior_sum` establish genuine normalized masses.
2. `abs_posterior_difference` establishes the pointwise sign split using positive active evidence and active evidence no larger than total evidence.
3. `exact_posterior_tv` sums the split with explicit summability to obtain exactly `1 - activeEvidence / evidence` under the one-half absolute-sum TV convention.
4. `predictive_event_contraction` proves the all-event kernel contraction. It bounds each signed term between the positive and negative half-variation terms, sums them, and cancels the equal total masses. It requires every event-kernel value to lie in `[0,1]`.
5. `predictive_event_family_bound` quantifies over every member of an arbitrary event family. Applying it to the event probabilities of any common family of probability kernels gives the manuscript's predictive-mixture TV bound. The proof does not assume a finite observation alphabet.
6. `omittedEvidence_eq` identifies the actual omitted infinite evidence sum with total minus active evidence. `omitted_evidence_bound` proves the normalized bound `b / (activeEvidence + b)` by positive-denominator cross multiplication.
7. `activeSets_cofinal` derives cofinality from monotone exhaustion. `active_evidence_tendsto`, `active_evidence_monotone`, `posterior_tail_antitone` and `posterior_tail_tendsto_zero` establish the manuscript's monotone limiting statement. `active_evidence_eventually_positive` and `active_posterior_tv_tendsto_zero` establish actual TV convergence even if early active sets have zero evidence.
8. `enumerated_grammar_accounting` packages the exact TV, predictive and omitted-evidence conclusions.

All eight obligations passed self-review. No truncation to a finite grammar or replacement of whole-record likelihoods by one-step likelihoods occurred.

The positive two-program example has evidence `1/100` on each program and exact active-posterior TV `1/2`. Two controls reject the false claim that raw omitted evidence `1/100` bounds posterior error and the false claim that the probability-kernel bound remains valid for a value-two test. Both fail with `False`, rather than a missing symbol or import.

## P24 dependency and obligation checks

1. `childPrior_sum` preserves total prior mass under normalized weights.
2. `childEvidence_factor` and `childEvidence_eq` factor the parent's prior from the entire child sum and invoke exactly the declared whole-record mixture identity.
3. `total_evidence_unchanged` preserves the full normalizer while leaving all other programs unchanged.
4. `child_posterior_sum` and `other_posterior_unchanged` derive the posterior statements by division by that same normalizer.
5. `predictive_event_unchanged` applies the same identity to the joint likelihood of the data record and any predicted event.
6. `RefinementContract` retains the normalization, positivity and summability needed for actual probability semantics. The contract gives summable nonnegative child posterior masses and a refined posterior sum of one.
7. `prior_preserving_refinement` packages the main prior, evidence and posterior conclusions. `identical_likelihood_evidence` covers exact atlas recodings as a special case.

All seven obligations passed self-review. Empty or zero-weight child families cannot satisfy normalized weights without carrying total weight one. A zero parent prior is allowed. The positive normalizer comes from the complete evidence, not necessarily from the parent alone.

The exact fixed-child versus stepwise-switching example gives different two-step likelihoods. Two controls reject giving each duplicate the full original prior and replacing a whole-record fixed-child mixture by independently remixed one-step likelihoods. Both fail with `False`.

## Development and remaining checks

P24 compiled on its first mathematical draft; later namespace, explicit auto-implicit setting and probability-semantics additions also compiled. P23's initial diagnostics concerned deprecated conditional rewrite names, unused section instances, unfolding definitions under sums, finding the right summability API, and an explicitly typed constant limit. These were implementation diagnostics. No target hypothesis or conclusion was weakened to resolve them. Available failed-source snapshots and diagnostic logs are retained in this directory.

Remaining work for this pair is the coordinator's cumulative import/inventory integration, axiom audit, full replay and release packaging. No mathematical P23 or P24 gap was identified. These two propositions do not close the remaining unrelated learning, curved-domain or continuous-observation targets.
