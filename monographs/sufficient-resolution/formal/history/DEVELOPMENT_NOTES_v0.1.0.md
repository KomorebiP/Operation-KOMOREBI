# Development failures and corrections

This file records failures rather than presenting only successful final runs.
No theorem was accepted on the basis of a failed or interrupted check.

1. The initial container had no Lean executable. The preserved five-part portable
   runtime was retrieved and reconstructed. Its inner archive was XZ, not Zstandard;
   the temporary filename was corrected before extraction.
2. Streaming container sessions were unavailable. Runtime extraction and longer
   checks used monitored subprocesses with durable logs instead.
3. The initial full `import Mathlib` compile exceeded the 45-second command limit.
   A separate bounded retry of that broad import reached the 180-second timeout.
   Replacing the broad import with the required `LinearMap.End` import eliminated
   the excessive loading. Later source compiles completed normally.
4. The first compression draft used the wrong namespace for operator evaluation
   (`LinearMap.mul_apply` instead of `Module.End.mul_apply`), a reserved identifier
   (`then`), and an insufficiently explicit zero-power extensionality proof.
   These were source/API errors and were corrected without weakening the claims.
5. The obstruction-transport draft needed an explicit final reflexivity step for
   subtype coercions. Its quotient-composition proof redundantly attempted quotient
   induction after `ext` had already passed to representatives. Both were corrected.
6. The concrete example required the actual pinned modules `Algebra.Field.Rat`
   and `LinearAlgebra.Prod`. A guessed `Data.Rat.Basic` module does not exist in
   this revision. Explicit `LinearMap.ext` replaced an `ext x` pattern rejected
   by warning-as-error linting.
7. The copied Lake manifest initially retained the portable workspace name. A
   hyphenated replacement was not a valid serialized Lean `Name`. Both package
   and manifest now use `Komorebi`. All dependency revisions remained unchanged.
8. Probing `leanchecker --help` was not a valid usage check: this executable has
   no help handler and treated the option as a request for its default project.
   The actual replay calls use explicit module names, as required by the shipped
   `LeanChecker.lean` source.

The relevant failed compiler logs and successful corrections remain under
`verification/development/`. Source scans and axiom checks apply to final production
files, not to deliberately invalid controls or old diagnostic text containing the
compiler's own placeholder messages.
