# Release audit

## Build

- PDF pages: 60
- Vector figures: 26
- PNG figures: 26
- Internal algebraic or high-precision checks: 51 of 51 passed
- Independent pytest tests: 13 of 13 passed
- PDF preflight warnings: 0
- LaTeX overfull boxes: 0
- LaTeX underfull boxes: 0
- Undefined references: 0
- Embedded author metadata: Komorebi P.

## Layout

The manuscript was rendered page by page at 180 DPI. The complete contact sheet and representative full-resolution pages were inspected. Chapter and part headings flow with the surrounding argument. Figures are kept with their captions and enough nearby text to avoid isolated title or figure pages.

## Claim control

The release distinguishes new constructions, proved identities, classical inputs, finite computations, open special-function questions, and major-conjecture interfaces. It does not claim a proof of RH or blanket historical novelty for every specialization.

## Reproduction

The clean build command is:

```powershell
python build_all.py
```
