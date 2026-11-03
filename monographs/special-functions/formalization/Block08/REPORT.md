# SF-LEAN-B08: positive-real values and lower comparisons

This block establishes the positive-real foundations and lower recurrences
used in Theorem F.2. For the canonical pair with 0<q,r,a,b<1, the complex
values on the real axis are identified with actual convergent real series.
On R>=0 those real values are nonnegative, are at least R, and are strictly
increasing. Their real derivative equations are checked. The maximum complex
norm on each radius is attained at the nonnegative real point and equals the
corresponding real value.

The lower product recurrences hold already for R>=1:

\[
\begin{aligned}
U_{\mathbb R}(R)&\ge U_{\mathbb R}(q(R-1))V_{\mathbb R}(r(R-1)),\\
V_{\mathbb R}(R)&\ge U_{\mathbb R}(a(R-1))V_{\mathbb R}(b(R-1)).
\end{aligned}
\]

Their logarithmic forms hold for R>1. With m=min(q,r,a,b)>0 and
B=1+2/m, all four child radii are at least two whenever R>=B. The stronger
R>=1 product range does not remove the R>=B condition needed for the later
growth propagation.

The new source has **22 named theorem declarations**, including supporting
lemmas. The registered scope is **201 names**: the inherited 39-name finite
core and 29,21,19,16,13,19,23,22 in Blocks01 through 08. The explicit lower
type bound, upper type bound, radial exponent limit and type-vector
proportions remain open. This block does not complete F.2.

## The real-valued interpretation

Define UReal(x)=Re(U(x)) and VReal(x)=Re(V(x)), with x embedded into the
complex field. Mapping the actual complex HasSum expansions by the continuous
real-part map gives the corresponding real HasSum statements for every real
x. Mapping those real series back into the complex field and using uniqueness
of their sums proves

\[
U(x)=UReal(x),\qquad V(x)=VReal(x)
\]

as identities with the real values embedded into the complex field. The
identification holds for all real x, including negative x. Nonnegativity and
the one-sided lower bound use x>=0. Each real series term is then nonnegative;
retaining its degree-one term, whose coefficient is one, gives UReal(x),
VReal(x)>=x. At x=0 both values are zero.

Restricting the existing actual complex derivatives to the real axis gives

\[
UReal'(x)=1+UReal(qx)VReal(rx),\qquad
VReal'(x)=1+UReal(ax)VReal(bx).
\]

Real-axis identification is used before taking the real part of the products.
The proof never introduces an order on the complex field. The derivatives
are at least one on x>=0, so the two real functions are strictly increasing
there. Their logarithms are strictly positive for x>1.

## Maximum modulus at the positive point

For every z with norm(z)<=R, positivity of the coefficients gives a termwise
norm bound by the real series at R. The actual complex and real HasSum
representations transport that bound to norm(U(z))<=UReal(R), and similarly
for V. At the point z=R>=0, real-axis identification and nonnegativity give
equality of the norm and the real value.

`maximum_modulus_real_axis` states this as an `IsGreatest` assertion for the
image of the sphere under the real-valued norm. Thus existence and attainment
of the maximum are part of the theorem. The result includes R=0. A negative
radius is not supplied as a maximum-modulus domain.

## Final-unit-interval comparison

The implementation uses a real mean-value theorem, rather than an integral
API. On [R-1,R], with R>=1, monotonicity and nonnegativity bound each product
in the derivative below by its value at the left endpoint. The derivative
comparison theorem therefore gives

\[
UReal(R)-UReal(R-1)\ge UReal(q(R-1))VReal(r(R-1)).
\]

Dropping the nonnegative UReal(R-1) yields the displayed product recurrence.
The second row uses the same argument with output VReal and scales a,b.
This proves exactly the needed inequality without claiming an integral
identity as an additional formalized interface.

For R>1, all child radii and both real function values there are strictly
positive. Applying monotonicity of the real logarithm and its product law
gives the logarithmic recurrences. Separately, R>=1+2/m implies
m(R-1)>=2; the four scale lower bounds then give all four child-radius
bounds. The threshold endpoint is included.

## Interfaces and correspondence

- `real_series_hasSum`, `real_axis_identification`: real expansions and their
  complex embeddings, for every real argument.
- `real_axis_zero`, `real_axis_nonneg`, `real_axis_lower_linear`: origin,
  nonnegativity and the linear lower bound.
- `real_axis_hasDerivAt`, `real_axis_differentiable`,
  `real_axis_deriv_ge_one`, `real_axis_strictMono`, `real_axis_log_positive`:
  actual derivatives and ordered positive-axis consequences.
- `complex_norm_le_real_axis`, `real_axis_norm`, `maximum_modulus_real_axis`:
  norm comparison and attained maxima on every nonnegative radius.
- `unit_shift_lower_from_deriv`, `real_axis_unit_lower`,
  `real_axis_log_unit_lower`: the comparison mechanism and both canonical rows.
- `minScale_bounds`, `minScale_positive`, `lowerThreshold_gt_one`,
  `lower_child_radii`: the exact threshold and its child radii.

The exact manuscript locator is the positivity paragraph and final-unit-
interval comparison in `monograph/sections_v11/coupled_growth_full.tex`,
Theorem F.2. [CLAIM_MAP.json](CLAIM_MAP.json) records the hypotheses and
remaining gap; [declarations.json](declarations.json) binds all new names.

## Verification and file I/O

The source-bound [receipt](evidence/receipt.json) contains **39 steps**:
version, nine package revisions, warning-as-error compilation and exact axiom
audits for eight coupled modules, same-kernel replay of those modules, four
rejection controls and one positive fixture file. The fresh coupled audit
covers 162 declarations; the finite core's 39-name evidence is inherited.
Only propext, Classical.choice and Quot.sound are allowed logical axioms.
Imported Mathlib is reused from the pinned cache, rather than freshly rebuilt
or replayed. No load-bearing numerical experiment is used.

The controls reject applying norm equality at a negative radius, replacing
the unit threshold R>=1 by R>=0, claiming child radii >=2 without the B
threshold, and a placeholder. These are checked interface rejections, not
blanket counterexample theorems for every possible unguarded variant. The
positive fixture consumes the real embedding, lower bound at R=2, closed-ball
norm bound, the attained maximum at R=0, the unit recurrence at R=1, the log
recurrence at R=12, and the exact worked threshold B=11 and its child radii.

```text
python tools/verify_coupled_positive_real.py --toolchain /path/to/toolchain --mathlib /path/to/mathlib --work /path/to/new/sf-block08
```

Use a new external work directory. --git and --packages support portable
layouts. The public verifier neither installs nor downloads dependencies.
Lean remains 4.34.0-rc2 and Mathlib remains
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`; the derivative and mean-value
imports were already cached. [IO_MANIFEST.json](IO_MANIFEST.json) records
actual input and output hashes and generated object hashes with their
unbundled status. [SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) seals immutable
records, the dated guide and all replay inputs. Review is
[self-review](SELF_REVIEW.md), not independent review.

## Phase closeout and continuation

Base: `13e65505a1ce2de3ece418b22b93b38811573207`. Cutoff and assessment are
the same SF-LEAN-B08 source-bound checkpoint. Earlier proof blocks, records,
guides, manuscripts and reading PDFs are preserved. Current source, I/O,
catalogue and continuation files are updated; no complete archive release
is claimed. The [Block07 closeout](../Block07/REPORT.md) retains the exponent,
eigenvector and spectral prerequisites and earlier deferred alternatives.

The real-restriction/mean-value route resolves this block's target. An FTC
proof remains deferred if future integral estimates need its interface.
A direct coefficient/binomial proof remains deferred if later all-degree
shift estimates need it. Neither alternative is refuted or exhausted.

Next: prove the explicit lower comparison with C=Q/(1-Q),
c_minus=log(2)/(B+C)^rho, and the normalized characteristic vector. This
requires the seed interval, the shifted child-radius inequality and the
finite descent/interval induction from the manuscript. Upper type bounds,
the radial exponent limit and type-vector proportions remain later steps.
Operator decoupling and full monograph coverage also remain open.
