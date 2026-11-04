# Paper IV visual guide: reconstructed source edition

3 November 2026 · Komorebi P.

This is an explicitly reconstructed edition of the selected 16 October 2026
visual guide. It supplies a complete editable source package and its rebuilt
28-page PDF. Every content page matches the selected PDF after Unicode NFKC
and whitespace normalization. The new cover identifies the reconstruction.

The source restores the documented later wording on V12 concerning poles and
complex-power branches, and the later evidence table on V26. The other source
content and all 24 drawings are retained. The `xcolor` table option is passed
before TikZ loads that package. Fonts missing from the Paper IV import are
supplied from the retained Paper I font set with the applicable font licenses.

Run with an existing XeLaTeX installation:

```sh
python build.py
```

Or use Tectonic:

```sh
python build.py --tectonic /path/to/tectonic
```

The build uses an isolated temporary directory and renders the authored TeX.
It does not execute the retained mathematical model or example scripts.
`main.tex` includes `pages.tex`; fonts, styles and drawings are bundled locally.
`BUILD_RECORD.json` records the compared PDFs, page-by-page text results and
rendered-page review. The compiler transcript records the original successful
Tectonic 0.17.0 build. A fresh build can have different PDF metadata bytes.

The evidence table reproduces the selected historical edition's execution
statements. No fresh Lean replay, mathematical proof audit, model regeneration
or example execution is claimed for this reconstruction. Its labels and numbers
retain their original scope and dates.

The original Paper IV import and its frozen manifests are preserved separately.
This package is the maintained source edition; it is not a claim that the
historical October 16 authoring files were recovered byte for byte.

Original text and figures follow the collection's CC BY 4.0 terms. Original
software follows its MIT terms. Font license files are under `fonts/`.
See the repository's `LICENSE.md` for complete terms.
