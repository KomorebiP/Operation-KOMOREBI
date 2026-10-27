# Development and execution failures — v0.5

These are distinct from successful proof checks and intentional rejection controls.

1. The session initially had no Lean binary on PATH. The five saved runtime ZIP
   chunks were restored. An attempted interactive streaming exec was unsupported
   and did not create its script. A subsequent Python XZ/tar restore timed out
   partway through; no complete-restore claim is made for that attempt.
2. Native tar/XZ extraction restored the required compiler and source/cache files.
   The first extraction filter omitted the separate `.ir.sig` files. The first
   dependency compilation failed with `missing data file for module Aesop.Script.Util`.
   A supplementary extraction of IR signature and interface files repaired the
   environment. Compiler hash, version, pinned Mathlib metadata, and selected
   upstream source hashes matched the retained predecessor records.
3. The first CertifiedOracle draft had two unused simp arguments. Strict warnings-
   as-errors checking rejected it. The redundant arguments were removed; no theorem
   assumption was weakened.
4. The first batched-data exporter removed the last theorem's proof expression
   along with its closing namespace. The generated batch failed parsing. The slice
   was corrected to stop at the actual `end` line, all data were regenerated, and
   every accepted batch compiled.
5. One grouped DEVELOPMENT build was interrupted while proceeding to CheckedBatch08.
   Earlier completed module logs were retained; the interrupted module was compiled
   again to completion. The later acceptance audit started with a new empty build.
6. Several enclosing calls interrupted groups in the final cold audit after already
   completed tasks had been durably recorded. No omitted or partial task is counted
   as passed. Source/input/build/log hashes were checked before resuming, and each
   remaining control was run in a separate synchronous call. All 47 planned tasks
   ultimately completed. The final PASS record was created only by the finisher.

The formal false, placeholder, false-membership, zero-separator, incomplete-queue
and wrong-fallback controls are intentional rejections. The twelve malformed Python
trace controls and the cap refusal are also expected outcomes, not successful
mathematical discoveries. Their rejection does not prove arbitrary external input
parsers free of bugs.

Raw incremental module records are in `v05_evidence/dev*.json` and matching logs.
The final accepted cold audit, with all commands and completed exit statuses, is in
`results_v05/LEAN_AUDIT.json`. Historical v0.4 failures and receipts remain preserved
inside the unchanged parent ZIP.
