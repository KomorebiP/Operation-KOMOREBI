# Final evidence summary — Core 1.0.0

Author: Komorebi P. Date: 2026-09-12.

- 117 / 117 active modules freshly compiled after removal of their project caches.
- 86 inherited active source modules unchanged; pinned mathlib caches reused.
- 543 / 543 theorem/lemma declarations audited; 127 new declarations include 63
  benchmark statements and other support/concrete statements.
- Axiom lists contain only propext, Classical.choice and Quot.sound.
- No forbidden proof tokens in active source files.
- Two complete runCached executions and 21 static benchmark candidate certificates.
- 1,068 exact diagnostic assertions, nine expected producer rejections, and three
  intentionally invalid Lean controls all behaved as required.
- Four corrected current draft Lean failures, 11 inherited failures, zero incomplete
  source snapshots. Exact attempts are preserved in the audit directory.
- Final-source hashes, attempted sources, logs, compiled outputs and direct imported
  dependencies agree with successful post-clean-start receipts.
- Final computation manifest passed the official Mathbox validator.
- Accumulated successful final Lean process time: 558.439 seconds. This is a sum
  of process measurements, not a separately measured end-to-end wall-clock time.

Lean 4.34.0-rc2; mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06;
one thread per Lean process, warnings as errors. Full environment and individual
receipts are in FINAL_VERIFICATION_RECEIPT.json and AXIOM_AUDIT.json.
The review and rebuild were performed by the same assistant; no independent
external review or Windows execution is claimed.
