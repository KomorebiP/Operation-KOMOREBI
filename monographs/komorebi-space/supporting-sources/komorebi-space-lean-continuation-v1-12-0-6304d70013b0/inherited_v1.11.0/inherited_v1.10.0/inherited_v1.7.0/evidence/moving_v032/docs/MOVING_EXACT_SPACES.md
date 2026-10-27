# Komorebi Space: controlled motion of exact realization spaces
## Focused verified block v0.32.0 — Komorebi P.

## 1. Scope and connection to earlier work

The earlier robustness theorem derived equality of kernels from an exact
old-kernel-preservation hypothesis and a strict perturbation radius. This block
allows the kernel itself to move. It proves a two-sided projector-motion theorem,
derives the new residual certificate for small perturbations of a split-surjective
defect, constructs a continuous linear equivalence of the two exact spaces, and
connects the bounds to the actual v0.30 two-stage quantitative-descent repair.

The source and its real Hilbert inner product remain fixed. The compared defect
operators have the same target normed space. No claim of rank stability follows
from norm closeness alone. All maps below are the original
`HilbertKernelProjection.projection` and `ResidualRobustness.Bound` constructions.
This project is a focused source closure, not a replacement for the historical
stack, atlas, or multiscale-synthesis repository.

## 2. Two-sided certificates imply projector motion

Let E be a real Hilbert space and R a real normed space. Let D,D':E->R be
continuous linear. Put q=P_{ker D}, q'=P_{ker D'}. Suppose the two independently
proved residual estimates are

\[
 \|x-qx\|\le C\|Dx\|,\qquad
 \|x-q'x\|\le C'\|D'x\|,\qquad C,C'\ge0.
\]

If ||D-D'|| <= epsilon, the theorem proves

\[
 \boxed{\|q-q'\|\le\max(C,C')\epsilon.}
\]

Neither inclusion of kernels is assumed. E need not be finite-dimensional; R
need not be complete for this comparison. There is no smallness threshold when
both constants are already supplied. The estimate may be uninformative if the
constants are large.

The proof first controls new exact vectors by C*epsilon and old exact vectors by
C'*epsilon. A Hilbert duality argument transfers one of these estimates to the
opposite orthogonal complement. Writing

\[
 (q-q')x=q(I-q')x-(I-q)q'x
\]

separates orthogonal components. Their squared norms are bounded using the
orthogonal decomposition x=(I-q')x+q'x. This gives the maximum coefficient, not
the sum. The sharper constant is a theorem about operators, not a finite sample.

For a fixed nonnegative M, the class of models satisfying a residual bound with
constant M carries its inherited operator metric. The map D |-> P_{ker D} is
proved `LipschitzWith M`, and hence continuous, on that class.

The code also proves

\[
 \|qx-q'y\|\le\|x-y\|+\max(C,C')\epsilon\|y\|,
\]

and

\[
 |\|x-qx\|-\|x-q'x\||\le\max(C,C')\epsilon\|x\|.
\]

**Source:** `MovingKernelBounds.lean`, especially `projection_motion`,
`projection_opNorm`, `projection_lipschitz`, `repaired_input_motion`, and
`distance_motion`.

## 3. Derive the new certificate in a split-surjective regime

Now R is Banach. Suppose A:R->E is a continuous linear right inverse of D,

\[
 DA=I_R,\qquad\|Ar\|\le a\|r\|,\qquad a\ge0.
\]

Assume ||D-D'|| <= epsilon, epsilon>=0, and a*epsilon<1. Define

\[
 T=(D-D')A,\qquad D'A=I_R-T.
\]

The source proves ||T||<=a*epsilon<1. Mathlib's geometric-series construction
`Units.oneSub` supplies the actual continuous inverse Z=(I_R-T)^{-1}. This is a
proved Neumann inverse, not a certificate field asserting invertibility. Set

\[
 \boxed{A'=AZ.}
\]

The checked identities and estimate are

\[
 D'A'=I_R,\qquad
 \|A'r\|\le\frac{a}{1-a\epsilon}\|r\|.
\]

An exact competitor x-A'D'x and the best-approximation theorem supply

\[
 \boxed{\|x-q'x\|\le\frac{a}{1-a\epsilon}\|D'x\|.}
\]

Thus D' is surjective and has closed range. Combining the two-sided comparison
with the old right-inverse bound gives

\[
 \boxed{\|q-q'\|\le\frac{a\epsilon}{1-a\epsilon}.}
\]

For a measured residual y with ||D'x-y||<=eta,

\[
 \|x-q'x\|\le\frac{a}{1-a\epsilon}(\|y\|+\eta).
\]

The conclusion is now proximity to the NEW exact space, not the reference space.
The uncertainty radius is still a mathematical input to certify.

**Source:** `SplitKernelPerturbation.lean`.

### Derive A instead of supplying it

For a surjective Hilbert-source map D, the restriction

\[
 D|_{(\ker D)^\perp}:(\ker D)^\perp\longrightarrow R
\]

is proved bijective and made a continuous linear equivalence by the bounded
inverse theorem. Its inverse, followed by inclusion, constructs A. An existing
`ResidualRobustness.Bound D` with constant C proves ||Ar||<=C||r||.

Accordingly, the user-facing interface requires only surjectivity of D, its
reference residual bound, norm error <= epsilon, and C*epsilon<1. The right
inverse, new certificate, and moving-kernel equivalence are derived.

This is a substantive surjectivity condition. It must not be applied to a
redundant, non-surjective residual map without an appropriate factorization or
additional evidence. The two-sided theorem above does not require surjectivity.

**Source:** `SurjectiveKernelMotion.lean`.

## 4. Explicit transport between the moving exact spaces

Define the splitting retractions

\[
 R_0=I-AD,\qquad R_1=I-A'D'.
\]

The source constructs

\[
 J:\ker D\simeq_L\ker D',\qquad
 Jx=x-A'D'x,
\]

with inverse

\[
 Jy\text{ reversed by }y\longmapsto y-ADy.
\]

More precisely, the inverse is R_0 restricted to ker D'. The proof verifies
R_0 A'=0 and R_1 A=0, then both inverse identities on the appropriate kernels.
The displacement satisfies

\[
 \|Jx-x\|\le\frac{a\epsilon}{1-a\epsilon}\|x\|.
\]

This comparison depends on the chosen splitting A. It is not generally the
orthogonal projection q' restricted to ker D, and neither R_0 nor R_1 is claimed
orthogonal for an arbitrary supplied A. The q,q' in the motion theorem are always
the canonical orthogonal projections for the declared Hilbert geometry.

**Source:** `SplitKernel.Certificate.kernelEquiv`, `kernel_transport_error`.

## 5. All-real moving-line example and exact motion norm

In Euclidean R^2, take

\[
 D_t(x,y)=x+ty,\qquad t\in\mathbb R.
\]

The kernel is the line {(-tb,b):b in R}. Its actual projector is proved to be

\[
 q_t=\frac1{1+t^2}\begin{pmatrix}t^2&-t\\-t&1\end{pmatrix}.
\]

A common right inverse r |-> (r,0) gives residual gain <=1 for every t. The
operator uncertainty satisfies ||D_s-D_t||<=|s-t|, hence the generic theorem
proves ||q_s-q_t||<=|s-t|.

The exact comparison to t=0 is stronger:

\[
 \boxed{\|(q_t-q_0)x\|^2=\frac{t^2}{1+t^2}\|x\|^2,}
\]

\[
 \boxed{\|q_t-q_0\|=\sqrt{\frac{t^2}{1+t^2}}.}
\]

The operator norm is proved with an all-vector identity and a unit-vector witness.
This is not inferred from sampled slopes.

For |t|<1, every field of the general split certificate is instantiated. Its
actual kernel equivalence has the formula

\[
 J_t(0,b)=(-tb,b).
\]

For nonzero t, (0,7) is old-exact but no longer new-exact. The new nonzero exact
vector (-7t,7) exists. Orthogonal projection instead sends (0,7) to
(-7t/(1+t^2),7/(1+t^2)); these are different choices with different preservation
properties.

The same q_t is proved to be the existing quantitative-descent repair with local
operator zero and overlap operator D_t. Thus its motion formula applies to that
actual two-stage interface. This example has a trivial first stage; the general
bridge below permits both stages to be nontrivial and to vary.

**Source:** `MovingKernelExamples.lean`.

## 6. Connection to the existing quantitative-descent theorem

Keep one raw local candidate Hilbert space E, including its chosen norm. Compare
(D,C) with (D',C'). Each system must have closed local range and closed overlap
range restricted to its own locally exact space:

\[
 \operatorname{ran}D,\quad\operatorname{ran}(C|_{\ker D}),\quad
 \operatorname{ran}D',\quad\operatorname{ran}(C'|_{\ker D'}).
\]

The existing v0.30 theorem supplies actual joint residual bounds G,G'. If
||D-D'||<=epsilon_D and ||C-C'||<=epsilon_C, then

\[
 \|\Delta-\Delta'\|\le\max(\epsilon_D,\epsilon_C),
 \qquad\Delta=(D,C).
\]

The target product retains its maximum norm. For the actual two-stage repairs,

\[
 \boxed{\|P_{D,C}-P_{D',C'}\|
 \le\max(G,G')\max(\epsilon_D,\epsilon_C).}
\]

There is also the simultaneous input-motion estimate. The new proof rewrites
with the old `repair_eq_projection` theorem; it does not introduce a replacement
notion of descent. It compares raw realization families in a common ambient
space, not values in unrelated view doctrines. No new weighted-cover norm or
unknown-connection estimator is supplied.

**Source:** `MovingDescent.lean`.

## 7. Boundaries and negative results

The general theorem `lost_exact_unit_forces_gain` states: if a unit old exact
vector x is orthogonal to the new kernel (q'x=0), and ||D-D'||<=epsilon, every
new residual certificate C' satisfies 1<=C'*epsilon. Thus deleting exact
directions under small error forces the new gain to grow. One cannot retain
only the old gain and conclude projection continuity for arbitrary maps.

At the perturbation-radius endpoint, D=I on R, A=I, and D'=0 satisfy a=epsilon=1.
The new defect is not surjective. This is a proved counterexample to replacing
strict a*epsilon<1 by a*epsilon<=1 in the split construction.

The finite checker additionally tests the classic rank-changing matrix pair
D_0=diag(1,0), D_t=diag(1,t). Their projections differ by one for every nonzero t
while the map difference tends to zero. These finite checks supplement the
already formalized v0.26 boundary; they do not provide a new universal Lean
proof of that historical example.

No full rank-stratified perturbation theorem for arbitrary non-surjective maps,
nonlinear residuals, changed inner products, infinite graphs, arbitrary stack
metrics, or automatic statistical certification of epsilon is claimed.

## 8. Reproducibility, provenance, and established background

There are eleven production modules and the root: six unchanged dependencies
from v0.26/v0.30 and five additions. The lexical explicit declaration inventory
contains 151 named theorems and 47 constructions; the additions contain 61 and
28 respectively. Counts include auxiliary lemmas and type abbreviations.

The pinned runtime is Lean 4.34.0-rc2 and mathlib commit
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The compiler/kernel and imported cached
mathlib dependencies remain trusted, not rebuilt from source. All project
modules are recompiled in each clean run. The runtime is not included.

Projection geometry, Neumann inversion, and the bounded inverse theorem are
classical analysis. This release claims their checked integration with the
actual Komorebi residual-certificate, kernel, and quantitative-descent APIs, not
novelty for these analytic principles. Relevant pinned mathlib sources are
`Analysis/InnerProductSpace/Projection/Basic.lean`,
`Analysis/SpecificLimits/Normed.lean` (`Units.oneSub`), and
`Analysis/Normed/Operator/Banach.lean`.

The exact finite checker uses Fraction arithmetic and independent Gaussian
nullspace/Gram calculations. It checks 36 split perturbation systems, 324
candidate vectors and measurement cases, 17 moving-line slopes, and 32 rank-loss
witnesses. Rational Frobenius bounds are conservative. Universal Hilbert and
all-real conclusions are Lean proofs, not finite extrapolation.

Development failures and execution metadata are retained in audit/development.
The manifest validator is a project-local version-1 field/hash validator, not an
independent execution attestation. The delivery receipt distinguishes source
compilation, axiom audit, finite testing, and archive integrity.
