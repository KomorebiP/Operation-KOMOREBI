# Self-Improving Intelligence — A Visual Guide

**Komorebi P. · Operation Komorebi · Visual companion v1.0.0 · 8 October 2026**

A 36-page standalone companion to *Self-Improving Intelligence: Representation,
Discovery, and Recursive Revision*, first edition v1.0.0. The unchanged 60-page
manuscript is included under `references/`.

## Read

Open `Self_Improving_Intelligence_Visual_Guide_v1.0.0.pdf`. All 36 pages have
bookmarks. The final reading-route table links back to the corresponding guide
pages. Source footers use `[S]` for the included manuscript, with its **printed**
page numbers rather than the PDF viewer's page index.

| Guide pages | Subject |
|---|---|
| 3–12 | What changes, the eight-cell diagnosis, complete trees, model uncertainty, and transport |
| 13–21 | Checked compiler shortcuts, a learned pruning rule, and repair-relative scope |
| 22–28 | Learned equations, exact evidence preservation, dependency updates, and costs |
| 29–36 | Fresh evidence, recursive continuation, remaining supplied structure, and reference routes |

Each illustrated page pairs a mechanism with its interpretation and a boundary.
The guide distinguishes constructed or acquired artifacts from the grammar,
teacher, checker, models, and other structures supplied by the designer.

## What is in this package

- `code/build_guide.py`: editable Python/ReportLab drawing and text source.
- `code/check_guide.py`: focused exact examples, source-count transcription
  checks, PDF geometry, glyph, and navigation checks.
- `code/export_pages.py`: exports the vector plates and selected previews.
- `code/verify_release.py`: verifies this frozen snapshot before rebuilding.
- `vector_pages/`: 36 individual SVG plates. Text is outlined for portable
  appearance. Edit wording in the Python source, then regenerate.
- `previews/`: the cover, full-tree/path plate, and certificate-dependency plate.
- `data/`: page summaries and a source crosswalk in JSON/CSV.
- `references/`: the unchanged source manuscript, its statement/assumption
  indexes and resource ledger, and selected unchanged JSON evidence records.
- `validation/`: focused checks, source integrity, rendering, and rebuild records.
- `REVIEW_NOTES.md`: changes, actual failures and corrections, and review limits.

This is the **guide source package**, not a replacement for the original full
research source package. The original research programs and complete test suite
remain in that original release.

## Rebuild

Python 3.10 or newer is needed. Versions used here are pinned in `requirements.txt`.
Run from this directory:

```bash
python code/verify_release.py
python -m pip install -r requirements.txt
python code/build_guide.py
python code/check_guide.py
python code/export_pages.py
```

The verifier should run **before** commands that replace generated outputs or
execution receipts. Changed files will no longer match the frozen inventory.

The same Python commands can be used from PowerShell. Windows execution has not
been tested in this release.

## Host fonts

No standalone font files are included. The PDF embeds its used fonts; SVG plates
carry their glyph outlines. Regenerating the source uses host-installed fonts.
The script searches common Linux locations for Lato, Noto Serif, and DejaVu.
Alternatively, set `KOMOREBI_FONT_DIR` to a directory containing these six font
roles as `Body.ttf`, `Bold.ttf`, `Italic.ttf`, `Serif.ttf`, `SerifBold.ttf`, and
`Math.ttf`. Select legally available fonts with the necessary mathematical glyphs.

Substituting fonts can change line breaks. The builder deliberately rejects text
that exceeds its allocated space. Mathematical glyphs unsupported by the chosen
text face are rendered with the math face instead of silently disappearing.

## Evidence boundary

The guide restates the first-edition theory. It does not report a new learned
agent, a new compiler benchmark, or new general mathematical results. Larger
algorithmic counters are transcribed from the included original JSON receipts.
Local examples are checked independently in the guide script.

The original 336,867-assertion suite was **not rerun** for this companion. Its
frozen 325-file source snapshot passed its original integrity verifier. Neither
checksum equality nor guide checks establish independent peer review or a
proof-assistant certificate.
