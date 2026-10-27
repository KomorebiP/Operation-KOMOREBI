# AVOC v0.23.0 — development failures and repairs

1. The first multiline updated-record syntax was rejected by the pinned Lean parser.
   That caused cascading elaboration messages, including automatically inserted
   recovery placeholders in diagnostics. No invalid object was counted as evidence.
   Explicit record-field layout repaired the parser error.
2. A first proof used `Nat.cast_add`, which is not available from the deliberately
   small Std import. It was corrected to `Int.natCast_add`.
3. A split/simp_all proof for preserved initial identity made no progress in one
   branch. Explicit funded/eligible case splits replaced it.
4. The first induction proof of exact baseline visit count over-simplified the
   successor equality before supplying an incremented induction hypothesis. An
   explicit `change` to the successor arithmetic goal repaired it.
5. Reducing 24 rejected transitions by ordinary kernel `decide` exceeded the default
   recursion-depth limit. Only that concrete theorem gets a local maxRecDepth=10000;
   it then kernel-checks. No native evaluator or new axiom was substituted.
6. A runtime compilation attempted immediately after the failed specialization
   encountered its missing import. It was rerun after the dependency passed and
   was never counted as proof or negative-test evidence.
7. Build-tool source review found inherited cache reuse checked current source and
   output but did not require direct-import fingerprints. The new helper records
   before/after imported object hashes and the parallel driver invalidates stale
   dependents. Every final local target was rebuilt after that repair.
8. A combined final-build/audit/negative-test call hit the host execution limit while
   the negative suite was incomplete. No live Lean child remained on inspection.
   The seven completed negative records were retained; unfinished files were rerun
   in smaller slices. The collector requires all 55 substantive final rejections.
9. A test deliberately altered the new specialization source to confirm the wrapper
   detects protected-source drift. Exact bytes were restored in `finally`, checked,
   and the final tests and source-hash collector were rerun. This is an expected
   rejection scenario, not a failed mathematical claim.

No theorem is admitted or left as a placeholder. The whole source inventory and
axiom audit pass. Broader limitations are in PROOF_BOUNDARY.md rather than being
listed as implementation repairs. In particular, this is not arbitrary program
verification, a live self-modifying deployment service or autonomous RSI evidence.
