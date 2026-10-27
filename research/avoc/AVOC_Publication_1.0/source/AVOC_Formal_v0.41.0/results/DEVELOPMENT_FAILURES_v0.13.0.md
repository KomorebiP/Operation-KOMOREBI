# Development failures and corrections — v0.13.0

- Attempting to materialize the portable runtime returned existing-path warnings. Runtime inspection confirmed all seven part files were already present. They were assembled and their CRC/SHA checks passed; no duplicate download was counted as new evidence.
- Initial imports `Mathlib.Data.List.ToFinset` and `Mathlib.Order.Prod` did not exist at the pinned revision. Existing imported APIs sufficed, and finite enumeration required `Mathlib.Data.Fintype.Powerset`.
- Initial finite frontier/width definitions lacked explicit classical decidability. They were changed to noncomputable definitions with local classical elaboration. No mathematical axiom was added by the project.
- A substitution removed a variable needed later in the insertion proof; explicit equality substitution fixed the orientation.
- Warnings-as-errors identified unused section hypotheses, unnecessary simp arguments and simpa calls, and one doc-comment placement before `omit`. These were repaired instead of suppressing the linters.
- Direct decision procedures for product strict order and recursive legality initially failed to synthesize executable decidability. Expanding the strict order into non-strict comparisons and simplifying recursive legality fixed the examples. No `native_decide` was used.
- The first aggregate invocation reached the host's 100-second call limit while entering module 16. No child remained. The unfinished module was recompiled and the remaining import order resumed without rerunning prepare or deleting completed outputs. The interrupted invocation is not counted as a completed build.
- A complete inventory revealed that the v0.12 count of 512 omitted 22 declarations with inline attributes. The corrected inherited total is 534; 59 new theorems give 593. Every listed declaration is checked by the new full axiom audit.

Saved development logs under `results/v0.13.0/dev*.log` are failure records, not current proof results. Current per-source successful clean logs are separate.
