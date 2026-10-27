# Execution and mathematical limitations

The inherited archive is unchanged. New-run failures and repairs are recorded below.

- Numerical leading-term probe at return index 14 had relative error 1.17670147255026e-6, above the predeclared 1e-6 asymptotic tolerance. All preceding exact-equality regressions passed. The probe was moved two return steps deeper (index 16); neither equality tolerances nor the asymptotic tolerance were loosened. The initial numerical source is retained.
- Lean development needed the explicit finite-type import, explicit Fin constructors, and exposed definitions for cross-module simplification. A proposed noncommutative group normalization was replaced by the correct additive commutative-group transport. Intermediate unfinished builds were rejected; none is verification evidence. Unused-tactic warnings were removed, not disabled.
- The first whole-project synchronous Lean invocation exceeded the outer 200-second execution envelope after compiling eight modules. It produced no final axiom-audit verdict and is not counted as a passed build. No Lean process remained afterward. The final runner splits the clean compilation into two synchronous stages, authenticating source and compiled-object hashes between stages and terminating a subprocess group on any internal timeout. The proof statements and warning settings are unchanged.
