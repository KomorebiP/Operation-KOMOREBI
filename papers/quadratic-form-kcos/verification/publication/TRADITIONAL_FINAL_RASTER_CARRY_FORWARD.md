# Final traditional PDF raster carry-forward

Final PDF SHA256: `56d1cd387af10f99329adaccad7340a312070e4408aa4fad52fc4d5a51c77074`. The frozen PDF has 85 pages and 4,558,023 bytes. A fresh `pdftoppm -r 150 -png` render completed with exit code 0; every page raster is 1275 × 1650 pixels.

Result: **PASS**. All 80 pages outside the contents pages match the previously inspected `759d458c…` PDF exactly, by both PNG SHA256 and decoded pixel equality. Actual changed pages are 2–6. The initial expected change set was 3–6; page 2 also contains the beginning of the contents. Its only changed pixels are subsection-title spacing within native-pixel bounding box `[210,1326,964,1470]`. The preceding contract prose, reading-map table, header and page number are unchanged.

Numerical_validation freshly displayed and inspected final page 2 at native 150 dpi: PASS, no clipping or collision. Publication_review independently freshly inspected all final contents pages 2–6 at native 150 dpi: PASS. Root acknowledged the page-2 deviation as resolved. These fresh reviews, together with exact equality of the remaining 80 pages, carry the coordinated 85-page layout assessment to the final PDF hash.

All 85 per-page hashes, equality results, allowed changes and changed-page dispositions are recorded in `work/TRADITIONAL_FINAL_RASTER_EQUIVALENCE.json`. Final rasters are in `work/traditional_final_toc_render/`. The historical comparison report is preserved at `work/TRADITIONAL_RASTER_EQUIVALENCE_759d458c.json`; the initial strict expectation check is retained at `work/TRADITIONAL_RASTER_EXPECTATION_CHECK_56d1cd38.json`. This was read-only PDF verification; no source, engine or PDF edits were made.
