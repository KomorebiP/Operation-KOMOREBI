# Komorebi Physics — verified publication and generator checkpoint

**Recorded:** 21 October 2026  
**Technical checkpoint:** `v0.50.0-g1`  
**Status:** PASS for the explicitly scoped strong-generator and publication gates. This is not a claim that the entire physics program or every written theorem has been formalized.

## The mathematical result now checked

For the existing free Dirac group on the infinite coefficient Hilbert space and its actual Fourier transport to physical torus spinor fields:

- The group is strongly continuous on all square-integrable fields.
- A strong derivative at zero exists exactly on the maximal Hamiltonian domain. In physical space this is the explicit first-order weighted Fourier domain.
- The derivative is exactly `-i H f`. Both domain inclusions are proved, rather than only agreement on finite packets.
- The physical domain is invariant under evolution. Hamiltonian commutation includes an actual domain witness, and the orbit satisfies the strong Schrödinger equation at every time.
- The velocity is continuous with only first-order Fourier regularity. Its norm, and the norm of the Hamiltonian output, are conserved.

The accepted source is `formal/generator/KomorebiPhysics/Relativistic3DGeneratorBridge.lean`. It contains **37 named theorems and two definitions**. Its exact source digest is:

```text
ee721cc3ab78f500bab87c1edb358be8b30a0892e7047c9e9cb5aa31a6d51499
```

The proof uses the existing modal exponential, vector-valued square-summable domination, continuous coordinate evaluations for the converse, and the actual physical Fourier equivalence. It does not replace the infinite field space with a numerical array.

## Formal verification actually executed

| Gate | Result and scope |
|---|---|
| Offline runtime recovery | Seven parts verified by the recorded combined SHA-256. Complete extraction exited 0. |
| Exact baseline operator target | Successful build, 3,064 jobs. |
| Generator target | Successful build, 3,066 jobs. |
| Generator strict source check | Pass with `-DwarningAsError=true`. |
| Named API | All 39 named declarations available. |
| Axiom audit | All 39 named declarations inspected. Only `propext`, `Classical.choice`, and `Quot.sound` observed. |
| Positive interface examples | Pass. |
| Three interface mutants | Wrong sign, missing imaginary unit, and missing domain witness rejected. |
| Placeholder mutant | `sorry` rejected by the warning-as-error gate. |
| Baseline API and axiom checks | Both rerun successfully. |
| Imported-environment kernel replay | `leanchecker` passed for the new module. |
| Separate-path strict source check | Exact copied source passed without importing its compiled generator module. |

There are **13 successful generator/compatibility gate records**, including the four expected rejections, in `audit/closeout_2026-10-21/formal/generator_final/gates.json`. The independent baseline rebuild log is alongside them. All final gate records name the same source digest. A lexical screen of the active new module finds no `sorry`, `admit`, custom `axiom`, `unsafe`, or `native_decide` token. Deliberately invalid test files are separate and are not active imports.

The compiler is Lean **4.34.0-rc2**, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned to `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The combined offline archive digest is `66dfa8ce4627489bc61e44a77782931d36c1b626a177790a5d4599034b70ec34`.

**Trust boundary:** Target source proofs were checked against pinned compiled dependencies. The compiler and all of Mathlib were not rebuilt from source. `leanchecker` replays the new constants in the imported environment using the same Lean kernel. It is not a second independent proof assistant or an empty-environment replay of every dependency. The old generic aggregate project root is not evidence for a fresh audit of every historical physics module.

The generic replay launcher's input verification, safe extraction, overlay installation and exact-pin attachment were tested in a new directory with `--prepare-only`. The full production compiler suite used the same explicit commands, recorded separately. The generic launcher was not run end-to-end as another independent full suite.

## Numerical and symbolic checks rerun

Five supplied suites returned exit 0 with new logs and script hashes: the 3,375-mode Fourier regression, exact Clifford and edge-case checks, finite adic identities, the Lorentz-sector BRST parity check, and the covariant backreaction benchmark. These are finite checks with the limitations stated in their scripts and reports, not substitutes for infinite-dimensional proofs or external reproduction.

The backreaction run completed **19 checks, including five negative controls**. It reproduced an unprojected-energy/available-energy ratio of approximately **2.6273 × 10^20** and a common normalization of approximately **3.8062 × 10^-21**. This preserves the physical-production obstruction. It does not solve the coupled production problem or establish cosmological predictions.

Not every electrovac, collapse, cosmology or external-data simulation was rerun.

## Publication, preservation and licensing

The book has **570 pages**, **573 bookmarks**, and **837 internal links**, with no invalid internal destinations found. All 570 pages rendered through PDFium. Revised license, scope and generator pages were also inspected at higher resolution. No text outside the media box, replacement characters, empty text pages, missing-glyph warnings, font-substitution warnings, undefined references, or overfull boxes were found by the final checks. Some inherited justified paragraphs report underfull-box notices, which are not missing text. The book is not asserted to be tagged PDF, PDF/A, or printer-specific press-ready output.

Five changed component documents were rebuilt in three TeX passes. The remaining component PDFs were carried forward from the prior source package, and all final component logs were scanned. The **107 original explicit LaTeX proof environments are unchanged**. Of **196 source image assets**, **194 are byte-identical**. Only the PDF and PNG representations of the verification-scope diagram changed, to reflect the checked generator result. No numerical plot data were altered. Preservation is not an independent proof of the inherited arguments.

The root `LICENSE` and printed notice now provide **CC BY 4.0** for original prose, figures and data, and **MIT** for original software. Original LaTeX and styles are offered under either license. Third-party quotations, datasets, software and other separately attributed material retain their own rights. Historical original-project notices are covered by the new grant only to the extent Komorebi P. holds the rights. The preserved baseline source ZIP is byte-identical.

The complete MIT text is included. The CC grant includes the license designation, attribution notice and official legal-code address. A complete CC legal-code copy is not vendored. No font programs are distributed.

The earlier claim that active book sources contained an “All rights reserved” notice was not reproduced in this inspection. The confirmed publication defect was the missing explicit top-level grant and printed open-license notice. Those are now present.

## Failures retained, not relabelled as passes

The first runtime-extraction process exceeded its command window after the combined archive hash passed. A subsequent complete extraction exited 0. Early Lean drafts failed on real/complex scalar actions, evaluator coercions, simplification and field-notation syntax. Those drafts were repaired before the accepted final checks. The logs of unsuccessful attempts remain under `audit/closeout_2026-10-21/formal/development_attempts/`.

An exploratory `leanchecker --help` call lacked the required executable path, and a later help probe exceeded its command window. Neither is part of the accepted evidence. The actual pinned, module-targeted kernel replay passed. Direct network fetching of the CC legal-code file was unavailable, so the package uses the official license notice and legal-code address rather than claiming to include a fetched full copy.

## Remaining obligations

The **main strong-generator bridge is checked**. The following are outside this certificate:

1. A formal linkage to an abstract unbounded spectral-functional-calculus API for `exp(-itH)`.
2. Formal centered graph-domain/strong-resolvent convergence and the third-order-regularity quadratic bounds. The written proofs remain in the mathematical chapter.
3. The broader historical cumulative/gauge evidence audit, including the known mismatched or missing receipts not covered by the exact target replays.
4. Independent specialist line-by-line review of the entire book and its bibliography. The current pass is a focused mathematical, computational and publication audit, not that whole-book review.
5. Actual finite sampled-lattice comparison, interacting fields and viable physical production. These remain distinct research problems under the book's explicit assumptions.

The source pin, next module and restart instructions are recorded in `PROGRESS_LEDGER_v0.50.0-g1.md`.
