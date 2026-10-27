# Paper XII external-source copy policy

Final-release decision recorded 2026-10-06.

The final release preserves `EXTERNAL_INPUT_AUDIT.md`, `SOURCE_MANIFEST.json`, `SEARCH_SCOPE.json`, `HASH_VERIFICATION.json` and this policy. These records supply the bounded review verdicts, acquisition locators, source versions, exact result/page/tag locators, audit-time extraction status and SHA-256 hashes.

Newly downloaded third-party PDFs, official-source HTML and extracted text under `acquired/` remain scratch research copies. They are omitted from the final release. Paths recorded for those copies identify where the auditor checked them during the work session; they are not packaged-file references or promises of continuing local availability. Their presence during the audit is distinct from their inclusion in the release.

The hash-verification record confirms the 22 checked scratch PDF/text/HTML copies matched their manifest hashes when verification ran. A recipient may reacquire a source using its official publisher, arXiv, author-hosted or stable-tag locator and compare the resulting bytes with the recorded hash. A changed unversioned webpage or compiled chapter can produce different bytes; that is a different source revision requiring a fresh comparison, not evidence that the earlier check was silently refreshed.

No `.research-cache` database was successfully ingested: the helper refused its write because the scratch workspace has no Git repository through which ignore coverage could be verified. The included provenance records do not claim otherwise. No third-party source contents are redistributed through these records.

This packaging decision changes source-copy availability only. It does not broaden the literature audit, close unread source proofs, validate an unspecified arithmetic application or alter any manuscript, bibliography or reference-list file.
