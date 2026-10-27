# Failures and repairs — block 11

## Resource failure and resulting verification scope

The restored portable archive was authenticated by its recorded SHA256. A fresh
predecessor replay and draft work were initially started concurrently. Large Lean
imports contended for the container's 4 GiB cgroup memory allowance, causing paging,
stalls and command timeouts. The predecessor scheduler was paused and then stopped.
Its partial logs are preserved under `incomplete_predecessor_v0.10.0`; there is no
complete new predecessor audit or kernel-replay result. No full-corpus fresh replay
or independently extracted second proof replay is claimed for v0.11.0.

Subsequent Lean work runs strictly serially with one Lean thread. The necessary
project dependency closure was compiled in this turn and the five new modules are
freshly rebuilt by the final verifier. It records the 13 reused project objects by
source and object hash. All pinned imported Mathlib objects remain reused artifacts.

The outer container launch of the final verifier returned a transport timeout even
though the launched process continued. It was inspected and monitored rather than
launching a competing duplicate. This is separate from any per-Lean-command result.

## Development proof failures

Drafts failed on continuous-linear-map coercion simplification, an uninferred
constant in filter subtraction, warning-fatal unused hypotheses/parameters,
deprecated `ContinuousLinearMap.sub_apply`, eta expansion of pointwise function
division, and a dependent orthogonal-projection rewrite. Fixes used explicit typed
constants and function equalities, targeted simp, and removal of genuinely unused
parameters. Warning checks were not disabled. Development logs retain each failed
and corrected pass. Production files do not contain admitted proofs or custom axioms.

## Finite computation failure

The first finite control attempted to pass redundant columns to a helper requiring
an independent basis, producing a singular Gram matrix. The control was corrected
to form the actual range projector as A times its exact pseudoinverse. This was an
implementation error, not a mathematical counterexample. The corrected tests check
actual rational matrices and known finite formulas, not infinite limits.

## Packaging filename repair

The first archive writer used Path.with_suffix on a versioned directory name,
which replaced the final .0 and produced v0.11.zip instead of v0.11.0.zip. Its
byte-integrity checks passed, but the requested filename existence check failed.
The writer now appends .zip to the full directory name. The final archive and
sibling integrity record use v0.11.0. No proof or execution input changed.
