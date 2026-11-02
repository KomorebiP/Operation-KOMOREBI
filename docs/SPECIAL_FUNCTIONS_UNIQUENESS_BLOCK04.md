# Special Functions: analytic uniqueness and F.1, 2 November 2026

SF-LEAN-B04 adds **16 checked declarations** proving analytic germ uniqueness,
normalized entire uniqueness, and the reverse canonical-series bridge.
Together with the preceding blocks, `coupled_F1_contract` covers the principal
statement of **Theorem F.1 in its ordinary odd-series formulation**.

For fixed labeled real scales `0<q,r,a,b<1`, there is a unique normalized
entire pair satisfying

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz),\qquad U(0)=V(0)=0.
\]

The pair is odd and has the strictly positive recurrence coefficients already
constructed in Block01. Its expansions converge on the whole plane. Competing
solutions are not assumed odd and need no supplied coefficient recurrence or
expansion. Actual derivative statements ensure complex differentiability.

The proof compares vanishing orders of differences. Their coupled equations
raise every finite lower order bound; infinite analytic order gives local
equality. The identity theorem gives global equality for entire functions.
This identifies arbitrary solution germs with the canonical coefficient sums.

The registered source scope is **124 named theorem declarations**: the inherited
39 in the finite core, 29 in Block01, 21 in Block02, 19 in Block03, and 16 here.
Supporting lemmas and bundled contracts are included in that count.

- [Exact result, mechanism, verification and remaining work](../monographs/special-functions/formalization/Block04/REPORT.md)
- [New production Lean source](../monographs/special-functions/lean/CoupledUniqueness.lean)
- [Claim correspondence](../monographs/special-functions/formalization/Block04/CLAIM_MAP.json)
- [All 16 new theorem names and source hash](../monographs/special-functions/formalization/Block04/declarations.json)
- [Source-bound replay receipt](../monographs/special-functions/formalization/Block04/evidence/receipt.json)
- [Focused self-review](../monographs/special-functions/formalization/Block04/SELF_REVIEW.md)
- [Continuation checkpoint](../monographs/special-functions/CONTINUE_HERE.md)

The replay compiles and axiom-audits all four coupled modules, then rechecks
them with the same Lean kernel against pinned cached imports. The finite
core's earlier verification is inherited. Four rejection fixtures and a
positive interface fixture check normalization, differential equations,
coefficient indexing, placeholder rejection, the preserved rational example,
and conditional uniqueness at zero scales. Mathematical review is self-review.

The reverse bridge is an explicit canonical `HasSum` expansion. The next
obligation is to extract the degree-seven coefficient jet from equality of
canonical analytic germs, then apply the existing guarded parameter inverse.
Generic Taylor coefficient-object transport, Perron growth, and full component
rescaling remain open. The full analytic monograph is not formalized.

The earlier [local analytic guide](SPECIAL_FUNCTIONS_ANALYTIC_BLOCK02.md) and
[entire-existence guide](SPECIAL_FUNCTIONS_ENTIRE_BLOCK03.md) retain their dated
scope. Earlier proof sources, evidence, manuscript sources and reading PDFs
are unchanged.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
