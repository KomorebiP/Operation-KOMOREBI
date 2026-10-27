# Failure and correction log — v13

Five current-block completed draft Lean failures were corrected:

1. PacketSelectiveAlgebra: unused section instances and a local-energy abbreviation
   prevented rewriting the final sum. Removed unused instances and unfolded the
   abbreviation before applying complete energy accounting.
2. GreedyPacketSelection: the energy function did not elaborate from a placeholder
   in the maximum lemma. Supplied it explicitly; removed an unused instance.
3. GreedyPacketConvergence: an overbroad conversion/ring invocation reported no
   progress. Replaced it with an explicit two-step inequality calculation.
4. AdaptivePacketSolver: simplification left the universally true coverage guard.
   Rewrote using the explicit conjunction of proved guard hypotheses.
5. AdaptivePacketBoundary: checkSetup's namespace was not open. Added the correct
   inherited namespace; all boundary statements then compiled.

The packaged attempt snapshots and compiler logs retain the exact failed drafts.
There were no current compilation timeouts or incomplete source snapshots. Six
inherited v12 failures remain in the audit history; eleven total completed failures
must not be described as eleven current-block proof failures.

One shell write/run attempted a duplicated relative directory while already inside
that directory, so no diagnostic source was written. Reissued from the correct
working directory. The diagnostic draft and final provenance-recorded run passed.
This orchestration failure is not a failed mathematical test or Lean proof.

Three intentionally invalid Lean controls were rejected as expected. Eight invalid
producer/export requests were rejected as expected in the deterministic diagnostics.
These negative controls are successful checks, not unresolved failures.

The final seal passed: 90 active modules, 455 declarations, complete allowed-axiom
coverage, matching source/log/output/dependency hashes. New module count is 12;
78 inherited final-source receipts were reused and hash-validated from v12.

- PacketSelectiveAlgebra: audit/20260912T102903080544Z/PacketSelectiveAlgebra.json

- GreedyPacketSelection: audit/20260912T103131737284Z/GreedyPacketSelection.json

- GreedyPacketConvergence: audit/20260912T103219182426Z/GreedyPacketConvergence.json

- AdaptivePacketSolver: audit/20260912T103254717307Z/AdaptivePacketSolver.json

- AdaptivePacketBoundary: audit/20260912T103614910506Z/AdaptivePacketBoundary.json
