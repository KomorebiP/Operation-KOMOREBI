# Paper I visual review

Reviewed source: `/workspace/scratch/9f53d520971c/paper1_inputs/Paper_I_Traditional_Final.pdf` (106 physical PDF pages, 8 front-matter pages followed by printed pages 1–98).

Scope: read-only layout and graphics review. All pages were rendered by Poppler to 1500 px on the long edge, inspected in twelve contact sheets, and figure, table, front matter, and suspected split-box pages were inspected individually. This is not a claim that every paragraph was read for prose or mathematical correctness.

## Findings

No visible overlap, clipping, missing figure, corrupted symbol, unreadable table, or broken graphical label was detected in the reviewed rendering. All ten main-text figures render cleanly. The 22 visual-atlas plates appear coherent and retain their complete graphics. Headings, headers, footers, and the Roman-to-Arabic page-number transition are consistent. The figures previously subject to overlap complaints, including main-text Figure 2, are clean in this source.

The following presentation defects should be corrected before the final issue:

| Physical PDF pages | Printed pages | Finding | Suggested correction | Screenshot |
|---|---|---|---|---|
| 9–10 | 1–2 | Section 2 and its introductory route box begin at the bottom of page 9. The box contains only its title there, with all explanatory prose on page 10. | Keep the section heading and its short route box together, or make route boxes unbreakable. | `paper1_visual/page-009.png`, `paper1_visual/page-010.png` |
| 28–29 | 20–21 | The short “How to read the result” box has only its title on page 28. Its body starts on page 29. | Make short explanatory boxes unbreakable. | `paper1_visual/page-028.png`, `paper1_visual/page-029.png` |
| 30–31 | 22–23 | Section 7 route box splits after its first two body lines. | Keep route box together. | `paper1_visual/page-030.png`, `paper1_visual/page-031.png` |
| 44–45 | 36–37 | Short “What we have established” box splits across the page boundary, separating its concluding sentence from its title. | Keep short explanatory box together. | `paper1_visual/page-044.png`, `paper1_visual/page-045.png` |
| 58–59 | 50–51 | Short “How to read the result” box is split across pages in the middle of the hyphenated word “assump-tions.” | Keep short explanatory box together. | `paper1_visual/page-058.png`, `paper1_visual/page-059.png` |
| 6–7 | v–vi | Only the final `psrank` row of the notation map falls on page 7, with its repeated table header and a large gap before “Small examples to keep in view.” | Start the notation table on the next page or adjust its spacing to keep all rows together. | `paper1_visual/page-006.png`, `paper1_visual/page-007.png` |

The first two entries are the strongest defects, because the title is detached from all body prose. Other theorem statements split across pages remain legible and do not show lost content. No source edits were made by this reviewer.

## Rendering notes

Poppler emitted several “Mismatch between font type and embedded font file” warnings. The reviewed rendered glyphs look normal. The warning itself is not evidence of a visible defect and is not an acceptance blocker without a reproducible rendering issue.

Intermediate renders: `/workspace/scratch/9f53d520971c/paper1_visual/page-001.png` through `page-106.png`. Contact sheets: `contact_001_009.jpg` through `contact_100_106.jpg` in the same directory.
