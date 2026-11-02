# SF-LEAN-B06: component-rescaling classification

This block proves Theorem G.1's component-rescaling equivalence and its
displayed scalar representation. For positive strict real contractions,
the canonical normalized entire pair admits nonzero complex constants A,B
with V(z)=A U(Bz) on the whole plane if and only if D=0, equivalently
q=b or qb=ar. The necessity direction allows arbitrary complex A,B.

The production source adds **19 named theorem declarations**, including
supporting lemmas. The registered scope is **156 names**: the inherited
39-name finite core, then 29,21,19,16,13,19 in Blocks01 through 06.
This count includes supporting results and bundled interfaces. Full analytic
monograph coverage remains open.

## Complex obstruction

The new complex-coefficient bridge embeds an ordinary odd series in a dense
scalar formal multilinear series, with zero even coefficients. Injective
HasSum reindexing and uniqueness of convergent expansions at zero identify
all coefficients. Absolute convergence from Block03 supplies the actual
canonical expansions. Multiplication by A and substitution z -> Bz give

\[
v_n=A u_n B^{2n+1}.
\]

At indices zero, one and two, normalization and the known coefficients give
AB=1, k=pB², and v₂=u₂B⁴. Hence D=k²u₂-p²v₂=0. This argument works over
the complex numbers and does not assume that A or B is positive or real.
Block01's exact real factorization identifies the two exceptional surfaces.
The coefficients are ordinary coefficients; no factorials are inserted.

## Constructive converse and scalar representation

Set S=sqrt(k/p)>0 and c=sqrt(S)>0. Define T(x,y) as the U component of the
canonical pair with scales (x,y,x,y). The two components coincide because
their recurrence rows are identical. Thus T is the unique normalized entire
solution of T'=1+T(xz)T(yz), T(0)=0. Uniqueness is stated with actual
HasDerivAt equations at every complex point.

On the exceptional surfaces the root identities are

\[
(a=S q,\ b=S r)\quad\text{or}\quad(b=q,\ a=S^2r).
\]

The effective scalar scales q and Sr both belong to (0,1). For the second
case (Sr)²=ar<1; for the first, Sr=b<1. The constructed pair is

\[
U(z)=c\,T_{q,Sr}(c^{-1}z),\qquad
V(z)=c^{-1}T_{q,Sr}(cz).
\]

The chain rule verifies the first coupled equation using c²=S. The second
equation matches the scalar factors either in their original order or in
the interchanged order. Both initial values are zero. Block04's normalized
entire uniqueness identifies the constructed pair with the canonical pair.
It follows that V(z)=S⁻¹U(Sz), supplying nonzero complex witnesses for the
existential statement.

## A full collision at zero defect

Scalar uniqueness also gives T(x,y)=T(y,x). Applied to the existing tuples
(1/4,1/2,1/4,1/2) and (1/2,1/4,1/2,1/4), this proves equality of both labeled
entire components, although the ordered parameter tuples differ. The earlier
finite-jet collision is therefore upgraded to a **full entire-pair collision**.
This is now a mathematical counterexample to removing the defect guard from
the germ inverse. It does not classify every cross-parameter collision.

## Interfaces and correspondence

- `rescaling_coefficient_identity`, `rescaling_forces_defect_zero`: complex
  rescaling and its coefficient obstruction.
- `scalarT_solution`, `scalarT_unique`: the normalized scalar entire solution.
- `reductionScale_surface`, `effective_scalar_scales`: real root identities
  and the admissibility of both effective scales.
- `coupled_scalar_representation`: the displayed G.1 representation, at every
  complex point, with S and c defined by positive real square roots.
- `canonical_component_rescaling`, `component_rescaling_iff_defect`,
  `component_rescaling_iff_surfaces`: the full functional equivalence.
- `scalarT_symm`, `boundary_entire_collision`: scalar symmetry and the
  strengthened collision.

The exact manuscript locator is Theorem G.1 in
`monograph/sections_v11/coupled_inverse_full.tex`. See
[CLAIM_MAP.json](CLAIM_MAP.json) and [declarations.json](declarations.json).

## Verification and file I/O

The fresh [receipt](evidence/receipt.json) binds all inputs by SHA-256 and
records **33 verification steps**: nine revision pins, version identification,
warning-as-error compilation and exact axiom audits for all six coupled
modules, same-kernel replay of those modules, four rejection controls and
one positive fixture file. The freshly audited scope is 117 declarations;
the finite core's 39-name evidence is inherited. Only propext,
Classical.choice and Quot.sound are permitted logical axioms. Imported
Mathlib is reused from its pinned cache, rather than freshly replayed.

The controls cover an absent reduction surface, the wrong odd rescaling
power, confusing sqrt(k/p) with k/p, and placeholder rejection. The positive
fixture distinguishes the two surfaces using examples lying on just one
surface each, checks the scalar representation and S=2, consumes the full
boundary collision, and rejects the normalized nonreal candidate A=-i,B=i
using its cubic coefficient. No numerical approximation is load-bearing.

[IO_MANIFEST.json](IO_MANIFEST.json) explicitly records replay input hashes,
output log and receipt hashes, generated object hashes and their packaging
status. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) seals the immutable
block records, dated guide and every replay input. Live continuation/release
guidance and generated catalogue pages are outside that immutable snapshot.

```text
python tools/verify_coupled_rescaling.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block06
```

The work directory must be new and outside the release. Explicit --git and
--packages options support portable local environments. The verifier neither
installs nor downloads dependencies. Lean remains 4.34.0-rc2 and Mathlib remains
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Review is a
[focused self-review](SELF_REVIEW.md), not independent review.

## Continuation

Base: `433fecf0b21011af7774fa41fde336e788949411`. Earlier blocks, their
records and dated guides, manuscript sources and reading PDFs are preserved.
Current source, proof correspondence, input/output records, catalogue and
continuation files are updated. No new complete archive release is claimed.
Cutoff and self-assessment refer to the same SF-LEAN-B06 source-bound
checkpoint; later results do not rewrite earlier evidence labels.

The [Block05 closeout](../Block05/REPORT.md) retains the inverse and coefficient
bridge, with its deferred derivative and tail-estimate methods. The
[Block04 closeout](../Block04/REPORT.md) retains F.1 uniqueness and its deferred
local norm-contraction method. These alternatives remain available if later
quantitative estimates require them; no old route is silently declared failed.

The direct scalar-construction route succeeded. Scaled-recurrence induction
and separate surface-symmetry constructions remain deferred alternatives,
not refuted approaches. The G.1 target is resolved. The next larger target
is the coupled Perron growth law: first establish an exact positive
characteristic-exponent contract and its dependencies, then prove the order
and type bounds. Operator decoupling and broader monograph coverage remain
separate obligations.
