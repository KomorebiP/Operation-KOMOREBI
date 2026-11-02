# SF-LEAN-B02: a local holomorphic solution of the coupled equations

This block proves the local analytic step of Appendix F.1 for the actual
coefficient sequences constructed in Block01. It adds **21 named theorem
declarations**, including supporting lemmas. Together with the preceding 29
coupled declarations and the 39-declaration finite core, the registered source
scope contains 89 names. These are not 89 independent discoveries, and the
analytic monograph is not fully formalized.

## Exact result

For labeled real parameters `0 < q,r,a,b ≤ 1`, define

\[
U(z)=\sum_{n\ge0}u_nz^{2n+1},\qquad
V(z)=\sum_{n\ge0}v_nz^{2n+1},
\]

using the recursively constructed `Scales.coefficients`. Lean proves that both
sums are complex differentiable on `‖z‖² < 2`, that both have value zero and
derivative one at the origin, and that throughout this disk

\[
U'(z)=1+U(qz)V(rz),\qquad V'(z)=1+U(az)V(bz).
\]

`coupled_local_solution` bundles the initial values and both `HasDerivAt`
statements. `coupled_differentiableOn`, `coupled_local_equations`,
`coupled_initial_derivatives`, and `coupled_odd` expose individual conclusions.
The coefficient normalization is ordinary Taylor coefficients, not derivatives
or exponential generating coefficients.

## Proof mechanism

For each point of the disk, choose `‖z‖ < R < √2`. Block01's majorant supplies
the uniform estimate

\[
|c_nw^{2n+1}|\le R(R^2/2)^n\quad (|w|<R).
\]

The right side is summable. The pinned Mathlib complex Weierstrass theorem
proves differentiability of the sum; its derivative-series theorem proves

\[
\sum_{n\ge0}(2n+1)c_nz^{2n}=\frac{d}{dz}\sum_{n\ge0}c_nz^{2n+1},
\]

as a `HasSum`, so convergence of the differentiated series is part of the
result. There is no premise assuming differentiability of the infinite sum.

Multiplication by a scale of norm at most one preserves the disk. Absolute
convergence therefore justifies the Cauchy product of the two contracted sums.
The product theorem explicitly identifies its degree `2*n+2` coefficient as
the finite convolution in the recurrence. Clearing the nonzero denominator
`2*n+3`, and splitting off the derivative series' `n=0` term, gives the two
equations. The first derivative term is one; the product begins at degree two.

The proof starts from the recursively defined sequences. It does not assume a
solution of the equations or replace those sequences by unspecified analytic
functions. The source, [declaration map](declarations.json), and
[claim map](CLAIM_MAP.json) fix the exact coverage.

## Verification and provenance

The fresh source-bound result is in [evidence/receipt.json](evidence/receipt.json).
Each command's output is retained with its SHA-256. The replay script checks
all nine dependency Git revisions, compiles the preceding coupled module and
this module with warnings treated as errors, checks every theorem's axiom
report against the exact declaration maps, replays both compiled modules with
`leanchecker`, and requires four negative fixtures to fail for their expected
diagnostics. The only allowed logical axioms are `propext`, `Classical.choice`,
and `Quot.sound`.

The negative controls assert the wrong origin value, the wrong initial
derivative, preservation of the disk by an expanding scale, and a placeholder
proof. Production sources contain none of those placeholders. The kernel
replay uses the same Lean kernel against cached imported dependencies; it is
not an independent proof checker or a fresh replay of all of Mathlib.

This execution uses native Windows Lean 4.34.0-rc2 and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The public Windows toolchain and
the pinned Mathlib cache were downloaded into a task-local tools directory.
This differs from Block01's offline Linux-kit restoration. The verifier
itself performs no download. `.gitattributes` preserves exact Special
Functions bytes so Windows line-ending conversion cannot invalidate the
source maps in a fresh checkout.

The mathematical review is a [self-review](SELF_REVIEW.md), not an independent
review. Block01 sources, declaration maps, progress records, and evidence are
preserved. The 39-declaration projector core is inherited from Block01's
verification; it is not freshly replayed by the Block02 command.

The imported README, Lean-status note, and finite-core guide are also preserved
at their frozen assessment hashes. The dated
[collection companion](../../../../docs/SPECIAL_FUNCTIONS_ANALYTIC_BLOCK02.md)
and `CONTINUE_HERE.md` give the current scope. Earlier checkout and diagnostic
failures are retained in [ATTEMPTS_AND_CORRECTIONS.md](ATTEMPTS_AND_CORRECTIONS.md).

The root `MANIFEST.json` and `SHA256SUMS` retain the earlier packaged-release
inventory. They are not a current repository-wide integrity certificate.
In particular, ten archive entries in that earlier inventory are absent from
the Git checkout, and the repository has additional imported supporting
sources. This block does not recover those archive bytes or claim a new full
archive validation. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) identifies
this block and its current entry-point files separately.

## Reproduction

Use an already populated environment at the pinned revisions and a new work
directory outside `monographs/special-functions`:

```text
python tools/verify_coupled_analytic.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block02
```

`--toolchain` contains `bin/lean` and `bin/leanchecker` (or `.exe` on Windows).
`--mathlib` is the pinned Mathlib Git checkout with populated build artifacts.
Its dependencies default to `MATHLIB/.lake/packages`; use `--packages` when a
portable kit stores the dependency checkouts together elsewhere. `--git`
accepts an explicit Git executable. No project-specific compiler paths are
required in the source.

## Remaining analytic work

This is a completed local phase, not an entire-solution theorem. The next
dependency is holomorphic extension from radius `R` to `R/Q` for strict
contractions `Q=max(q,r,a,b)<1`, including agreement on overlaps and preservation
of the equations. Then glue the radius ladder into entire functions.

Uniqueness among arbitrary normalized analytic solutions, the reverse
analytic-solution-to-coefficient bridge, the analytic-germ version of the
degree-seven inverse theorem, the Perron growth law, and full component
rescaling equivalence remain open formalization obligations. The case where
all four scales equal one is admitted by this local theorem and supplies no
entire-continuation conclusion.

The alternatives of sparse formal power-series packaging and a direct
derivative-majorant proof were deferred after the uniform-convergence route
proved the local target. They were not refuted or exhausted. See
[TARGET.md](TARGET.md) for the route decision and base checkpoint.
