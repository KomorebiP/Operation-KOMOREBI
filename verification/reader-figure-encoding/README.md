# Lossless browser figure encoding

233 existing figure previews across 13 groups use lossless WebP: Papers V,
VIII, XI and XII; Komorebi Space; four Quantum families; Realization Boundaries;
Machine-Native Reasoning; Komorebi Methodology; and the Large Signal Model.
The original PNG bytes are retained under `original/`; the manuscript PDF
sources have not changed. The 13 figure receipts bind the original PNG hash,
decoded RGBA hash, and browser image hash.

The conversion reduces the published images from 17,815,944 to 6,455,134 bytes,
saving 11,360,810 bytes under the unchanged site size gate. The original PNGs
remain in GitHub rather than being copied into the reader-site artifact.

Recheck with the pinned dependencies in `website/requirements.txt`:

```text
python -B tools/encode_reader_figures.py --check
python -B -m unittest discover -s tools -p test_reader_figure_encoding.py -v
```

`tools/encode_reader_figures.py --apply` reproduces the conversion from the
original asset layout and is idempotent on the converted layout. It checks
decoded pixel equality before preserving the original and removing the
published duplicate. The shared figure loader verifies both original and
derived hashes and pixel equality during site builds. Tests also reject
changed pixels even if the encoded-image hash has been updated.

After rerunning an existing PNG figure generator, rerun `--apply` before
publication to restore the browser encodings and receipts. Existing archived
original bytes must still match; changed source figures require review.
