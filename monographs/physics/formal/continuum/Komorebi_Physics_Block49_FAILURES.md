# Block 49 Failure Ledger

The following failed or incomplete operations were excluded from proof evidence.

1. Several parent dependency builds exceeded the external command window while filling the pinned cache. The unchanged project was resumed until the Block 48 target completed all 3,063 jobs.
2. The first physical-adjoint proof draft relied on simplification of `torusFourierEquiv (torusFourierEquiv.symm x)`; the simplifier unfolded the synthesis map instead of closing the inverse law. The proof was repaired with the explicit `apply_symm_apply` theorem.
3. The first adjoint calculation allowed subtype coercions to determine the Hilbert space incorrectly. Ambient values were made explicit with `.1` projections.
4. The first domain-inclusion draft supplied an explicit vector argument to a submodule inclusion whose vector argument is implicit. The application was corrected to pass only the membership proof.
5. The first API-generation script referenced a shell variable inside Python and failed with `NameError`. It produced no audit evidence and was rerun correctly.
6. No timeout, partial build, scratch compilation, or prose status was counted as a checked theorem.
