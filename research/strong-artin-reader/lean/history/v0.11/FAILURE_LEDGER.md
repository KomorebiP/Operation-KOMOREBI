# v0.11 development failure ledger

Failures below are preserved as proof-engineering or execution failures. None is counted as a mathematical counterexample.

1. **Initial local-algebra draft:** Lean rejected noncomputable quotient definitions and flagged an unused primality hypothesis. Fixed by placing definitions in a noncomputable section and tightening theorem scopes. No theorem statement was weakened.
2. **Generic branch draft:** rewrite direction errors around powers and subtraction prevented elaboration. Fixed by using the correct `pow_mul` orientation and injectivity lemma.
3. **Polynomial reduction lemma:** an unqualified `map_sub` resolved to the wrong namespace. Fixed by using the polynomial-specific mapping API.
4. **Twist construction:** direct unfolding across `AdjoinRoot` produced a dependent typeclass/definitional-equality obstruction. Fixed by proving and reusing an explicit `eval₂_defectPolynomial` formula rather than changing the mathematical claim.
5. **Twist inverse proof:** coefficient constants did not simplify automatically. Fixed with an explicit checked `twistHom_of` lemma and ring-hom rewrites.
6. **Branch-support integration:** first import failed because compiled `.olean` files were outside the portable Lake search path. They were placed in the workspace build search directory; unchanged mathematics then elaborated.
7. **Branch-support draft:** first elaboration exposed typeclass-linter warnings and two coercion/rewrite issues. Replaced implicit local instance tricks with explicit instance arguments and exact `ZMod.val_injective` usage. The same theorem then passed.
8. **Quotient-support draft:** first proof used a branch-equality rewrite at the wrong syntactic level and manually reproved a quotient universal-property equality. Fixed by changing the kernel-membership goal to the composed-hom evaluation and using Mathlib's `Ideal.Quotient.liftₐ_comp` theorem.
9. **Equivariant-quotient draft:** only failure was an unused section-variable linter error on a theorem that did not need primality. The theorem was explicitly scoped with `omit`; statement unchanged.
10. **Aggregate five-module replay command:** the outer container command reached its overall execution limit after the fifth module had emitted its axiom output and produced its `.olean`. This aggregate timeout was not treated as proof success. The fifth module was then rerun standalone and returned **RC=0**. Finally, the packaged `verify.py` was executed independently over all five modules and returned **RC=0**.

No active v0.11 source contains `sorry`, `admit`, or a custom `axiom` declaration.
