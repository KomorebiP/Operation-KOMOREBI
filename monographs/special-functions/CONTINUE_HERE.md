# Continue Special Functions formalization

Current checkpoint: **SF-LEAN-B04**, based on repository commit
`b479654cc33423e56e3dd81cd1f63f9e19efcf84`. Start with
`formalization/Block04/REPORT.md`, then its claim map, declaration map,
self-review and source-bound execution receipt.

`lean/CoupledUniqueness.lean` adds 16 declarations proving analytic germ
uniqueness, normalized entire uniqueness, and the reverse canonical-series
bridge. `coupled_F1_contract` covers the principal Theorem F.1 statement in
the ordinary odd-series formulation: unique normalized entire pair, recurrence,
positive coefficients, expansions everywhere and oddness. The registered
source scope contains 124 names, including supporting lemmas and the preceding
108. The full monograph remains open.

The uniqueness proof raises every finite vanishing-order bound for the two
solution differences. Infinite order gives equality of germs; global analytic
identity gives equality of entire functions. The competitor is not assumed
odd or supplied with a coefficient recurrence. The reverse bridge is an
explicit canonical `HasSum` expansion.

Next executable step: prove that equality of two canonical analytic germs
forces equality of their coefficients at degrees three, five and seven.
Use power-series coefficient uniqueness or iterated derivatives; remember
that the kth derivative is k! times the ordinary degree-k coefficient. Then
apply Block01's positive-scale, nonzero-defect inverse. Keep ordered labels
and the exceptional-locus collision. Uniqueness at a fixed scale tuple is
not parameter injectivity across tuples.

Use `tools/verify_coupled_uniqueness.py` with Lean 4.34.0-rc2, Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and a fresh external work
directory. The native Windows environment now includes the five cached
artifacts needed for `Mathlib.Analysis.Analytic.Order`. Do not stop merely
because Lean is absent from PATH.

Direct coefficient extraction is deferred to the inverse step. The local
norm-contraction uniqueness route is deferred after the order proof succeeded.
Perron growth and full component rescaling remain separate later obligations.
There are no delegated or delayed runs to reconcile.

Preserve all four blocks' records and put the next theorem family in a new block.
The root package manifest remains an earlier release snapshot; use each
block's source-bound records for its exact claims. Block02's manifest retains
its earlier guidance snapshot; the later immutable manifests exclude this
live continuation file.
