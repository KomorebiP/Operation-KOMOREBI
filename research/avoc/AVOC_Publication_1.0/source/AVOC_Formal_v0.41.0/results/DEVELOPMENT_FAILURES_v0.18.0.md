# AVOC v0.18.0 — development failures and repairs

1. The runtime had to be reconstructed from the seven preserved offline parts.
   Part CRC/SHA and combined SHA checks passed. A host limit interrupted extraction;
   extraction resumed. A full tar comparison also timed out and is not counted as
   success. One tracked batteries documentation symlink was left as an empty file
   and restored exactly from the pinned git entry. Final tracked worktrees are clean.
2. A streaming execution attempt was unsupported by this container. No background
   session was available; subsequent work used bounded synchronous calls.
3. Several build batches reached the host execution limit. Unfinished targets
   were rerun. Final proof/audit records require normal completion and current
   hashes. The final 98-target tail was interrupted on PlannerMain; it was rerun.
4. Truncation and executable-adapter proofs initially encountered unused-instance
   warnings, a dependent induction hypothesis, deprecated simplifier names and
   an action-list length rewrite. Instances were scoped, hypotheses simplified,
   and exact arithmetic/equality arguments substituted. Current sources compile.
5. A runtime reward-bound proof unfolded the protocol before rewriting the exact
   receipt-consumption case. Separating simplification from the final definitional
   equality repaired it. No mathematical assumption was added.
6. The first trace wrapper used an eager default argument to `Option.getD`, which
   could recompute the initial recommendation even when a cached one existed.
   Source review caught the uncounted duplicate. An explicit match now reuses the
   root result and evaluates a new recommendation only when absent. This was fixed
   before the recorded independent regression and final CLI runs.
7. The first copied collector printed an inherited v0.16 baseline description even
   though it actually compared the v0.17 archive. The description was corrected and
   the collector rerun. The baseline hash and 87 source comparisons were correct.
8. One combined negative/demo invocation hit a host limit after the negative cases
   had returned. Missing or uncertain CLI records were rerun and final checks use
   the successful records only.

No successful count is inferred from an interruption, static scan or failure of a
malformed proof script. The final axiom audit checks all 953 declarations. New
negative tests reduce to false numeric or option equalities and their corresponding
positive/negative facts are established independently in the library.
