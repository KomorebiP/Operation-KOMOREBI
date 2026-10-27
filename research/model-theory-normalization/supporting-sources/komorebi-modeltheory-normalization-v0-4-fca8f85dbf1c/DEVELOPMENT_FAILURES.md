# Development and execution failures — v0.4

Failures are preserved separately from accepted execution evidence.

1. The current environment initially had no Lean executable. Five saved archive
   chunks were materialized and their XZ tar payload restored. An interactive
   streaming exec request was unavailable. The first tar filter omitted `.ir`
   files, causing the concrete missing `Init/Prelude.ir` failure. A second extraction
   restored IR files. Pinned Lean and Mathlib checks then succeeded.
2. Draft proofs encountered API/elaboration issues, set-coercion rewrites,
   deprecated `if_pos`/`if_neg`, unused simp arguments, and module-level computation
   reduction. Concrete reference proofs use `decide +kernel`; `#eval` additionally
   needs the meta import. These were corrected, not counted as successful proofs.
3. An inherited MatrixImageBoundary development compilation was interrupted before
   a result. It is not required by the new dependency closure and is not claimed
   as replayed in the completed audit.
4. The initial monolithic cold audit was interrupted after 20 successful builds.
   It has no successful overall result. Its snapshots/logs remain in
   `new_evidence/interrupted_cold/`. A new empty-build audit was initialized with
   before-hashes and completed in bounded synchronous batches.
5. One enclosing invocation of that batched audit was interrupted after the axiom
   task completed. No child remained running. The persisted queue, accepted input
   hashes, completed build hashes and logs were checked before continuing individual
   controls. All 30 tasks subsequently completed. Per-task runtimes remain the
   accurate sum; a partially completed invocation is absent from the active-batch
   duration list.
6. Negative-control proof errors and corrupted-trace rejections are intentional
   test outcomes, not development failures. They are counted separately.

Recorded non-PASS development JSON attempts:

- `001_DiscoveryRank.json`: FAIL
- `002_DiscoveryRank.json`: FAIL
- `003_DiscoveryRank.json`: FAIL
- `005_DiscoveryWorklist.json`: FAIL
- `006_DiscoveryWorklist.json`: FAIL
- `007_DiscoveryWorklist.json`: FAIL
- `009_DiscoveryTermination.json`: FAIL
- `031_DiscoveryLogic.json`: FAIL
- `033_DiscoveryExamples.json`: FAIL
- `036_DiscoveryTrace.json`: FAIL

No missing compiler output is promoted to PASS. Earlier unsuccessful drafts are
not accepted library sources. The exact final library has no sorry/admit/new
axiom dependency, and all strict compilation and axiom controls completed.

## Packaging correction

The first packaging script used `Path.with_suffix` on a directory ending in
`v0.4`, which incorrectly named the archive `v0.zip`. The first extraction
attempt failed with FileNotFoundError for the intended `v0.4.zip`; it did not
perform a successful replay. Filename construction was corrected, the incorrect
newly produced archive was removed after verifying its hash, and the package
was rebuilt and subjected to the actual fresh replay. No predecessor ZIP was
modified by that error.
