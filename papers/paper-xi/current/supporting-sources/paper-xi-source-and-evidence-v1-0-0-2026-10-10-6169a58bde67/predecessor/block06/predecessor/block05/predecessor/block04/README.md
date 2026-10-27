# Paper XI — Publication Block04 source checkpoint

Working continuation v0.4.0, 10 October2026. This is **not** the final coordinated Paper XI release and **not** a closure of Conjecture66.

Start with `publication/pdfs/Paper_XI_Conjecture66_Progress_v0.4.0.pdf` (77pages). The new independently editable PartIII is `publication/pdfs/Paper_XI_Conjecture66_Block04_v0.4.0.pdf` (23pages). Read `BLOCK04_REVIEW.md`, the versioned `PROGRESS_LEDGER.md`/JSON and `CONTINUE_HERE.md` for scope and restart instructions.

The new source develops conductor normalization, rank-nine candidate filters, rank-eight profile/capacity separation, the classical source-defined candidate, fixed finite extensions and quadratic markings, and two explicit conditional finite correction procedures. Ordinary proofs, inherited arithmetic arguments, finite tests and historical formal evidence are kept separate.

## Reproduce the finite checks

Requires Python3.10 or later. These tests use the standard library only.

```
python tools/verify_package.py
python tools/replay_block04.py --output ../block04_replay
```

The runner checks23 new methods,15 inherited B03 methods and12 inherited B01 methods. Keep output outside the checkpoint root because strict integrity checks reject additional files. The seven other historical B03 arithmetic program executions are preserved but not part of this runner.

## Rebuild the new PDF and cumulative reader

Requires XeLaTeX with the packages used in the source and the fonts referenced by `komorebi-publication.sty`. The inherited style currently uses Linux font paths for the URW Base35 family and an installed DejaVu Sans Mono. No standalone font files are distributed. Configure installed font paths when building on another operating system. The delivered PDFs do not require any fonts to be installed separately.

The PDF assembly/review tools require PyMuPDF and Pillow, listed in `requirements-publication.txt`.

```
python tools/build_block04.py --output ../block04_build
python tools/assemble_reader.py --continuation ../block04_build/Paper_XI_Conjecture66_Block04.pdf --output ../block04_assembly
```

The preserved33-page B02 PDF is not rebuilt from missing source. All52 PartI/II pages are retained by the assembler, with named-link resolution. Text/render reproducibility passed; strict PDF byte identity did not.

## Contents and evidence

`predecessor/block03/` is the complete compact Block03 checkpoint, including the original baseline readers and its own ledger. `sources/inherited/` contains the selected constructor/marking records and the next reading queue. `evidence/block04/` records source hashes, exact primary-source locators, ordinary proof boundaries and restart targets. `verification/block04/` contains successful finite receipts, PDF build and assembly checks, reproducibility results and review records.

The compact checkpoint does not contain every historical dependency. The separately delivered complete recovered-source working ZIP includes the full hash-verified Block01 scientific baseline. The complete editable Block02 archive remains unrecovered in both packages.

The latest ledger snapshots are under `ledger_snapshots/`. Preserve stable task IDs and append rather than overwrite history in the next block.
