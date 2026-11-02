# Special Functions: positive-real comparisons, 2 November 2026

SF-LEAN-B08 proves the real-axis and lower-comparison foundations for F.2.
The canonical complex functions are identified with actual convergent real
series on the real axis. For R>=0 their real values are at least R and are
strictly increasing. The real derivative equations are checked, and the
maximum complex norm on each radius is attained at its nonnegative real point.

Both lower product recurrences along the radii p(R-1) hold for R>=1, and
their logarithmic forms hold for R>1. At R>=B=1+2/min(q,r,a,b), all four
child radii are at least two. The proof uses a real mean-value comparison
on the final unit interval, with explicit order and positivity hypotheses.

The source adds **22 theorem declarations**, including supporting lemmas,
bringing the registered scope to **201 names**. The explicit power/type
comparisons and asymptotic growth conclusions of F.2 remain open.

- [Exact result, proof, verification and continuation](../monographs/special-functions/formalization/Block08/REPORT.md)
- [Production Lean source](../monographs/special-functions/lean/CoupledPositiveReal.lean)
- [Claim correspondence](../monographs/special-functions/formalization/Block08/CLAIM_MAP.json)
- [All 22 names and source hash](../monographs/special-functions/formalization/Block08/declarations.json)
- [Source-bound replay receipt](../monographs/special-functions/formalization/Block08/evidence/receipt.json)
- [Input/output inventory](../monographs/special-functions/formalization/Block08/IO_MANIFEST.json)
- [Focused self-review](../monographs/special-functions/formalization/Block08/SELF_REVIEW.md)
- [Current continuation file](../monographs/special-functions/CONTINUE_HERE.md)

The fresh replay has 39 steps, with compilation, axiom audits and same-kernel
replay of eight coupled modules, four rejection controls and one positive
fixture file. It freshly audits 162 coupled declarations and inherits the
finite core's 39-name evidence. Mathlib's pinned cache is reused; review is
self-review. Exact fixtures exercise the origin, the R=1 unit endpoint,
the worked threshold B=11, and the distinction between real values and norms.

Actual source files, hashed I/O, current records and catalogue are updated.
Earlier proofs, manuscripts and reading PDFs are preserved. The
[characteristic-exponent guide](SPECIAL_FUNCTIONS_CHARACTERISTIC_BLOCK07.md)
retains its dated scope. Next is the explicit lower power comparison and its
seed/descent induction, followed by the remaining upper and asymptotic bounds.

[Return to Special Functions](works/monographs-special-functions.md) ·
[Evidence catalogue](STATUS_CATALOG.md#monographs-special-functions)
