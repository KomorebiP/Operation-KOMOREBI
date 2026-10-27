# Continue the model-theory bridge from Logical Resolution v0.1

This is a new logical-resolution branch, not p-adic Block 16 or Representation
Calculus v0.5. Treat its released bytes and named coverage as the current source.
Read README, THEOREM_NOTE, FORMALIZATION_COVERAGE, PROOF_AUDIT, RESULTS, and the
failure ledger before editing. Check integrity before a replay; audit scripts
intentionally rewrite current execution evidence.

## Completed first target

The specified value-equality/state-quantifier fragment exactly captures unary
observational types. Surjective exact transport preserves all formulas. Finite
certified tests give defining formulas; infinite streams supply a genuine
nondefinability boundary. Quantifier rank does not add state distinctions within
a fixed system in this initial fragment.

## Next bounded target

Build an explicit semantics-preserving translation of this syntax into a standard
first-order/many-sorted encoding, then add a small genuinely relational example.
A binary relation not determined by the existing observations can make a quantified
query distinguish states with the same old observation profile. Specify the
additional preservation condition before allowing that relation through a quotient.

Do not claim ordinary full first-order type equivalence from observational equality.
Do not assume quantifier elimination, elimination of imaginaries, saturation,
compactness, or an elementary-embedding property. The stream relation is an infinite
formula family, not a single definable equivalence in this fragment. The finite
horizon completeness assumption must be certified, not inferred from enough samples.

## Reproduction

    python tools/verify_integrity.py
    python tools/run_checked.py --lean /path/to/lean

All modules use only matching Lean/Std. Keep the two inherited source files byte
identical unless an explicit migration is necessary and recorded. Retain false
claim and placeholder rejection controls. Include partial failure results rather
than asserting verification if a compiler task does not complete.
