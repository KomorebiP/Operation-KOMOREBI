# Paper IV visual source correspondence: resolved

3 November 2026 · Komorebi P.

Paper IV now has a complete, explicitly identified reconstructed source edition
of its selected visual guide. The rebuilt PDF has 28 pages. All 27 content pages
match the selected 16 October PDF after Unicode NFKC and whitespace normalization;
the cover identifies the new reconstruction. All 28 rendered pages were reviewed,
with detailed inspection of the cover and physical pages 14 and 28.

[Read the visual guide online](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/atlas/)
· [Rebuilt PDF](../publication/paper-iv-visual-reconstruction/Paper_IV_Visual_Guide_Reconstructed.pdf)
· [Editable source package and build instructions](../publication/paper-iv-visual-reconstruction/README.md)
· [Build and page-comparison record](../publication/paper-iv-visual-reconstruction/BUILD_RECORD.json)
· [Provenance receipt](../verification/visual-guide-provenance/2026-11-03.json)

The reconstruction starts from the retained October 8 editable guide. It restores
the later PDF's distinction between tangent poles, positive integer reciprocal
powers and general complex-power branches on V12, and its revised evidence table
on V26. The online guide now uses this source, including both later corrections.
Its drawings and manuscript return links retain their existing sources.

The package includes all fonts, styles and 24 vector drawings needed to build the
PDF. An early `xcolor` option declaration resolves a package load-order clash.
The missing Paper IV font binaries are supplied from the collection's retained
Paper I font set with their licenses. The restored content pages preserve the
selected PDF's text and pagination.

This closes [F04](FINALIZATION_QUEUE.md#f04) through its documented reconstructed
edition route. The original imported source, selected PDF and dated freeze
records remain available as history. The current edition has a source, build,
PDF comparison and page review, so source correspondence is no longer open work.

Paper VIII's related checksum discrepancy is also resolved by a
[new crosswalk revision](../publication/paper-viii-visual-crosswalk/VISUAL_TO_TRADITIONAL_CROSSWALK_v2.json).
It binds the retained 34-page PDF while preserving all 32 original plate records
and manuscript bindings. All 32 titles, printed locators and page labels were
rechecked against the PDF; the HTML converter rechecks stable manuscript labels,
numbers, kinds and titles. The imported crosswalk remains historical evidence.

The evidence table describes its retained dated checks. This work adds source
and edition verification; it does not add Lean execution, proof review or model
execution. The accepted formal scope remains 68 scoped results.

Proofreading self-review covered the changed source text and presentation
wrappers. The restored wording matches the selected PDF; no new mathematical
formula, proof step or theorem claim was introduced.

To check the artifact identities, run `python -B tools/visual_guide_provenance.py`.
To repeat the PDF comparisons and Paper VIII page checks, run the same command
with `--pdf`; this optional check requires `pypdfium2`.
