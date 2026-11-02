# SF-LEAN-B03: entire existence under strict contraction

Base checkpoint: SF-LEAN-B02 at Git revision `db811c96` (the complete hash is
recorded in this block's progress record). Lean remains 4.34.0-rc2 and Mathlib
remains `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

Target: for the same labeled positive real scales with `q,r,a,b<1`, prove
that the existing recurrence sums `Scales.U` and `Scales.V` converge absolutely
at every complex point, are complex differentiable everywhere, and satisfy
both normalized coupled differential equations on the whole plane. Preserve
their initial values and odd symmetry. Ordinary coefficient `u_n` multiplies
`z^(2*n+1)`; there is no factorial renormalization.

This is the entire-existence part of Appendix F.1. Uniqueness among arbitrary
analytic solutions, the reverse coefficient bridge, the global Perron growth
law, and full component-rescaling equivalence are separate obligations.

Routes considered:

1. Construct primitives on `R/Q`, prove overlap agreement, and glue the radius
   ladder. The first uncertain step is the disk-primitive API and preservation
   of both equations after extension.
2. Use the absolutely convergent Cauchy product to bootstrap coefficient-series
   convergence outward. The decisive check is that the shifted series term is
   bounded by `norm(z)` times the norm of the finite Cauchy convolution, since
   the recurrence denominator `2*n+3` is at least one. An induction on the
   number of contractions should then reach every finite radius. The same sums
   define the extension, so overlap agreement needs no separate gluing choice.
3. Prove a direct super-geometric coefficient estimate from strict contraction.
   This needs a new explicit decay estimate and has a different asymptotic
   bottleneck from the summability bootstrap.

Route 2 is selected first. It reuses Block02's actual sums and Cauchy-product
algebra. The norm-one boundary is a discriminator: powers of `Q=1` do not
enter the initial convergence region, so the global target requires `Q<1`.

Completion requires compiled proofs, an exact theorem/axiom inventory,
same-kernel module replay, and diagnostic-checked negative controls. Existing
blocks and their source-bound evidence remain unchanged. Record failures as
proof-route failures, compiler/API corrections, or environment failures as
appropriate, rather than treating every failed tactic as a mathematical
obstruction.
