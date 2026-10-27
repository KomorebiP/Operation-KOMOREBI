# RRCT v0.42 Compact Evidence Policy

The active continuation package is decision-complete rather than raw-data complete.

It retains:

- runtime and model source
- exact intervention configuration
- source-summary artifacts and an independently stored compact SHA-256 manifest
- causal contrast receipts
- aggregate results
- tests
- protocol, interpretation boundary, and unresolved gaps

It omits historical sealed-row streams because the present adjudication can be recomputed from compact summary artifacts. Original rows remain relevant as cold archival evidence for byte-level independent audit, rare-event investigation, or reinterpretation of fields not retained in the summaries.

A future compact package must preserve enough information to determine why a conclusion was reached and whether a successor result genuinely supersedes it. A prose conclusion without configurations, source hashes, condition-level outcomes, and failed controls is not sufficient.

The v0.42 adjudicator requires an exact manifest match. It rejects a summary whose bytes changed after manifest creation, as well as missing or unexpected condition files. The manifest is a post-hoc packaging-integrity control, not a prospective scientific preregistration.
