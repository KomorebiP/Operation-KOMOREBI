# Analytic evaluation bridge

`PolynomialAnalyticEvaluation.lean` is checked with the pinned Lean runtime, warnings as errors and default resource limits.

The scalar strict derivative is proved by `MvPolynomial.induction_on`: constants, addition and multiplication by one variable. The derivative functional is the finite sum of evaluated formal partials times coordinate projections. Finite coordinate assembly gives the actual matrix `PolynomialWeightedInverse.jacobian F a`. No analytic or derivative assumptions are added to the polynomial system.

Analyticity uses the pinned Mathlib `AnalyticOnNhd.eval_mvPolynomial` followed by finite `AnalyticAt.pi`.

Development checks initially failed on: (1) implicit scalar inference and reversed argument order for the constant derivative lemma; (2) non-definitional presentation of pointwise functions and competing Pi topology/module instances; (3) simplification of formal-variable derivatives and unused argument/section lint checks. Explicit continuous-linear-map extensionality, `convert!`, the `Pi.single_apply` simplification, and omission of genuinely unnecessary completeness hypotheses resolve these without suppressing linters or changing any statement.

Final local compile returned exit code 0. Release validation is owned by the parent and is not asserted here.
