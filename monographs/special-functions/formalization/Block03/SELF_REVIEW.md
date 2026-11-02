# Focused self-review: entire existence and the global equations

Primary verdict: **proved as written**, for the exact entire-existence claim
stated here. Review provenance: self-review.

Claim card: for every labeled real tuple with `0<q,r,a,b<1`, the functions
`Scales.U` and `Scales.V` defined in Block02 by the Block01 coefficient
recurrence are absolutely convergent odd series everywhere, are complex
differentiable everywhere, vanish at zero, and satisfy the two normalized
coupled differential equations everywhere. There is no claim of uniqueness
among arbitrary analytic functions or of a Perron growth law.

The base revision is `db811c96832833ddd900e9a50437d02f838587ef`. The exact
reviewed production source is bound by `declarations.json` and the execution
receipt. The ordinary coefficient at index `n` multiplies `z^(2*n+1)`.

Dependency graph:

`local absolute convergence + recurrence → norm Cauchy-product bootstrap →`
`convergence on each contraction-ladder level + Q^n→0 → convergence everywhere →`
`uniform bounds on smaller balls → holomorphy and derivative HasSum →`
`finite convolution identity + recurrence → global coupled equations`.

| Obligation | Assessment |
|---|---|
| Actual mathematical objects | Passed: the module imports the unchanged `U`, `V` and coefficient definitions; it constructs no surrogate solution. |
| Convolution degree | Passed: two odd degrees add to `2*n+2`; the shifted original term has degree `2*n+3`. |
| Denominator and norm bound | Passed: the exact multiplier is `2*n+3 ≥ 1`, with no division by `z` or positivity assumption on generic coefficients. |
| Bootstrap summability | Passed: norm summability of both contracted series precedes the Cauchy-product theorem and comparison test. |
| Induction base | Passed: `norm(z)≤1` lies strictly inside the previously proved disk `norm(z)^2<2`. |
| Ladder induction | Passed: each positive scale is at most `Q`; nonnegative `Q^n` preserves the inequality. |
| Reaching every radius | Passed: strict `Q<1` is used explicitly in `Q^n→0`; `Q=1` is not admitted. |
| Uniform analytic argument | Passed: absolute convergence at `R=norm(z)+1` dominates all terms on the smaller ball. |
| Differentiation | Passed: the derivative series is a `HasSum`, not a formal differentiation assertion. |
| Global product and equation | Passed: both contracted sums are absolutely convergent at the actual arguments; the derivative's index-zero term is one. |
| Zero and boundary points | Passed: no cancellation by `z` is used, and every finite complex point has a larger majorizing radius. |
| Agreement with the local solution | Passed: the same functions and sums are used throughout. |
| Arbitrary analytic-solution uniqueness and growth | Out of scope and retained as open obligations. |

At `n=0`, the finite convolution is `x*y*c_0*d_0*z²`, and the next
coefficient is `x*y*c_0*d_0/3`. This checks the absolute degree, denominator,
and first differentiated coefficient. At `z=0`, the equations give derivative
one, so a negative unit derivative is rejected. The norm-one ladder fixture
tests the strictness boundary without asserting that every boundary tuple
fails to be entire.

External leaves are the pinned Mathlib absolutely convergent Cauchy-product,
geometric-power limit, uniform-limit holomorphy, and derivative-series
theorems. Their exact typed hypotheses are discharged in Lean. No numerical
computation is used as proof evidence. The replay's trusted-import scope and
all command logs are described in `REPORT.md` and `evidence/receipt.json`.

The strongest safe statement is entire existence of this constructed pair
with the global equations. The gap to full Appendix F.1 is the reverse Taylor
coefficient correspondence and uniqueness among arbitrary normalized analytic
solutions. The next discriminating check is the coefficient-level product and
derivative API for a general holomorphic solution germ.
