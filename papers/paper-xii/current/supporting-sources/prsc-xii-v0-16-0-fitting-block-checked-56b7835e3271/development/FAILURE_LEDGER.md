# Development failures and their resolution

- Initial determinant proofs encountered elaboration/coercion and typeclass
  errors. They were corrected; failed compiler logs and source hashes are retained.
- The block stabilization proof initially mixed DecidableEq instances for matrix
  identities. Entrywise equality resolved this, without an additional axiom.
- Coordinate transport in tensor base change required explicit linear-map
  coercions and finite-sum multiplication identities. Corrected sources compile.
- One combined container invocation timed out during a sequence of rebuilds.
  It did not provide a completed compiler record for the interrupted invocation.
  The cause was not isolated. No compiler success is inferred from it. The
  affected module was rerun and the final clean verifier uses one Lean thread
  and explicit per-process timeouts with process-group cleanup.
- The early development runner did not copy each failed source revision. Its
  failed-run logs contain source hashes, not a complete version-control history.
  Final source bytes and every final successful run are independently retained.
- The one-by-one boundary example exposed Matrix type-alias transparency issues
  in tactics. Using Matrix.of and explicit determinant goals repaired the proof.
- The first residue-field proof attempted a dependent rewrite of the prime
  ideal, invalidating its attached primality instance. A separate kernel/map
  equivalence avoided that invalid rewrite; no mathematical hypothesis changed.
- A missing predecessor object-path import was an environment setup failure.
  The exact three predecessor source modules were copied unchanged and rebuilt.
- Probes intentionally tested unavailable API names. These are development
  lookup failures, not failed mathematical statements; probes are outside lean/.

The deliberately false theorem, a placeholder proof, and an incorrect zero-module
normalization are negative controls. Their rejection is required, not repaired.

- A final import reduction removed the broad Mathlib.Tactic import. The first reduced
  attempt exposed a previously implicit dependency on Ideal.BigOperators. That
  dependency is now explicitly imported. The final reduced-import source closure
  passed the clean replay; no theorem statement or mathematical proof was weakened.
