# Machine-Native Reasoning HTML reading edition

This cache preserves the reconstructed 4 November 2026 manuscript as 121 semantic reading articles. It is separate from the accepted nine-chapter core and does not add mathematical assurance. The unchanged 977-page PDF and editable source are available through the reconstructed-edition reader.

READING.json binds every retained TeX file, WebP image, gzip article slice and packed part by SHA-256. The browser verifies both part and decompressed article; tools/reading_payload.py performs the same checks before the full site link validator parses the complete article. Packed bodies and images stay in pinned GitHub storage because Pages is close to its existing 1 GiB deployment limit.

The converter is retained here for audit. To regenerate in an isolated workspace, put these four scripts under tools/, unpack the source ZIP under output/MNR, and provide site/tools from this repository. Pandoc 3.13 is expected under output/vendor/pandoc-3.13/pandoc.exe; its official Windows archive SHA-256 is 23e1f2e978a3df80db8bf65c9c59534f41a23140480cfb4f783a882ab7dc6a4e. Use build_mnr_html.prepare(), export_figures(), render_figures(), and render_pages(), then run check_mnr_math.cjs against MathJax 3.2.2 and package_mnr_html.py. Two standalone TikZcd diagram PDFs are rendered from the matching original main.tex expressions into output/mnr-figure-work/diagram-1.pdf and diagram-2.pdf before packaging. BUILD_RECEIPT.json in the source package identifies Tectonic 0.17.0. The checked cache, rather than a system TeX/Pandoc installation, is used in CI.

See PROOFREADING.json for exact review scope, display-only math adaptations and validation. Frozen source files and original artifacts were not rewritten.
