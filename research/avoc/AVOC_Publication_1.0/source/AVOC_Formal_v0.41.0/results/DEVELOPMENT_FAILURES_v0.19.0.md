# Development failures and repairs — v0.19.0

- A requested streaming container session was unavailable. No background/extraction success was claimed; extraction was rerun synchronously and completed after seven part CRC/SHA and combined SHA checks passed.
- Several outer execution calls ended before a build/test batch finished. The first unfinished targets/cases were rerun. Every final target/case must have its own current successful record; interrupted batches are not counted.
- In the first monitor proof, a case split had already reduced `halted=false` to `false=false`; supplying the old equality failed. Replacing that branch proof by reflexivity fixed it.
- A first archive-retention proof used `subst` on a ticket having multiple equalities; Lean selected a receipt-subject equality rather than the desired exact pending equality. The repaired proof rewrites with the explicitly named ticket equality.
- Initial monadic codec proof simplification did not unfold the required `Except` operations. The small decode/resume functions were rewritten with explicit matches, preserving their intended behavior and making each error/success branch directly checkable. Follow-on compiles against the unsuccessful dependency were not counted as successful checks. Final dependency-order rebuilds pass.
- A harmless but warning-as-error `unnecessarySimpa` complaint in the false-root obstruction proof was repaired with direct simplification of the contradictory hypothesis. No linter exemption or proof shortcut was added.
- Early live runs and tests preceded the final archive/codec proof extension. They are preliminary evidence only. Final regression requires current source hashes, and stale cases are rerun.

No new mathematical counterexample to an inherited theorem was found in this block. Operational timeouts, mutation and post-commit failures in the final regression are intentional test cases and must be reported as faults, not successful/negative evidence events.

## Final evidence collector field repair

The first final collector run raised `KeyError: identity` while inspecting the real Python store ticket. It had mistakenly used the pure-model nested identity shape instead of the executable store's retained `target_bytes` field. The collector was corrected to inspect the actual serialized schema, and all checks were rerun. No failed collector run was labeled PASS. The planner, monitor, and gate sources were unchanged.
