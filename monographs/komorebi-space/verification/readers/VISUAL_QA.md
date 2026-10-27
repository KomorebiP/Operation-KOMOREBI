# Reader visual and structural QA

The current PDFs contain 163 monograph pages, 25 Lean guide pages, and 20 visual guide pages. The additional page in each reader is the publication and reuse notice.

All 208 pages were rendered and visually reviewed in contact sheets. Full-size checks covered all covers, the new notice, a dense analytic proof page, and a 3D visual investigation. No clipping, overlap, missing glyphs, or layout defects were observed. Inherited chapter and appendix page breaks were preserved.

Automated checks found zero out-of-page text words and zero invalid internal destinations across 404 links. The three PDFs expose 47, 17, and 18 bookmarks respectively. Every listed PDF font is embedded. All three contain the license notice as extractable text.

A second clean three-pass build was compared with the reviewed build. All 208 pages have identical extracted text, word geometry, and render pixels at 54 dpi; bookmarks and links are identical. The files are byte identical after substituting the PDF document IDs. The delivered files are from the second build, with hashes in `FINAL_PDF_CHECKS.json`.

The first build's main output used `Realization_Calculus_Volume_I_Komorebi_Space.pdf`; it was renamed without changing bytes to the canonical `Komorebi_Space.pdf`. The builder now writes the canonical name. `BUILD_REPORT.json` retains the paths as recorded during the clean build. `FRESH_BUILD_COMPARISON.json` maps the tested and delivered names.

These checks concern publication delivery. They do not substitute for the release's separate formal verification.
