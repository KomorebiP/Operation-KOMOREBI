# Special Functions: entire existence, 2 November 2026

SF-LEAN-B03 adds **19 checked declarations** proving that the previously
constructed coupled functions extend to the whole complex plane when all four
positive real scales are strictly less than one.

The same coefficient sums now converge absolutely at every complex point,
are holomorphic everywhere, and satisfy

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz),\qquad U(0)=V(0)=0.
\]

The proof propagates convergence through the recurrence, using the absolutely
convergent Cauchy product and the denominator `2*n+3`. A contraction-ladder
induction reaches every finite complex point. Uniform bounds on smaller balls
then justify holomorphy and termwise differentiation. No choice of glued
extensions is required: these are the same sums as in Block02.

The registered source scope is **108 named declarations**: the inherited 39
in the finite core, 29 in Block01, 21 in Block02, and 19 here. Supporting lemmas
are included in that count. This completes the entire-existence step, with
the global equations, but does not prove the full analytic monograph.

- [Exact result, proof mechanism and replay instructions](../monographs/special-functions/formalization/Block03/REPORT.md)
- [New production Lean source](../monographs/special-functions/lean/CoupledEntire.lean)
- [Claim correspondence and remaining obligations](../monographs/special-functions/formalization/Block03/CLAIM_MAP.json)
- [All 19 new theorem names and source hash](../monographs/special-functions/formalization/Block03/declarations.json)
- [Source-bound verification receipt](../monographs/special-functions/formalization/Block03/evidence/receipt.json)
- [Focused mathematical self-review](../monographs/special-functions/formalization/Block03/SELF_REVIEW.md)
- [Continuation checkpoint](../monographs/special-functions/CONTINUE_HERE.md)

Compilation treats warnings as errors. The exact axiom audit and same-kernel
replay cover all three coupled modules against the existing pinned Mathlib
cache; the finite core's 39-declaration record is inherited. Four negative
controls check a missing strictness guard, an incorrect denominator, an
incorrect derivative sign, and a placeholder proof. A positive fixture checks
the existing rational parameters beyond the old local disk. Review is
self-review, not independent review.

The next step is the reverse Taylor coefficient bridge and uniqueness among
arbitrary normalized analytic solutions. The same bridge supports the
analytic-germ version of parameter recovery. Perron growth and full component
rescaling remain later obligations.

The [Block02 guide](SPECIAL_FUNCTIONS_ANALYTIC_BLOCK02.md) retains its earlier
local scope. All earlier formal sources, manuscript sources and reading PDFs
are preserved. Current catalogue entries link to this dated extension record.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
