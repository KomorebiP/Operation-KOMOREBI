# Review and validation notes
## Grounded Abstraction: Identifiability, Representation Change, and the Limits of Learning

**Komorebi P. · Operation Komorebi · Expanded theoretical edition v0.5.0 · 9 October 2026**

## Scope

This 33-page, five-part theoretical edition follows the 23-page first draft. It adds exact noisy correction memory, memory migration, output-relative continuation under model uncertainty, a common-quotient criterion, and minimum linear predictive realization from available initial evidence. Six new statement/proof pairs and three analytical figures develop those relationships. No training, broad agent implementation, or empirical claim of learned grounding is part of the revision.

All six new pairs received internal mathematical review against their stated hypotheses, proof mechanisms, counterexamples, and small exact examples. The ten earlier pairs were checked for verbatim preservation, their assumptions were revisited in context, and their finite suite was rerun unchanged. This is not independent peer review, a proof-assistant certificate, or a complete novelty audit. The classical foundations and the integrated interpretation remain distinct contributions.

## Recorded final inventory

| Item | Outcome |
|---|---|
| Manuscript | 33 pages including cover, contents, guide, five parts, appendices, and references |
| Statement/proof pairs | 16: nine theorems, five propositions, and two corollaries |
| Added pairs | Six relative to v0.1.0, not six mathematical priority claims |
| Additional formal material | Three definitions and nine labeled counterexamples |
| Analytical figures | Seven, each supplied as vector PDF, SVG, and PNG |
| References | Twelve; two new primary-source entries |
| Predecessor preservation | All ten statement/proof pairs verbatim; two original reference programs byte-identical |
| Small exact suite | 17 groups and 42,311 assertions passed |
| Retained checks | Eight groups and 18,919 assertions rerun |
| Added checks | Nine groups and 23,392 assertions passed |
| Source audit | No missing/duplicate labels, missing/unused bibliography entries, missing figures, or unmatched proofs |
| Final LaTeX | No warnings, unresolved references, missing-character diagnostics, or overfull/underfull boxes |
| PDF preflight | All 33 pages rendered; no out-of-page words or unresolved/replacement markers; used fonts embedded |
| Clean rebuild | Identical extracted PDF text on all 33 pages and matching scientific results with only recorded runtimes excluded |

Counts describe the document and bounded finite computations. They are not independent proofs, empirical samples, or numbers of new discoveries. `validation/fresh_rebuild.json` records the actual clean-build commands and comparisons; `validation/computation_manifest.json` pins the executed source, scripts, and figure PDFs.

## Substantive mathematical developments and boundaries

### 1. Less output does not automatically require less calibration

The earlier draft's surrounding prose suggested that requesting a smaller output could enlarge the all-word identifiable domain under the same partial-calibration class. The new Proposition 11.1 shows that this is too broad. When every uncalibrated linear extension is permitted and the requested linear output is nonzero, uncertainty can be directed back into that output at the first uncalibrated step. The domain remains exactly the full-state calibrated core. The identically zero observation is a separate trivial case.

The prose was corrected. The earlier full-state theorem and proof were not changed. Positive output-relative results now use an explicitly different, structured candidate class rather than silently importing a favorable restriction.

### 2. The unknown model is fixed along the entire history

The paired-state theorem uses a finite supplied family of linear models and a common observation. Each candidate is compared with a reference under the same action word. A descending kernel in a doubled state space gives a finite exact test for agreement of every future output. The agreeing initial-condition subspace need not be invariant under either physical candidate.

In the nilpotent example, each fixed candidate gives outputs 2, 1, 0, 0, ... from the same initial state. Alternating the candidate dynamics instead gives a nonzero second-step output. Replacing fixed uncertainty by arbitrary switching therefore changes the problem. The word-length bound is conservative. The exact illustration code checks subspaces and finite words but does not export a general-purpose provenance-carrying witness compiler.

### 3. Whole-space agreement has a stronger quotient criterion

The invariant closure of every discrepancy image must remain in the observation kernel. This condition is equivalent to a shared linear quotient when the agreement claim covers every initial vector. The smallest common quotient uses the reference system's largest future-unobservable subspace. Such a shared quotient preserves outputs even under model switching.

That stronger conclusion must not be read back into the weaker restricted-initial-state theorem. The hidden-return counterexample also shows why checking only QD=0 is insufficient: QA D can be nonzero at the next step. A valid abstraction must preserve invisibility through the admitted continuation family.

### 4. Output agreement and evidence initialization are separate

Given an agreeing initial subspace, the learner's initial record must distinguish its observable future classes. For a linear initial record and a linear predictor, the record kernel must lie in the reference future-unobservable subspace. A reachable/observable quotient then gives the exact minimum linear predictor dimension.

A one-dimensional initial family can require two dynamic state coordinates. Conversely, a three-dimensional physical system can admit a two-dimensional common predictor. These are linear-realization dimensions, not universal source-code, byte, or nonlinear encoding lower bounds. The reference reachable space is used to construct a predictor; not every candidate's physical trajectory must remain in it.

### 5. Noisy correction preserves joint associations, not just marginals

The probability-memory theorem assumes finite static worlds, exact likelihoods, fresh conditionally generated reports, and always-available nondestructive experiments. Its memory preserves both future report probabilities and target posteriors. The record consists of joint masses on target/likelihood-profile cells. A finite interpolation argument identifies those masses from joint target/history probabilities up to length m-1, where m is the number of distinct likelihood profiles.

Preserving only target posteriors is a weaker contract. The theorem is not claimed for that weaker contract. Impossible reports do not receive arbitrary normalized posteriors. Independent nuisance distinctions can be removed, but dependence between the target and the sensor law can be essential. Two priors with identical marginals yield posterior target probabilities 3/4 and 1/4 after the same report.

The four masses in the example are not four bits. Exact probability storage, growing denominators, and numerical conditioning require separate resource analysis. Nearly equal likelihood profiles can make the interpolation poorly conditioned.

### 6. A changed evidence language does not fill new memory automatically

For all priors on the same finite world set, the new cell-mass record can be reconstructed from the old exactly when every old cell lies inside one new cell. Aggregation is possible; arbitrary recovery after a split is not. Point masses provide the obstruction. A restricted reachable family of priors may permit a reconstruction excluded by the all-prior theorem. Model admission and allocating probability to new candidate worlds are separate operations.

## Small exact computation

The old program is unchanged. The added standard-library program uses integers, sets, `fractions.Fraction`, and small vector spaces over F2. Its nine groups cover fixed one-action and two-action candidate families, unrestricted calibration, whole-space quotient equivalence, evidence initialization, direct word checks, rational hidden-return and switching examples, noisy-profile Bayes updates, zero-probability reports, all partitions of a four-world set for memory migration, and the noisy sensor's association formulas.

Domains are recorded beside every group in `validation/observable_checks.json`. The paired-kernel and invariant-subspace calculations are compared with direct finite word evaluations. Aggregated Bayesian updates are compared with raw-world updates. These are separate project-authored calculations, not external independent implementations. The combined 17-group count does not establish arbitrary-state theorems; their support is the manuscript's prose arguments.

The local wrapper gives each exact-suite or preservation subprocess a twenty-second wall limit and checks matching input hashes before and after execution. It adds no memory/affinity cap, GPU work, network interaction, or learned-agent experiment. The legacy-v1 manifest has additional input pins. The delivered verifier is project-authored, not an authenticated external audit distribution or proof kernel.

## Actual corrections and presentation review

1. The unrestricted-completion output suggestion was corrected as described above. This is a substantive correction to an informal scope suggestion, not a changed predecessor theorem or an unexpected failed finite assertion.
2. The first expanded layout had 35 pages with sparse continuation and appendix/reference pages. Repeated nonmathematical exposition was tightened and the reproduction appendix consolidated. An interim layout left one reference on a separate page. The final layout is 33 pages. All ten old and all six new statement/proof pairs remain present.
3. A plot annotation initially crossed a line. It was moved into whitespace. The structured-uncertainty diagram was clarified to state explicitly that its hidden discrepancy direction lies in the output kernel. The three new figures were regenerated and the final PDF rerendered.
4. The two new references were checked at different depths. Tzeng was reviewed through primary metadata and abstract, not full text. Petreczky and colleagues were checked through the primary repository record and selected full-text definitions and realization results. Earlier documented access limits remain in the preserved source map. No complete review of all twelve full papers is claimed.

No mathematical assertion or LaTeX compilation failed in the completed v0.5 runs. This does not erase the scope correction, the earlier first-draft hypothesis correction, or the layout issues. Deliberately failing model scopes and invalid migration claims are negative controls, not unexpected computation failures.

## Visual review and rebuilding

All 33 pages were rendered with PyMuPDF and inspected in three contact sheets. The cover, probability-memory theorem, paired-model output theorem, common-quotient proof, minimum-predictor theorem, new figures, and references received additional full-page or direct-figure review. `validation/visual_review.json` states the exact reviewed set. Mechanical preflight checks geometry, glyph markers, font embedding, and build diagnostics; it is not a proof of mathematical validity.

The clean rebuilding script creates a temporary copy, removes its existing PDF and build directory, runs the supplied Bash build, both exact suites, preservation, source audit, PDF preflight, and receipt verification. It compares extracted text on every page and eight scientific/index files. Only the two suite reports' `runtime_seconds` fields are excluded. Data, statement locations, model results, and counts are not ignored. The shipped vector figures are reused in this check; they were generated separately during authoring.

This is same-environment reproducibility. PDF byte identity, Windows execution, PDF/A, tagged accessibility, cross-platform agreement, and independent replication are not certified. The frozen snapshot inventory should be verified before rerunning programs that replace timed reports. Historical validation files remain explicitly under `history/v0.1.0/` and are not represented as new executions.

## Publication boundary

The work remains an expanded theoretical edition moving toward 1.0. It has not undergone independent peer review, Lean verification, or a comprehensive priority audit. Supplied model classes, likelihoods, and algebraic semantics remain inputs to the theory, not achievements of an implemented learner. The original v0.1 PDF and source ZIP were not edited. No standalone font, private conversation transcript, or third-party full paper is distributed.
