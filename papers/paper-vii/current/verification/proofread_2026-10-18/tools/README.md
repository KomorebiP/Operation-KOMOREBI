# Proofreading build and preflight procedures

These are the procedures used during the October 18 authoring run. The package-relative root replaces the scratch run path; the build commands and checks are unchanged.

- `rebuild_and_refresh.py` writes the three editable PDFs and logs, refreshes the traditional map and both guides, synchronizes the nine current PDF copies, and writes `../build/BUILD_RESULTS.json`.
- `pdf_preflight.py` checks every current PDF page, links, known invalid character mappings, text bounds and final typesetting diagnostics. It writes `../PDF_PREFLIGHT.json` and the font inventories under `../build/`. It is mechanical preflight; visual acceptance is recorded separately.

These **authoring commands change package files**. After an edit or rerun, renew current metadata, final visual review, packaged build replay, report/source pins and the integrity manifest before calling the result a new validated release. To verify the shipped release without changing it, use the root README's read-only commands instead.
