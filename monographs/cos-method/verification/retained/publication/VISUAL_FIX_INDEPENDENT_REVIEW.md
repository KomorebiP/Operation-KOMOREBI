# Independent review of the publication layout repair

Date: 7 October 2026. Reviewer: claims_audit, independently of the figure and guide authors. Review scope: figure layout, mathematical legibility, archived plotting data, and preservation of the frozen engine/proof sources. This is a bounded publication review, not a replacement for the mathematical or implementation audits.

**Verdict: PASS for all 48 final native figures, all 18 visual-guide pages, and all 7 Lean-guide pages.** No remaining clipped formula, crossed annotation, concealed plotted series, or box overflow was found in that inspected set. Final traditional PDF has 85 pages; independent page inspection is assigned separately to numerical_validation (1–20 and 41–65), publication_review (21–40), and lean_companion (66–85). Their actual page verdicts must be merged by the release coordinator; this report does not claim to have individually inspected those 85 pages.

## Exact final artifacts

| Artifact | Pages / figures | SHA-256 |
|---|---:|---|
| Traditional PDF | 85 pages | `759d458cc5152abdd8544938b23dca1ea7c1579f930bb16df8f37fa65b5722b5` |
| Visual guide PDF | 18 pages | `44f4dee6fdfa379dadcff29f3eac56e56fdc5887f6e53053da360bbc9d409de7` |
| Lean guide PDF | 7 pages | `9aa12eefff6c02a9de0dcb299cd0e802cd0598a0f3b4d5849d4709115a6ac969` |
| Traditional figure 08, final corrected category labels | 1 native PNG | `de6b8fd478e89d70ee1ecffeffa6c934439861a4caaca61983936259330bd508` |

The complete 48-PNG hash and coverage inventory is `work/independent_visual_qa/REVIEWED_ARTIFACTS.json`. It contains 28 files under traditional/figures_final (two archived charts carry number 24), three under traditional/figures_packets, and 17 under visual/figures.

## Inspection method and coverage

Every final figure was displayed individually at its original pixel resolution. No figure verdict is based solely on a contact sheet. Visual-guide pages 1–18 and Lean-guide pages 1–7 were freshly rendered with Poppler at 150 dpi and individually inspected. Lean page 6's heading was additionally rendered at 300 dpi; the full word “Safe” is present. Visual page 13 was freshly re-rendered and rechecked after the final thin-spacing change. A fresh render of all 18 pages from the final visual PDF exactly matches the PNG hashes of the individually inspected set (`visual/final_render_check.json` under the evidence directory).

| Native figure range | Coverage | Result |
|---|---:|---|
| Traditional 01–17 | 17 PNGs | PASS; figure 08 rechecked after category correction |
| Traditional 18–27, including both 24 charts | 11 PNGs | PASS; all eight derivatives and three unchanged originals inspected |
| Traditional packet runtime, coverage, tolerance charts | 3 PNGs | PASS; byte-identical to pre-repair originals |
| Visual 00_pipeline through 16_exact_control | 17 PNGs | PASS |
| Visual-guide final page embeds and prose/equations | 18 individual pages | PASS |
| Lean-guide final definitions, inventory, obligations and prose | 7 individual pages | PASS |

## Problems found and resolved during this independent pass

The prior publication review's contact-sheet verdict missed objective defects. In particular, the original traditional figure 02 had arrows crossing block-kernel formula labels; original figure 07 placed packet text over its plotted points, extended the third label through the right boundary, and crossed the data with explanatory notes. Contact sheets were inadequate evidence for the earlier unconditional “no overlaps” finding. The repair required native figure review and individual page inspection.

This independent pass found two additional defects after the initial repair: Lean page 3's five aligned definitions crowded summation limits into the next row, and traditional figure 08 displayed “Fine 32” while its archived category was `fine_64`. The author added four explicit 6 pt definition-row gaps and corrected the category to “Fine 64,” with a display-label mapping recorded. Both changes were rechecked. Figure 08's numerical coordinates did not change. A raw literal `\n` in the draft figure 25 title was also flagged before freezing and replaced by an actual newline; the final two-line title was inspected.

The final visual-guide COS display on page 13 was rechecked after the release coordinator's requested thin spaces around the primed sum, payoff coefficient, real-part operator and characteristic function. The mathematical tokens and page count remain intact.

## Independent data and source preservation

`PRESERVATION_CHECK.json` and `EARLY_PRESERVATION_CHECK.json` in the evidence directory are produced by reviewer-written checking scripts, not merely copied author verdicts.

* All 187 protected pre-repair records match their original SHA-256: engine files, Lean project records selected by the baseline prefix, all archived CSVs, and provenance records. No engine or mathematical proof source was modified by the layout review.
* For eight late derivatives, all 80 plotted points match independently reconstructed coordinates from nine archived CSVs. Signs, absolute-value conventions, CSV grouping/order, repeated reference-grid sizes, and archived `1e-16` zero-display floors were checked. All nine CSV hashes, original PNG hashes and final derivative hashes match their recorded values. Charts 23, 26 and 27 are byte-identical to their originals.
* For early CSV-backed plots and the rank-summary replacement, all 197 plotted points match the archived fields and explicit recipes. Figure 10 keeps the original positive-error subset, sorted by retained-block count; its two zero-error full-retention rows remain in the unchanged CSV. The binary 10-by-8 support staircase matches `phase <= depth` exactly. The rank-summary rows and QR discrepancy-control row match the archived CSVs exactly.
* Figure 16 and all three packet charts are byte-identical to their pre-repair originals.
* The visual guide's before/current finite-control `checks` dictionaries match exactly. Its scientific finite controls were preserved through the layout regeneration. All 17 native visual figures were separately inspected; rebuilt figure 02 shows both plus signs and the equals sign clearly.

## Explicit preservation limit for figures 05–07

A lossless regeneration of the original singular/eigenvalue curves is not established. The original numerical vectors and native generators for those three illustrations were unavailable in the supplied material. The final publication therefore uses disclosed replacements: figure 05 displays the exact archived phase-rank audit; figure 06 displays the QR identity and its archived maximum absolute and relative L2 discrepancies; figure 07 displays the unchanged rounded packet centers and second-centered-moment labels (9.97/28.14, 4.24/2.95, 1.30/1.33), plus the moment definitions. These labels were checked against the original figure itself. No hidden vector was fabricated or inferred from aggregate statistics.

The original three PNGs remain unchanged under engine/figures_final. Their original curves remain available as raster evidence, but complete numerical reconstruction of those curves remains an unresolved provenance limitation. The final replacements preserve the available summaries and mathematical relations; they should not be described as lossless relayouts of unavailable vectors.

The visual and Lean repairs add no new production benchmark, formal theorem, or numerical acceptance claim. The earlier raw-claim and staged-correction audit scopes remain those stated in `CLAIM_AUDIT.md` and `STAGED_CORRECTION_AUDIT.md`.
