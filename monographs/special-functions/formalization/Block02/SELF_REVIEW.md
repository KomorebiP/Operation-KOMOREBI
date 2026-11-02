# Focused mathematical self-review: SF-LEAN-B02

Claim card: for every labeled positive real scale tuple with each entry at
most one, the two sums of `Scales.coefficients` are holomorphic on
`‖z‖²<2`, are odd, vanish at zero, and satisfy the normalized coupled
differential equations there. Ordinary coefficient `u_n` multiplies
`z^(2*n+1)`. No factorial normalization is introduced.

The exact reviewed source is identified by `declarations.json`; the execution
receipt binds that source and all replay inputs. The base repository revision
is `cfff62cde8c8a5aac109fc84bf89c73b0e3daad1`. Review provenance: self-review.
Primary verdict: **proved as written**, for the exact local claim below.
The exact Lean statements, rather than the whole Appendix F.1, are the target.

Dependency graph:

`Block01 positivity + geometric bounds → uniform bounds on smaller balls →`
`complex differentiability + HasSum of derivatives → contracted Cauchy product`
`+ coefficient recurrence → coupled_local_solution`.

| Obligation | Assessment |
|---|---|
| The sums use the constructed recurrence | Passed: `U` and `V` project `Scales.coefficients` directly. |
| Local uniform convergence | Passed: a strictly smaller intermediate radius gives ratio `R²/2<1`. |
| Differentiation is justified | Passed: Mathlib's complex derivative-series theorem gives `HasSum`, not only a formal coefficient identity. |
| Contracted arguments remain admissible | Passed: `mul_mem_localDisk` requires norm at most one; equality is allowed. |
| Infinite product is valid | Passed: absolute summability is proved at both contracted arguments before invoking the Cauchy product. |
| Index and degree matching | Passed: factors at degrees `2*i+1` and `2*(n-i)+1` sum to `2*n+2`; the shifted derivative has the same degree. |
| Constant and denominator | Passed: `c_0=1`, denominator `2*n+3>0`, and `U'(0)=V'(0)=1`. |
| Domain boundary | Passed: every point claim is strictly inside `‖z‖²<2`; no boundary convergence is used. |
| Odd symmetry | Passed: the odd-power identity is proved for the defined sums. |
| No circular analytic assumption | Passed: no equation for an infinite sum is assumed as a hypothesis. |
| Entire continuation, analytic uniqueness, reverse coefficient recovery | Out of scope and retained as open obligations. |

The external leaves are the pinned Mathlib uniform-limit and absolutely
convergent Cauchy-product theorems. Their exact typed hypotheses are discharged
in the compiled proof; no approximate numerical computation is load-bearing.
The origin and first derivative check the minimum index, and permitting all
scales equal to one checks that a local result is not mislabeled as entire.

For execution evidence, inspect `evidence/receipt.json` and every command log;
only a receipt with `status: passed` supports the final formal verdict. The
scope of kernel replay and its trusted imports are stated in `REPORT.md`.

The remaining gap to the full Appendix F.1 is extension/gluing and uniqueness
among arbitrary entire solutions. The cheapest next formal check is a
holomorphic primitive on a disk whose derivative is the contracted product,
followed by agreement of old and new solutions on the smaller disk.
