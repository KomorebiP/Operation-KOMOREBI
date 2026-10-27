# Independent semantic review of the polished Paper IX

**Claim reviewed.** The polished manuscript preserves the mathematical claims and arguments of the consolidated edition, restores identified omissions with the appropriate evidence, and does not enlarge the scope of the proved results through editorial changes.

**Verdict: proved as written. Status: PASS.** This verdict concerns mathematical fidelity of the revision and the identified restorations. It is not a new Lean compilation, a line-by-line reproof of every archived declaration, a blanket certificate for the recovered Annals manuscript, or fresh authentication of the external Nishibuchi and Stacks sources.

The reviewer was a separate agent who did not edit the TeX or Lean sources. This separation supports an independent review but cannot exclude errors shared by different reviewers.

## Dependencies and evidence

The preserved consolidated manuscript supplies the original claims and proof summaries. Its archived Lean declarations and earlier verification reports supply their formal evidence. The revised manuscript changes the prose and adds source-grounded restorations. The current statement index connects those assertions to their exact source files. The restored Bernoulli specialization instead has an explicit elementary formal-series derivation and is separately marked as having no matched dedicated Lean bridge.

I read all eight original and revised TeX files and their changes. For the central analytic claims, I also inspected the actual polynomial implicit-function, supplied-selection, and integral-specialization declarations and proofs. For the restorations, I inspected the raw baseline ZIP members `CongruentialEuler.lean`, `StandardWindow.lean`, `WindowIndependence.lean`, `StandardWindowPeriod.lean`, `NormalizationBoundary.lean`, and `ZigzagCoefficients.lean`, and the preserved `AffineSharedCorrection.lean`. I read the native progress note behind the added restricted-results summary.

## Obligation matrix

| Obligation | Result | Decisive check |
|---|---|---|
| Original mathematical formulas and references retained | Passed | All 1,407 recognized original mathematical expressions remain, after whitespace normalization. There are 97 inserted expressions. No original label or Lean reference was removed. |
| Hypotheses, coefficient domains, and exceptional cases preserved | Passed | Positive nonlinear depth, square uniqueness, actual solved-block invertibility, prime/composite distinctions, and zero conventions remain explicit. |
| Finite obstruction and shared correction arguments | Passed | Taylor cancellation uses positive nonlinear depth; the affine specialization explicitly permits depth zero. Separate solvability remains part of the compatibility criterion. |
| Weighted lifting and joint motion | Passed | Reconstructed the normalization at scale p^(s+1), the strict threshold r>2s, full-ball uniqueness, the sign of H(a)+Kv, and the error depth 2M−3s. |
| Analytic local graph and derivative | Passed | Actual evaluated formal partial derivatives are used; the block inverse has upper-right block −J⁻¹K. Open product neighborhoods and both directions of the root equivalence are retained. |
| Integral analytic specialization | Passed | Coefficients and center are included into the ambient p-adic field. The text does not make the p-adic integers a vector space over their fraction field. |
| Restored arithmetic statements | Passed | The actual raw source statements and coefficient normalizations match the new text. The Bernoulli derivation is separately classified. |
| Open questions remain open | Passed | Native 13.2/13.3, fraction-field singular persistence, sharper arithmetic, and historical interface work retain their limitations. |
| Statement-to-source links | Passed | Frozen index: 62 mapped statements, 202 links, 110 labels, 53 distinct local references. Independently checked source hashes and declared names for all 24 newly added links. |
| Fresh external-source authentication | Out of scope | Earlier exact-source records are retained. No new inspection of the external papers is claimed. |
| Fresh Lean compilation | Out of scope | No mathematical Lean source was edited. The manuscript correctly distinguishes the earlier 91-check polynomial build from older arithmetic builds. |

The expression comparison is a textual preservation check, not a mathematical proof or a claim that every TeX token is unchanged. The prose, explanatory hypotheses, and added expressions were separately reviewed. Counts are not theorem totals.

## Substantive restorations and clarifications

1. **Universal denominator bound.** The product runs over rows 1 through n. Induction in the actual packet recurrence gives D_(N,j)(n) C_(N,j)(n) in Z, with the empty-product case at n=0. This matches the preserved denominator-clearing declarations.
2. **Bernoulli boundary.** With B(z)=z/(exp(z)−1), the identity 2B(z)−B(2z)=z/sinh(z) gives C_(2,1)(n)=(2−2^(2n))B_(2n), including n=0. The quotient notation removes a common initial zero and denotes a regular formal series. The text and index explicitly state that no dedicated Lean bridge was matched.
3. **Standard address window.** Lucas reduction requires j<p; it gives unit pivots, integrality of the actual normalized coefficients, and address-independent reduction. No condition m|(p−1) is needed for these statements.
4. **Common residual period.** The added period does require m|(p−1), m>0, j<p, and n≥1. The proof can use the already established all-address bound, while the cited original source proves it directly in the Hurwitz ring. It is a sufficient period, with no unsupported minimality claim.
5. **Factorial-loss counterexample.** The values −1/84 and 703/5460 differ by 64/455, whose 3-adic valuation is zero. Multiplication by 3! gives 384/455, of valuation one. These exact values match the original recursive coefficients and the checked refutation of a universal normalized bound without factorial loss.
6. **Signed zigzag normalization.** The relation gamma_m=(−1)^m Z_(2m+1) uses the formal generating function sec(t)+tan(t), rather than a different zigzag sign convention. The source proves the required bridge.
7. **Affine shared correction.** The restored paragraph uses q≥1 and L≥0, with a common lower root and separately valid corrections. Its finite quotient and equality-of-label criterion match the raw affine theorem, including depth zero and composite moduli.
8. **Restricted native progress.** The summary accurately points to the preserved intrinsic Ext¹ obstruction under a finitely presented commutative integer-algebra restriction, finite polynomial CRT, and the rectangular-relation criterion. It retains their external/prose status and does not identify them with the general native conjectures.
9. **Local clarity fixes.** The Taylor divisibility consequence now explicitly specializes R=Z. The finite singular lift set specifies L≥1 and a lower root. The affine Mahler kernel has natural-number indices. Weighted inversion is stated for constant coefficient one. The Native 13.2 encoding is described as one of the needed links, preserving the other unresolved requirements.

## Checks and resolved issues

The review used direct reads, complete TeX diffs, extraction of inline/display mathematical expressions, label/reference comparisons, and SHA-256 comparison of all newly linked raw sources. Details are in `SEMANTIC_PRESERVATION.json` and `SEMANTIC_NEW_LINKS.json`; the current maps and statement index are fingerprinted in `SEMANTIC_REVIEW.json`.

An intermediate edit produced the phrase “; which identifies.” The editor corrected it. The semantic review also identified the ambiguous integer specialization of the Taylor lemma, implicit lower-root/depth hypotheses in the open section, and wording that could make encoding appear to be the sole remaining Native 13.2 obligation. These were corrected before the final freeze. No unresolved mathematical defect was found in the frozen revision. The parent reported an initial statement-index path delimiter mismatch; the normalized archive paths were then checked successfully, including this review's independent checks of the 24 new links.

## Remaining limits

The review does not recover unavailable historical TeX, figures, or experiment files. It does not formalize the Bernoulli boundary derivation or the external/prose results summarized from the native note, and it does not close the open research extensions. Those limitations are visible in the manuscript and the separate completeness report.

The strongest supported conclusion is that the frozen polished edition faithfully presents the checked core, includes the identified source-supported restorations, and states the remaining limits accurately. The remaining release step is PDF layout inspection and packaging against these exact manuscript and map hashes.
