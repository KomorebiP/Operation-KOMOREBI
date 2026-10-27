# Final proofreading and publication report

## Delivered edition

**Realization Boundaries: Finite Grammar, Infinite Groups, and the Limits of Reconstruction**  
Komorebi P. · Realization Calculus

The final monograph has 64 pages, 12 chapters, three appendices, eight vector figures, and 45 numbered theorem, proposition, lemma, and corollary statements. The manuscript, figure source, arithmetic implementation, tests, and verification records are synchronized. Original inputs were not overwritten.

## Substantive mathematical correction

**Propositions 9.3 and 9.4, printed page 35.** The predecessor claimed that completion failed to reflect isomorphisms on the family consisting only of the paired-prime groups G_A. Its proof instead used the inclusion D → G_A, whose source is not a member of that family.

The corrected statement retains faithfulness on residually finite groups and failure of fullness on the paired-prime subcategory. Failure to reflect isomorphisms is stated on the larger full subcategory containing D and the groups G_A. A new proposition proves the opposite behavior within the paired-prime family: a supplied homomorphism G_A → G_B is an isomorphism exactly when its induced map of completions is an isomorphism. Diagonal coordinate units, the torsion-image obstruction, and the automorphism criterion prove this assertion.

The common-completion construction, root criterion, selector classification, and exact oracle theorem did not require a change in their conclusions during this review.

## Other mathematical and expository corrections

1. A computable profinite presentation of the uncountable group P is explicitly an effective inverse system of finite groups, not a computable countable presentation of P's underlying set.
2. The topological support-obstruction extension explicitly requires Hausdorff target coordinate groups, so that the relevant kernels are closed.
3. Description complexity uses a fixed finite binary encoding and bit length. An arbitrary symbol from a countable alphabet is not a free unit-cost infinite-information token. Translation length bounds are stated unambiguously.
4. Finite-stage splitting is described as splitting over finitely generated rational images, not as a claim about all finite subgroup extensions.
5. The finite-target equivalence is called a natural bijection, not a literal equality of Hom sets. The purity argument explicitly says homomorphism when it needs one.
6. Uniform marked decoding remains distinct from nonuniform unmarked decoding with an infinite-order element and finite exception data. The arrows in the effective figure are not asserted to compute an isomorphism to an arbitrary copy.
7. In the arithmetic atlas, additive divisibility is described as finding a half rather than a square root.

## Implementation defect and repair

The earlier residue normalization used `int(value)` and silently truncated a fractional input such as 1.9. The element constructor also accepted floating-point rational inputs, which could conceal unintended binary approximations. These were input-contract defects, not counterexamples to the printed group identities.

The revised implementation rejects noninteger prime labels, residues, indices, and multipliers, and accepts rational coordinates only as integers or `Fraction` values. It rejects Boolean values where a genuine integer is required. Direct construction normalizes the same way as the factory. Selector values must be Boolean or integer bits. Prime caches are type-sensitive so an invalid float equal to a cached integer cannot bypass validation. Root multipliers must be positive integers. A separate regression suite exercises these boundaries and exact finite diagonal-automorphism inversion.

## Fresh execution

| Suite | Exact finite assertions | Outcome |
|---|---:|---|
| Core arithmetic | 114,738 | PASS |
| Supplemental mathematics | 53,284 | PASS |
| Release regressions | 21,047 | PASS |
| **Total** | **189,069** | **PASS** |

The total includes seven named mathematical negative controls and 39 malformed-input rejection cases. The Python example extracted from Chapter 11 passed its four assertions separately. The standalone worked examples also ran successfully. Reports record the tested source hashes and finite parameters.

These checks do not prove statements about every infinite selector, noncomputability, or grammar nonrealizability. The universal claims rely on the ordinary proofs in the book.

## Typesetting and visual review

All pages were rendered with PDFium and inspected in contact sheets. Revised proof, figure, table, glossary, and reference pages were inspected at larger scale. All eight figures were reviewed separately. The final TeX log has no unresolved references, overfull or underfull boxes, missing-character warnings, or duplicate destination warnings. The final PDF's text bounds, internal links, bookmark destinations, page labels, and font embedding were checked separately.

Prime-pair labels now use the indexed primes instead of the ambiguous phrases “even prime” and “odd prime.” The paired-prime figure's connector lines no longer run through number labels. The effective-representation figure distinguishes abstract sameness of type from a computable map. Registry columns use ragged-right text, glossary entries are kept together, and redundant appendix prose was reduced to remove an avoidable spillover page.

## References and production incidents

Five cited references were checked against primary author or publisher sources. The reference-check record identifies the exact locations inspected. Historical priority for the combined construction has not been established.

A DOI redirect for the Calvert–Harizanov–Shlapentokh article failed to load through the web tool. Its bibliographic metadata were checked using the publisher's issue listing and the authors' arXiv preprint instead. The full paywalled published article was not reviewed.

One JPEG contact sheet could not be opened by the image viewer despite existing on disk. Re-encoding it as PNG succeeded, and the affected pages were inspected. A first attempt to extract the printed Python example accidentally included the LaTeX option `[language=Python]`, producing a SyntaxError in the extraction helper. The extractor was corrected to remove the LaTeX option, and the unchanged printed Python example then executed successfully. A combined rendering and preflight command also exceeded its execution limit. The checks were rerun in smaller steps with cached page dimensions and completed successfully: 19,080 text boxes, 191 internal links, 87 bookmarks, and all embedded fonts passed their checks. None of these production incidents remains an unresolved defect in the final PDF or arithmetic code.

## Verification limits

No Lean compiler was available in the runtime and no Lean compilation was performed. The formalization appendix remains a plan. This is an internal mathematical and publication review, not independent external peer review or a historical-priority certification. No universal proof was inferred from a finite test count.
