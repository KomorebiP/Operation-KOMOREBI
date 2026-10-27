# Independent audit of the centered Dirac target

**Primary verdict: correct only after a stated restriction.**

Sections 3 and 4 establish the centered bounded operator, full graph-domain
limit, all-nonreal strong-resolvent limit, and exact-constant third-moment
rates. The compact-time *supremum* corollary needs `T ≥ 0` stated explicitly.
The other target statements are mathematically sound under their written
hypotheses. No claim here certifies unfinished Lean source.

## Revision and provenance

Reviewed the exact `source/generator/Block50_Spectral_Generator_Bridge.tex`
from `Komorebi_Physics_Open_Publication_Package.zip`, together with the
actual checked definitions in the Block 49 project and generator overlay.
File identities are recorded in `AUDITED_INPUTS.json`.

This is an independent subagent review of the raw claim and proof. The
reviewer did not author those arguments or the new formal modules. Review
agreement is not a proof certificate. No numerical experiment or fresh Lean
execution was performed for this review.

## Dependency graph

Clifford relations and modal Hermitian symmetry imply the exact square and
norm identities. Those identities give the uniform centered bound and the
modal difference identity. The existing maximal-domain characterization,
the sine bound, and dominated convergence then give the full graph-domain
limit.

Modal Hermitian invertibility away from the real axis, the uniform imaginary
part bound, and the coordinatewise inverse identities construct the global
resolvents. Their resolvent identity plus graph-domain convergence gives
strong-resolvent convergence.

The global cubic sine remainder and the difference norm identity give the
generator rate. A differentiated product of the two modal unitary groups
gives the propagator rate without commuting their distinct generators.
Square summability converts each modal bound to the infinite-space bound.
The existing Fourier equivalence transports those results to physical fields.

## Obligation matrix

| Obligation | Status | Evidence or boundary |
|---|---|---|
| Same complete coefficient space | Passed | Existing `CoeffL2` is a genuine `ℓ²` space over all integer modes. |
| Actual physical Fourier transport | Passed | Existing map is a surjective linear isometry, with coefficient correspondence. |
| Fixed nonzero spacing boundedness | Passed | Modal square is `(m²+Σq_j²)I`; `|q_j|≤1/|h|`. |
| Boundedness at zero spacing | Out of scope | Modal zero fill equals continuum `H`, which is unbounded globally. |
| Exact modal difference norm | Passed | Mass cancels; anticommutation eliminates all mixed terms. |
| Full graph-domain convergence | Passed | Squared errors dominated by `4|k|²‖f_n‖²`, summable on the actual maximal domain. |
| Two-sided punctured limit | Passed mathematically | `q_{-h}=q_h` or the two-sided removable sine limit; old one-sided Lean lemmas alone do not finish this target. |
| Resolvent existence for every nonreal `z` | Passed | Modal coercivity and finite dimension give inversion, with a uniform norm bound. |
| Continuum inverse lands in its domain | Passed | For `g=Rf`, coordinatewise `Hg=f+zg`; the right side is in `ℓ²`. |
| Resolvent identity sign and typing | Passed | `R_h f-Rf=R_h(H-H_h)Rf`, with the domain witness above. |
| Third moment supplies domain membership | Passed | `x²≤1+|x|⁶`, combined with existing `ℓ²` membership. |
| Sine constant and all real signs | Passed | Integrated remainder gives `|sin y-y|≤|y|³/6`; division uses `|h|`. |
| Propagator rate without false commutation | Passed | Differentiate `U_h(t-s)U(s)`, keeping operator order. |
| Negative time | Passed | Reverse integration limits or use a unit-interval parametrization with `|t|`. |
| Compact-time supremum | Conditional | Require `T≥0` explicitly; pointwise formulation is already sound. |
| Operator-norm resolvent convergence | Out of scope; false in general | Resonant high modes give the counterexample below. |
| Finite sampled-lattice interpretation | Out of scope | No sampling or interpolation theorem follows from a same-space multiplier limit. |
| Fresh formal certification | Not addressed | New Lean modules are still under development. |

## Independent critical derivations

For `Δ=Σ_j δ_j α_j`, Hermitian symmetry and anticommutation give
`Δ²=(Σ_j δ_j²)I`. Therefore `‖Δψ‖²=(Σ_j δ_j²)‖ψ‖²`. This works for
arbitrary spinors and does not require choosing eigenvectors or an invariant
one-dimensional subspace. Real mass cancels exactly in `H_h-H`.

For a Hermitian modal operator `A`, write `z=a+ib`. Expansion gives
`‖(A-z)ψ‖²=‖(A-a)ψ‖²+b²‖ψ‖²`. Thus `b≠0` makes `A-z` injective and,
in four dimensions, bijective. Its inverse has norm at most `1/|b|`.
Coordinatewise inverses applied to any `ℓ²` vector are therefore in `ℓ²`.
The continuum inverse belongs to the maximal domain because `Hg=f+zg`.
This independently verifies the unbounded-domain step rather than treating a
finite-mode inverse as a global inverse without summability.

Let `F(s)=U_h(t-s)U(s)`. The derivative is
`F'(s)=i U_h(t-s)(H_h-H)U(s)`, with that order retained. Integrating from
zero to `t` yields exactly the sign in the manuscript's Duhamel formula.
Both exterior factors preserve norm. The middle factor has operator norm
`sqrt(Σδ_j²)`, so no commutation of `H_h` and `H` is needed. For negative
`t`, the norm of the oriented integral uses `|t|`.

The first-order domain does not itself imply a third-order rate. The rate
statement must retain its explicit weighted-summability premise. In Lean,
a `tsum` is totalized, so defining a square root of that sum without requiring
summability would be an invalid replacement for finiteness.

## Strong convergence is not norm convergence

Take `m=0`, `z=i`, `h=1/N`, and the mode `n=(N,0,0)` for positive integer
`N`. The centered momentum is `sin(2π)/h=0`; hence the centered resolvent on
that mode is `iI`. The continuum modal resolvent has norm
`1/sqrt((2πN)²+1)`. Applied to a unit spinor in that mode, the resolvent
difference has norm at least
`1-1/sqrt((2πN)²+1)`, which tends to one.

This is a mathematical boundary example, not a newly executed finite test.
It explains why fixed-vector strong convergence is the correct target and
why allowing a test vector to depend on spacing would change the claim.

## Source checks and remaining gap

Read `AGENTS.md`, `CONTINUE_HERE.md`, `docs/SOURCE_MAP.md`, the Block 49 proof
guide, actual Fourier/operator/domain definitions, and the raw target proof.
The checked domain and Fourier statements match the mathematical objects
used in the target. No manuscript edits were made.

The remaining implementation gap is to compile the requested constructions
and conclusions with exactly these domains, quantifiers, constants and maps,
then audit their dependencies and execute discriminating controls. The most
important immediate checks are full versus one-sided spacing convergence,
nonzero-spacing boundedness, nonreal inverse/domain identities, and the
third-moment premise on the propagator rate.
