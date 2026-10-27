# Release procedure

1. Update the version in `pyproject.toml`, `CITATION.cff`,
   `src/komorebi_pr_lasm/__init__.py`, and
   `src/komorebi_arc3_offline/__init__.py`.
2. Update `CHANGELOG.md` and any changed claim boundaries.
3. Run the core test suite and both examples.
4. Run the controlled benchmark and compare its machine-readable output
   with the retained reference ledger.
5. Build and install the wheel into an isolated target.
6. Tag the reviewed commit as `vX.Y.Z` and push the tag.
7. Confirm that the tag-triggered `Release` workflow publishes the wheel, source distribution, checksums, and paper PDF.

Do not attach downloaded ARC environment source files to a public release
unless their distribution terms have been reviewed independently.
