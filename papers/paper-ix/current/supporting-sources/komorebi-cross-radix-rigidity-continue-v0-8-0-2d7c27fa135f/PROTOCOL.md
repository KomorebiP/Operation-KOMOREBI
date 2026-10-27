# Continuation Protocol — v0.8.0

## Governing rule
Source + strict Lean audit outrank narrative. Never promote a claim from conversation alone.

1. Read `START_HERE.md`, `CONTINUE_HERE.md`, `AUDIT.json`, `PROOF_BOUNDARIES.md`, and `BELL_EXTERNAL_INTERFACE.md`.
2. Treat all v0.7 sources as immutable. New work belongs in new modules/checkpoints.
3. Compile with pinned Lean `4.34.0-rc2`, pinned Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and `-DwarningAsError=true`.
4. Scan for `sorry`, `admit`, and custom `axiom` declarations.
5. Run representative `#print axioms` for load-bearing theorems.
6. Distinguish theorem failure from proof-engineering failure, timeout, import/cache failure, or orchestration failure.
7. Keep three notions separate: absolute orbit-hull minimality, raw shell/jet mask minimality, and invariant shell/jet mask minimality.
8. Do not assert the candidate explicit divisor-upward / jet-downward closure formula until its Fourier/jet transition theorem is actually proved.
9. Bell remains external. Do not broaden Bell Theorem 1.5 beyond its checked integer-valued scope.
10. Do not revive the naive base-independent integral normal form; any integral strengthening must retain local defect data.
11. Update `AUDIT.json`, source hashes, clean logs, and `MANIFEST.json` before packaging the next checkpoint.
