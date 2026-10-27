# Building and checking the reading release

Start from this package root. Use Python3 with PyMuPDF and the installed TeX environment. XeLaTeX, pdfLaTeX, BibTeX (or bibtex.original), fontconfig, DejaVu and URW P052 are required for the three original readers. Fonts are dependencies and are not included. The tests are offline. Optional reproduction of the Markdown AST audit also requires Pandoc. Rendering contact sheets with tools/render_readers.py additionally requires Pillow.

```sh
python tools/verify_package.py
python tools/replay_release.py --output ../paper_xi_replay
python tools/audit_release.py --output ../paper_xi_audit
python tools/build_readers.py --output ../paper_xi_build
```

The builder also supports bounded separate calls:

```sh
python tools/build_readers.py --output ../paper_xi_build --stage traditional
python tools/build_readers.py --output ../paper_xi_build --stage visual_guide
python tools/build_readers.py --output ../paper_xi_build --stage lean_guide
python tools/build_readers.py --output ../paper_xi_build --stage assemble
```

Assembly needs all three compiled readers, matches their exact source fingerprints and resolves the 107 registered reading routes against actual destinations. Shell escape is disabled. The two research companions are copied unchanged. No original-source rebuild of the missing Block02 portion is claimed.

The supplied compatibility build.py in each source directory delegates to this central builder. Output must remain outside the immutable package. Run with PYTHONDONTWRITEBYTECODE=1 when importing individual modules manually. The delivered replay sets this itself.

The 24 new publication regression methods are followed by the immutable B06 publication suite (15) and four retained finite suites (28,23,15,12). Six suites total, not a count of universal theorem validations. The direct arithmetic matrix programs and a Lean compiler are not invoked.

Use `python tools/audit_release.py --output ../paper_xi_ast --pandoc-ast` to reproduce the selected raw-Markdown parser audit. Use `python tools/verify_historical_archive.py historical/Paper_XI_Working_Block01_2026-10-10.zip --output ../paper_xi_history.json` only in the full recovered-source package, where that archive is present.

The final environment uses the deterministic timestamp and no-shell-escape flags recorded in tools/build_readers.py. Identical PDF bytes were obtained in this environment. Other TeX/font/library versions can legitimately produce different bytes. Do not replace the frozen PDFs without a new review and ledger version.
