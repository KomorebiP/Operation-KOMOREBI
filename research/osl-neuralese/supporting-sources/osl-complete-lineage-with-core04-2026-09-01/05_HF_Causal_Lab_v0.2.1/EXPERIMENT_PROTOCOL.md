# OSL Hugging Face causal and compositional test protocol

## Question

Can sentence training induce a reusable operator-relevant representation in a randomly initialized transformer, and how much of that representation requires explicit formal scaffolding?

This package tests a bounded synthetic operator world. It does not test awareness or consciousness.

## Executable world

The generator executes five operators before rendering text:

1. `OBSERVE`
2. `TELL`
3. `IMAGINE`
4. `INFER`
5. `AUTHORIZE`

The state records provenance mode, original source, accessibility, direct observation, authorization, and action eligibility for every agent and fact.

Each story is encoded once. Six interlocking outputs are read from the same story representation for a selected agent and fact. This prevents a separate encoding from being learned for every question.

The five provenance modes are exactly balanced in every split. Authorization is independently balanced to 40% within each provenance mode so authorization and action eligibility cannot be learned as constant outputs.

## Matched training arms

| Arm | Added supervision |
|---|---|
| `answer_only` | Six answers for one selected state cell |
| `state_supervised` | Answer loss plus the complete formal state |
| `equivalence` | Complete state plus lexically distinct equivalent-path contrastive loss |
| `operator_regularized` | Equivalence loss plus a learned primitive transition objective |

Every arm uses the same transformer architecture, tokenizer, query heads, optimizer family, update budget, and data.

## Frozen controls

- Exact executable state as the ceiling
- Majority and question-only baselines
- Word and character TF-IDF
- Frozen random-transformer features with trained linear readouts
- Shuffled-label control
- Random formal-state geometry
- Answer-matched formal near misses
- Norm-matched random intervention directions

## Evaluation splits

- `id`: unseen executable traces from the training length range
- `length_ood`: longer traces
- `motif_ood`: a causally linked `TELL -> INFER` motif excluded from training
- `syntax_ood`: held-out sentence constructions
- `joint_ood`: longer traces with the held motif and held syntax
- `codebook_id`: episodic operator renaming with known arbitrary tokens and a legend
- `codebook_ood`: a new arbitrary token set with a legend

All surface variants of a concrete trace remain in one split. Alpha-renamed structural hashes are assigned to disjoint deterministic split buckets before sampling. Cross-split structural hashes and alpha-renamed hashes are then audited and reported.

## Primary measurements

1. Balanced provenance-mode accuracy
2. Exact agreement across all six interlocking outputs
3. Strict correctness across nuisance renderings of the same program
4. Formal triplet accuracy against same-answer near misses
5. Layerwise CKA with the full formal state and a permutation null
6. Causal conversion from communicated evidence to direct observation
7. Protected-output retention under that conversion

## Causal test

Calibration pairs differ by one final direct-observation event. The original discoverer remains unchanged. A direction is estimated only on calibration pairs. Its scale is selected only on calibration pairs.

On untouched pairs, a coherent conversion must jointly change provenance mode and direct-observation status to the executable counterfactual values while preserving accessibility, original source, authorization, action eligibility, and an unrelated protected state cell.

The same evaluation is performed for norm-matched random directions. Models must already answer the original and textual counterfactual correctly for a pair to enter the strict eligible-pair analysis.

## Interpretation gates

The package reports individual endpoints and a strict conjunction.

- ID capacity gate: at least 85% balanced provenance accuracy
- Joint OOD behavior: at least 80% provenance accuracy and 60% six-output exact match
- Baseline advantage: at least 10 percentage points over the strongest shortcut baseline
- Formal triplets: at least 65% and at least 10 points above the random-transformer control
- Causal eligibility: at least 70% of pairs
- Causal coherence: at least 50% on eligible pairs
- Protected retention: at least 95%
- Causal advantage: at least 20 points above the strongest random-direction control

Passing only behavioral endpoints supports systematic task learning. Passing geometry adds evidence of an organized state representation. Passing selective causal intervention and held-out composition is required for strong evidence of a reusable operator abstraction.

If only scaffolded arms pass, the justified conclusion is that the corresponding supervision induced the structure. A pretrained model is deliberately excluded from the primary emergence test because it would measure transfer from prior training.

## Statistical status

`smoke` and `pilot` profiles are engineering studies. The `confirmatory` profile is sized for stronger replication, but publication-level inference still requires an independent rerun with untouched generator seeds and a frozen protocol hash.
