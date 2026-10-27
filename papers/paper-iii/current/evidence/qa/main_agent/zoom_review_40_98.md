# Main PDF visual review: physical pages 40–98

**Result:** every assigned page was inspected as an actual rendered image. The only material finding is Figure 5 interrupting the statement of Theorem 21.3 across physical pages 49–51. No other clipping, overlap, unreadable mathematics, accidental blank pages, or figure/statement interruption was found in this range.

## Scope and provenance

- Reviewer: `/root/expanded_audit/main_math_zoom`.
- Reviewed main PDF: `Paper_III_Final_v1.0.0.pdf`, 99 physical pages at the frozen review point.
- Exact coverage: **physical pages 40–98 inclusive (59 pages)**. Printed pages are 36–94. This reviewer does not claim inspection of pages 1–39 or 99.
- Physical 40–79: independently rendered with Poppler `pdftoppm` at **144 dpi**, 1224 × 1584 pixels. Each full image was opened with original image detail.
- Physical 80–98: parent-provided renders at **120 dpi**, 1020 × 1320 pixels. Each full image was opened with original image detail.
- Dense mathematical pages, all assigned diagrams, and all atlas pages V1–V24 (physical 75–98) were actually inspected. Text extraction served only orientation and source lookup.

Frozen input SHA-256 supplied by the parent at rendering time:

```text
847f242b12d6c5ca0fabee33f08b5243fb08734f61ece60c1adf4199a2d7b266
```

At report-write time the publication path had already changed to a 602,047-byte PDF with SHA-256 `e5de4c6e348c5be4c8c4bc49dc15be7aeaee285c28b47e0145aa2fedecd834e1`. **That newer hash does not identify the image set inspected here.** The original frozen PDF was reported as 602,088 bytes. Individual hashes for all 59 inspected images are in the JSON companion report. This provenance mismatch was reported immediately to the parent. The parent subsequently confirmed that root had proceeded with the authorized Figure 5 layout rebuild and will coordinate targeted post-build checking. This report is a historical baseline review.

Observed Poppler version: 26.05.0. The 144 dpi rendering command was:

```sh
pdftoppm -f 40 -l 79 -r 144 -png /workspace/scratch/9014da510e4f/paper3_release/publication/Paper_III_Final_v1.0.0.pdf /workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page
```

The render process exit status and elapsed time were not retained; no claim about either is made. All 40 resulting images existed and were opened successfully. The parent produced the shared 120 dpi images.

## Material finding: Figure 5 interrupts Theorem 21.3

| Physical page | Printed page | Observed content |
|---|---|---|
| 49 | 45 | Theorem 21.3 begins near the bottom with “Suppose” and its commutative square. |
| 50 | 46 | Figure 5 occupies the full page. |
| 51 | 47 | The same theorem statement resumes at the top with “is a commuting square. Then”. |

The full-page figure is inserted inside one theorem statement. This is a material reading-flow problem; the diagram itself is clear, and no mathematical defect is inferred.

The source figure occurs in `manuscript/chapters/03_nonlinear_coordinates.tex`, approximately lines 943–948, immediately before `thm:obstruction_naturality` around line 950. A minimal repair is to flush Figure 5 after its figure environment and before that theorem, for example with `\clearpage`, followed by a rebuild and targeted visual check. No manuscript or PDF was edited by this reviewer.

## Other observed layout results

- Mathematical displays, diagrams, subscripts, and superscripts remain readable and contained in the inspected range. No missing-glyph boxes or visible clipping were observed.
- No accidental blank pages were found. The conclusion on physical 73 and atlas introduction on physical 74 are intentionally sparse.
- Figure 6 on physical 71 follows the completed Theorem 27.8 and precedes Corollary 27.9. Its placement does not interrupt a statement.
- All 24 atlas pages (physical 75–98) are readable, including matrix and candidate tables, rectangular products, shear and gauge illustrations, tree syntax, nonlinear curves, and the final evidence table. Labels, arrows, captions, and shaded callouts remain contained.
- Direct page-to-page continuations without an unrelated inserted page were not treated as defects: examples include 40–41, 42–43, 58–59, 59–60, 62–63, and 69–70.

## Inspected image manifest

Each entry below denotes an image actually opened and visually inspected. The JSON companion records dimensions, dpi, and SHA-256 for every image.

| Physical page | Printed page | DPI | Image |
|---|---|---|---|
| 40 | 36 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-40.png` |
| 41 | 37 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-41.png` |
| 42 | 38 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-42.png` |
| 43 | 39 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-43.png` |
| 44 | 40 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-44.png` |
| 45 | 41 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-45.png` |
| 46 | 42 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-46.png` |
| 47 | 43 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-47.png` |
| 48 | 44 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-48.png` |
| 49 | 45 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-49.png` |
| 50 | 46 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-50.png` |
| 51 | 47 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-51.png` |
| 52 | 48 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-52.png` |
| 53 | 49 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-53.png` |
| 54 | 50 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-54.png` |
| 55 | 51 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-55.png` |
| 56 | 52 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-56.png` |
| 57 | 53 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-57.png` |
| 58 | 54 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-58.png` |
| 59 | 55 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-59.png` |
| 60 | 56 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-60.png` |
| 61 | 57 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-61.png` |
| 62 | 58 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-62.png` |
| 63 | 59 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-63.png` |
| 64 | 60 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-64.png` |
| 65 | 61 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-65.png` |
| 66 | 62 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-66.png` |
| 67 | 63 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-67.png` |
| 68 | 64 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-68.png` |
| 69 | 65 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-69.png` |
| 70 | 66 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-70.png` |
| 71 | 67 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-71.png` |
| 72 | 68 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-72.png` |
| 73 | 69 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-73.png` |
| 74 | 70 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-74.png` |
| 75 | 71 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-75.png` |
| 76 | 72 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-76.png` |
| 77 | 73 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-77.png` |
| 78 | 74 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-78.png` |
| 79 | 75 | 144 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/zoom_pages/page-79.png` |
| 80 | 76 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-80.png` |
| 81 | 77 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-81.png` |
| 82 | 78 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-82.png` |
| 83 | 79 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-83.png` |
| 84 | 80 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-84.png` |
| 85 | 81 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-85.png` |
| 86 | 82 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-86.png` |
| 87 | 83 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-87.png` |
| 88 | 84 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-88.png` |
| 89 | 85 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-89.png` |
| 90 | 86 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-90.png` |
| 91 | 87 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-91.png` |
| 92 | 88 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-92.png` |
| 93 | 89 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-93.png` |
| 94 | 90 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-94.png` |
| 95 | 91 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-95.png` |
| 96 | 92 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-96.png` |
| 97 | 93 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-97.png` |
| 98 | 94 | 120 | `/workspace/scratch/9014da510e4f/paper3_visual_qa/main_agent/pages/page-98.png` |

## Limits

This is a visual layout audit, not a new mathematical proof audit or a claim about Lean formal coverage. It is complete for the 59 assigned physical pages only. The parent is responsible for the remaining pages and for consolidating the main-PDF review. The reported finding applies to the frozen rendered image set; any later layout revision must be checked against fresh renders.
