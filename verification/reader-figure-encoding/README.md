# Lossless browser figure encoding

143 existing figure previews in Paper V, Komorebi Space, and three Quantum
families use lossless WebP. The original PNG bytes are retained under
`original/`; the manuscript PDF sources have not changed. The five figure
receipts bind the original PNG hash, decoded RGBA hash, and browser image hash.

The conversion reduces the published images from 12,693,310 to 4,845,708 bytes,
saving 7,847,602 bytes under the unchanged site size gate. The original PNGs
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
