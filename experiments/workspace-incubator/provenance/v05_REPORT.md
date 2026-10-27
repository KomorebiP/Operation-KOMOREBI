# Komorebi Workspace Incubator v0.5
## Memory noninterference, path dependence, and retained information

**Author: Komorebi P.**  
**Date: September 27, 2026**  
**Status: executed paired development plus explicitly post-outcome diagnostics. No certified J-space claim.**

## Executive result

Four 1,500-update continuations compare random programs with a 50% neutral-program mixture, within two unchanged v0.4 parent lineages. Both curricula improve native factual recall under longer computation. The neutral-enriched curriculum does not provide a consistent advantage. Severe word-dependent failures remain beyond the trained length.

A more important diagnostic changes the interpretation of those failures. A joint linear decoder recovers almost every factual bit from the two agents' retained states, even when their own cue-driven retrieval fails. Many apparent memory-loss cases are therefore failures of native access to still-decodable information, not evidence of wholesale erasure. The external decoder is a supervised measurement, not an autonomous or native repair.

## 1. Recovery and experimental contract

The v0.4 ZIP SHA-256 is cc9e30e26877ef1dc65f868e1324ce5dca0a97b2083823dab2cd93487a5e6fcb. Its exact 196-file manifest and 21 predecessor tests passed on restoration before the successor was built. Required parent checkpoints and four runtime modules are included unchanged, together with the source report and manifest. The full earlier archive is not duplicated.

Parents are work_310401 and work_310403. Their original random initializations are independent, but ancestral training budgets differ and both parents were selected for competence. Each paired comparison starts from byte-identical parent weights. These are not four fresh-from-scratch independent replications.

The architecture is unchanged:171,602 parameters, two independent 64-dimensional recurrent agents and eight-dimensional messages. Both agents see the full observation stream. No protected memory array, declared workspace coordinate, geometric objective or extra model module is introduced.

The fixed contract was written before the main continuations. It specifies 1,500 updates, batch 96, all-weight AdamW restart at 0.0003, two working stages followed by factual reload, and a maximum working length 12. The first 200 updates use lengths2, 4, 6; subsequent updates sample2, 4, 6, 8, 12. Each child sees 144,000 episode presentations. Presentations are paired across arms, not144,000 independent unique worlds.

Random words use uniform identity/left-flip/right-flip/swap symbols. In the neutral arm, half the words replace their second half with the first half reversed. Each primitive is involutive, so the constructed word is globally neutral. Worlds, roles, cues, query-type draws, aliases, lengths, recall pairs and RNG consumption match. Counts of operation applications match; exact opcode frequencies need not match.

Both arms receive the original terminal task/private losses plus four terminal factual-recall branches from the same post-working state, covering all eight facts. This shared added supervision and additional optimization mean parent-to-child gains cannot be assigned exclusively to neutral-word exposure. Neutralization also changes semantic target distributions and higher-order program statistics, not an isolated abstract algebra variable.

## 2. Matched native behavior

Each bank contains 512 independently generated procedural cases. Each assay uses one working program followed by separate factual recall branches, rather than the older pooled three-stage score. Every case is read through both agents and all four late consumers. All-fact recall uses four separate cue branches from the same source state. All eight bits must be correct for that agent-case to count. Scores average the two agents, not independent training seeds. Every main metric uses the final checkpoint.

The following table is exact working report and all-eight-fact native reconstruction after random programs whose induced action is not identity. Above length 12 is extrapolation. All 256 worlds and both aliases may occur in training; this is not unseen-world or unseen-alias generalization.

| Lineage | Length | Parent work / memory | Random child work / memory | Neutral child work / memory |
|---|---:|---:|---:|---:|
| A | 3 | 100.00% / 99.71% | 100.00% / 100.00% | 100.00% / 100.00% |
| A | 6 | 99.80% / 97.56% | 100.00% / 100.00% | 100.00% / 100.00% |
| A | 12 | 99.41% / 87.21% | 100.00% / 100.00% | 100.00% / 100.00% |
| A | 24 | 96.68% / 50.78% | 100.00% / 99.51% | 100.00% / 99.22% |
| A | 48 | 80.47% / 9.77% | 99.80% / 92.97% | 100.00% / 84.47% |
| B | 3 | 100.00% / 99.32% | 100.00% / 99.80% | 100.00% / 99.80% |
| B | 6 | 100.00% / 99.12% | 100.00% / 99.90% | 100.00% / 99.80% |
| B | 12 | 100.00% / 94.04% | 100.00% / 99.32% | 100.00% / 99.80% |
| B | 24 | 95.21% / 65.43% | 100.00% / 99.02% | 100.00% / 99.32% |
| B | 48 | 63.09% / 19.34% | 99.80% / 88.18% | 99.51% / 88.57% |

All 35 conditions per model, including private recall and every late consumer, are retained in RESULTS.json and the individual raw banks. The higher pooled consumer score is not substituted for exact working report or all-fact reconstruction.

## 3. Neutral-program enrichment is not a general repair

At length 48, the same semantic identity can be implemented by different native paths. Relation words shorter than the requested length are repeated and padded with identity tokens. They are never truncated through an incomplete relation. The training mixture explicitly generates inverse palindromes, not the commuting-flip or swap-conjugation families; nevertheless short strings can occur by chance in random training. No strict withheld-template guarantee is claimed.

| Family at length 48 | A random memory | A neutral memory | B random memory | B neutral memory |
|---|---:|---:|---:|---:|
| random_nonidentity | 92.97% | 84.47% | 88.18% | 88.57% |
| mirror_identity | 89.26% | 83.59% | 86.72% | 87.79% |
| identity_tokens | 48.34% | 49.32% | 74.22% | 62.79% |
| flip_involution | 50.20% | 39.36% | 56.93% | 49.02% |
| commuting_flips | 92.38% | 76.76% | 87.40% | 87.50% |
| swap_conjugation | 41.21% | 31.64% | 53.71% | 61.72% |

The neutral arm has no consistent advantage. It is materially worse on several A conditions, slightly better on some B conditions and worse on others. Two initialization lineages do not support a population-wide curriculum ranking.

A particularly clear failure in the random-trained A child is 92.38% all-fact recall after48 commuting-flip operations versus41.21% after48 swap-conjugation operations. Both words represent identity and have the same duration and initial worlds. Current exact work is 100.00% versus96.09%, respectively. Different harmless working paths can have very different effects on native recall.

## 4. What the operation/communication perturbations establish

A fixed secondary comparison leaves observation encoding and initial cue processing intact, but changes only the work phase. Removing work-phase exchange degrades both current computation and factual recall. Zeroing messages while retaining the receiver update can preserve more memory but destroys correct work. Exchange-only repetition often preserves more background than the full long loop, but also changes current use.

These comparisons do not isolate one source of drift. They are out-of-training perturbations, and omission of a learned update changes the algorithm as well as its computation budget. The data do not justify saying that communication alone, or the local work operator alone, causes the entire failure. All six mechanism conditions per model remain in the output banks.

## 5. A post-outcome probe audit corrects the memory-loss interpretation

After observing long-loop recall failures, an external diagnostic was introduced. Its training bank has 4,096 separately generated examples; its test bank has 1,024 examples with another seed. The neural agents remain frozen. Probes receive final native hidden states, not world arrays, cues, query answers or behavior labels as input. Correct world bits are used only to fit the supervised diagnostic on its training bank.

The initial diagnostic used separate single-agent ridge and small nonlinear decoders. They were weak even on the unstressed baseline. This was an important information-access mismatch: native recall includes communication between both agents, whereas those probes saw only one state. Their failure cannot establish absence of factual information. Their raw data, weights, predictions and negative findings are retained.

The follow-up concatenates the two 64-dimensional states and fits a standardized linear ridge decoder with the same fixed regularization used in the single-agent analysis. A preliminary joint fit was observed before its durable rerun; this is explicitly exploratory, not fresh confirmation. It does not alter the recurrent agents.

| Stressed model, swap-conjugation length 48 | Native all-fact recall | Joint linear all-fact decoding | Joint bit decoding | Joint recovery among native failures |
|---|---:|---:|---:|---:|
| A_parent | 6.40% | 89.45% | 98.54% | 89.20% |
| B_parent | 8.40% | 85.55% | 97.97% | 86.25% |
| A_random | 40.53% | 95.61% | 99.45% | 93.60% |
| B_random | 54.00% | 97.85% | 99.72% | 96.28% |

These native scores and decoder scores use the same 1,024-case diagnostic bank, not the earlier 512-case main bank. Native means average the agents; the joint decoder has one world prediction per paired case. Conditional recovery counts the paired decoder against each agent's native recall failure and is not an independent-sample significance claim.

For the two random-trained children, most native all-fact failures still have an exactly decodable world in the pair:93.60% and96.28% of the failed agent-case comparisons. This is concrete evidence against interpreting every retrieval failure as complete erasure. It does not show perfect retention or establish that either agent alone has no nonlinear representation of the missing facts.

Shuffling training world labels reduces joint bit accuracy to48.86–49.71% across the retained conditions; all-eight exactness is0.29–0.68%. Shuffling the test partner state reduces all-eight exactness to3.61–5.96%. The latter disrupts paired state content and is not an information-free null. These controls concern the external decoder, not causal intervention on the neural agents.

The joint decoder is not a native workspace, an autonomous repair, a learned reciprocal writer or evidence of a privileged Jacobian geometry. It exposes a new access target the current agents have not yet implemented reliably.

## 6. More recurrent cueing did not solve the access problem

A second post-outcome diagnostic repeated the same native cue from one through eight times, without new world observations or hidden-state edits. Four independent branches cover the facts. All depths are retained; there is no best-depth promotion. The first read reproduces the original native diagnostic exactly.

| Random-trained model after swap48 | One native cue | Two cues | Eight cues |
|---|---:|---:|---:|
| A | 40.53% | 41.46% | 29.20% |
| B | 54.00% | 53.91% | 24.71% |

The tiny improvement for A at two cues is not a repair. Longer repetition generally worsens recall. The unstressed controls also deteriorate after many repeated accesses. This is another extrapolation limit, not evidence that adding more recurrent steps inherently yields a stronger workspace.

## 7. Mathematical clarification

The companion note proves by elementary induction that memory invariance for every primitive operation on every reachable state implies invariance for every finite composition. The uniform reachable-state condition is not established by our finite neural banks. It also gives two exact counterexamples: correct working flips can damage memory under neutral loops, and an exact group action can satisfy every neutral relation while changing memory on a nonidentity step. Neutral-loop laws alone are insufficient.

Exact integer checks cover 4 states, 132 length/state cases for the group-action counterexample and 32,764 state/word checks for a memory-preserving realization through length 12. These support the written examples and induction, not a universal neural result or a novelty claim.

The revised engineering target is native cue-conditioned access to pair-retained information while preserving working behavior. A phase-local access repair with matched training and capacity controls is specified in notes/ACCESS_REPAIR_NEXT_DESIGN.md. It has not been implemented or trained in this block.

## 8. Verification and remaining boundaries

Twenty successor tests pass, including the paired generator contract, query information barrier, exact opcode algebra, independent target reconstruction, matched stored histories, parent hashes, process return codes and byte-exact training replay. The predecessor integrity check and 21 tests are separate, not added to claim 41 new tests.

A full 1,500-update A-neutral replay reproduces all 78 model tensors, optimizer state, data/Torch RNG states, every checkpoint field and checkpoint bytes exactly. All 35 evaluation banks reproduce arrays, bytes and result objects exactly from that replay. This is same-environment determinism, not external replication.

The independent integer/NumPy scorer rechecks 3,870,720 recorded output entries from the 210 main banks. This count includes factual bits, private reads and reused cases, not independent experiments. A separate diagnostic audit rechecks 1,114,112 bit predictions in 52 score groups and repeats inference for the saved single-agent MLP and ridge probes and joint ridge probes. The training replay's repeated decisions are not added to the main evidence count.

Actual child operating-system return codes were captured for all four main continuations and six main evaluations, and for the diagnostic/replay commands. The initial streaming launcher was unavailable before the shell executed. A monitored local supervisor replaced it; no experiment was left running for later delivery. The 20-update smoke is a paused engineering run, not another scientific lineage.

No new projected-state support audit, no-wire competence run, unilateral semantic-write validation, untouched RRCT v0.62 primary, pretrained language model or partner-transfer experiment was executed here. Previous support and private-solvability failures remain unresolved. No J-space, self-model or subjective-experience certification follows.

The aggregate computation manifest uses the consulted version1 structure with a local structure/path/hash validator. The canonical plugin CLI was not installed as a runnable file; it is not claimed as executed. Per-command before/after input hashes and actual exit records supplement the legacy schema. See the separate final verification record for clean-extraction and exact archive results.
