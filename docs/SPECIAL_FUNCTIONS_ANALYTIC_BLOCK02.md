# Special Functions: local analytic formalization, 2 November 2026

SF-LEAN-B02 adds **21 checked Lean declarations**. The two functions defined
by Block01's recurrence are holomorphic on `norm(z)^2<2`, can be differentiated
term by term, and satisfy

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz),\qquad U(0)=V(0)=0,
\]

for labeled positive real scales at most one. Lean also proves odd symmetry
and `U'(0)=V'(0)=1`. The product and derivative identities concern the actual
convergent sums; the equations are not assumed as premises.

The registered sources now contain 89 named declarations: 39 in the inherited
finite core, 29 in Block01, and 21 in Block02. This counts supporting lemmas,
and does not establish full analytic-monograph coverage.

- [Exact mathematical result, dependencies and limits](../monographs/special-functions/formalization/Block02/REPORT.md)
- [Production Lean source](../monographs/special-functions/lean/CoupledAnalytic.lean)
- [Claim correspondence](../monographs/special-functions/formalization/Block02/CLAIM_MAP.json)
- [All 21 theorem names and source hash](../monographs/special-functions/formalization/Block02/declarations.json)
- [Replay receipt and command logs](../monographs/special-functions/formalization/Block02/evidence/receipt.json)
- [Focused mathematical self-review](../monographs/special-functions/formalization/Block02/SELF_REVIEW.md)
- [Continuation checkpoint](../monographs/special-functions/CONTINUE_HERE.md)

The new module and the preceding coupled module pass warning-as-error
compilation, exact axiom audits and same-kernel replay on native Windows Lean
4.34.0-rc2 with the existing Mathlib pin. Only `propext`, `Classical.choice`,
and `Quot.sound` appear. The finite core's earlier 39-declaration verification
is inherited. Mathematical review here is self-review, not independent review.

The next step is extension and agreement along the strict-contraction radius
ladder `R → R/max(q,r,a,b)`, followed by gluing. Analytic uniqueness, reverse
coefficient recovery, global Perron growth and full rescaling equivalence
remain open. The local result allows scales equal to one and asserts no
entire continuation.

The imported README, Lean-status note and finite-core guide remain frozen at
their assessed Block01 source hashes. This dated companion and the updated
catalogue describe the new scope. Reading PDFs, manuscript sources and earlier
formal evidence are unchanged.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
