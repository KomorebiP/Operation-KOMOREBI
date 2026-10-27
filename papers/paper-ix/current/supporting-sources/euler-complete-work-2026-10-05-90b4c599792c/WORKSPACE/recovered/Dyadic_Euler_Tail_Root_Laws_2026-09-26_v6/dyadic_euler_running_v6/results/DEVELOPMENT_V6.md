# Development and failure record — v6

The seven retained bounded scientific runs all completed with exit status zero. No assertion failure or timeout occurred in these runs. Their individual manifests and scientific results are authoritative for the executed scopes.

The original v5 release matched all 124 ledger entries. The v4 mathematical foundation and v5 distribution/resultant checks were then rerun freshly. Historical v5 timeout attempts remain in the preserved notes and are not converted into passes.

## Figure export failure

The first user-visible Matplotlib export failed with `PermissionError` when writing `figures/08_multiplier_classes_v6.png`. The extracted figure directory was owned by the container process and was not group-writable. Its group write permission was corrected. The complete plotting cell was rerun, and both PNG/PDF figure pairs were produced successfully. No outputs from the failed attempt were assumed valid. The scientific result JSON files and their input/output hashes were unaffected.

## Document revisions

The first successful PDF build was rendered and reviewed. The standalone appendix contents page was expanded to include subsection navigation. A short parameter table and the paired discriminant comparison were kept together. The classical source list was moved to a separate final page to avoid an orphaned citation continuation. Final PDFs were rebuilt and rendered. No overfull boxes, missing glyph warnings, out-of-page text spans, or empty text pages were detected.

No font files are included. No Lean run or historical-priority search was performed.

## Packaging validation selection error

A final packaging preflight used the glob `MANIFEST_*V6.json`. This also selected `MANIFEST_VALIDATION_V6.json`, which is a summary of validation results, not an execution manifest. The manifest validator correctly rejected that summary for lacking the execution schema, and the packaging attempt stopped before creating the release archive. The selector was corrected to the seven explicitly named execution records. All seven execution manifests then passed; the release ledger and ZIP member hashes were checked separately. This was a packaging-file selection error, not a scientific assertion failure or a damaged execution record.
