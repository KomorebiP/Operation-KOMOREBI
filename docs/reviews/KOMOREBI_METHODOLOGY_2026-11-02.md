# Komorebi Methodology: proofreading and HTML reading edition

Reviewed 2 November 2026 from collection revision
`75caee1d5ebc01d64b439101d94cd5d1c1fc3bb0`.

[Read the complete essay online](https://KomorebiP.github.io/Operation-KOMOREBI/read/komorebi-methodology/index.html).

## Proofreading

The review covered the full preface, all nine numbered essay chapters, the closing
reflection, source and verification notes, nine bibliography entries, three figure
captions, and local notation and cross-references. The sources are
`Komorebi_Methodology.tex`, `essay.tex`, and `sources.tex` in
`monographs/komorebi-methodology/`.

- Routine edits: none. No objective spelling, grammar, punctuation, or LaTeX error
  requiring a correction was identified in this pass.
- Mathematical-token changes: none.
- Unresolved proofreading issues: none identified within that scope.
- The manuscript, original diagrams, PDF, delivery manifest, and historical audit
  files are unchanged. This pass did not audit the mathematical proofs, verify
  external citations, execute Lean, or repeat the historical PDF layout review.

The existing source package already records its written review and 28-page PDF
review. Those are inherited records, not new review claims from this conversion.

## Reading conversion

The edition contains 12 source-derived text pages plus references and contents.
The authored order is preface, nine chapters, closing reflection, then source and
verification notes. The print cover and automatically generated printed contents
are represented by the HTML title and chapter index.

The conversion preserves all 164 mathematical expressions in order, three global
equation numbers, unnumbered subsection headings, nine bibliography entries, and
three figure captions. The browser diagrams are byte-identical copies of the PNGs
already supplied with the source package, with receipts binding each to its
original PDF and PNG. The published source downloads retain their exact bytes.

Print-only wrappers are translated into the existing reader panels and headings.
The superscript source citations become numbered bibliography links. Source-line
anchors, previous/next links, chapter filtering, text settings, saved passages,
comparison links, search entries, and the work overview use the shared reader.

`tools/methodology_sections.json` records exact source digests and contiguous
ranges. Changed sources stop the build pending a reviewed selection. The source
package's byte-preservation Git attribute prevents Windows newline conversion
from invalidating its existing delivery manifest.

## Validation

- `python -B -m unittest discover -s tools -p 'test_methodology_reading.py' -v`:
  all three checks passed, including the normal published-equation checker,
  equation and figure numbers, citation and passage targets, source drift
  rejection, heading structure, and original image identities.
- Shared navigation, reader display, and usability checks: 26 tests passed.
- `python -B verify_manifest.py`: all 54 payload files matched the delivered
  manifest (55 package files including the manifest).
- In an isolated copy, `exact_checks.py`: 40/40 groups passed, 665 finite cases;
  `integrity_checks.py`: 17/17 controls passed. The retained package and its
  historical receipts were not overwritten. Finite cases do not establish the
  unbounded arguments.
- Browser inspection confirmed chapter navigation, rendered equations, equation
  labels, the memory derivation, and the chapter contents panel. Browser checks
  inspect presentation, not mathematical correctness.

The website workflow includes the new source-preservation tests and runs its
complete site and link checks before publication.
