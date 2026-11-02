# SF-LEAN-B04: analytic uniqueness and the Appendix F.1 contract

This block proves uniqueness of normalized analytic solution germs and
normalized entire solution pairs. Combined with the preceding existence,
coefficient and convergence results, `coupled_F1_contract` covers **Appendix
F.1 in the manuscript's ordinary odd-series formulation**: a unique normalized
entire pair, oddness, strictly positive real coefficients, the coefficient
recurrence, and convergent expansions on the whole plane.

For labeled real scales `0<q,r,a,b<1`, the solution satisfies

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz),\qquad U(0)=V(0)=0.
\]

Competing entire functions are not assumed odd or supplied with a coefficient
expansion. Their differential equations are expressed by actual `HasDerivAt`
statements at every point. This ensures complex differentiability and avoids
using a totalized derivative as a substitute for differentiability.

The new `lean/CoupledUniqueness.lean` contains **16 named theorem declarations**,
including supporting lemmas and the bundled correspondence contract. The
registered source scope contains 124 names: 39 in the inherited finite core,
29 in Block01, 21 in Block02, 19 in Block03, and 16 here. These are not 124
independent discoveries. The full analytic monograph remains incomplete.

## Germ uniqueness by vanishing order

Suppose `(f,g)` and `(F,G)` are analytic near zero, have the same initial
values, and solve the same coupled equations near zero for the same fixed
scale tuple. Put `h=f-F` and `k=g-G`. The derivative differences satisfy

\[
\begin{aligned}
h'(z)&=h(qz)g(rz)+F(qz)k(rz),\\
k'(z)&=h(az)g(bz)+F(az)k(bz).
\end{aligned}
\]

If `h` and `k` vanish to order at least `n`, scaling preserves that lower
bound and multiplication by analytic functions cannot lower it. The order
of a sum is at least the smaller summand order, so both derivatives vanish
to order at least `n`. Since `h(0)=k(0)=0`, the derivative-order theorem gives
order at least `n+1` for both differences.

Induction proves every finite order bound. Infinite analytic order means
local vanishing, so the pairs agree as germs. The zero-scale case is handled
directly by the zero initial value of the difference; it does not use an
inverse scale. Conditional germ uniqueness therefore holds for arbitrary
real scales, including zero and noncontracting scales. Strict positive
contraction is used when supplying the canonical entire solution from Block03.

For entire solutions, complex differentiability supplies global analyticity.
The analytic identity principle promotes equality near zero to equality on
the whole complex plane. The conclusion compares functions at a **fixed**
parameter tuple; it does not assert parameter identifiability across tuples.

## The reverse analytic-to-series bridge

For a normalized analytic solution germ under the manuscript's strict
positive scale hypotheses, `analytic_solution_germ_eq` identifies it with
the already constructed `(Scales.U, Scales.V)` germ. Consequently
`analytic_solution_hasSum` gives, near zero,

\[
f(z)=\sum_{n\ge0}u_nz^{2n+1},\qquad
g(z)=\sum_{n\ge0}v_nz^{2n+1},
\]

where `(u_n,v_n)` is exactly the unique Block01 recurrence sequence. Neither
parity nor a recurrence is an input premise on `(f,g)`. For an entire solution,
`entire_solution_hasSum` supplies these expansions at every complex point, and
`entire_solution_odd` supplies global oddness.

The exact Lean bridge is a canonical convergent `HasSum` representation.
Transport to every coefficient of a separate caller-supplied Mathlib
multilinear Taylor-series object remains an API task. In particular, the
analytic-germ parameter inverse of Appendix G.2 still needs the explicit
finite-coefficient extraction step; fixed-parameter solution uniqueness is
not a proof of that inverse.

## Main interfaces

- `analytic_pair_germ_unique`: local uniqueness with equal initial values,
  analytic germs and local differential equations, for any real scale tuple.
- `entire_solution_unique`: conditional uniqueness of normalized entire pairs.
- `coupled_entire_exists_unique`: existence and uniqueness under `0<q,r,a,b<1`.
- `analytic_solution_hasSum` and `entire_solution_hasSum`: canonical expansions
  of arbitrary analytic solution germs and entire solutions respectively.
- `coupled_F1_contract`: the complete stated ordinary-series F.1 correspondence.

See [CLAIM_MAP.json](CLAIM_MAP.json) for the exact scope and
[declarations.json](declarations.json) for all new names and the source hash.

## Verification and provenance

The source-bound execution is recorded in
[evidence/receipt.json](evidence/receipt.json). The replay checks all nine
dependency revisions, warning-as-error compilation and exact axiom inventories
for all four coupled modules, and same-kernel replay of those four modules.
Allowed logical axioms are only `propext`, `Classical.choice`, and `Quot.sound`.
Imported Mathlib is reused from the pinned cache rather than freshly replayed
from an empty environment. The finite projector core's 39-declaration record
is inherited.

Four negative fixtures must reject an incorrect origin normalization,
zero functions that fail the equations, a wrong initial recurrence coefficient,
and a placeholder proof. A positive fixture consumes the unique-solution and
series interfaces at the preserved rational example and checks conditional
uniqueness when all scales are zero.

The compiler remains native Windows Lean 4.34.0-rc2, with Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Five cached module artifacts
needed for `Mathlib.Analysis.Analytic.Order` were added using the pinned
Mathlib cache. No dependency revision changed. The public verifier itself
performs no installation or download.

```text
python tools/verify_coupled_uniqueness.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block04
```

Use a new work directory outside the release. `--packages` handles alternate
portable layouts; `--git` selects an explicit executable. Review is a
[focused self-review](SELF_REVIEW.md), not independent review. There is no
load-bearing numerical computation.

The base is `b479654cc33423e56e3dd81cd1f63f9e19efcf84`. Earlier blocks,
their guides and execution evidence, reading PDFs and manuscript sources are
preserved. The live continuation guide and dated release note are updated.
The immutable artifacts are bound by [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json),
which excludes mutable guidance and the current catalogue. Earlier manifests
retain their original checkpoint snapshots. No new complete archive release
or reconstruction of missing archive bytes is claimed.

## Phase closeout and next step

The vanishing-order route resolves germ and entire uniqueness and yields the
canonical series bridge. Direct dense Taylor coefficient extraction and the
local norm-contraction route were deferred after that success, not refuted.
The dense coefficient route remains relevant to the next inverse obligation.

Next: prove that equality of the two canonical analytic germs forces equality
of the six coefficients at degrees three, five and seven. Then apply the
existing degree-seven inverse with its positive-scale and nonzero-defect
hypotheses. Preserve the exceptional-locus collision and ordered labels.
Perron order/type growth and full component-rescaling equivalence remain
separate later formalization goals.
