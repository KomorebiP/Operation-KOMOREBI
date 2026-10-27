# First-edition review and validation
## Grounded Abstraction: Identifiability, Representation Change, and the Limits of Learning

**Komorebi P. · Operation Komorebi · Version 1.0.0 · 9 October 2026**

## Scope

This 43-page, six-part theoretical edition consolidates the 33-page v0.5 manuscript and adds a bounded quantitative connection among probability memory, repeated correction, partially hidden dynamics and one posterior decision. It adds four statement/proof pairs, three labeled counterexamples and two analytical charts. There was no agent training, external calibration, broad benchmark campaign or claim that a neural system learned grounding.

All twenty formal statements received an internal assumption review. The four added arguments were examined against their stated hypotheses, boundary cases, proofs and exact illustrations. The sixteen inherited statement/proof pairs remain verbatim and their two small exact suites were rerun. This does not constitute independent peer review, a full novelty audit or proof-assistant verification. The established mathematical ingredients are acknowledged rather than counted as new discoveries.

## Recorded first-edition inventory

| Item | Result |
|---|---|
| Reading manuscript | 43 pages, including cover, contents, two reading guides, six parts, appendices and references |
| Formal statements with prose proofs | 20 pairs: 12 theorems, 6 propositions and 2 corollaries |
| First-edition additions | 4 statement/proof pairs; not 4 priority claims |
| Definitions and counterexamples | 3 definitions and 12 labeled counterexamples |
| Analytical figures | 9, supplied as PDF, SVG and PNG |
| References | 14; actual review depth is recorded in SOURCE_MAP.md |
| Predecessor preservation | All 16 v0.5 statement/proof pairs verbatim and 4 reference/figure programs byte-identical |
| Complete small exact suite | 28 groups and 70,241 assertions passed |
| Retained scope | 17 groups and 42,311 assertions rerun |
| Added scope | 11 groups and 27,930 assertions passed |
| Source audit | No missing/duplicate labels, missing/unused bibliography entries, missing figures or unmatched formal proofs |
| Final compilation | No LaTeX warnings, unresolved references, missing-character diagnostics or overfull/underfull boxes |
| PDF preflight | All 43 pages rendered; no out-of-page words or unresolved/replacement markers; used fonts embedded |
| Clean rebuild | Same-environment comparison of every page's extracted text and ten scientific/index files; actual result in validation/fresh_rebuild.json |

These counts describe the document and deterministic finite implementations. They are not independent proofs, statistical samples, external replications or measures of empirical generality.

## Mathematical review

### 1. A finite retained record is not the entire learner's memory

Proposition 15.1 rounds a normalized k-vector to denominator N by a fixed largest-remainder rule. The result remains a probability vector and differs by at most k/(2N) in total variation. Its k ceil(log2(N+1)) field count intentionally uses a simple literal encoding rather than an optimal code exploiting the sum constraint.

That count excludes installed programs, model descriptions, report histories, indices and transient exact arithmetic. The implementation uses rational arithmetic for transparent checking. It is not an implementation with a proved bounded working-memory footprint.

The same proposition bounds a Bayes update under a positive likelihood floor. Its proof centers a [0,1]-valued test function, uses the resulting oscillation bound and separates prior perturbation from likelihood perturbation. It does not assume every Bayesian update contracts distance.

### 2. Repeated noisy correction requires one observation contract

Theorem 15.2 assumes a fixed finite world, cells constant in the target, normalized report laws, fresh reports conditional on the fixed world and chosen experiment, and a common positive floor beta for every admitted actual and representative report probability. The within-cell discrepancy epsilon is explicit. Exact likelihood-profile cells are the epsilon=0 case, provided the floor holds.

A matched data-dependent selector is permitted when it uses only the retained earlier record and independent randomness. A hidden world-dependent selection mechanism cannot be omitted from the evidence. The true cell update uses the conditional mixture of world likelihoods, which remains within the declared floor and discrepancy bounds. A zero-mass cell makes no contribution and is not divided by its mass.

The result gives a sufficient finite-horizon denominator, not an optimal storage theorem or a time-uniform stability claim. The initial bound can use the actual initialization error. The example's prior is exactly representable and therefore uses e0=0. Increasing N does not remove a nonzero model-error term.

The rare-event counterexample shows that a tiny probability rounded to zero can dominate the exact posterior after a later report. The example's likelihood floor tends to zero across the family. A variant makes both outcomes possible in both worlds while retaining the same limiting failure. This is evidence amplification, not incorrect rounding arithmetic.

### 3. Almost invisible is not the same as permanently invisible

Theorem 16.1 separates visible and hidden coordinates and uses a nonnegative two-by-two comparison matrix for their norm growth. The nominal visible update is the same G as in the physical model. The initial visible error and physical norm allowances are explicit.

If the return block B is exactly zero and initialization agrees, visible prediction is exact even when the hidden component is unstable. For nonzero return, the error is bounded by a forced recurrence driven by the hidden norm allowance. An infinite sum requires g<1, d<1 and (1-g)(1-d)>bc. Two stable diagonal blocks alone are insufficient when their feedback is too strong. Conversely, failure of this sufficient norm comparison does not establish instability of a particular signed system.

The result can cover switching only when that switching is explicitly allowed and the same bounds apply throughout. It does not reinterpret the earlier fixed-unknown-model equivalence theorem as an arbitrary-switching theorem.

### 4. The final decision uses the same posterior and response

Theorem 17.1 combines cell-probability error e and a uniform within-cell response allowance d only after specifying a common bounded K-Lipschitz loss. The risk error is at most xi=min(1,e+Kd), and minimizing the approximate risk incurs posterior regret at most 2xi. A strict gap larger than 2xi against every other action preserves the unique minimizer. The universal phrasing covers a singleton decision set without taking the minimum of an empty set.

An upper-risk test can justify issuing the selected decision under the model posterior. It is not a frequentist coverage guarantee, a statement that the real world belongs to the model, or a bound on the realized loss of every individual world. The combination must retain the same observed history, cell meanings, prior, initial conditions, future action word and loss. Valid certificates about different problems cannot be substituted.

### 5. One complete quantitative example

The eight worlds are (s,theta,n). Four joint target/sensor masses start at (3,1,1,3)/8, with n independently uniform. Three reference reports equal to one have specified likelihoods 1/4 and 3/4 under the two sensor conventions. The exact target posterior is 41/56.

Four count fields with denominator 65,536 use 68 literal retained bits. Their rounded masses are (1755,15799,585,47397)/65536. The actual mass error is 1/114688, but the certificate correctly uses the larger proved allowance 21/32768 rather than substituting a post hoc exact error.

A later three-step response follows one fixed candidate matrix with visible multiplier 1/2, hidden multiplier 1/2, return magnitude 1/64 and forward coupling 1/8. The hidden n changes the sign of the return. Its norm comparison gives response allowance 481/32768. The combined radius is 251/16384.

For decisions 0 and 1/8 and loss min(1,absolute error), the retained-record risks are 23991/262144 and 8777/262144. The exact model-posterior risks are 173737/1835008 and 81105/1835008. The approximate risk gap exceeds twice the proved radius, so the selected decision 1/8 is also the unique model-posterior minimizer. Its certified risk upper bound is 12793/262144, approximately 0.04880, below 3/50.

The nuisance n is not recovered by the reference observations. The response remains approximate exactly where evidence leaves it unresolved. This is one coherent finite example, not an empirical risk estimate or an agent capability result.

## Exact implementation coverage

`code/quantitative_checks.py` uses Python integers and fractions.Fraction. Its eleven groups include small rational simplex grids, likelihood-update comparisons, every specified binary history through five reports, matched adaptive selectors with within-cell likelihood discrepancy, rare-event and impossible-observation controls, signed and switching block systems, partial sums under the strict comparison condition, the feedback counterexample, the joint risk example over multiple horizons and denominators, sufficient-precision formulas and invalid arguments. Bounds appear beside each group in `validation/quantitative_checks.json`.

The two retained programs preserve their original domains. Independent elementary calculations compare exact probabilities with aggregated updates, interval/linear constructions with direct finite behavior, and response risks with full eight-world enumeration. These alternatives are authored within the same project. They are not independent external implementations. Floating point is used only to draw figures and display decimal approximations, not to decide mathematical acceptance.

The wrapper gives each exact suite and preservation subprocess a twenty-second wall limit. The intact predecessor archive, source, all Python programs and nine figure PDFs are pinned before and after execution. Successful execution is recorded in the legacy-v1 project-local manifest. No authenticated external audit service, Git revision, proof kernel, process-memory cap, GPU or network interaction is claimed.

## Actual corrections and failures

1. The first compiled layout had 45 pages. Compilation completed, but PDF preflight failed because two tables produced underfull-box diagnostics. Ragged-right table columns removed the diagnostics. Redundant appendix prose was consolidated, the conclusion received a clean page opening, and bibliography typography was adjusted to avoid one isolated final reference. No formal statement or proof was deleted. The first preflight failure and build log remain in `validation/development/`.
2. Full-page review found the second new chart's legend near a plotted trajectory. The legend was moved into unused upper-left space, both new chart exports were regenerated and the PDF was rebuilt. The pinned computation receipt was regenerated after that script/figure change.
3. The strict decision-gap statement was written with a universal condition over competing decisions, rather than a minimum over a possibly empty competitor set. This is a scope/notation clarification for the allowed singleton decision set, not a counterexample to the bounded-risk argument.
4. Several reference fetches failed to provide readable full text: the Project Euclid endpoint returned an iframe, HAL presented an anti-bot page and the direct publisher endpoint for the approximate-bisimulation article returned HTTP 403. An author-hosted full PDF supplied selected passages for the latter. The filtering reference remained a metadata/contextual review. Those failures were not counted as full-text verification.

No mathematical assertion failed in the completed first-edition suites. Deliberate rejection of impossible updates and invalid quantitative premises is a negative control, not an unexpected failure. This does not erase the earlier drafts' documented hypothesis and informal-scope corrections, whose records remain in the retained predecessor archive.

## Visual and source review

All 43 pages were rendered through PyMuPDF and inspected in three contact sheets. Selected first-edition proofs, the frontmatter guide, both new charts, the integrated example, statement map and bibliography received full-page inspection. After the last chart and appendix edits, pixel comparison with the reviewed render showed changes only on physical pages 35 and 43, which were reinspected. Mechanical preflight checks text geometry, glyph markers, font embedding and LaTeX diagnostics; it does not prove a mathematical statement.

All seven inherited figure assets remain available. The two new charts were actually generated from exact rational illustration data with Python/Matplotlib. The matched source and figure-generation code are included. No generative pictorial imagery is used.

The fourteen-reference bibliography has targeted source review, not a comprehensive literature or priority audit. Entries 1–12 retain the earlier recorded review depth except for the specifically noted contextual recheck. The two added sources have different review depths, stated in SOURCE_MAP.md. Their presence does not turn the direct proofs into externally reviewed claims.

## Reproduction and publication boundary

The clean rebuild script copies the delivered source into a new temporary directory without its build tree or PDF. It rebuilds with the supplied vector figures, reruns all three suites and preservation, audits source and PDF, and validates the new local receipt. It compares extracted text on every page and ten scientific/index files, excluding only the top-level runtime_seconds fields of the three suite reports. `validation/fresh_rebuild.json` contains the actual commands and comparisons. Data, hypotheses, source indices, count domains and result values are not ignored.

This is same-environment reproducibility, not independent or cross-platform replication. The PowerShell script was not executed on Windows. Binary PDF identity, PDF/A and tagged accessibility are not certified. Checksum equality proves agreement with the shipped snapshot inventory, not origin authentication or mathematical truth. Verify that inventory before rerunning scripts that replace timed receipts.

The original v0.5 PDF, ZIP and notes remain unchanged. A complete copy of its source ZIP is retained, with selected history files for reading convenience. No standalone font files, third-party full papers or private conversation transcripts are distributed.

Version 1.0 closes the stated theoretical and editorial scope. State-changing noisy filters, general model admission, unrestricted semantic learning, time-uniform finite-memory guarantees without additional assumptions and complete proof-assistant verification remain separate research tasks.
