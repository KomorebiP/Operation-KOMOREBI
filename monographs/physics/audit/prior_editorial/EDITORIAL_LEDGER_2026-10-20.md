# Editorial completion and document checks

## Reading edition

The book has 558 pages, compared with 622 in the source compilation. It contains eight mathematical
and physical-model treatments, five visual atlases, five formalization/verification companions,
a new verification synthesis, and the retained computational appendices. The obsolete collection-planning
guide is replaced by current front matter and the evidence synthesis. All seven physics themes remain.

The sources were edited and recompiled. This is not a cover placed over the earlier PDFs.
The reading copy removes edition stamps, progress-block labels, future-edition promises, and repeated
local tables of contents. Introductions and transitions establish a continuous route through the subjects.
A source concordance preserves 151 implementation notes moved out of the mathematical narrative.

The Dirac operator treatment now points to the following generator proof rather than presenting
that identification as still mathematically absent. The formalization companion identifies the
remaining compiler work separately. The evidence diagram is updated accordingly.

The fiber-production energy obstruction also controls the opening and interpretation of the cosmology
account. A prescribed distribution is not described as a demonstrated microscopic production prediction.
Genuine hypotheses, negative results, and verification deficiencies remain in the book.

## Executed document checks

- All eighteen LaTeX components built successfully. Final logs have no undefined references,
  missing-glyph warnings, or overfull boxes.
- The assembled book has 575 bookmarks, 21 linked contents entries, 260 restored source-internal
  links, and 40 retained external links. The destination scan finds no invalid internal targets.
- Every final page was rendered with PDFium. Openings, transitions, the revised evidence figure,
  representative proofs, tables, and technical pages received additional visual review.
  This is not a claim that every equation has received an independent mathematical review.
- The text/bounds scan finds no empty pages or text extending outside page bounds.
- The reading-part scan finds no matching project-version labels, numbered development blocks,
  “this edition”, “next phase”, “restart point”, or handoff language.
  Mathematical uses of “version” and ordinary bibliographic identifiers are not prohibited words.
- In the compared source files, all 107 explicit LaTeX proof environments are byte-identical in
  their ordered bodies. This text invariant does not cover manually marked proofs and is not
  a proof of mathematical correctness. Full editorial changes are retained separately.

## Repaired execution issues

The initial PDF link-transfer routine handled explicit page destinations but omitted named destinations.
It was repaired to use the resolved source pages of named links. The final assembly restores all 260
source-internal links and records no unresolved source link.

A contact-sheet helper initially searched for `.jpg` files, while the renderer produced `.jpeg` files.
The file matching and numeric page ordering were corrected. A separate long rendering command exceeded
the tool window without producing its output folder. The complete final PDF was subsequently rendered
successfully, and selected pages were rendered separately at higher resolution.

An earlier generator layout produced an overfull text line. The source layout was adjusted and rebuilt.
No overfull warning remains in the final component logs.

## Not performed by this pass

No Lean compiler run, new mathematical theorem, complete numerical reproduction, empirical calibration,
or exhaustive independent proof/literature audit is claimed. Recorded formal passes remain records of
their original runs. The generator draft remains uncompiled. Physical-model limitations are preserved.

## Restart point

Use this reading PDF and its `source/` tree for future publication edits, not the obsolete collected PDF.
Keep changes to theorem status separate from editorial changes. For formal continuation, use the retained
exact Lean archive and the uncompiled generator draft, restore the pinned runtime, and issue actual build
and axiom-audit evidence before changing a formal-certification label.

Internal editorial record: reading consolidation after the analytic generator manuscript.
