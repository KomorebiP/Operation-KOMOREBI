# Build and replay

## Read-only operation

All commands below write outside the checkpoint. Preserve the delivered tree so that the strict SHA-256 verifier continues to pass. Python bytecode writes are disabled by the drivers.

```text
python tools/verify_package.py
python tools/replay_block05.py --output ../b05_replay
python tools/check_publication.py --output ../b05_checks/publication.json
python tools/build_atlas.py --output ../b05_build
python tools/compare_pdfs.py publication/pdfs/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf ../b05_build/Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf --output ../b05_checks/rebuild.json
```

The four finite suites use Python's standard library. They contain respectively 28, 23, 15 and 12 unittest methods. These counts are separate scopes, not a theorem count. The runner checks the correct historical JSON count fields, rejects stale output receipts, records exact source hashes and reports timeouts/failures.

The figure renderer requires Matplotlib. Building and PDF checks require PyMuPDF (`fitz`) and an installed `pdflatex`. The LaTeX source uses standard PSNFSS, hyperref, TikZ and the other packages explicitly named in the wrapper and included publication style. No external network service is required by the programs. On Windows these tools may be installed natively or run inside an existing WSL TeX environment. Prebuilt PDFs do not require LaTeX.

```text
python tools/draw_atlas.py --output ../b05_figures
python tools/test_atlas.py --output ../b05_checks/new_finite_models.json
```

The renderer creates one figure per plate, in PDF/SVG/PNG plus a manifest and exact data file. It does not retrieve images. Do not distribute locally installed font files. Fonts embedded in the finished PDFs are not standalone font distributions.

## Reproducibility scope

An isolated source copy rebuilt the final atlas and all 96 figure exports byte-for-byte in the checked runtime. Every atlas page also matched in extracted text and 100-dpi pixels. This does not establish byte identity across different Python, Matplotlib, TeX or font versions. The inherited manuscripts retain their own earlier reproducibility records. B05 does not relabel those historical results.

The original three reader source trees are preserved for the next block but were not rebuilt here. Their font paths and dependencies need an audit in a new working copy. The new atlas build is independent of those historical wrappers. The missing complete B02 editable archive is not required to rebuild the new atlas; the 77-page research companion remains a preserved PDF.
