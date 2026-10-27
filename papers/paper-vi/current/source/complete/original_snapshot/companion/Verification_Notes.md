# Verification Notes

The notes below describe the supplied 31-page, 37-test baseline. For the current 34-page checked edition (54 tests; 33 complete scoped Lean results), see `RELEASE_AUDIT.md` and `../verification/verification_status.json`.


## Build

- LaTeX engine: `pdflatex` through `latexmk`.
- Final paper length: 31 pages.
- Paper-local bibliography commands: none.
- Undefined references: none.
- Overfull boxes: none reported.
- Underfull boxes: none reported.
- All pages rendered successfully and inspected as a contact sheet and at full-page scale.
- PDF annotations and internal links were preserved after metadata scrubbing.

## Code and tests

- Python profile: CPU finite and numerical verification.
- Automated tests: 37 passed.
- Figure outputs: 19 PNG figures and 19 vector PDF figures.
- Machine-readable results: `results/numerical_results.json`.
- Summary table: `tables/numerical_summary.csv`.
- Installable wheel: `dist/projector_transfer_semigroups-1.2.0-py3-none-any.whl`.
- The wheel was installed into a clean target directory and imported successfully.
- No GPU was used or claimed.

## Representative residuals

- packet-semigroup block convolution: `2.5535e-15`;
- exact Markov lumping defect: `5.5511e-17`;
- Bayesian packet reconstruction: `0`;
- Bayesian refinement commutation: `1.1102e-16`;
- Bayesian information-loss factorization: `7.2858e-17`;
- measured Bayesian coarsening defect `L1`: `4.8787e-2`;
- certified Bayesian defect bound: `1.1016e-1`;
- conditional-expectation tower: `0`;
- fractional semigroup law: `2.0817e-17`;
- exact fractional-naturality residual: `0`;
- fractional refinement defect / common-gap certificate: `5.1059e-1` / `9.5079e-1`;
- fractional-semigroup defect / certificate: `1.2969e-1` / `4.4480e-1`;
- Feynman-Kac enumeration: `1.6653e-16`;
- Feshbach projected resolvent: `5.5511e-17`;
- memory-kernel Laplace identity: `6.9389e-18`;
- Duhamel refinement identity: `2.1077e-16`;
- observed low-mode PDE order: `1.999854`.

## Metadata and provenance scan

The PDF information dictionary contains exactly:

- Title: `Projector-Resolved Seed Calculus VI`;
- Subject: `Transfer semigroups, stochastic, Bayesian, fractional, and PDE realizations`;
- Author: `Komorebi P.`.

Creator, producer, dates, keywords, custom metadata, and XMP metadata are absent. A source scan found no personal-name remnants, account paths, or conversational production language.

## Archive verification

- The complete release archive was independently extracted.
- Every internal SHA-256 entry in the extracted release passed.
- The extracted complete release passed all 37 tests.
- The source-focused archive was independently extracted and passed all 37 tests.
- The source-focused archive rebuilt the complete 31-page PDF successfully.

## Claim control

Theorems, classical inputs, numerical certificates, boundaries, and conjectures are labeled separately. The paper does not claim a universal continuum limit, a universal finite packetization of stochastic models, or a solution of arbitrary Bayesian, fractional, or PDE problems.

## Archive checks

The complete release and source-focused archives were independently extracted. The complete archive passed all 37 tests. The source archive passed all 37 tests and rebuilt the 31-page paper successfully. The external SHA-256 ledger records the final archives and principal deliverables.
