# Review and validation notes
## Grounded Abstraction: Identifiability, Representation Change, and the Limits of Learning

**Komorebi P. · Operation Komorebi · First theoretical draft v0.1.0 · 9 October 2026**

## Scope

The principal deliverable is a new 23-page theoretical manuscript. Its proofs concern explicit finite evidence models, memory under exact candidate filtering, finite noisy records, and partially calibrated linear operators. Four analytical figures and a small exact illustration program support the exposition. No agent training, empirical cognitive evaluation, or large-scale implementation was performed.

All ten formal statement/proof pairs received an internal review of their assumptions and proof mechanisms. This is not independent peer review, a proof-assistant certificate, or a comprehensive mathematical priority audit. Classical arguments and existing source relationships are acknowledged rather than counted as new discoveries.

## Recorded outcome

| Item | Result |
|---|---|
| Reading PDF | 23 pages, including cover, contents, reading guide, four parts, appendices, and references |
| Statements and prose proofs | 10 pairs: 5 theorems, 4 propositions, 1 corollary |
| Additional formal material | 3 definitions and 6 labeled counterexamples |
| Analytical figures | 4, each supplied as PDF, SVG, and PNG |
| References | 10, with actual review scope in SOURCE_MAP.md |
| Small exact checks | 8 groups and 18,919 assertions passed |
| Source audit | No duplicate labels, missing references, missing/unused bibliography keys, missing figures, or unpaired statement/proof environments |
| Final LaTeX diagnostics | No warnings, unresolved references, missing-character diagnostics, or overfull/underfull boxes |
| PDF preflight | All 23 pages rendered; no detected out-of-page words or unresolved/replacement markers; all used fonts reported embedded |
| Clean rebuild | Identical extracted text on every page, identical illustration data, and matching finite scientific results after omitting only runtime |

The finite assertion count measures executed checks, not independent proofs, statistical samples, or empirical generality. The original run and the clean rerun both completed. Commands, timings, software, input hashes, and output hashes are recorded separately.

## Substantive correction made during review

The initial wording before the partition-memory corollary required the evidence family to **contain** every union of partition cells. That was insufficient. Additional events can split a cell and distinguish two candidate sets that have the same old occupancy.

The delivered statement requires evidence to **consist exactly** of the unions of the stated partition cells. A two-world, constant-target example shows the necessity of that boundary: the singleton candidate sets have identical occupancy, but a newly admitted singleton event produces a nonempty target set in one case and contradiction in the other. Two corresponding checks were added.

This was a proof-hypothesis correction found by internal review, not an unexpected failed numerical assertion. The original illustration code already used exactly the atom-union family. Both the manuscript and the negative control now make the restriction explicit.

Other qualifications were tightened before release. The pair-cover cost is for one fixed nonadaptive test set used for all initial codes, not the optimum of every adaptive policy. The noise certificate states nonnegative tolerances, probability ranges, an empty-set convention, and abstention. Approximate continuation explicitly requires bounded linear maps and an ambient growth bound.

## Boundaries of the main results

**Identification and initialization.** A target may be determined by the family of protocol laws without being determined by one finite observed record. A behavioral quotient may exist without the observer being able to initialize it. The predictor theorem preserves one common output language, not privileged latent coordinates or a learned encoder.

**Acquisition.** The exact trichotomy relies on total nondestructive tests of one fixed world, all available throughout the protocol. The destructive-test counterexample rejects the stronger inference that pairwise separability always gives one successful investigation. A reset that changes the hidden state is not a free replay of the original state.

**Correction memory.** The signature preserves every future intersection filter and the possible target set, including empty sets. Its memory count applies to all candidate subsets under exactly the partition evidence algebra. Reachable-subset restrictions, additional evidence, changed targets, and model admission require their own analysis. Logical state count is not byte-optimal program storage.

**Noise and uncertainty.** The majority-error example uses fresh conditionally independent Bernoulli observations and equal priors. Every finite outcome string remains possible in both worlds. The coordinate-radius result permits centers outside the represented model family and uses explicit coverage/model-error premises. A small radius cannot establish that the true process is represented. An unconditional coverage guarantee is not automatically a guarantee conditional on a rare issuance event.

**Linear continuation.** Calibration inputs and full output vectors are exact. The compatible class contains all fixed linear extensions, independently for each action. The theorem identifies the maximal full-state predictable domain for all finite words. It does not identify a complete operator outside that domain, recover an unknown initial vector, or characterize a smaller output-relative target.

**Approximation.** The nominal trajectory stays in its invariant subspace, but the actual trajectory need not. The ambient operator bound controls errors after they leave the calibrated domain. Local fit alone supplies no such bound.

## Small exact computation

`code/exact_checks.py` uses integers, finite sets, exact rational arithmetic, and small vector spaces over F2. Its domains are recorded per group. They include all one-action systems with at most three states, small nondestructive test tables, the destructive-test control, all 256 candidate subsets of the eight-world sensor, an intersection-closed non-Boolean evidence family, exact Bernoulli outcome laws, finite coordinate-radius examples, small linear completion families, and rational leakage examples.

Alternative elementary calculations cross-check partition refinement against continuations, pair coverage against adaptive trees, binomial formulas against direct outcome enumeration, and invariant-domain recursion against explicit linear completions. These alternatives are project-authored, not independent external implementations.

The local execution wrapper imposes a ten-second subprocess wall limit. No memory/affinity cap, GPU computation, network interaction, or training is part of the check. The legacy-v1 manifest has additional before/after input pins. Its verifier is project-authored, not an authenticated distribution of an external audit tool.

## Presentation and access issues

The first layout had 25 pages and an amsmath warning caused by legacy binomial syntax. Replacing it with `\binom` removed the diagnostic. Repeated nonmathematical exposition and appendix text were tightened to avoid nearly empty continuation pages. After the correction-memory boundary was added, a temporary 24-page layout again had an orphan continuation. Condensing repeated explanations retained the proofs, the new counterexample, and the final 23-page layout.

Visual review found that a dashed boundary crossed two labels in the calibrated-core diagram. The labels were moved away from that boundary, the four figures regenerated, and the final PDF rebuilt and rerendered.

Some literature endpoints failed or supplied only metadata. The original predictive-state paper resolved an incomplete author list on its abstract page. SOURCE_MAP.md records which full texts or selected passages were actually available. Failed retrievals are not counted as full-text review.

No mathematical assertion or LaTeX compilation failed in the completed runs. That does not erase the insufficient preliminary corollary hypothesis, the initial warning, or the layout and source-access issues.

## Visual review and clean rebuilding

All final pages were inspected in two contact sheets. The cover, corrected memory theorem/corollary page, radius theorem, calibrated-core proof and figure, and source references received additional page-level review across the draft and final renders. The final correction page and core diagram were explicitly rechecked after editing. Mechanical preflight tests geometry and text markers, not mathematical validity.

The clean rebuild started from a new source copy without its build directory or existing manuscript PDF. It used the shipped vector assets, ran the supplied Bash build, reran the small exact suite, audited the source, and verified its new local execution receipt. All 23 pages have identical extracted text. The exact result JSON differs only in the recorded runtime, and the illustration data and statement index are byte-identical.

This is same-environment reproducibility, not independent or cross-platform replication. The PowerShell build was not executed on Windows. PDF byte identity, tagged accessibility, and PDF/A were not certified. No standalone fonts, third-party full papers, or private conversation transcripts are distributed.

The prior Machine Understanding and Self-Improving Intelligence PDFs were not modified. This new draft closes the stated first-draft scope, not the open problems of output-relative calibrated continuation, noisy correction memory, or learning a general grounded representation from experience.
