# IV–VI page QA

PASS. All 36 IV–VI lesson pages have passed the bounded final layout review. No unresolved clipping, overlap, missing block or material rendering defect was found.

| Paper | Physical pages | Lesson numbers | Lessons |
| --- | --- | --- | ---: |
| IV | 50–61 | 45–56 | 12 |
| V | 62–73 | 57–68 | 12 |
| VI | 74–85 | 69–80 | 12 |

The final PDF has 116 physical pages and 110 lessons. Its SHA256 is `3334d18814f2752ebd9a76ec965bf3165ea77119534b04896132d4ebabf4d530`.

All 36 covered pages were inspected through nine four-page contact sheets derived from 110 dpi Poppler renders. Full-page images were inspected separately for pages 54, 59, 61, 64, 65, 71, 73, 76, 81, 82, 83 and 85. The final changed pages 64 and 76 were inspected again at full render size. The other 34 final page-image hashes match the reviewed baseline exactly; the JSON records both snapshots.

Titles, figure labels and colorbars, central formulas, reading and worked-example paragraphs, carry-forward strips and source/scope footers fit their allocated regions. Dense formulas fit the margins. Sampled full-page figure text, body prose and footers are legible. The actual character modulus, signed Padé full-degree/simple-zero restriction and V12 finite-reference scope remain visible.

The initial PDF render showed fine white crosshatching between heatmap cells on pages 64 and 76. Root authorized a rendering-only correction. V03 and VI03 now retain vector axes/text with 300 dpi colored mesh layers. Their final guide-page renders are smooth; data, formulas, grids and ranges are unchanged. `V03_VI03_rendering_revision.json` records the correction and separate figure checks.

`FINAL_RENDER_EQUIVALENCE.json` confirms the final render transfer. `STRUCTURAL_QA.json` matches the final PDF hash and passes its structural checks. The final compile log contains zero Warning, Overfull or Underfull entries.

This review covers all 36 pages at contact scale and 12 distinct pages at full 110 dpi render size. It does not assert a fresh universal proof, bibliography audit or verification at every zoom, renderer or printer. No mathematical prose was edited during the final page review.
