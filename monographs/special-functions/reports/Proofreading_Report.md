# Special Functions

REALIZATION CALCULUS  /  DEEP PROOFREADING REPORT

## Outcome

The manuscript has been revised throughout for prose, mathematical definitions, stated hypotheses, notation, cross-references, source attribution and consistency between the expository chapters and proof appendices. The corrected book retains the established monograph design and all ten proof appendices.

| Document | Reviewed input | Corrected output |
| --- | --- | --- |
| PDF pages | 132 | 134 |
| Structure | Five parts, seven chapters | Five parts, seven chapters |
| Proof appendices | Ten | Ten |
| Vector figures | 32 | 32, original assets preserved |
| PDF bookmarks | Preceding design navigation | 153 validated bookmarks |

## What the review changed

The most important corrections concern the Hankel order convention, arithmetic support and zero-depth notation, the distinction between positive-definite and positive-semidefinite examples, and the interpretation of zero orbits. These are substantive clarity and consistency repairs, not merely stylistic polishing.

The editorial ledger records 90 edit groups across 22 changed or added production TeX files. An edit group can contain several replacements. These counts are not counts of independent mathematical mistakes. The exact source diff is included alongside the readable change log.

## Scope

The entire manuscript was read and compared internally, including its seven chapters, ten proof appendices, evidence register, glossary and references. This is a deep editorial and mathematical-consistency review, supported by fresh finite computations. It is not a new Lean certification, exhaustive independent reproof of every theorem, or systematic historical-priority survey.

All 428 original research files remain byte-identical to the supplied package. Fresh evidence was added separately. The production PDF uses the same 32 vector figure assets.


---

# Substantive corrections

DEFINITIONS, DOMAINS AND LOGICAL DISTINCTIONS

## Hankel order and degree

Glossary, Chapters 3 and 7

The glossary now uses an order-m matrix indexed from 0 to m-1. It therefore tests real polynomials of degree at most m-1. An order-five test covers degree four, not degree five.

## Arithmetic support and depth zero

Chapter 2 and glossary

The squarefree and coprimality restrictions are explicit in the exponential representation. The undefined E(0) shorthand is replaced by A(0) = Z_Q(2a) - 1, with Z_Q defined before use. The excluded n = 1 atom is explained.

## Two nonconvexity arguments

Section 3.5 and Appendix C

The positive-definite midpoint example does not establish the positive-semidefinite case because zero is permitted there. The main text now also gives the separate semidefinite example already proved in the appendix. Its normalized convex-combination mass is exactly -1/25.

## Zero-orbit interpretation

Chapter 4 and glossary

The zeros of d_N are counted with multiplicity. Each corresponds to an N-fold rotation orbit of zeros of D_N. The earlier glossary wording conflated the two functions.

## Signed quadratic forms

Chapter 3 and Appendices C and I

A negative value of the signed quadratic form is not called a negative norm. The real-polynomial domain and the exclusion of the zero polynomial in strict positivity statements are stated explicitly.

## Definitions and parameter bounds

Chapters 1, 2 and 6; Appendix I

Maximum modulus, normalized feedback banks and polynomial squared norms are defined before use. The weak-tap domain is 0 < epsilon <= 1. Sector and boundary assumptions are clarified at their point of use.


---

# Proof and exposition alignment

READER-FACING REPAIRS WITHOUT RECASTING OPEN CLAIMS

## Scalar and coupled growth

Growth statements were checked against the fixed-width lower comparison and the positive-eigenvector argument in their appendices. The text retains strict positivity and contraction assumptions. Positive lower and finite upper type bounds are not rewritten as existence of an ordinary type limit.

## Inverse problems and finite resolution

Coefficient-recovery statements now say derivatives through order seven, rather than implying seven independent informative derivatives. Compact-window closeness remains distinct from exact parameter recovery and global growth. A sufficient observation radius is not presented as an optimal detection threshold.

## Exact laboratories

The diagonal anchor is described as scaled hyperbolic sine, not scaled sine. Ordinary and exponential generating functions, their different products, and finite polyphase carry conventions are distinguished. Worked commands now identify the package research directory rather than an earlier session location.

## Navigation and theorem references

Theorem identifiers are qualified by appendix. Vague source-file proof pointers now lead to the relevant proof inside the book. Resolution figures have automatic numbered references. A stale spectral section number was replaced with a live reference. Caption, equation and code breaks were checked after the changes.

## Bibliography and evidence language

Duplicated references were consolidated into 15 numbered entries. Targeted primary-source checks corrected titles and metadata and added the published Voros erratum. Project self-review records are explicitly distinguished from external peer review, and archived computation counts are separated from the fresh runs.

The bibliography review was targeted. It did not independently establish the priority of every construction. The erratum publication record was checked, not every possible implication of its contents. Retrieval failures and their limits are recorded in the package.


---

# Fresh computational evidence

COMPLETED RUNS AND THE RECOVERED TIMEOUT

| Suite | Exact assertions | Numerical assertions | Guards |
| --- | --- | --- | --- |
| Ten foundation scripts | 19,871 | 5,576 | 61 |
| Three coupled / resolution scripts | 5,272 | 26 | 13 |
| Combined | 25,143 | 5,602 | 74 |

These are executed finite assertion statements, not independent theorems or exhaustive parameter coverage. The foundation exact count includes 540 helper assertions in the arithmetic-inverse checks. Numerical assertions are not directed-rounding interval certificates.

## Coverage

The foundation scripts cover nonlinear and asymmetric dilation, complex arithmetic depth, orbit zeta values, arithmetic orthogonal polynomials, dilation type, arithmetic inverse calculations, multiple-prime sieves, spectral continuation, and the sequence/polyphase laboratory. The coupled scripts cover coefficient recurrences, finite inverse formulas and resolution certificates.

All 14 coupled/resolution figure pairs were regenerated. The book retains the original 32 vector figure assets. Regeneration establishes that the relevant figure pipeline runs, not that a finite plot proves an unbounded statement.

## Execution failure and recovery

The first aggregate foundation run reached the execution environment time limit after nine scripts had written passing reports. The runner did not finish its aggregate summary. The remaining laboratory script was executed separately against the same isolated input snapshot and passed. The coupled suite then completed normally. No mathematical or numerical assertion failure was reported by these completed scripts.

The raw logs and per-script results are retained. The audit does not mislabel the interrupted orchestration as an uninterrupted successful run. A separate exact check of the newly surfaced semidefinite counterexample also passed and is not added to the suite totals.

## Reproduction

The source package includes original research scripts, isolated execution snapshots, outputs, the corrected manuscript and a build script. The convenience replay helper uses a new evidence directory and refuses existing destinations. All book claims retain their mathematical hypotheses regardless of computation status.


---

# Publication checks and boundaries

FINAL LAYOUT, REPRODUCIBILITY AND REMAINING LIMITS

## Publication checks

The final book has 134 pages and 153 PDF bookmarks. All pages were rendered and reviewed in contact sheets, with full-size inspection of representative mathematical pages and the revised passages. Automated checks found no invalid internal links or text outside the defined safe area. The final LaTeX build contains no warnings, unresolved references, overfull boxes or missing-glyph messages.

A clean build from the extracted delivery source passed. All 134 pages matched the delivered PDF in extracted text and rendered pixels at 72 dpi, and the bookmarks matched. PDF metadata bytes differed, as expected between builds. The machine-readable ARCHIVE_REBUILD.json records the comparison. SHA-256 file inventories and the exact production-source diff are also included.

## What remains outside this pass

No Lean compilation was performed. The finite tests do not replace the analytic proofs. Independent mathematical review remains a distinct step, and this report does not certify the absence of every possible mathematical error.

The text continues to leave open the existence and values of ordinary type limits, possible oscillations, several zero and angular-growth questions, and extensions outside the strictly positive contraction domain. The displayed degree-four positivity and degree-seven detector do not settle the intervening degree-five and degree-six detection question. Sufficient resolution bounds are not claimed to be optimal.

The separate companion visual guide remains in its earlier design. Preserved historical source documents are clearly separated from the production monograph and may retain their own earlier labels and layouts.

## Audit map

FRESH_VERIFICATION.json: fresh computation totals, PDF checks and source preservation.

editorial_changes.json and EDITORIAL_CHANGELOG.md: recorded editorial replacements and explanations.

source_changes.patch: exact changes to the editable production source.

MATH_EDIT_REVIEW.json: mathematical-string comparison aid, not a proof of semantic equivalence.

ARCHIVE_REBUILD.json: clean extracted-package build and delivered-PDF comparison.

research/proofread_runs/: retained source snapshots, script reports and regenerated figures.

