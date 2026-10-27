# Release assembly scripts

These are the exact one-time scripts used to assemble the 18 October 2026 Paper XI release. Their absolute paths describe the original execution workspace; they are retained as provenance. The final guide and release-document scripts require the accepted compiler, axiom and source-review records before emitting success statements. The source bridge binds the working, portable and delivered formal sources. The visual binding script combines completed direct reviews with separately checked pixel invariants.

For a new portable reader build, use `tools/build_readers.py`. For archive and extracted-tree verification, use `tools/verify_release.py`. For formal replay, use the documented commands in `formalization/README.md`. Failed historical attempts remain under `verification/lean/` with their original outcomes.
