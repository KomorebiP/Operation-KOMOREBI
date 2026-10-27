# Development failures and corrections

1. Runtime extraction hit a 20-second container wall cap. The saved five-part
   compressed archive was completely reconstructed first and its SHA-256 matched
   the v0.4 provenance. No extraction-completion claim is made from that timeout.
   The recovered core compiler and Std did work: Lean --version, both inherited
   modules, and the final six-module cold audit all completed successfully. No
   Mathlib extraction/build is required by this branch.
2. The first ObservationalFirstOrder draft used an unqualified rewrite twice and
   rewrote the already transformed left side to its quotient again, instead of
   rewriting the right side. The fix builds both explicit preservation
   equivalences and composes them. The failed source snapshot and diagnostic are
   retained under evidence/.
3. The first LogicalBoundaries draft applied simp after congr had already closed
   the goal. Warning/error "No goals to be solved" rejected it. The redundant
   tactic was removed; the failed snapshot and log are retained.
4. Initial reference-audit development used direct arithmetic expressions for
   delayed-observation checks. Before the retained run, these were replaced by
   actual finite transition-system evaluations. No padded check is used as a
   substitute for the independently proved infinite-stream theorem.

These development attempts are separate from the completed retained cold run.
The final run uses immutable input hashes and expected-outcome controls.

5. The first packaging command used Path.with_suffix on a directory ending in
   v0.1, producing a filename ending in v0.zip. The naming bug was corrected to
   append .zip to the entire directory name. The final release is explicitly
   Komorebi_ModelTheory_Normalization_v0.1.zip. Integrity and extraction checks
   use that exact file.
