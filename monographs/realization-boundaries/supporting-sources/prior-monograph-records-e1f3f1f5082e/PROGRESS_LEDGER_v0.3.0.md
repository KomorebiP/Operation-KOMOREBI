# Realization Boundaries — technical continuity ledger

Package checkpoint: 0.3.0, the first integrated monograph handoff. This version label belongs to the technical record and is not printed in the reading edition.

## Completed

- Integrated both source notes into a 64-page monograph with 12 chapters, three appendices, glossary, references, and eight vector figures.
- Expanded the ordinary proof development to include pure-preimage classification, all diagonal homomorphisms, endomorphism and automorphism formulas, root-fiber counting, and the faithful-versus-full distinction for completion.
- Preserved marked/unmarked, syntactic/effective, and finite-observation/source-realization boundaries.
- Replayed 114,738 inherited exact finite assertions and added 53,284 supplemental assertions. All passed, including seven negative controls.
- Executed the printed Chapter 11 example from the package root.
- Produced a theorem-to-source inventory, reference data, build script, environment report, input hashes, page geometry checks, and a selected-page preview.
- Rendered and visually reviewed the PDF. Corrected the transient figure-parser and TeX-package failures described in the review record.

## Evidence status

Ordinary written proofs: supplied throughout.
Exact finite arithmetic: executed and passing.
PDF build and layout: executed and reviewed.
Lean formalization: not performed.
External peer review: not performed.
Historical priority for the combined family: not established.

## Unresolved obligations for stronger certification

A future Lean development must construct the direct sum and product, prove unique divisibility of P/D, and establish the section-to-ambient equivalence before importing any classification claim. The effective theorem needs separate computability semantics, including the nonuniform constants in an unmarked copy. Literature comparison for rank-one mixed abelian groups remains distinct from proof correctness.

## Exact restart point

Use the reading edition and `verification/theorem_inventory.csv` as the statement contract. Appendix B gives the ordered formalization interfaces. Start with the ambient layer (Theorems 2.1 through 2.6 and Theorem 4.2), not by postulating the rational quotient or the common-completion theorem. The current code base is in `src/`; no prior archive needs to be unpacked for normal reproduction.
