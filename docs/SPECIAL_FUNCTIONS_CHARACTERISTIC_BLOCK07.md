# Special Functions: characteristic exponent, 2 November 2026

SF-LEAN-B07 proves the characteristic-exponent section preceding Theorem F.2.
For 0<q,r,a,b<1, there is a unique rho>0 with
(1-q^rho)(1-b^rho)=(ar)^rho. The real matrix with rows (q^rho,r^rho) and
(a^rho,b^rho) has the stated positive right and left eigenvectors. The right
vector is normalized by its maximum coordinate.

The complex spectrum is exactly {1,q^rho+b^rho-1}; the second eigenvalue has
absolute value below one. The actual complex matrix spectral radius is one,
and conversely spectral radius one at a positive exponent forces the same
determinant equation. This gives a unique positive spectral exponent too.

The source adds **23 theorem declarations**, including supporting lemmas,
bringing the registered scope to **179 names**. These are matrix/exponent
prerequisites. The analytic order, type bounds and type-vector proportions
in F.2 remain open.

- [Exact result, proof, verification and continuation](../monographs/special-functions/formalization/Block07/REPORT.md)
- [Production Lean source](../monographs/special-functions/lean/CoupledCharacteristic.lean)
- [Claim correspondence](../monographs/special-functions/formalization/Block07/CLAIM_MAP.json)
- [All 23 names and source hash](../monographs/special-functions/formalization/Block07/declarations.json)
- [Source-bound replay receipt](../monographs/special-functions/formalization/Block07/evidence/receipt.json)
- [Input/output inventory](../monographs/special-functions/formalization/Block07/IO_MANIFEST.json)
- [Focused self-review](../monographs/special-functions/formalization/Block07/SELF_REVIEW.md)
- [Current continuation file](../monographs/special-functions/CONTINUE_HERE.md)

The fresh replay has 36 steps, including compilation, axiom audits and
same-kernel replay of seven coupled modules, four rejection controls and one
positive fixture file. It freshly audits 140 coupled declarations and inherits
the finite core's 39-name evidence. Mathlib's pinned cache is reused and review
is self-review. Exact fixtures check exponent one and normalized vectors for
the rational and symmetric examples, a negative second eigenvalue, matrix
orientation, and excluded boundary inputs.

Sources, hashed I/O, current records and catalogue are updated. Earlier proof
blocks and reading/manuscript files are preserved. The
[component-rescaling guide](SPECIAL_FUNCTIONS_RESCALING_BLOCK06.md) retains its
dated scope. Next are the positive-real comparison inequalities leading to
the analytic growth bounds; the full monograph remains incomplete.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
