# Komorebi Physics: Continuum, Geometry and Refinement

The reading copy is `Komorebi_Physics_Collected_Monograph.pdf`.
It is a 558-page collected mathematical monograph with a common physics palette,
continuous folios, a linked contents, and nested PDF bookmarks.

## Contents of this package

`source/` contains the edited LaTeX texts, styles, frozen figure assets, and retained data.
`compiled/` contains the eighteen source-built component PDFs and their final TeX logs.
`book/` contains the front matter, part leaves, verification synthesis, page map, and assembly checks.
`audit/` contains the editorial change records, source concordance, proof-environment comparison,
document checks, and progress record. These records intentionally retain development identifiers.
`formal/` preserves the inherited checked-source archive and the uncompiled generator draft.
`reference_record/` preserves selected earlier computation, provenance, and verification records.
Historical records are evidence of their stated runs, not fresh certification of this book.

The mathematical chapters are not a development log. Source versions and compiler pins are retained
where they identify reproducible formal evidence, in the technical part and the supporting records.
Equation, section, theorem, and figure numbering is local to each named treatment. Book pagination is global.

## Rebuild the reading volume

Use Python with the packages in `requirements.txt`, a TeX installation providing `xelatex` and
`pdflatex`, and the packages imported by the source preambles. Install the following font families
separately: P052, Nimbus Sans, Latin Modern Mono, Latin Modern Math, EB Garamond, and Lato.
Font files are not distributed in this package.

From this directory run:

```text
python build_documents.py
python assemble_reading_volume.py
```

The first command performs three passes for each source document and returns a failure status
when a component does not build. To build a subset, pass substrings of the document filenames,
for example `python build_documents.py Physics_Dirac_Monograph`.
The second command assembles the reading volume from the `compiled/` PDFs.

The outer-book typesetting script uses Linux font locations by default. For another installation,
set `KOMOREBI_BOOK_FONT_CONFIG` to a JSON file mapping `BookSerif`, `BookBold`, `BookItalic`,
`BookSans`, and `BookSansBold` to local installed font paths. No font download is performed by the scripts.
The build is layout-reproducible with the stated assets and dependencies, not promised byte-identical
across compiler or font installations. PDF creation metadata can also vary.

The book build reuses the supplied figures. It does not rerun all numerical experiments or Lean.
The historical atlas programs retain their original directory assumptions. Some legacy physical-model
programs require external inputs or a staged directory tree, as documented in the technical appendices.
The source-comparison audit additionally needs the predecessor source roots and is therefore retained
as `audit_with_original_sources.py`, not as part of the standard document-build command.

## Verification boundary

This is an editorial and document-build completion, not a new theorem-certification run.
The exact formal archive is inherited unchanged. The generator, centered-resolvent, and regularity-rate
arguments have written proofs but are not newly compiler-certified by this package. The Lean archive
alone does not include a complete pinned compiler and Mathlib runtime.

A changing sampled spatial lattice is not identified with the fixed infinite Fourier family.
The cosmological transport calculations retain the prescribed-distribution assumption and the recorded
production-energy obstruction. Interacting gauge/gravity constructions retain their explicit hypotheses.
A complete independent mathematical, empirical, or literature-priority audit has not been performed
by this editorial pass.

## Rights and source preservation

No source is relicensed by this collection. Existing notices are retained with the historical records.
The figures and source identifiers support traceability. The checksum manifest reports the exact bytes
in this package, not proof validity or empirical verification.
