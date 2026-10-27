# Causal Editor 1.2: dose, persistence and replay

Komorebi P. · September 27, 2026

**Disposition:** implemented browser refinement with finite software and numerical validation. No new neural training, natural-localization certificate or claim of improved model competence.

## The change

The prior editor exposed a real hidden-state edit and optional fixed suffix. This release adds a measured edit-strength curve and a persistent paired trajectory. The model receives the edited activation once. Future operations update that state rather than reconstructing an edited preview after each action.

The source weights and report/interaction/PCA/random frames are unchanged. Weight SHA-256: `5a3e9e80c8d7173295db73b058bc11bdc223533abf79041631f2f2546e58626b`. Frame SHA-256: `38866bdb36359bfbc935ad3eea911492b9bae613e8024a65cbce1a6b84770826`.

## Measured default case

The guided case uses lineage A, calibrated access, facts [0,1,0,1,1,0,1,0], case seed 2711, cue [0,1], no optional prefix, and a donor changing the temporary pair from [0,1] to [1,1]. Both branches include the existing matched two-operation preparation.

| Donor strength | Agent 1 | Agent 2 | Facts recalled, agents 1 / 2 | Private labels |
|---:|---|---|---|---|
| 0.00 | [0,1] | [0,1] | 8/8 / 8/8 | 2/2 correct |
| 0.50 | [0,1] | [0,1] | 8/8 / 8/8 | 2/2 correct |
| 0.55 | [1,1] | [1,1] | 8/8 / 8/8 | 2/2 correct |
| 1.00 | [1,1] | [1,1] | 8/8 / 8/8 | 2/2 correct |

The 0.55 value is the first tested point on a 0.05-spaced grid, not a continuous optimum or an independently confirmed threshold. Both private labels and all eight facts in both agents are required for the displayed strict case pass. This favorable case does not replace the earlier multi-history preservation failures.

The seven-control comparison on the same context preserves the original answer under no edit, random directions and the complement. J, activation, PCA and the whole donor give the donor answer. This does not establish Jacobian uniqueness.

After a full J edit is committed, a native swap sends the original branch to [1,0] and retains [1,1] in the edited branch, for both agents. Changing the selected consumer, running an independent audit, or modifying the preview cannot alter this committed state. Undo restores its previous stored vectors exactly within the same JavaScript implementation.

## Dose and control interpretation

The sweep independently computes predictions, donor-class softmax scores, private-label predictions, and original-versus-edited factual recall at every grid point. Softmax is not labeled as calibrated confidence. Manual offsets are suppressed during this diagnostic so alpha zero is a genuine no-op. At other times, the editor explicitly warns when alpha zero still has a nonzero manual offset.

Memory comparison records individual originally correct facts that become wrong. Net accuracy alone could hide one lost fact offset by one recovered fact. “No new errors” is distinct from “all facts correct.” The stricter button only proposes a measured point with both current donor answers and all private/factual answers correct.

Whole-state endpoint choices cannot be swept through fractional strengths and mislabeled as native. Dimension labels and displayed formulas now update for the 61-dimensional complement and 64-dimensional whole-state alternatives.

## Persistent inference and replay

There are two committed branches, each containing its own two-agent state. Working steps use the original work functions plus two silent updates. Reload uses the selected learned retrieval mechanism; it intentionally requests original factual values rather than the temporary donor value. A read has no state transition. The memory audit creates four independent branches and does not mutate live state.

Session import checks checkpoint and candidate hashes, shape, finiteness, mode, opcode, length and computation bounds. It ignores saved predictions and reexecutes the recorded actions. It can reproduce a supplied activation snapshot's computation without authenticating that snapshot's claimed origin. The UI makes this boundary explicit.

Limits: 64 committed actions, a total step-budget of 256, at most 12 operations in each working action, and 4 MB imported JSON. Unexpected or invalid inputs leave the current session untouched. Context changes cancel and discard stale scans rather than allowing earlier asynchronous results to appear under a new case.

## Verification

The new engine has 16 contract checks. The refined UI suite has 17 scenarios, including real downloads/imports, mobile operation, reference nonmutation, cancellation, control comparisons, and deliberately poisoned saved answer fields. Fifteen inherited causal-browser scenarios are also rerun.

The inherited numerical ports reproduce 4,608 original reference decisions and 1,344 causal reference decisions without mismatches.

The new persistent API is independently checked against the original PyTorch definitions on 24 trajectories and 168 snapshots. It matches 5,376 output/private decisions and 768 final factual-bit decisions with zero mismatches. Maximum observed state difference is approximately 1.27e-5 and maximum logit difference is approximately 3.68e-5. Origins are supplied paired snapshots; subsequent patch arithmetic, native work, silence, retrieval, logits and recall are recomputed by the original PyTorch implementation. The reported decision count includes repeated private reads and reused states, not independent scientific trials.

The delivered HTML is loaded into Chromium at desktop and 390-pixel phone sizes. No page errors or network requests occur in the tested `set_content` sessions. The separate actual file:// navigation assay is blocked by browser administrative policy with `ERR_BLOCKED_BY_ADMINISTRATOR`; it is not counted as passed. Opening a downloaded HTML attachment on a specific Android device remains unverified here.

## Scientific boundary

This is a better instrument for examining output-changing latent edits, not a new learned workspace. Candidate writes can fail memory preservation or later computation. Same-rank alternatives can work. The raw projector's natural-state support is still uncertified. The included networks are not the hidden state of this chat assistant. An editable numerical subspace and favorable examples are not enough to conclude a general J-space has emerged.
