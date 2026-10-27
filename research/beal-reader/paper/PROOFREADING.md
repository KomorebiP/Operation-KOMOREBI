# Conservative proofreading of the Beal reader

Mode: final self-review of the newly authored paper sources.
Scope: main.tex and chapters/00_reading.tex through chapters/24_sources.tex,
with the prepared shared preamble read for local conventions.

## Routine checks

The full new manuscript was reread for definitions, display integration,
cross-references, English agreement, consistent local field and coefficient-field
roles, notation, quantified domains, and claim status. The paper has 107 explicit
labels, no duplicate labels, no missing ordinary references, and no missing
citation keys. The embedded bibliography contains the authenticated keys supplied
by the literature reviewer.

No prose semicolon remains. The two semicolon characters in the source belong
to TeX math spacing commands. No replacement character, abstract, visible TODO,
or unresolved figure placeholder appears. The five figure paths resolve to the
exact generated shared figures. Header, author and date conventions are those
of the prepared series preamble.

## Mathematical-token changes

No mathematical-token correction was made during the final conservative
proofreading pass. Earlier substantive authoring and audit refinements are listed
in AUTHORING_NOTES.md. They were made as explicit mathematical edits with proof
review, rather than silently classified as copyediting.

## Validation

`python3 beal_set/build.py --only paper` completed and stabilized the references.
The clean 48-page build had no undefined reference/citation, overfull or underfull
box, missing glyph, or PDF-string warning. All reported fonts are embedded,
subsetted, and have Unicode mapping. The final evidence-only run-status update
is rebuilt with the same script before handoff.

The mathematics received a separate internal adversarial audit and its external
applications a separate primary-source check. Neither is represented as human
peer review. Final whole-page layout QA is tracked by the parent release report,
not claimed merely from this source pass.
