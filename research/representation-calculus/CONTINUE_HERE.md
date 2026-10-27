# Continue from Representation Calculus v0.4

This is the representation-calculus branch, not p-adic Block 16. v0.3 is frozen
under history; three reused p-adic module-generator files are recorded separately.
Read FORMAL_NOTE.md, FORMALIZATION_COVERAGE.md, RESULTS.md and DEVELOPMENT_FAILURES.md.
Verify distribution integrity before rerunning anything that rewrites evidence.

## Completed mathematical target

A valid prime-power certificate with t nonzero diagonal factors has exact minimum
t among all-state/all-word encodings into free residue arrays, when the INITIAL
ENCODING is linear. The competitor's transitions and observations may be nonlinear.
The upper-bound constructed machine remains an ordinary linear machine.

The proof builds a linear surjection from the competitor's image to the certified
principal ideals. A submodule of R^n needs at most n generators, while t nonzero
principal factors need at least t. This replaces a generally insufficient state-
cardinality lower bound. All 202 frozen certificates have generated minimum endpoints.

The linearity restriction is essential. TorsionEncodingBoundary proves that two
order-two factors modulo 16 need two linear coordinates but fit into one residue
under a NONLINEAR parity code. Do not silently remove this hypothesis.

## Next work

1. Freeze a structurally held-out input family before the discovery run and compare
   matched computation/prover budgets. Synthetic inherited regression is not new
   discovery or evidence of superiority.
2. Independently, formalize executable row-closure iteration and its module-length
   termination argument, rather than claiming the Python implementation is verified.
3. Preserve all-state vs single-seed, free coordinate count vs state cardinality,
   literal matrix source vs intended informal semantics, and theorem existence vs
   executable extraction boundaries.

The new Mathlib bridge required only a module-header conversion of legacy Std files.
Proof/definition bodies are unchanged and the frozen originals remain in history.
All generated modules must be rebuilt in module mode; mixing cached legacy oleans
with the new modules is invalid.
