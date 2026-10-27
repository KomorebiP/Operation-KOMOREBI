# Semantic Retraction Factorial v0.3.0: Scientific Boundaries

Author: Komorebi P.  
Status: prospective design memo, not an outcome report

## Purpose

v0.3 asks one focused question left unresolved by v0.2:

> On a genuinely fresh finite bank, can the model's own decoder select a semantic state and a calibration-only prototype realize that state without the oracle?

The experiment separates two possible bottlenecks. A **selector** assigns a deep hidden state to one of eight visible D4 states. A **section** supplies a canonical hidden representative for the selected state. v0.2 compared conditions that changed both components at once. v0.3 changes one component at a time.

The primary domain is the sealed v0.4 checkpoint panel, 64-step identity-preserving paths, and all binary continuations through length six. It is a finite D4 decision-repair study. It is not a test of unrestricted language, arbitrary tasks, or infinite-depth dynamics.

## Core selector by section factorial

For a native cut state \(h\) with true visible state \(y\), define

\[
q_O(h)=y,
\qquad
q_D(h)=\operatorname*{argmax} Dh,
\]

and

\[
s_A(j)=b_j,
\qquad
s_P(j)=\mu_j.
\]

Here \(b_j\) is the learned anchor and \(\mu_j\) is a prototype constructed only from the sealed calibration split. The four core interventions are:

| Condition | Selected label | Section state |
| --- | --- | --- |
| `oracle_anchor` | \(q_O(h)\) | \(s_A(q_O(h))\) |
| `oracle_prototype` | \(q_O(h)\) | \(s_P(q_O(h))\) |
| `decoder_anchor` | \(q_D(h)\) | \(s_A(q_D(h))\) |
| `decoder_prototype` | \(q_D(h)\) | \(s_P(q_D(h))\) |

The decoder label must be computed once from the native cut state and reused byte for byte in both decoder conditions. When \(q_D(h)=y\), the oracle and decoder branches using the same section must begin from identical tensors. A violation is an implementation error, not a learned outcome.

`decoder_prototype` is the previously missing cell. It must not be renamed or interpreted as nearest-prototype selection. Nearest-anchor and nearest-prototype conditions are separately named secondary diagnostics. The prototypes are **held-out calibration prototypes**, not cross-fitted evaluation prototypes.

## Fresh-bank status

The production bank consists of 64 calibration contexts and 64 evaluation contexts, with eight distinct 64-step identity paths in each split. Every evaluation uses all eight visible starts and all 127 binary suffixes of length zero through six. Lengths five and six are the prospectively extended continuation strata. Results must be reported separately by suffix length so shorter cases cannot hide a depth-six failure.

Production entropy is unavailable until the complete design, executable, tests, exclusions, thresholds, and receipts are committed. Before entropy access, the checkpoint-free sealer independently requires the authenticated protocol bytes to be canonical, to carry the frozen schema/status and NumPy runtime, and to match the fixed 64/64-context, 8/8-path, length-64 bank design. A single 256-bit root is then drawn once and domain-separated into calibration and evaluation streams. Exact context and path hashes must be disjoint across the two splits and excluded from every registered v0.2 or earlier bank.

The sealer also requires at least 64 MiB free before requesting production entropy, so a known-full filesystem cannot consume the one permitted draw before the small bank artifacts are written.

The calibration split may be used only by the frozen prototype estimator. For each checkpoint, the runner constructs the prototype from calibration-only states before it constructs evaluation operators or performs any evaluation rollout. The prototype tensor and its construction receipt are included in the terminal result; there is no separate durable prototype precommit. Evaluation labels, states, predictions, or summaries may not influence prototype construction, selector definition, thresholds, or aggregation.

A hidden ray is defined only when every coordinate and its float64 Euclidean norm are finite and that norm is strictly greater than $10^{-12}$. The calibration prototype section is usable only when each of its eight fixed-order float64 resultant sums satisfies this strict norm threshold before normalization. A finite ray at or below the threshold is an undefined scientific case, not an unexpected nonfinite computation. The decoder label is still computed once with the frozen lowest-index tie break, but selector correctness requires the native cut ray to be defined. Pass-bearing self-decoder commutation independently requires the stepped ray to be defined. In secondary nearest-section diagnostics, an undefined query is marked undefined and scored incorrect through a zero-state placeholder; nearest-section outputs never enter either decoder gate.

The v0.2 bank remains spent even though its primary learned run aborted. v0.3 does not rehabilitate it. The v0.3 spend receipt is written immediately before any fresh calibration or evaluation state is passed through a learned checkpoint. Parameter-only checkpoint authentication and sealed-bank generation or verification may occur before that receipt. Once spent, a bug fix or revised analysis requires a new bank and version. A same-bank rerun is posthoc sensitivity only.

The one-draw firewall is local to the fixed project tree and assumes an honest operator. Copying the pre-draw tree cannot be physically prevented; divergent draws are instead made detectable by the archived design, draw, bank, and seal receipts.

This is prospective with respect to new cases. It is not prospective model discovery because the hypotheses were motivated by v0.2 and the twelve v0.4 checkpoints have already been studied.

## Fixed-checkpoint limitation

All four v0.4 arms and seeds 101, 211, and 307 are evaluated. Each arm claim requires all three of its seeds to pass independently. An all-panel label requires all twelve checkpoints. Seeds, arms, contexts, starts, paths, and suffixes may not be pooled to rescue a failed checkpoint.

A pass confirms fresh-case behavior for this fixed checkpoint cohort. Independent checkpoint replication requires checkpoints trained after the protocol is fixed, using new training seeds. Architecture-independent evidence additionally requires a separately trained architecture and a separately sealed bank.

## Primary operational gates

The primary arm is preregistered as `polar_cr`; its arm label requires all three seeds. Other arms receive the same per-checkpoint gate and an all-panel label requires all twelve checkpoints. For `decoder_prototype`, the following suffix quantities are required independently at lengths five and six in every claimed checkpoint:

| Quantity | Required value |
| --- | ---: |
| Suffix accuracy conditional on correct selection | at least 0.995 |
| Unconditional suffix task accuracy | at least 0.99 |
| `oracle_prototype` suffix task accuracy | at least 0.995 |
| Cuts correct on every suffix in the stratum | at least 0.99 |
| Worst-context suffix accuracy | at least 0.95 |
| Damage conditional on native correctness | at most 0.005 |
| Gap from `oracle_prototype` accuracy | at most 0.01 |
| Wrong-prototype counterfactual accuracy | at least 0.95 |
| Wrong-prototype factual leakage | at most 0.05 |
At every evaluation prefix, the decoder selector must be at least 0.99 overall and at least 0.98 in the worst context. Because each context has only eight starts, the exact integer implementation of 0.98 requires 8/8 starts in every context. Empty-suffix correctness is a prefix-level structural check. Wrong-prototype counterfactual accuracy and factual leakage are nevertheless checked separately at H5 and H6, not pooled across H0--H6.

The section must also decode correctly on all eight representatives, be idempotent on every tested section and cut state within \(10^{-6}\) maximum hidden discrepancy, and commute semantically for both generators at least 0.99 overall with worst-context coverage at least 0.95. That one-step worst-context denominator is also eight starts, so its exact 0.95 gate likewise requires 8/8 in every context.

If native error is at least 0.01 in every required prefix/horizon stratum, require at least 50 percent net relative error reduction. If any required stratum is below 0.01, repair superiority is explicitly `NOT_EVALUABLE_LOW_NATIVE_ERROR`; the operational interface may still pass if all accuracy and damage gates pass. The result reports operational-interface and repair-superiority statuses separately. A zero rescue denominator is never converted into a successful repair claim.

All performance-rate thresholds are applied to integer numerators and denominators, using exact ceiling or floor inequalities rather than rounded displayed percentages. The hidden-state idempotence tolerance is a separate continuous numerical check. Context is the sampling block. Starts, paths, and suffixes are repeated audit cases, not independent population replicates. Factorial contrasts and finite-bank operational gates are reported separately.

An autonomous retraction label does not require prototypes to outperform anchors when both are already at ceiling. v0.3 reports paired prototype-minus-anchor contrasts descriptively but preregisters no threshold or separate prototype-advantage label.

## Valid negative results and procedural invalidation

The following are valid scientific negatives. They fail the associated label but do not erase correctly completed independent conditions:

- low selector accuracy
- a prototype section that decodes poorly or has any nonfinite or at-most-(10^{-12}) resultant norm
- failed idempotence or semantic commutation
- insufficient repair, excessive damage, or failure of state-specificity controls
- oracle success with autonomous failure
- one section passing while another fails
- projection diagnostics failing while the core anchor/prototype factorial remains valid

The following invalidate the affected learned result:

- source, checkpoint, code, protocol, bank, or receipt mismatch
- calibration/evaluation overlap or overlap with the spent-bank registry
- applying any fresh-bank state to a learned checkpoint before the durable spend receipt
- evaluation information entering prototype or selector construction
- target-map or noncommuting word-order failure
- unexpected nonfinite computation in any branch that is defined by the fitted section and projector status, or corrupted output
- missing checkpoint census, canonical `RESULT.json`, staged verification binding, or terminal `COMMIT.json`
- changing code, thresholds, aggregation, or conditions after the bank is spent

The corrected projector audit is a parameter-only preflight and uses an explicit float32-aware rank tolerance. The optional projection branch is not a validity prerequisite for the four core factorial cells. This prevents an ambient diagnostic from aborting an otherwise valid semantic-section experiment.

An undefined calibration prototype is a valid negative for prototype-bearing cells, and an unavailable projector is a diagnostic negative; their deliberately undefined tensors are not treated as unexpected nonfinite computation. Defined native, anchor, prototype, projection, and clean-reference branches must remain finite or the learned run is procedurally invalid.

The runner is a NumPy reconstruction bound to the sealed checkpoint bytes and state-dict digests. It does not claim bitwise equivalence to the source training backend; that unestablished backend equivalence is a limitation on interpretation, not a tested tolerance gate.

Before spend, the runner authenticates and restricted-loads all twelve parameter files, checks the frozen NumPy version, exclusively reserves and syncs the result namespace, physically allocates one GiB for `RESULT.json` plus a commit reserve, and hard-links the actual result-reservation inode to a same-directory canary. It verifies inode identity and link-count restoration, removes the canary, and syncs the bundle and parent directories before the reservation can authorize spend. A staged canonical result is verified before the reserved `COMMIT.json` is filled and published last. The verifier in the same frozen executable decodes compact Boolean case evidence and recomputes gate-bearing rates, exact thresholds, aggregations, and provenance hashes. The continuous hidden-idempotence residual is thresholded again from its stored summary but is not reconstructed from raw hidden tensors. The verifier does not rerun model forwards, use an independent gate implementation, or independently reconstruct prototype tensors, so it is an output-integrity and aggregation verification rather than an independent learned replication.

If spend-marker publication raises after the exclusive marker path has appeared, the bank is conservatively treated as spent even if the marker is partial. The physical result reservation is retained and a best-effort `SPEND_PUBLICATION_FAILED.json` is written; automatic prospective retry is forbidden.

## Permitted conclusions

| Observed pattern | Strongest permitted conclusion |
| --- | --- |
| Primary `polar_cr` arm passes | An autonomous calibration-only finite-horizon semantic retraction operates on this fresh bank in all three sealed `polar_cr` seeds |
| Oracle and decoder prototype agree when selection is correct, with excess errors concentrated at wrong selections | The tested residual errors are localized to selector mistakes; this is a descriptive diagnostic, not a separate pass label |
| Decisions agree but hidden or logit geometry does not | A coarse decision interface exists, not trajectory identity |
| All twelve existing checkpoints pass | Fresh-case confirmation within the existing architecture and training cohort |

No v0.3 result by itself establishes a global additive quotient, exact hidden-state equivalence, unrestricted bisimulation, architecture independence, or universal Neuralese. A failed tested section likewise does not prove that every nonlinear semantic section is impossible.
