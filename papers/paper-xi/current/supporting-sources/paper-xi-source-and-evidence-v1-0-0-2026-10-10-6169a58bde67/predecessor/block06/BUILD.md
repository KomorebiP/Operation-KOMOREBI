# Build and replay the synchronized readers

## Dependencies

The checked environment supplied Python 3, PyMuPDF (`fitz`), a TeX Live installation with XeLaTeX, pdfLaTeX and BibTeX, and locally installed URW Base 35 fonts. The four retained finite suites also use the Python packages named in their predecessor sources. The tools use the environment already available and do not install anything.

The monograph and Lean reader use XeLaTeX. The core visual guide uses pdfLaTeX. All runs disable shell escape. The builder accepts the usual `bibtex` executable and the `bibtex.original` fallback needed by this runtime's broken legacy BibTeX symlink.

## Single coordinated build

Run from the root of an extracted source checkpoint:

```text
python tools/build_readers.py --output ../paper_xi_b06_build
```

Use a new output directory for each build. For environments where a single long invocation is undesirable, execute the same build in stages:

```text
python tools/build_readers.py --output ../paper_xi_b06_build --stage traditional
python tools/build_readers.py --output ../paper_xi_b06_build --stage visual_guide
python tools/build_readers.py --output ../paper_xi_b06_build --stage lean_guide
python tools/build_readers.py --output ../paper_xi_b06_build --stage assemble
```

Each compilation receipt is bound to its source fingerprint. The assembly refuses stale receipts. The final stage resolves 107 registered reading routes and writes genuine local companion links after all current destinations are known. It copies the two research PDFs unchanged. It does not rebuild their missing or preserved historical sources.

A custom installed URW folder can be supplied with `--font-dir /path/to/installed/urw-base35`. It must contain the expected P052 and Nimbus Sans OpenType files. Do not put those binaries into this package or a redistributed copy. The builder writes a small path configuration only in the build directory.

## Verification and replay

```text
python tools/verify_package.py
python tools/replay_block06.py --output ../paper_xi_b06_replay
python tools/verify_package.py
```

The replay consists of 15 publication regression methods and four finite suites with 28, 23, 15 and 12 methods. It records source hashes and rejects stale result files. It does not run Lean, Lake, the historical arithmetic matrix constructors, or all seven extra Block 03 arithmetic programs.

## Visual inspection

```text
python tools/render_readers.py --kind Traditional --output ../paper_xi_b06_render
python tools/render_readers.py --kind Visual_Guide --output ../paper_xi_b06_render
python tools/render_readers.py --kind Lean_Guide --output ../paper_xi_b06_render
```

This produces 85-dpi page images and contact sheets for the revised original readers. Inspect dense or changed pages at larger scale as well. Current review receipts and selected images are included under `verification/block06`.

## Reproducibility scope

An isolated build from a copied current source reproduced all three revised original PDF files byte-for-byte in the checked environment. This is not a cross-platform guarantee, and it does not overwrite previous blocks' recorded failures of strict PDF binary reproduction.

The final monograph retains 55 underfull-spacing diagnostics in dense inherited prose, without overfull boxes or missing references. The visual build emits the `epstopdf` warning that shell escape is disabled, even though its figures are already PDF. The Lean build has no diagnostics. These are reported, not suppressed and described as a warning-free build.
