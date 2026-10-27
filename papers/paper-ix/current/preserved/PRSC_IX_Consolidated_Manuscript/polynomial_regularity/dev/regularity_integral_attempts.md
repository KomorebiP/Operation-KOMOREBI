# Integral bridge and control development

Author: Komorebi P.

The first bridge compile failed because expected-type inference selected the field as the coefficient ring inside the rectangular parameter-Jacobian expression. Replacing the ambiguous coercion by the explicit `algebraMap` fixed the elaboration. The evaluation and Jacobian inclusion lemmas then compiled with warnings treated as errors.

The first control compile rejected unused completeness assumptions and a simplification that reduced finite indices before the `join` coordinate rules matched. Removing the unused hypothesis and using the explicit `join_solved`/`join_free` rules fixed both issues. All initial linear controls compiled, followed by the nonlinear polynomial and its actual root and Jacobian checks.

The final specialization initially failed to elaborate a rectangular matrix product expressed with a bare lambda. Writing the rectangular matrix with `Matrix.of` fixed instance inference. Several attempts to close the derivative conversion by simplification failed because the inserted matrix wrapper remained distinct to the simplifier. An explicit entrywise equality for that exact rectangular matrix, followed by rewriting the derivative theorem, compiled successfully. The nonlinear control also required the explicit zero-coordinate identity and `Matrix.neg_mulVec` to normalize its derivative to negative identity.

Final status: both `PolynomialRegularityIntegral.lean` and `PolynomialRegularityControls.lean` compiled successfully with the pinned portable Lean runner, one thread, a 240-second timeout and warnings treated as errors. The integral module contains nine theorems and two definitions. The controls contain ten theorems and two definitions.

No failure was hidden by changing a mathematical hypothesis, disabling a linter, admitting a proof, or adding an axiom. These are proof elaboration and simplifier repairs. Final validation is recorded by the separate fresh verification gate.
