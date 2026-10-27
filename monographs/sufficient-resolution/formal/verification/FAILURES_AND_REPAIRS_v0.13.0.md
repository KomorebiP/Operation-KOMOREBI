# Actual development failures and repairs

Initial drafts used ambiguous `residual` (colliding with the root filter name), an
old absolute-value triangle name, and an incorrect reverse-triangle API name.
They were corrected to the pinned Mathlib names and an explicitly qualified
DiscrepancyResidual.residual. An initial downstream compile consequently had a
missing dependency object; it was rerun after the dependency passed.

A new projection lemma required the submodule argument explicitly. A positivity
proof for a filter-indexed parameter needed the explicit hypothesis hl i rather
than expecting the tactic to instantiate the universal assumption. Both were
corrected without changing the mathematical contract or weakening warning checks.

The corrected five modules compile with warnings as errors. Diagnostic compiler
logs and argv/exit-status records are under development_v0.13.0. No deliberate
placeholder, custom axiom, unsafe declaration or native_decide was added to a
production module. Deliberate negative controls are separate verification files.

The finite checker and test suite passed their first completed runs in this turn.
The full cumulative corpus is not claimed freshly replayed; only the new block's
22-module project dependency closure is in the fresh proof-verification contract.
