# Contributing

Technical corrections, clearer explanations, reproducible counterexamples, and improvements to the arithmetic or verification tooling are welcome.

Start with the [building instructions](docs/BUILDING.md). State the exact theorem, definition, example, or documentation claim affected by a proposed change. Distinguish a mathematical correction from an implementation or presentation change.

For Lean changes, preserve the pinned dependencies unless an upgrade is the explicit purpose. Update relevant positive contracts and rejection controls. A rejection counts only when it fails for the intended reason. Run the full verifier into a new evidence directory and report the result. Never edit an accepted historical receipt to represent a new run.

The code must preserve the stated quantifiers and interfaces. A computability claim requires an actual native oracle or ordinary-computability proof. Finite experiments do not substitute for an infinite theorem. Keep marked and unmarked copies, source groups and completions, and raw codes and represented equality distinct.

For Python changes, run the three exact-arithmetic suites described in the publication README. For publication edits, rebuild the PDF and inspect the affected pages. Keep proof provenance, the statement registry, and progress records aligned with changes to mathematical scope.

Use the existing Komorebi P. attribution and MIT license. Do not add personal identities, an institutional affiliation, a DOI, or a repository URL that the project has not supplied.
