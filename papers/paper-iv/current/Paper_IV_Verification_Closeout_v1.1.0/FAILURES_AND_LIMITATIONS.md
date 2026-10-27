# Failures, repairs and limitations

## Executed failures and successful replacement checks

**Stale distribution manifest.** The recovered top-level verifier returned failure
because 73 excluded font files were still named by its 908-row manifest. Every
surviving file matched. The recovered 836-file tree is retained unchanged. A new
root manifest inventories the actual derivative release. No font file was restored.
See `verification/baseline_authentication/` and `verification/BASELINE_PRESERVATION.json`.

**Ineffective warning flag.** An isolated placeholder was accepted under the
inherited `-E warning` flag with exit code 0. The same source was rejected under
`-DwarningAsError=true` with exit code 1. The corrected policy is used by every
production compilation and current compiler control. The isolated bad theorem is
not part of the production import closure. See `verification/warning_policy/`.

**Initial test-fixture race.** The first new verifier suite passed 37 of 38 tests.
The descendant-cleanup test expired before observing startup, so it did not prove
that a descendant was launched. A child-readiness handshake now separates bounded
startup and execution windows. The final 42-test suite passes. The old script,
failed JSON and full trace remain in `verification/failed_attempts/verifier_tests_A/`.

**Incorrect historical availability report.** The earlier runner hardcodes that
SymPy and mpmath are unavailable, despite their being installed. The new finite
runner detects actual versions, executes the underlying unchanged suites, and
writes separate results. The old reporter is retained as a historical artifact,
not the active entrypoint.

## Retrieval and scope limitations

The exact older, unsaved fixture-control API failure was not recovered. The new
source gate uses the recovered typed interface directly. It registers the loaded
module correctly before execution and tests `MapRow`, `RegisterRecord`, and
`LeanTarget` mutations. It does not claim that an unavailable script was replayed.

Network-based compiler provisioning was unavailable in this container. Recovery
of the archived five-part compact runtime enabled the successful exact-pin replay.
The runtime cache is not redistributed in this package. External object caches
were not rebuilt from source.

The October 16 standalone visual PDF is recovered, but not its exact updated
editable source. The unchanged October 8 editable baseline and the exact text
changes on the three affected pages are retained. The separate PDFs are not
claimed as byte-identical outputs of a fresh typesetting run here.

There was no new independent proof kernel, full new semantic reproof, external
peer review, native Windows test or licence selection. These limits do not change
the successful source replay of the stated 68-result contract.
