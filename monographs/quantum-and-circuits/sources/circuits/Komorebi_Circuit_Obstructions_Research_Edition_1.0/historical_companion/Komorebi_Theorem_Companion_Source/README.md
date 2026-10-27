# Komorebi Circuit Obstructions — theorem companion source

Document edition 1, September 21, 2026. This is a documentation supplement to the fixed source release v1.0.0, not a new research tag.

## Contents

- `theorems.tex`: complete editable LaTeX source for the 28-page PDF.
- `theorem-map.json`: all 29 numbered entries mapped to the eight maintained claim groups, source sections, and printed/PDF pages.
- `SOURCE_PROVENANCE.json`: source archive, source-document hashes, and the precise verification boundary.
- `source_snapshot/`: the exact 15 source documents and evidence records used for transcription.
- `BUILD_AUDIT.json`: document checks and the two repaired typesetting failures.
- `evidence/quick_run/`: the fresh source quick-run record from this documentation session. Absolute paths in that record are historical execution provenance.
- `build.py`: standard-library helper for three-pass LaTeX compilation.

## Build

A conventional TeX Live installation with pdfLaTeX and the packages named at the top of `theorems.tex` is required. Run:

```sh
python build.py
```

The PDF and compilation logs are written under `build/`. This source uses no external images or bibliography database and performs no network downloads. No font files are distributed.

## Proof status and scope

The document covers the eight maintained circuit-obstructions claim groups and supporting arguments. They are written, self-reviewed proofs with exact finite evidence, not Lean-verified declarations. The broader Komorebi Lean theorem atlas was not assembled here. Numbered entries are not a count of new discoveries.

The repository's source integrity and quick suite were rerun successfully. Full scientific and historical results are quoted from the pinned source evidence and were not rerun for the document edition. No source-release tag, remote repository, permissions, or licensing was changed. The source release's rights notice is retained.

## Corrected document-build failures

The first build stopped because `amsthm` and `newtxmath` were loaded in the wrong order, causing an `openbox` macro conflict. The next build exposed a custom `Top` macro name collision. Package ordering and operator names were corrected. The final build has resolved references and no overfull boxes; the rendered pages were inspected. Neither failure was a mathematical assertion failure.
