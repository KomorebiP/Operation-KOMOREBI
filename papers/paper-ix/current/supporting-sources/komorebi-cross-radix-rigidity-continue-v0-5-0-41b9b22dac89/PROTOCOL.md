# Continuation Protocol

## Governing rule

**Source + strict Lean audit outrank narrative.** Never promote a claim because it appeared in conversation or an old progress note.

## Protocol

1. Read `START_HERE.md`, `CONTINUE_HERE.md`, `AUDIT.json`, then the relevant `src/*.lean` files.
2. Treat v0.4.0 as immutable baseline. Put new work in new modules/versioned checkpoints.
3. Compile with pinned Lean `4.34.0-rc2`, pinned Mathlib commit `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and `-DwarningAsError=true`.
4. Run a placeholder scan for `sorry`, `admit`, and custom `axiom` declarations.
5. Run representative `#print axioms` on load-bearing new theorems.
6. Distinguish theorem failure from proof-engineering failure, timeout, missing import, bad module path, or resource exhaustion.
7. Bell's generalized Cobham theorem remains an explicitly external leaf until genuinely formalized.
8. The naive base-independent integral normal form is false; preserve the square-sequence obstruction unless a new theorem explicitly retains/localizes the defect.
9. Reconstruct temporary/unpersisted Reynolds/DFT/decoder/lcm claims from definitions and compile them before citing them as proved.
10. Prefer exact algebraic formulas and constructive maps to numerical evidence.
11. When a new theorem is proved, update the audit ledger immediately with theorem name, hypotheses, source file, dependencies, and proof boundary.
12. Before packaging, recompile every new module from a clean module path and preserve logs and SHA-256 hashes.

## One-line protocol

`Read START_HERE.md -> CONTINUE_HERE.md -> PROTOCOL.md -> AUDIT.json; continue only from saved Lean theorems, preserve v0.4.0, formalize the missing Reynolds/DFT/affine-decoder/lcm layer first, compile every new claim with pinned Lean/Mathlib and warnings-as-errors, keep Bell external, and retain the square-sequence integral obstruction.`
