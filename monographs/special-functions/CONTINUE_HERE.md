# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B03**, based on repository commit
`db811c96832833ddd900e9a50437d02f838587ef`. Start with
`formalization/Block03/REPORT.md`, then its claim map, declaration map,
self-review and source-bound execution receipt.

`lean/CoupledEntire.lean` adds 19 checked declarations: for positive scales
strictly less than one, the actual recurrence sums converge absolutely and
satisfy the normalized coupled differential equations on the whole plane.
They are entire. The source scope is 108 names, including the preceding 89;
supporting lemmas are counted. Earlier sources and evidence are preserved.
The full monograph remains open. Do not stop merely because Lean is absent
from PATH.

The entire-existence step is resolved by a coefficient-series bootstrap,
without constructing or gluing new primitives. For `Q=max(q,r,a,b)<1`, the
recurrence and Cauchy product prove convergence on every ladder level
`norm(z)*Q^n≤1`; these levels exhaust the plane. Uniform radius majorants
then prove holomorphy and the global equations for the same functions.

Next executable step: use the Taylor-series derivative and product APIs to
prove that an arbitrary normalized analytic solution has the established
coefficient recurrence. Then apply recurrence uniqueness and analytic identity
to finish Appendix F.1's uniqueness, and transport the coefficient inverse
to Appendix G.2's analytic-germ statement. Perron growth and full component
rescaling remain separate later obligations.

Use `tools/verify_coupled_entire.py` with Lean 4.34.0-rc2, Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external work
directory. The native Windows run reuses the existing pinned environment;
the preserved offline Linux kit is described in `formalization/Block01/REPORT.md`.

The primitive/gluing and direct asymptotic coefficient-bound routes were
deferred after the coefficient bootstrap succeeded, not disproved. There are
no delegated or delayed runs to reconcile.

Preserve all three blocks' records and put the next theorem family in a new block.
The root package manifest remains an earlier release snapshot; use each
block's source-bound records for its exact claims. Block02's manifest retains
the earlier continuation-guide snapshot at its original checkpoint; Block03's
immutable source manifest excludes this live guidance file.
