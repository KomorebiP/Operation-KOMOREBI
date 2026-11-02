# Special Functions: component rescaling, 2 November 2026

SF-LEAN-B06 proves Theorem G.1's full component-rescaling equivalence and
explicit scalar representation. For positive strict real contraction scales,
nonzero complex constants A,B with V(z)=A U(Bz) exist exactly when D=0,
equivalently q=b or qb=ar. The complex necessity direction is retained.

With S=sqrt(k/p)>0 and c=sqrt(S), the checked representation is
U(z)=c T(q,Sr)(c^-1 z) and V(z)=c^-1 T(q,Sr)(cz). Both effective scalar
scales lie in (0,1), and T is the unique normalized entire scalar solution.
The proof verifies both equations and identifies the constructed pair by
the existing entire uniqueness theorem.

The existing boundary tuples now have a proved collision of the full labeled
entire pairs, although their ordered scales differ. This strengthens the
earlier finite-jet counterexample and shows why the germ inverse's defect
guard cannot be dropped.

The source adds **19 theorem declarations**, including supporting lemmas,
bringing the registered scope to **156 names**. Full analytic-monograph
coverage remains open.

- [Exact result, proof, file I/O and remaining work](../monographs/special-functions/formalization/Block06/REPORT.md)
- [Production Lean source](../monographs/special-functions/lean/CoupledRescaling.lean)
- [Claim correspondence](../monographs/special-functions/formalization/Block06/CLAIM_MAP.json)
- [All 19 names and source hash](../monographs/special-functions/formalization/Block06/declarations.json)
- [Source-bound replay receipt](../monographs/special-functions/formalization/Block06/evidence/receipt.json)
- [Input/output inventory](../monographs/special-functions/formalization/Block06/IO_MANIFEST.json)
- [Focused self-review](../monographs/special-functions/formalization/Block06/SELF_REVIEW.md)
- [Current continuation file](../monographs/special-functions/CONTINUE_HERE.md)

The fresh replay has 33 steps: dependency checks, compilation and axiom
audits of six coupled modules, same-kernel replay, four rejection controls
and one positive fixture file. It freshly audits 117 declarations and inherits
the finite core's 39-name evidence. Mathlib's pinned cache is reused; review
is self-review. Input and output hashes are recorded explicitly.

The next larger target is the Perron growth law, beginning with an exact
characteristic-exponent contract. Operator decoupling and broader coverage
remain separate obligations. Earlier sources, guides, reading PDFs and
verification records are preserved; the current files and catalogue are
updated.

The earlier [analytic-germ inverse guide](SPECIAL_FUNCTIONS_GERM_INVERSE_BLOCK05.md)
retains its dated scope and links to the preceding proof blocks.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
