# Continuation Protocol — v0.7.0

## Governing rule
Source + strict Lean audit outrank narrative. Never promote a claim from conversation alone.

1. Read `START_HERE.md`, `CONTINUE_HERE.md`, `AUDIT.json`, `PROOF_BOUNDARIES.md`, and `BELL_EXTERNAL_INTERFACE.md`.
2. Treat v0.6.0 and earlier certified sources as immutable baselines. Put new work in new modules/checkpoints.
3. Compile with pinned Lean `4.34.0-rc2`, pinned Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and `-DwarningAsError=true`.
4. Scan for `sorry`, `admit`, and custom `axiom` declarations.
5. Run representative `#print axioms` for load-bearing theorems.
6. Distinguish theorem failure from proof-engineering failure, timeout, import/cache failure, or shell-status error.
7. Bell remains external. Do not replace its checked integer-valued Theorem 1.5 scope with a broader claim.
8. Do not revive the naive base-independent integral normal form; future integral work must retain local defects.
9. The next primary target is active-shell / shell-jet minimal-hull sharpening of the now-certified uniform common hull.
10. Update `AUDIT.json` and hashes before packaging any new checkpoint.
