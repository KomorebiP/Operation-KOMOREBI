# AVOC v0.37.0 — development failures and repairs

1. **Missing prior source artifact.**  The retained v0.36 workspace contained only Markdown
   specification files.  The full v0.36 source ZIP claimed in the earlier response was absent.
   The new block was reconstructed from the frozen v0.35 source and the retained specification.

2. **Partially extracted Lean runtime.**  The first local compile failed because compiled
   mathlib objects were missing from an interrupted portable-runtime extraction.  The verified
   archive was re-extracted completely before any source failure was interpreted as a proof
   failure.

3. **Bounded build interruptions.**  Multiple inherited-build slices reached the host execution
   limit.  Each slice resumed from current successful outputs.  The final aggregate build
   returned `Build completed successfully (1965 jobs)`.

4. **Concrete evaluator reduction attempt.**  Direct kernel reduction/`decide` for the complete
   concrete Bellman recommendation was too expensive and an exploratory `#eval` timed out.
   The universal evaluator/Bellman correspondence remains kernel-checked.  Concrete choices
   were executed through the proved evaluator and independently asserted by the runtime tests.
   No `native_decide` axiom was introduced.

5. **First codec pass.**  It exposed ambiguous helper names, incorrect use of a derived setup
   theorem against an independently supplied quote, and an attempt to call a noncomputable
   confirmation specification from executable code.  The repair added exact fee checks and a
   finite `confirmExec`, then proved `confirmExec = confirm`.

6. **SQLite initialization bug.**  The first checkpoint insertion had one fewer SQL value than
   columns.  The schema insertion and row-count validation were corrected before final runs.

7. **Rejected-fallback test design.**  A first probability setting made direct cold generation
   preferable to trying warm first.  After correcting that modeling error, the all-in-one
   horizon-three test exceeded the host limit and left an unfinished intent.  It was excluded
   from successful evidence rather than reported as a pass.  Final evidence uses separate
   warm, cold, crash-recovery and boundary cases.

8. **Native executable attempt.**  Building a standalone Lean executable began compiling large
   C-object portions of cached dependencies and exceeded the execution window.  The unused
   executable target was removed.  Final tests use the checked Lean interpreter entrypoint.

9. **Unsplit negative suite.**  A first monolithic run exceeded the outer execution limit.
   It produced no completion claim.  The complete suite was rerun in bounded slices with one
   record per file; all 103 final records are substantive rejections.

10. **Source-scan false positive.**  The first scanner confused the inherited ordinary function
    `admit p ...` with the proof tactic.  The rule was narrowed to standalone tactic syntax,
    and the independent full axiom audit was retained.

None of these unresolved attempts is counted as positive verification evidence.
