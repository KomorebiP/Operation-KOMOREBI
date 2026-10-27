# Continuation guide visual review: PDF pages 7–13

Reviewed 12 October 2026 by the independent audit subagent using the PDF skill's visual inspection workflow. Root reviewed PDF pages 1–6 separately.

**PDF reviewed:** `continuation/publication/Continuation_Guide.pdf`

**Observed PDF SHA-256:** `e939949fc5d860bac91f53fb1956af851ba186ced21cdd63502f35bfd659e3a7`

**Scope:** Each actual rendered page `tmp/pdfs/page_07.png` through `page_13.png` was viewed individually at original resolution, 857 × 1109 pixels. The PDF includes a title page, so the printed footer numbers on these seven pages are 6–12. An additional 2× PDF rendering of the equation (14) region was inspected to confirm its tag placement. This review did not rely solely on extracted text or a contact sheet.

## Outcome

**No clipping, text/table overlap, malformed displayed equation, or misplaced equation tag was observed on these seven pages.** The long boundary-case table breaks cleanly across pages 12 and 13 and repeats its heading.

**Two repeated typography problems should be corrected before calling this guide fully polished.** Ordinary prose prints source-style mathematical identifiers literally, and headings carry duplicate numbering. There is also one minor avoidable equation-introduction split.

## Page findings

| PDF page | Findings |
|---|---|
| 7 | Displayed equations (7) and (8) are clear and correctly tagged. Prose prints literal `p_n`, `C_n`, `u_j`, and `δ_n` rather than proper mathematical subscripts. Heading reads `5.3  3. WR01: ...`, duplicating the original route's manual section number inside the generated section number. No overlap or clipping. |
| 8 | Prose prints `p_*`, `a_*`, `A_n`, and `L_n` literally. Heading repeats numbering as `5.4  4. WR02: ...`. The final word `Consequently` introduces equation (9), which begins page 9. This is legible but would read better if kept with the equation. |
| 9 | Equations (9)–(15) and their tags are legible and within margins. Equation (14) was additionally inspected from a 2× PDF detail render and its number is correctly placed at the right. Raw identifiers continue in prose. Heading repeats numbering as `5.5  5. WR03: ...`. |
| 10 | Heading duplication continues (`5.6  6. ...` and `5.6.1  6.1 ...`). Prose includes literal brace syntax in `B_{M₁} ⊆ B_{M₂}` and literal `a_θ`. This is the most conspicuous remaining prose-math formatting issue. Displayed estimates are properly typeset. |
| 11 | Displayed equations (16) and (17) and the parameter-limit expression are clean. Prose continues to show `P_C`, `a_ε`, and `a_M` literally. Subsection headings retain two numbering systems. No clipped text. |
| 12 | Equations (18) and (19) are properly aligned and tagged. The closed-image and uniqueness paragraphs show literal `B_M`, `y_j`, `u_j`, `y_M`, and `a_min`, including underscores inside prose set notation. The boundary table starts cleanly and neither row displayed on this page is split awkwardly. |
| 13 | Boundary table continuation is clean, with repeated column headings, no overlap, and a clear bottom rule. Literal `C_n` remains in a prose cell. Remaining white space below the final paragraph is normal end-of-document space rather than clipped or missing content. |

## Recommended corrections

1. In the publication conversion step, typeset inline mathematical identifiers and expressions as inline math. In particular, remove visible literal `_` and brace syntax from ordinary mathematical prose. Preserve literal code identifiers only when they intentionally name code.
2. Retain either generated section numbering or manual route numbering, not both. The current headings concatenate the two.
3. If feasible after reflow, keep `Consequently` with the following displayed equation (9).

These are publication-conversion corrections. They do not require changing any mathematical statement or proof. No source or PDF edits were made by this reviewer.

## Verification limits

The parent supplied a passing font-embedding, page-boundary, and TeX-warning preflight. This review does not independently rerun those tests. The PDF hash was independently recomputed and matched the supplied value. A final rebuilt guide will have a different hash and needs a fresh visual pass over the reflowed pages before this record can be treated as final acceptance.
