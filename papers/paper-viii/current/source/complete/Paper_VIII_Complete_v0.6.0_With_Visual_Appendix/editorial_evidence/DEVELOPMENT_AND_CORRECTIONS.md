# Editorial development and corrections

This record concerns the visual-appendix addition, not the historical mathematical development.

## Source selection

Two different sixth-block releases had the same nominal version. The selected handoff is the 392-declaration, 40-module release with 56/56 finite items, not the 341-declaration branch with a remaining conditional recompression item. Its source snapshot and eight-page supplement are preserved. The separately exposed numerical companion is an exact extraction of the original package already contained in the selected handoff.

## Corrected during this addition

- An early generator contained a Python string-escape warning. The strings were made explicit before the successful warning-as-error generator run.
- The first TeX build failed because intended multiline TikZ labels contained single TeX control prefixes such as `\first`. Those labels now use proper line breaks.
- The initial object table started in the preceding text paragraph, producing an overfull line. The table was placed in its own paragraph.
- A later build exposed missing `cost` and `err` mathematical macros. Both are now explicitly defined.
- Render inspection found that complex matrix entries outgrew square grid cells. The drawing helper now supports separate cell width, and the affected Fourier/Kronecker cells were widened.
- The precision table displays only weights zero through eight, although all 27 choices and budgets through twelve are checked. Its text/index now states the displayed range.
- Wording for the first option on the second edge was clarified. The diagonal kernel-witness explanation now explicitly retains `0 <= k < d`.

All failures preceded the accepted build. The first two failed TeX logs are retained separately. No failed command is counted as an accepted check.

## Preserved original TeX warnings

The original 45-page manuscript rebuilt successfully and matched all saved pages in text and 72-dpi rendered appearance. Its own TeX source retains seven underfull-box warnings and a `cmtiup` package-name warning. The new appendix has none of the checked overflow/underfull/unresolved-reference warnings. The original source was not edited to remove its historical warnings.

The recovered original package already documents a broken `bibtex` launcher in the build environment. The working `bibtex.original` executable was used. The new wrapper uses that executable when available and otherwise uses `bibtex`.

## What was not run

No Lean compiler or fresh GPU benchmark was invoked. Replayed verifier tests are Python software tests. The separate numerical recompression mirror is NumPy code using numerical rank and declared tolerances, not extracted Lean. Replotting the 22 original figures uses saved benchmark rows, not new timing measurements.
