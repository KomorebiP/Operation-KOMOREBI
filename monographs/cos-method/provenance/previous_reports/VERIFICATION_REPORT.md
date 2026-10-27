# K-COS monograph: proofreading and verification report

## Result

The corrected monograph contains **122 pages**, four parts, twelve chapters, four appendices, and seven external references. It retains the professional plum-and-gold design, linked contents, visual atlas, formalization guide, glossary, and consolidated bibliography.

This pass reviewed the LaTeX prose and mathematical statements, reconciled numerical summaries with exact endpoint records, corrected the numerical reporting code, reran the numerical checks, rebuilt the PDF, and inspected the rendered layout. It is not an end-to-end formal verification of the monograph or software.

## Substantive corrections

### 1. QR-core and residual-completion statements

The QR-update theorem and residual-completion theorem still identified the nonzero spectrum of the large factor with an entire core spectrum. An orthonormal basis can contain unused directions, which add zero eigenvalues to the core. Both statements now assert agreement of **nonzero** spectra with multiplicity. Agreement with the entire core spectrum is qualified by the exact-range/full-row-rank hypothesis. The proofs make the isometry argument explicit. A residual-completion proof was added.

The earlier range-core correction remains intact. Eight finite exact symbolic controls include oversized-range, QR-update, and residual-completion examples. These are checked examples and negative controls, not replacements for the general written proofs.

### 2. Dimensionally correct frontier restriction

The frontier-to-I/O proof equated an ambient projected operator with a smaller compressed Gram matrix. The proof now introduces the coordinate inclusion J, distinguishes H_F = J^T H J from J H_F J^T, and proves the restricted power identity on the initial support. Exact path-graph controls check depths zero through four.

### 3. Probability and algorithm hypotheses

The text now states independence of Gaussian and noncentral chi-square components explicitly. It handles an empty active spectrum directly. For a negative-only nonzero spectrum, the positive saddlepoint is restricted to mean(Q) < q < 0; at q >= 0 the survival probability is zero.

The noncentral deterministic shift now has the precise formula q0 = ||(I-P_T) M^(1/2) mu||^2, where P_T projects onto the weighted random range. This replaces an ambiguous “active subspace” condition.

Orthogonality and completeness of the phase projectors are stated locally. The polynomial error theorem compares the same polynomial and initial block under both operators, rather than automatically covering independently adapted restart coefficients. Both singular-value lists are explicitly zero-padded to the sample-space dimension. The packet operation count includes packet-center evaluation at order zero. The zero-frequency decay rate is defined by continuity. The adaptive planner's input and failure conditions are explicit.

### 4. Numerical reporting defect

The old interval implementation converted logarithmic endpoints to ordinary binary64 numbers before subtracting them. That subtraction distorted narrow widths and could report an arithmetic-only width of zero. The same problem occurred in the independent exact-law helper.

The corrected implementation subtracts interval endpoints and evaluates the multiplicative-ratio summary **before** converting those diagnostic quantities to binary64. The authoritative outward endpoint strings and the separate directed acceptance rule were not changed. The returned probability enclosures at the three retained fixed-resolution inputs are byte-for-byte identical before and after the reporting patch.

Two regression tests were added for the reporting behavior. The independent exact-law helper is also checked for a positive nonzero arithmetic width. The only modified engine source files are `interval_kcos.py` and `test_interval_kcos.py`.

### 5. Corrected numerical table and figure

For the retained exact inputs with 128 COS modes and 90 interval decimal digits, the full endpoint strings give:

| Target probability | Logarithmic width, decades | Probability ratio minus one |
| --- | ---: | ---: |
| Near 10^-100 | 8.933925602968493e-13 | 2.057112391533425e-12 |
| Near 10^-1000 | 7.014176662312046e-12 | 1.615073862239687e-11 |
| Near 10^-5000 | 3.342473832579869e-11 | 7.696330420917249e-11 |

The table, evidence summary, and corresponding figure now agree. Displayed approximation values are distinguished from upward-rounded bounds. The independent exact-law interval is fully contained at each input. Original historical CSVs remain available, with their old diagnostic summaries preserved as historical records. No timing or performance result was reinterpreted as a new benchmark.

### 6. Prose, notation, and references

The application-specific factor of one-half in the SKAT-like statistic is distinguished from the general quadratic-form definition. The implementation notation for the cumulant generator, support endpoint, payoff integral, and mode count is mapped to the preceding theory. Ellipsized decimal strings were removed from a purported spectral enclosure. Reference-convergence evidence is distinguished from a full quadrature error enclosure. The stopping-rule prose now agrees with fail-closed behavior at resource caps.

The volume defines SKAT and linkage disequilibrium at first use, uses book terminology consistently, improves selected sentence and list punctuation, and retains mathematically necessary hyphens and semicolons. Four primary references were added for COS truncation, mode counts, damping, and the SKAT application. The COS paper's 2008 online date and 2008–2009 volume designation are made explicit.

## Executed numerical verification

An unchanged baseline replay passed the original 58 tests. After the reporting correction, the final replay passed **60 of 60 tests**, with no failures, errors, or skips:

| Group | Tests | Result |
| --- | ---: | --- |
| Streaming, phase, pruning, residual, and case-study checks | 31 | Pass |
| Signed and noncentral analytic-ledger engines | 8 | Pass |
| Directed interval backend and width-reporting checks | 5 | Pass |
| Accuracy-driven controller | 2 | Pass |
| Verified spectrum and matrix-to-tail bridge | 4 | Pass |
| Directed acceptance and serialization | 10 | Pass |
| **Total** | **60** | **Pass** |

The final replay record confirms that the engine source hashes were unchanged during execution. The delivered engine matches those tested hashes.

Two additional independent controls passed:

* The exact-spectrum 0.02 chi-square(80) control near 10^-5000 met a requested multiplicative tolerance of 10^-18. The directed ratio upper bound is below 9.202e-20, and the independent finite Erlang interval is fully contained.
* The exact-binary64 64-by-64 factor control near 10^-16 met a requested tolerance of 10^-12. All 64 known eigenvalues are contained, and the directed probability ratio upper bound is below 2.783e-15.

The eight new symbolic controls and the pre-existing exact range-core script also passed. Full literal inputs, output endpoints, commands, and outcomes are retained in `verification/proofread_replay_final/` and `verification/proofread_checks/`.

## Publication checks

All 61 numbered source environments are retained: 35 theorems, 12 corollaries, six propositions, two lemmas, five remarks, and one algorithm. The proof-environment count increases from 38 to 39. No original source label was lost. Preservation counts are not a proof of correctness.

The PDF has 97 bookmarks and 194 links. Every page was rendered with PDFium. All eight contact sheets were inspected, with selected corrected pages examined at full rendered size. The static check found no text outside page bounds, blank text pages, invalid internal link destinations, replacement characters, duplicated source labels, or undefined references/citations. The final LaTeX pass has no overfull boxes, unresolved-reference warnings, or missing-glyph warnings.

Six underfull table-cell warnings remain. These concern spacing in narrow table cells, not clipping. This report does not claim that the build is entirely warning-free.

## Formal verification boundary

**Lean was not rerun.** Neither `lean` nor `lake` is installed in the working environment. The Lean files are unchanged from the supplied publication package. The package retains the recorded compiler evidence for 26 theorem declarations, eight definitions, and the 34-declaration axiom audit.

Those formal modules cover finite Gram algebra, refinement, streamed identities, coefficient order, and arithmetic consequences of supplied enclosures. They do not formalize all Gaussian reductions, spectral construction, inversion bounds, or interval-library correctness. The present edits do not expand that formal coverage.

The directed numerical guarantee remains conditional on the stated interval arithmetic and transcendental implementation. Finite tests do not prove correctness for all inputs, and no new native-GPU benchmark or universal comparison against Davies' algorithm was performed.

## Recovered issues during this pass

A first new regression test incorrectly demanded relative agreement of 1e-12 between an internal binary width and the width after outward decimal serialization. That test failed because serialization legitimately enlarges a very narrow interval. The final test bounds the enlargement by the decimal endpoint quantization units plus the final binary64 conversion error. The initial failure and explanation are retained in `development_failure.md`.

An initial build exceeded the short command limit and left a truncated auxiliary file. The next build failed while reading that auxiliary file. Removing only generated auxiliary files and rerunning the three-pass build completed successfully. The failure log is retained. The initial text-only file fetch also returned no content; page-image reading and the supplied editable LaTeX provided usable content. A publisher fetch returned HTTP 403 for the truncation-range paper; the authors' arXiv record supplied its journal metadata and abstract instead.

## Evidence locations

* `verification/proofread_checks/changes.patch`: complete textual changes against the supplied sources.
* `verification/proofread_checks/edits.json`: editorial reasons and before/after text.
* `verification/proofread_checks/publication_audit.json`: PDF, reference, source-preservation, and Lean-file checks.
* `verification/proofread_checks/corrected_fixed_resolution_controls.json`: exact inputs, unchanged enclosures, corrected widths, and independent containment checks.
* `verification/proofread_checks/exact_algebra.py`: eight reproducible exact symbolic controls.
* `verification/proofread_replay_final/`: final 60-test replay and two independent controls.
* `verification/retained/previous_monograph_publication_report.md`: previous publication report, preserved as historical evidence.

The current report supersedes earlier top-level publication summaries. Earlier source and build records are retained for provenance, not represented as newly executed checks.
