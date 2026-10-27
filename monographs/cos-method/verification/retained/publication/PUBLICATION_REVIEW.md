# Publication review: final repaired combo

Date: 2026-10-07. Reviewer: publication_review. Scope: conservative mathematical proofreading, evidence wording, caption/Markdown portability, native figure inspection and assigned final PDF pages. Separate proof, computation and Lean-build audits retain their own scopes.

**The earlier contact-sheet layout clearance is withdrawn.** That inspection missed real intra-figure collisions, including arrows crossing formulas, notes obscuring curves and clipped annotation boxes. It did not justify the earlier “no overlaps” wording. The repaired set has now received individual native figure inspection and individual PDF-page review with recorded artifact hashes and reviewer coverage.

## Frozen artifacts

| Artifact | Pages | Final SHA-256 |
| --- | ---: | --- |
| Traditional PDF | 85 | `56d1cd387af10f99329adaccad7340a312070e4408aa4fad52fc4d5a51c77074` |
| Visual guide PDF | 18 | `44f4dee6fdfa379dadcff29f3eac56e56fdc5887f6e53053da360bbc9d409de7` |
| Lean guide PDF | 7 | `9aa12eefff6c02a9de0dcb299cd0e802cd0598a0f3b4d5849d4709115a6ac969` |

Traditional Markdown SHA-256 remains `082f054095aa2ef23455a09f8612e8ac1d14529d17c4aed73e1298aaa6053d01`; caption-export evidence pins final canonical TeX SHA-256 `93c9a8b37d58d68634f3401564857a467bc47a5ce4d2cb1cb651b8117ac27f84`.

## Actual full-resolution coverage

| Coverage | Reviewer / evidence | Verdict |
| --- | --- | --- |
| Traditional 01–17 native figures | publication_review; `TRADITIONAL_EARLY_FIGURE_REVIEW.json`; claims_audit also checked all final figures | PASS, including final 08 correction |
| Traditional 18–27, both 24 filenames, native figures | Eight derivatives authored by publication_review; independently checked by claims_audit in `VISUAL_FIX_INDEPENDENT_REVIEW.md` | PASS; authorship disclosed |
| Three traditional packet charts | claims_audit native inspection; unchanged image bytes | PASS |
| All 17 visual native figures | publication_review and claims_audit | PASS |
| All 18 visual PDF pages | publication_review and claims_audit, individual 150 dpi pages; final spacing-only p13 rechecked | PASS |
| All 7 Lean PDF pages | publication_review and claims_audit, individual 150 dpi pages; p6 heading also checked at 300 dpi | PASS |
| Traditional pages 21–40 | publication_review, individual native 150 dpi pages; fresh final-PDF renders all byte-identical to inspected set | PASS |
| Traditional final contents pages 2–6 | publication_review, fresh final-hash native 150 dpi renders | PASS |
| Traditional pages 1–20 and 41–65 | numerical_validation; `TRADITIONAL_PAGE_INDEPENDENT_REVIEW.md` | PASS; final-hash raster equivalence recorded separately |
| Traditional pages 66–85 | lean_companion, independent of traditional author; `TRADITIONAL_PAGES_66_85_REVIEW.md` | PASS; final-hash raster equivalence recorded separately |

The three assigned traditional page ranges cover all 85 pages; the guides add 25, for 110 pages in the coordinated review. This reviewer personally inspected 25 traditional pages, all 18 visual pages and all 7 final Lean pages. No native figure clearance rests only on a contact sheet. Exact own page evidence is `TRADITIONAL_21_40_PAGE_REVIEW.json`; complete traditional raster carry-forward is `TRADITIONAL_FINAL_RASTER_EQUIVALENCE.json`. The complete final traditional comparison detected spacing changes on pages 2–6 (not only the initially expected 3–6); all other 80 page rasters are byte/pixel-identical. Page 2 was freshly cleared by numerical_validation and publication_review. Final visual renders equal the individually reviewed set (`visual/validation/final_render_verification.json`). Own guide records are `VISUAL_FULL_RESOLUTION_REVIEW.json` and `LEAN_FULL_RESOLUTION_REVIEW.json`.

## Specific repairs checked

- Traditional 02: arrows no longer cross block-kernel formula labels. Early chart notes, legends and formulas occupy reserved space outside axes.
- Traditional 05–07: unavailable original vectors prevented a lossless curve reconstruction. Final disclosed replacements show the exact archived phase-rank audit, exact archived QR discrepancy control with the unchanged identity, and the original rounded packet-center/moment summaries with definitions. No hidden vector was reconstructed.
- Traditional 08: “Fine 32” became “Fine 64” to follow archived partition identifier `fine_64`; the irregular label follows the same convention. Coordinates did not change. Both final native PNG and PDF p32 were checked.
- Traditional late curves: notes no longer cross the 19 green series, 20 cluster, 21 convergence curve or 22 left curves; both 24 charts keep interval/certificate annotations outside axes. Figure 22 footer fits; figure 25 uses an actual title newline, rather than literal `\n`.
- Visual 01 colorbar/spectrum labels have separate space; 02 plus/equals signs are clear in dedicated separator areas; 07 cap box no longer clips; 12 COS legend no longer hides curves. Packet/mode-decay notes are outside curves. All 17 final images were checked individually.
- Visual p13: thin spaces separate the primed sum, payoff coefficient, real-part operator and characteristic function; mathematical tokens and controls are unchanged.
- Lean definitions have adequate row gaps, long declaration names wrap clearly, the 26-row inventory stays together and contents has its own page. All seven final pages were checked. Fresh renders disproved a transient impression that p6 “Safe” lacked its first letter; there is no final heading defect.
- Traditional final contents p2–6: wider subsection/subsubsection number columns separate long labels such as 26.10.1 from titles. The p5 concern is resolved.
- Traditional Markdown: all 31 balanced original TeX captions pass individually through Pandoc and are matched by image filename; caption mathematics remains Markdown math. Zero raw HTML math spans/div wrappers remain; named table anchors remain present.

## Preservation and portability

Independent scripts reconstructed all 80 coordinates in the eight late derivatives from nine archived CSVs and all 197 points in early CSV-backed plots/rank summaries. Recorded grouping, repeated reference-grid sizes, signs and archived zero-display floors match exactly. All 187 protected pre-repair records remain byte-identical. Charts 23/26/27, early 16 and all three packet charts retain original image bytes. Visual before/current finite-control `checks` dictionaries match exactly. Evidence: `independent_visual_qa/PRESERVATION_CHECK.json` and `EARLY_PRESERVATION_CHECK.json`.

Original 05–07 PNGs remain unchanged under `engine/figures_final`. Their unavailable vectors are a provenance limit; the replacements must not be called lossless regeneration of those curves. No new benchmark claim was added by the repair.

All 48 Markdown image targets exist and are PNGs: 31 traditional, 17 visual, none Lean. No PDF is embedded as a Markdown image. All 31 converted canonical captions are present. Relative paths require sibling asset directories; uploading a Markdown file alone can lose images. `MARKDOWN_EMBEDDING_REVIEW.json` pins Markdown/image hashes. All 39 Markdown files in the v1.9 archive have preserved extracted copies; the packet v0.1 archive contains no Markdown files.

## Mathematical and evidence wording

Changed traditional material and the integrated packet section were conservatively proofread. Fresh final source checks record 161 distinct traditional labels, no duplicates/missing references, balanced environment counts in all three sources and no stale v1.7 candidate title. The inventory retains 55 theorem/lemma/proposition/corollary statements (61 recorded environments including remarks and algorithm). `PUBLICATION_SOURCE_CHECK.json` pins final revisions.

Authors resolved nonempty-packet and nonnegative-integer expansion-order hypotheses; common COS conditions include nonnegative threshold, truncation endpoint above it, admissible tilt and positive integer mode count. Visual reduction states PSD covariance and symmetric quadratic matrix. Packet formulas state the transform half-plane/logarithm branch. Acceptance compares a directed ratio upper endpoint with an exact-tolerance lower endpoint and preserves literal outer endpoints. This reviewer did not edit theorem/proof contents.

Archived measurements are qualified in prose, abstract, conclusion, tables and plots. Fresh validation reports 58 selected test methods: 48 production plus 10 directed regressions. The final nonfinite-only guard amendment and earlier finite-run source hashes are distinguished. Fresh displayed upper bounds round outward: extreme-tail ratio at most `9.202e-20` against tolerance `1e-18`, with exact Erlang interval contained; 64-dimensional binary64 matrix ratio at most `2.783e-15` against tolerance `1e-12`, with known eigenspectrum enclosed.

The focused Lean build records 26 theorems, 8 definitions and 34 audits. Finite algebra and real enclosure-composition results assume supplied enclosures. Gaussian reduction, spectral inclusion, probability coupling, COS inversion/remainders and interval implementation correctness remain formal obligations. No full Lean probability certificate is implied. The visual Erlang curve uses Decimal point arithmetic at precision 90 and is an illustration, not an interval enclosure or fresh production benchmark.

## Remaining limits

No remaining clipping, annotation collision or concealed series was found in final inspected figures/pages. Complete historical experiment regeneration and original vectors for 05–07 remain outside demonstrated evidence. The probability pipeline is not fully formalized in Lean. Those limits remain disclosed.
