# Failures and scope of recovery

1. A pseudo-terminal/streaming execution attempt was unsupported by this host.
   It did not create the requested restoration script. The immediate follow-up
   invocation reported that missing file. The script was then created in a
   normal synchronous call.
2. Full portable-runtime extraction exceeded the 200-second execution envelope
   after four parts. A selective retry also exceeded it, after five parts.
   No continuing child process was left running. The new proof block was made
   Std-only and compiled with the complete available pinned compiler and Std.
   The complete seven-part compressed archive was independently hashed; its
   SHA-256 matches the retained pin. Full Mathlib restoration is NOT claimed.
3. An exploratory SymPy helper called .subs on the Python integer 1. Explicit
   sympification corrected this implementation error before the matrix result.
4. Lean development exposed unused simp arguments, an already-closed goal,
   a reducibility issue for deciding a negated membership predicate, and one
   remaining linear integer identity. Removing unused arguments, unfolding
   the predicate, and using omega completed the unchanged statements.
   An exploratory smoke test tried omega on an unrestricted distributive law;
   that tactic was inapplicable. It was not counted as a theorem check.
5. The first exact-check run compared an unexpanded polynomial with its
   expanded normal form structurally. Expanding the coefficient implementation's
   output corrected the comparison. No arithmetic formula changed.

The final exact run and all 44 new Lean declarations passed. The manifest and
fresh-extraction replay record identify the accepted sources. No floating-point
residual was used as an equality proof, and the gamma phase remains unresolved.
