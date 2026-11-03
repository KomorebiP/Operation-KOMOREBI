# SF-LEAN-B03: entire existence for the coupled functions

This block proves the **entire-existence part of Appendix F.1**. For the same
labeled positive real scales with `q,r,a,b<1`, the existing recurrence sums
converge absolutely at every complex point, are holomorphic on the whole plane,
and satisfy both normalized differential equations there:

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz),\qquad U(0)=V(0)=0.
\]

The new module `lean/CoupledEntire.lean` contains **19 named theorem
declarations**, including supporting lemmas. The registered source scope is now
108 names: the inherited 39-declaration finite core, 29 in Block01, 21 in
Block02, and 19 here. This is not a count of independent discoveries.
Uniqueness among arbitrary normalized analytic solutions and the full analytic
monograph remain open formalization obligations.

## The extension mechanism

The proof uses the same functions `Scales.U` and `Scales.V` as Block02; it does
not introduce new piecewise extensions. Consequently the entire functions
agree with the previously checked local sums by definition.

For two coefficient sequences, let `C_n(z)` denote the finite degree-`2*n+2`
Cauchy convolution of their values at the two contracted arguments. The
recurrence gives the exact identity

\[
(2n+3)e_{n+1}z^{2n+3}=zC_n(z).
\]

Since `2*n+3 ≥ 1`, taking norms gives

\[
|e_{n+1}z^{2n+3}|\le |z|\,|C_n(z)|.
\]

Absolute convergence of the two contracted series implies summability of
`|C_n(z)|` by the normed-ring Cauchy-product theorem. The bound therefore
proves absolute convergence of the shifted new series. Adding its finite
initial term yields convergence of the whole series. This norm bootstrap
does not require positivity or a geometric estimate of the individual
coefficients; positivity is used in the inherited local starting bound.

Put `Q=max(q,r,a,b)<1`. Lean proves by induction on `n` that both series
converge whenever

\[
|z|Q^n\le1.
\]

At level zero, this follows from Block01's convergence on `|z|²<2`.
Multiplication by any of the four scales lowers one ladder level. For every
fixed complex `z`, the sequence `|z|Q^n` tends to zero, so some finite level
applies. This proves absolute convergence everywhere without constructing
primitives or making gluing choices.

For a fixed point, choose the larger real radius `R=|z|+1`. The absolute
coefficient series evaluated at `R` uniformly majorizes the terms on the
smaller ball. The complex Weierstrass theorem proves holomorphy, and its
derivative-series theorem supplies the actual convergent termwise derivative.
The exact finite convolution identity and the recurrence then prove the two
global differential equations, including their constant term.

## Public conclusions

- `coefficient_series_entire`: absolute convergence of both actual recurrence
  series at every complex point.
- `coupled_entire`: `Differentiable ℂ s.U ∧ Differentiable ℂ s.V`.
- `coupled_entire_equations`: both derivative identities everywhere.
- `coupled_entire_solution`: both initial values and both `HasDerivAt`
  equations at every complex point.

Odd symmetry remains the existing `coupled_odd` theorem, and the normalized
initial derivatives remain one. No old result is counted again as a new
theorem. The precise coverage is in [CLAIM_MAP.json](CLAIM_MAP.json), and all
new theorem names and the production source hash are in
[declarations.json](declarations.json).

## Verification

The source-bound result is recorded in [evidence/receipt.json](evidence/receipt.json).
The verifier checks all nine dependency revisions, warning-as-error compilation
and exact axiom reports for all three coupled modules, and same-kernel replay
of those modules. The allowed logical axioms are only `propext`,
`Classical.choice`, and `Quot.sound`. Imported Mathlib declarations are reused
from the pinned cache rather than freshly replayed from an empty environment.

Four deliberately invalid fixtures must be rejected: the radius-two ladder
claim with `Q=1`, a wrong first recurrence denominator, a wrong sign in the
initial derivative, and a placeholder proof. A separate positive fixture uses
the existing rational scales at `z=3+4i`, beyond the previous local disk, and
checks the global differential-equation interface.

The compiler is native Windows Lean 4.34.0-rc2, with Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06` and the same eight supporting
package pins. No new dependency download is needed for this continuation.
The mathematical review is a [self-review](SELF_REVIEW.md), not an independent
review. No numerical approximation or finite experiment is load-bearing.

```text
python tools/verify_coupled_entire.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block03
```

The work directory must be new and outside the release. For portable layouts,
`--packages` supplies the dependency-checkout directory and `--git` selects an
explicit Git executable. The script performs no installation or network access.

## Provenance and remaining work

The base is `db811c96832833ddd900e9a50437d02f838587ef`. Blocks01 and 02,
their Lean sources, their dated guides, and their execution evidence remain
unchanged. The reading PDFs and manuscript sources are unchanged. The current
continuation guide and dated release note are updated; Block02's manifest
binds their earlier bytes at its original checkpoint, rather than promising
that live guidance never changes. The current block has its own
[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json).

The root package manifest remains the earlier packaged-release inventory;
this block does not reconstruct absent archives or claim a new archive release.

The selected coefficient-bootstrap route resolves entire existence and the
global equations. The primitive/gluing route and the direct asymptotic
coefficient-bound route were deferred after this success, not refuted.
See [TARGET.md](TARGET.md) and
[ATTEMPTS_AND_CORRECTIONS.md](ATTEMPTS_AND_CORRECTIONS.md).

The next missing implication in Appendix F.1 is uniqueness among arbitrary
normalized analytic solutions. A useful route is to show that their Taylor
coefficients satisfy the established recurrence, then use coefficient
uniqueness and the analytic identity theorem. That reverse coefficient bridge
also unlocks Appendix G.2's analytic-germ parameter recovery. Perron growth and
full component-rescaling equivalence remain separate later obligations.
