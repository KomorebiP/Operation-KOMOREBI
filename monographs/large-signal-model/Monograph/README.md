# Large Signal Model publication source

The formal companion completes reviewed Lean mappings for all 87 numbered
proposition cores. Its accepted evidence contains 254 proof modules, 4,454 named
declarations and 2,887 named theorems. The exact theorem assumptions and source
correspondence are recorded in the sibling `Lean/COVERAGE.json`. Explanatory
prose and additional unnumbered claims retain their separate scope.

The complete 174-page layout is preserved in `source/Original_Monograph.pdf`.
The original publication's full XeLaTeX authoring files were unavailable. This
package retains that layout, the corrected editable mathematical body, its
scientific figures, fonts, glossary, references and reproducible update script.
It does not claim to reconstruct the missing XeLaTeX sources.

`build_monograph.py` applies explicit reviewed text and formal-status patches.
`source/FOUNDATIONS.md` is the corrected editable body, derived from the retained
`source/Original_Foundations.md`. The two figure files referenced directly by the
body are in `assets/figures`; every publication figure remains in the layout
input. The builder preserves the mathematical text and figures and refreshes the
single generated formal-count prefix. It refuses to overwrite later body edits.

`source/FORMAL_STATUS.json` supplies the publication's current coverage,
inventory, execution summary and compact grouped formal guide. The accepted
Lean receipt is `../Lean/verification/current/report.json`. Its 697 accepted
stages comprise 694 Lean stages and three Python checks. The permitted logical
axioms are `propext`, `Classical.choice` and `Quot.sound`.

Publication build and visual acceptance are separate records in
`review/CURRENT_ACCEPTANCE.json`. The current 174-page PDF passed its rebuild,
content and changed-page visual checks. Previous publication metadata is retained under
`review/predecessor_review_v018` with its original provenance.

Rebuild with Python 3 and the pinned PyMuPDF dependency. The required P052 fonts
and their upstream license are bundled in `assets/fonts`:

```bash
python3 -m pip install -r requirements-rebuild.txt
python3 build_monograph.py
```

The build fails if a required passage is missing, replacement text does not
fit, the page count changes, bookmarks move, or an untouched page changes in
text or pixels. It records those checks in `build/MONOGRAPH_VALIDATION.json`.
