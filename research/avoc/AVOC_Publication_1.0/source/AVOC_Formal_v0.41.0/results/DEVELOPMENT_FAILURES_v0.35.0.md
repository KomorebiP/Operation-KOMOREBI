# AVOC v0.35.0 — development failures and repairs

The following failures occurred and were not counted as successful evidence while unresolved.

1. **Missing inherited object files.**  The first new-module check ran before the pinned local
   dependency graph had been rebuilt.  The inherited graph was compiled in resumable bounded
   slices, and the new module was checked only after its imports existed.
2. **Concrete-example reduction failures.**  Initial `norm_num` attempts did not unfold the
   inherited selected affine implementation through proof-carrying records.  The proofs were
   rewritten to use the existing exact execution-cost theorems and explicit arithmetic goals.
3. **Codec namespace error.**  The first warm-plan builder referred to `reuseCharge` through
   the wrong namespace.  It was corrected to the checked search-guard namespace and rebuilt.
4. **Rational wire mismatch.**  Early example files encoded probabilities as strings, while
   the inherited parser requires exact `[numerator,denominator]` arrays.  The examples were
   corrected; the malformed forms remain rejected.
5. **Audit output path error.**  The first v0.35 axiom-audit invocation still directed its log
   to the historical v0.34 directory.  That run was not used.  The path was corrected and the
   complete 1,860-declaration audit was rerun successfully in v0.35.
6. **Host execution limits.**  The clean build and first negative-test batch exceeded the
   outer command limit.  The same dependency graph resumed from current records; unfinished
   targets and negative files were rerun in bounded groups.  No timeout was counted as a pass.

No proof placeholder, custom axiom, or unresolved new theorem remains in the delivered source.
