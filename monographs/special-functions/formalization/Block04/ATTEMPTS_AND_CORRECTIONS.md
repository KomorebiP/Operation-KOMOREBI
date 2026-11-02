# Route and implementation notes for SF-LEAN-B04

The direct Taylor coefficient route was considered first. The vanishing-order
API gave a cheaper discriminator: scaling preserves lower order bounds, and
an order-n bound for a derivative gives an order-(n+1) bound for its function
when that function vanishes at zero. The
induction proves uniqueness without needing a dense coefficient representation.
The canonical series representation then follows by identifying the solution
germ with the existing recurrence sums.

The direct coefficient route is deferred for the remaining finite-jet inverse
step, not refuted. A local norm-contraction proof is also deferred; it is not
needed after the vanishing-order proof and could be revisited for quantitative
stability estimates.

The product-difference helper was written with separate derivative-output
functions and product-input functions. This prevents an incorrect reuse of
the U row's output/input alignment for the V row. The mathematical product
identity and both equation rows are checked in the final source.

Compiler corrections were limited to two warning-as-error issues: using a
direct simplification for the derivative of a linear scaling map, and marking
an intentionally retained analytic-context parameter as unused by the scaling
order proof. No mathematical hypothesis or conclusion changed to repair a gap.

The final source has no placeholder, custom axiom, unsafe construction or
native decision procedure. The placeholder fixture is isolated under
`lean/uniqueness_controls/` and must fail. The clean full replay binds the
accepted source, rather than treating scratch compilation as final evidence.
