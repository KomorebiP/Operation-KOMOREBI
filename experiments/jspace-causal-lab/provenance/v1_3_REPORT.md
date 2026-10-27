# Causal Editor 1.3: matched persistence challenges

Komorebi P. · September 27, 2026

**Disposition:** implemented browser instrument, bounded frozen-model causal assay, and numerical/software verification. No neural training, new naturally localized J-space, or broad persistence guarantee.

## What changed

The new **Does it last?** tab follows three branches: the original prepared state, a single candidate edit, and the whole donor reference. All receive the same subsequent working operations. The patch is never reapplied. The previous direct editor, dose scan, persistent session, import/export, memory workbench and historical evidence tabs remain.

The original engine, causal engine, live-session engine, weights and candidate frames are unchanged. Weights SHA-256: `5a3e9e80c8d7173295db73b058bc11bdc223533abf79041631f2f2546e58626b`. Frames SHA-256: `38866bdb36359bfbc935ad3eea911492b9bae613e8024a65cbce1a6b84770826`.

### Three branches, not just a before/after picture

A failure of the edited branch is not automatically an isolated failure of its edit. If an actual donor execution also fails the intended later operation, the continued task itself is problematic. The interface therefore distinguishes:

- **Transferred:** both reference branches answer correctly and the edited branch gives the intended donor answer.
- **Reverted:** both references answer correctly, but the edited branch gives the original answer.
- **Other error:** both references answer correctly, but the edited branch gives neither intended answer.
- **Reference error:** at least one reference already fails its own intended answer. These observations remain visible and are not quietly discarded.
- **Factual reload:** the intended content becomes the remembered facts. Losing the temporary donor contrast at this point is intentional, not an edit failure.

Conditional transfer scores display their denominator and reference-failure counts. A missing eligible contrast produces no score, rather than a spurious 100 percent.

## Execution semantics

A challenge begins before the prepared state's final silent delay. The selected candidate is written once and any preview suffix is applied once. The chosen challenge program then runs continuously through the original work transitions and learned communication. Checkpoint reads apply the normal two silent updates to copies, then compute four late consumers and a four-branch factual audit. Monitoring does not update the trajectory or add extra committed recurrent steps.

After the final work operation, its normal silent delay is committed. The requested factual reloads then update the state in sequence, without resetting it. Four reloads cover all eight facts, beginning with the original selected pair. Eight reloads repeat that pass. In contrast, the *audit at each checkpoint* uses four independent branches. These two measurements are explicitly separated.

The selected access-channel cuts affect factual reloads only. They do not change preceding working-phase communication. Exact factual references are evaluator values and never substitute for predictions from the frozen answer network.

A captured live origin is conservatively labeled: its native history is not authenticated by the challenge. Whole donor continuations establish a native-operation witness only relative to their starting source. A whole donor reference is not a native-localization certificate for the projected branch.

## User-facing controls

Choose one swap, two neutral-loop families, identity tokens, or a custom program of at most 48 operations. Inspect actual original/edited/donor answers, all four consumers, both private labels, and every recalled fact. A plot tracks mean factual recall across categorical checkpoints, with exact agent values available in the tables.

The fixed-setting bank varies worlds, cues, private labels, aliases, prefix programs of length 0, 3 or 6, and nonzero donor changes. It uses the chosen method, strength, agent selection, manual offsets and suffix unchanged across all cases. There is no per-case dose search. The bank can run 8, 16 or 32 histories per selected lineage. Every completed case has an inspector and raw export; a cancelled incomplete case is retained separately and cannot enter completed-case scores.

Both settings and source context are frozen when a run starts. Changing them cancels an in-flight computation. Already displayed results retain their recorded settings. The preview and previously committed live session are never mutated by a challenge. The phone dock now acts on the challenge tab instead of accidentally switching to the older workbench.

## Guided case

The unchanged guided case yields these actual outputs in both agents:

| Stage | Original | Edited | Donor reference |
|---|---|---|---|
| Initial write | [0,1] | [1,1] | [1,1] |
| One subsequent swap | [1,0] | [1,1] | [1,1] |
| Reload original factual pair | [0,1] | [0,1] | [0,1] |

All eight facts are recalled correctly in the guided checkpoint audits. This favorable demonstration is not substituted for the varied-history assay below.

## Fixed settings on varied histories

A written, hashed execution contract preceded the bounded assay. Bank seed: **271313**. There are **32 procedural input histories**, each evaluated through both previously selected model lineages, three intervention methods, and two working-program families. These are not 64 distinct input histories or fresh model training replications. The two lineages have distinct original initializations but competence-selected histories and unequal ancestral budgets.

All edits use alpha 1, both agents, zero manual offsets and no preview suffix. The tested methods are report-J, random rank three, and the J complement. The two 48-operation families are repeated LRLR and SLSR. Both induce identity on the abstract working pair at lengths 12 and 48. All histories also contain the matched two-operation preparation and possibly a prefix. The long lengths exceed relevant inherited working-training coverage; they are stress tests, not a new training result.

At 0 and 12 challenge operations, both original and donor references are correct in every case. The J edit returns the intended donor pair in **64/64 agent-cases per lineage per family**. Random and complement edits return the donor in **0/64** at those checkpoints. These controls do not establish Jacobian uniqueness: same-rank alternatives worked in the preceding study and are still available in the editor.

### Forty-eight-operation result

All denominators in this table are 64 agent-case observations, arising from 32 paired histories, not 64 independent trials.

| Family | Lineage | Edited exact donor pair | Edited all-eight-fact recall | Reference errors | Transfer among reference-competent observations |
|---|---|---:|---:|---:|---:|
| LRLR repeated | A | 64/64 | 61/64 | 0/64 | 64/64 |
| LRLR repeated | B | 64/64 | 63/64 | 0/64 | 64/64 |
| SLSR repeated | A | 61/64 | 43/64 | 9/64 | 54/55 |
| SLSR repeated | B | 62/64 | 54/64 | 10/64 | 54/54 |

The near-perfect conditional transfer on the harder family must not conceal reference failures, factual-recall failures, or private-label failures. Requiring both references to be correct, edited output correct, all eight edited facts correct, and the edited private label correct gives only **34/64** and **47/64** observations for the hard family. The corresponding commuting-loop counts are **58/64** and **63/64**.

A native donor is not a preservation oracle. On the hard family, all-eight recall in the native donor is **45/64** and **54/64**, compared with **43/64** and **54/64** in the projected branch. The original references retain all eight at **57/64** and **56/64**. This supports a distinction between projection-specific errors and weakness of continued native computation, not a declaration that the edit is harmless.

The raw 384 trajectories retain every checkpoint, all four consumer predictions, private readouts, factual bits and evaluation references. A history is reused across controls, families, agents and times. Raw count is not statistical replication. No population confidence, universal guarantee, or new emergence claim is assigned to these measurements.

## Verification

- 20 new engine contract checks pass.
- 17 new browser scenarios pass, including cancellation, immutable preview/live state, frozen bank settings, inspecting each case, real downloads, and 390-pixel phone behavior.
- 17 inherited refinement-browser scenarios were rerun on the actual 1.3 HTML, including the old dose scan and replay workflow.
- Twelve new numerical trajectories, with 96 checkpoints, were independently recomputed using the original PyTorch definitions. There were zero mismatches in 2,304 consumer decisions, 576 private decisions and 4,608 factual-bit decisions. Maximum state discrepancy was approximately 1.91e-6 and maximum logit discrepancy 3.40e-6. Origin encoding was also independently recomputed.
- Chromium matched the Node fixture's same 7,488 decisions with zero mismatches and zero state difference in these sampled paths. This is sampled verification, not a universal cross-device equivalence theorem.
- A separate integer auditor reconstructed world inputs, working references, reload references, eligibility, factual scores and all 84 aggregate cells. It rechecked 209,664 recorded output entries. The runtime and frame input hashes still matched their pre-assay values.

Exact file-set and archive verification are recorded in the separately delivered final verification JSON. The local computation-manifest validator is not the canonical Mathbox executable. No uninstalled validator or unexecuted check is described as passed.

## Failure and limitation record

A streaming-shell launch failed before the assay file or process existed. A normal foreground command subsequently ran the complete 384-trajectory assay and returned exit zero. The source hash freeze was made by that successful execution, not the failed launch.

The initial layout inspection found insufficient contrast in the new colors against the inherited light theme and a phone dock routing issue. These were corrected before final browser checks. They did not affect neural outputs or change the already frozen assay engine.

Actual file:// navigation was blocked by the managed browser with ERR_BLOCKED_BY_ADMINISTRATOR. Tests loaded the delivered HTML using Playwright set_content. A specific Android attachment viewer's ability to launch the file remains unverified. No in-chat HTML renderer was invoked.

No model was retrained. Projected states still lack a passed natural-support certificate. The three centered report dimensions are output-informed and rank-limited by four classes. No no-wire competence, autonomous writer, new-partner transport or language-model result was added. The app changes its bundled small neural networks, not this chat assistant's hidden activations.
