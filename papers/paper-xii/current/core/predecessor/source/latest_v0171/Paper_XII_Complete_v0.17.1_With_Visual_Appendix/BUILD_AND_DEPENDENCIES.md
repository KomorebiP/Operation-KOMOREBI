# Build and dependency notes

## Source authority

`formal_release/` is the v0.17.1 reverified release, unchanged. Its current proof
sources include 96 registered modules. The main manuscript remained at editorial
version v0.17.0 because v0.17.1 changed verification evidence, not the paper.
`visual_appendix/` is the independent editorial appendix, also unchanged.
`history/` is historical material, not the current status authority.

`Run-PaperXII.py` is a convenience wrapper. It runs inherited scripts from disposable
copies under `build/` so reruns do not silently overwrite the packaged evidence.
The wrapper itself makes no network requests or dependency installations.

## Python

Python 3.10+ is required by the scripts. The supplied `requirements.txt` records
versions available for the current appendix and bundle checks:

- SymPy 1.14.0 — exact symbolic examples.
- pypdf 5.9.0 — append PDF pages and preserve navigation.
- PyMuPDF 1.26.7 — page and link checks.
- NumPy 2.3.5 — the historical finite checker.
- Matplotlib 3.10.8 — the recovered original figure generator.

The original manuscript figure PDFs are preserved, not regenerated. The historical
Matplotlib version was not authenticated here; regeneration may change metadata or
appearance across library versions. All generator source is available for inspection.
The integrity checker uses only the standard library.

## LaTeX

A TeX distribution must provide `pdflatex`. The manuscript uses `amsart`, geometry,
fontenc, lmodern, microtype, amssymb/mathtools, amscd, bm, aliascnt, enumitem, graphicx,
booktabs, array, longtable, hyperref, cleveref, and the amsplain bibliography style.
The matching `.bib` and `.bbl` are included. `Build-Paper.sh` uses BibTeX when it is
available and otherwise accepts the supplied matching `.bbl`.

The appendix additionally uses tabularx, multicol, xcolor, TikZ, tcolorbox, fancyhdr,
and bookmark. It builds its own bibliography-free visual pages and appends them to
the preserved baseline using Python. No external images or web services are needed.

The manuscript shell builder requires Bash. The supplied Lean toolchain and shell
runners are Linux/WSL-oriented; native Windows Lean execution is not claimed.
The appendix's Python builder can use an installed Windows `pdflatex`.

The appendix integration checker is intentionally pinned to the supplied 36-page
main manuscript plus 18-page appendix. If editing changes pagination, update its
page-count, page-label, and preservation expectations together. The full reading
edition is combined at PDF level, not a single flattened LaTeX file. Both editable
LaTeX source trees are included.

## Lean

The compiler and Mathlib cache are intentionally separate from this source bundle:

- Lean 4.34.0-rc2, compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- All nine dependency revision records are in
  `formal_release/RUNTIME_DEPENDENCY_PINS.json`.
- Expected portable-kit structure: `toolchain/bin/lean`, `workspace/`, and the
  pinned workspace package caches.

Run:

```bash
python3 Run-PaperXII.py lean --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

Or, from `formal_release/`, use the original launcher:

```bash
bash Run-Reverified.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The original launcher rebuilds project objects and overwrites that working copy's
verification report. Prefer the wrapper to keep the shipped evidence immutable.
A RUNNING report is not PASS. Interrupted work must not be counted as a certificate.

## Historical source

The recovered original manuscript package includes its Python plotting source and
finite checker. It also includes older LaTeX, old theorem ledgers, and historical
prose audits. These explain provenance; they do not override the current corrected
formal contract. Historical developer scripts and logs may contain original absolute
container paths. They are retained as records, not promised as portable entry points.

`tools/generate_original_figures.py` is the portable plotting copy. It writes to
`build/original_figures/` by default, or to the explicit `--output` directory. It
never needs to write to the old `/mnt/data/...` destination.
