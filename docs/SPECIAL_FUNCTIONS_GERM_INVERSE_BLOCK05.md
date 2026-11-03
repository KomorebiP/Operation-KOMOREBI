# Special Functions: analytic-germ inverse, 2 November 2026

SF-LEAN-B05 adds **13 checked theorem declarations** connecting equality of
the canonical analytic germs to the parameter inverse of Appendix G.2.
The registered source scope is **137 names**, including supporting lemmas
and the preceding 124 declarations. Full analytic-monograph coverage remains
open.

For two labeled positive scale tuples with every scale below one, equality
near zero of both U components and both V components implies equality of all
four parameters, provided the first tuple's defect D is nonzero. The proof
extracts every coefficient from germ equality, then applies the existing
degree-seven inverse. Ordered labels and the exceptional-locus guard remain
part of the theorem.

The bridge pads the odd series with zero even coefficients and constructs
Mathlib's scalar formal multilinear series. Uniqueness of convergent Taylor
representations gives coefficient equality. These are ordinary coefficients:
degrees three, five and seven have sequence indices one, two and three.
The same bridge identifies every coefficient of arbitrary supplied Taylor
objects representing a normalized analytic solution germ, resolving that
remaining API obligation from Block04.

- [Exact result, proof mechanism, verification and continuation](../monographs/special-functions/formalization/Block05/REPORT.md)
- [Production Lean source](../monographs/special-functions/lean/CoupledGermInverse.lean)
- [Claim correspondence](../monographs/special-functions/formalization/Block05/CLAIM_MAP.json)
- [All 13 names and source hash](../monographs/special-functions/formalization/Block05/declarations.json)
- [Source-bound replay receipt](../monographs/special-functions/formalization/Block05/evidence/receipt.json)
- [Focused self-review](../monographs/special-functions/formalization/Block05/SELF_REVIEW.md)
- [Continuation checkpoint](../monographs/special-functions/CONTINUE_HERE.md)

The fresh verification has 30 steps: dependency pins, warning-as-error
compilation and axiom audits of five coupled modules, same-kernel replay,
four rejection controls and one positive fixture file. The pinned Mathlib
cache is reused. The 39-declaration finite core retains its prior evidence;
98 coupled declarations receive fresh axiom audits. Review is self-review.

Next is the full component-rescaling equivalence of Appendix G.1. Perron
growth remains a separate obligation. This block proves neither a stable
numerical inverse near D=0 nor an inverse for unlabeled components. The old
exceptional example remains a finite-jet collision.

Earlier sources, reading PDFs and proof evidence are preserved. The earlier
[F.1 guide](SPECIAL_FUNCTIONS_UNIQUENESS_BLOCK04.md) retains its dated scope.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
