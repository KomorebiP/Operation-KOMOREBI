# Euler XXIII: spectral detection is not critical-value nonvanishing

**Operation Komorebi — 4 October 2026 (UTC)**

## Status and boundary

This release adds four mathematical Lean modules with 42 named theorem/lemma
declarations. The complete project contains 836 declarations in 91 modules.
Counts include helper lemmas and negative controls, not separately novel results.
All 87 incoming mathematical modules are byte-for-byte unchanged.

The new results are: exact Euler-defined scalar undepletion; finite spectral
Vandermonde separation; a proved counterexample to the proposed unrestricted
simplicity inference; the exact moving-critical-value calculation for a quadratic
jet; and a uniform finite spectral escape theorem for the ACTUAL infinite
depleted Euler packet sum. Two fresh-output complete Lean replays passed.

No new Euler root family, remaining critical scalar, universal simplicity result,
or numerical coverage extension is claimed. The counterexample is synthetic,
not an Euler residual. The full infinite epsilon-resolvent identity, together
with all differentiated interchanges, is not added as a Lean theorem here.

## 1. The exact undepletion relation

For m >= 1, use the existing arithmetic coefficients

\[
\beta_m=-\frac{2^{2m}(2m-1)B_{2m}}{(2m)!},
\qquad
\widehat\beta_m=(1-2^{2m-1})\beta_m.
\]

The zero-depth convention is separate: beta_0 = depleted beta_0 = 1. Every
residual statement below has r > 0, so only positive depleted indices occur.
Put epsilon = 2^(2r-1). Lean proves

\[
\frac{\beta_{r+q}}{\beta_r}
=
\frac{\widehat\beta_{r+q}}{\widehat\beta_r}
\frac{1-\epsilon}{1-\epsilon4^q}.
\]

Every denominator is proved nonzero from the actual rational definitions. The
statement lives first over Q and is compatible with its dyadic embedding.

For w(e,z)=(1-e)/(1-ez), with 1-ez nonzero, Lean proves, for every M >= 0,

\[
w(e,z)=1+\sum_{m=0}^{M-1}e^{m+1}z^m(z-1)
+\frac{e^{M+1}z^M(z-1)}{1-ez}.
\]

In particular,

\[
w(e,z)-1=\frac{e(z-1)}{1-ez},
\quad
w(e,z)-1-e(z-1)=\frac{e^2z(z-1)}{1-ez}.
\]

At z=4^q, q>0, the two differences have exact dyadic valuations 2r-1
and 4r-2+2q respectively. These valuation consequences were checked with exact
rational arithmetic; their scalar algebraic identities are kernel-checked.
At q=0 both differences are identically zero.

**Lean:** `UndepletionAlgebra.lean`, especially
`eulerBeta_undepletion_ratio` and `spectralWeight_finite_expansion`.

## 2. What Vandermonde separation actually proves

For distinct nodes z_i not equal to 1, form the matrix

\[
M_{i,m}=(z_i-1)z_i^m,\qquad 0\le i,m<s.
\]

The orientation is packet rows, correction-order columns. It is a diagonal
matrix times the classical Vandermonde matrix. Lean proves

\[
\det M=\prod_i(z_i-1)\prod_{i<j}(z_j-z_i)\ne0.
\]

Hence, if all s moments of a fixed amplitude vector vanish,

\[
\sum_i(z_i-1)a_i z_i^m=0\quad(0\le m<s),
\]

then every a_i vanishes. Applying this separately to values and slopes proves
the fixed-argument, finite-vector separation theorem.

For ordered positive packet indices q_i and z_i=4^(q_i), elementary factorization
gives

\[
v_2(\det M)=2\sum_{i=0}^{s-1}q_i(s-1-i).
\]

This specialized valuation formula is exact-tested in this release; the Lean
module proves the generic determinant and injectivity statements. The underlying
Vandermonde identity is classical and is imported from mathlib, not presented
as a historical novelty.

**Not implied:** a single epsilon-weighted sum being zero does not force all its
spectral coefficients to vanish. A moving critical point also changes the packet
value and slope vectors. Those changes are not covered by fixed-argument
Vandermonde injectivity.

**Lean:** `SpectralSeparation.lean`.

## 3. Exact counterexample to the proposed unrestricted inference

Use the SAME scalar weight w(e,z) as above and define rational polynomials

\[
p_1(x)=\frac{31}{84}(15x^2-254x+1001),
\]
\[
p_2(x)=-\frac{127}{84}(3x^2-62x+245),
\]
\[
F(e,x)=1+w(e,4)p_1(x)+w(e,16)p_2(x).
\]

Lean proves exactly

\[
F(0,x)=x^2,\qquad F(8,x)=(x-8)^2.
\]

Both p_1 and p_2 have nonzero discriminant and have no critical zero over any
characteristic-zero nontrivially normed field. The constant packet 1 is a unit.
The observation matrix at nodes 4 and 16 is invertible. Nevertheless there is a
double root at parameter 0 and another double root at the nonzero dyadic
parameter 8. Its location changes from 0 to 8.

Moreover, the first spectral VALUE correction at the original critical point is

\[
3p_1(0)+15p_2(0)=-4448\ne0.
\]

Thus even a nonzero first value correction, not only a nonzero slope correction,
is insufficient without a strict error comparison at the actual perturbed
critical point.

This is a **synthetic resolvent-weighted example, not an Euler counterexample**.
It does not satisfy the full Euler packet arithmetic, nor is that claimed.
Its role is to refute the inference based only on scalar resolvent structure,
individual simple packets, and spectral injectivity.

The Python audit also includes a separate same-center negative control for
arbitrarily small prescribed dyadic parameters epsilon=2^N, 1<=N<=20. It does not
supply a new universal Euler statement.

**Lean:** `CriticalPerturbationJets.lean`, including
`spectralProbe_critical_at_zero`, `spectralProbe_critical_at_eight`,
`spectralProbe_first_defect_nonzero`, and the two packet-squarefreeness lemmas.

## 4. The correct local invariant includes motion of the critical point

Consider the exact quadratic jet model

\[
Q(e,y)=ay^2+e(by+c)+e^2d,\qquad a\ne0.
\]

Lean proves that its actual analytic derivative vanishes at

\[
y_e=-\frac{eb}{2a},
\]

and that

\[
Q(e,y_e)=ec+e^2\left(d-\frac{b^2}{4a}\right).
\]

The correction -b^2/(4a) is precisely the term lost if one evaluates only at the
old critical point. The model has a critical zero there if and only if this
computed scalar is zero.

For a general analytic deformation

\[
F(e,x)=f(x)+eg(x)+e^2h(x)+\cdots
\]

with f(alpha)=f'(alpha)=0 and f''(alpha) nonzero, the formal second-order
calculation gives

\[
x(e)=\alpha-e\frac{g'(\alpha)}{f''(\alpha)}+O(e^2),
\]
\[
F(e,x(e))=eg(\alpha)
+e^2\left(h(\alpha)-\frac{g'(\alpha)^2}{2f''(\alpha)}\right)+O(e^3).
\]

These last general analytic expansions are explanatory deductions. This release
formalizes the exact quadratic model, NOT a general parameterized implicit
function theorem or a universal radius/error estimate.

The compiled nonvanishing certificate is deliberately explicit. After locating
the actual critical point x_e and proving

\[
F(e,x_e)=eC+R,
\qquad |R|<|eC|,
\]

Lean concludes F(e,x_e) is nonzero. Neither the point nor the strict inequality
is assumed to follow from Vandermonde separation.

**Lean:** `quadraticJet_critical_iff`, `quadraticJet_drift_coefficient`,
`dominant_critical_value_nonzero`, `moved_value_certificate`.

## 5. A finite spectral escape theorem including ALL Euler packets

There is a stronger positive result than finite-face injectivity. Define, for
r>0 and m>=0,

\[
S_m(x)=\sum_{q\ge0}4^{mq}\widehat\Pi_{r,q}(x),
\]
\[
\widehat\Pi_{r,q}(x)
=8^q\frac{\widehat\beta_{r+q}}{\widehat\beta_r}
P_q(x)\mathscr A(x-q).
\]

This sum is constructed from the ACTUAL inherited source, packet polynomial,
and Bernoulli coefficients. It is a spectrally dilated DEPLETED residual, not
the original undepleted H_r.

Work first with its integral numerator. The q-th numerator packet has norm

\[
\left|4^{mq}8^q\widehat\beta_{r+q}P_q(x)\mathscr A(x-q)\right|_2
\le2^{-(2m+3)q}.
\]

Lean proves summability and the whole positive-packet tail bound

\[
\left|\sum_{q\ge1}4^{mq}8^q\widehat\beta_{r+q}
P_q(x)\mathscr A(x-q)\right|_2
\le2^{-(2m+3)}.
\]

The head is exactly widehat beta_r times the source. Its norm is

\[
|\widehat\beta_r\mathscr A(x)|_2
=|\beta_r|_2=2^{-(s_2(r)-1)}.
\]

Therefore, if s_2(r)<=2m+3, the entire positive-packet tail is strictly smaller
than the head. The full numerator has the head norm, and division gives

\[
\boxed{|S_m(x)|_2=1\quad\text{for all }x\in\mathbf Z_2.}
\]

Define

\[
M_r=\max\left(0,\left\lceil\frac{s_2(r)-3}{2}\right\rceil\right).
\]

The Lean natural-number expression is `(binaryDigitSum r - 2)/2`, with truncated
natural subtraction. It agrees with the displayed formula for r>0.

Hence

\[
\boxed{|S_{M_r}(x)|_2=1.}
\]

A corollary is also compiled: if S_0(x)=0, there exists m<M_r with
S_(m+1)(x) != S_m(x). Otherwise a finite telescoping induction would give
S_(M_r)(x)=S_0(x)=0, contradicting its unit norm.

Thus a depleted root cannot be invisible to all of the first M_r unweighted
spectral correction layers. This resolves the infinite-tail problem for
DETECTION, without relying on a finite active-face approximation.

Examples of the guaranteed number of spectral steps:

| s_2(r) | M_r |
|---:|---:|
| <=3 | 0 |
| 4 | 1 |
| 8 | 3 |
| 64 | 31 |
| 514 | 256 |

This is NOT a bound on wall-resolution depth. It does NOT prove a nonzero
critical value of the original epsilon-weighted undepleted residual.

**Lean:** `DepletedSpectralEscape.lean`, especially
`depletedSpectralValue_unit`, `depletedSpectralValue_escape`, and
`depletedSpectral_correction_detects_zero`.

## 6. Formal scope by module

| New module | What is proved | Not asserted |
|---|---|---|
| UndepletionAlgebra | Actual rational beta-ratio identity, finite correction formula and remainder | Full infinite resolvent/all-derivative interchange |
| SpectralSeparation | Generic determinant and fixed-point moment injectivity | Moving-root transversality |
| CriticalPerturbationJets | Exact jet critical value, analytic negative controls, strict norm-gap certificate | Automatic Euler-specific gap or critical-value nonzero |
| DepletedSpectralEscape | Actual infinite depleted packet convergence and finite spectral escape | Original Euler root simplicity |

The incoming v22 multiplicity ceiling and all its hypotheses remain unchanged.
No new classification of terminal 129, terminal 161, or any other outstanding
arithmetic progression is claimed. No historical-priority assessment is made.

## 7. Execution record

Input archive: `history/Komorebi_Euler_Lean_v22_2026-10-04.zip`.
Its 396-entry manifest passed, and its full 794-declaration baseline was compiled
and axiom-audited before this block. All 87 inherited mathematical source files
remain unchanged.

The final project passed two full clean replays. Replay B used a separate source
copy and fresh project output. The 836-declaration axiom audits agree exactly:

```
Classical.choice
Quot.sound
propext
```

All 93 final .olean files have matching hashes between replays. The mathematical
sources are unchanged from the hashes recorded before both runs.

Replay A: 261.570624 seconds. Replay B: 251.281466 seconds. These times exclude
runtime restoration and reuse the pinned Lean/mathlib dependency cache. The
compiler and its dependencies were not rebuilt or independently bootstrapped.

The exact standard-library Python audit passed 4,352 registered checks, including
288 actual undepletion ratios, 1,440 finite correction expansions, 1,280 exact
remainder valuations, 377 finite integer spectral-escape values, and the rational
negative controls. The complete ranges and counts are in
`evidence/spectral_exact_checks.json`. Bounded tests are supporting checks;
universal statements above follow from Lean proofs. Earlier conversational
quick-test counts are not reproduced or adopted as new execution evidence.

Development failures were import-path shadowing, finite geometric-sum rewrite
issues, determinant-product syntax, derivative coercions, and linter/API issues.
They were corrected before both final replays. Diagnostic logs are retained.
The proposed unrestricted simplicity inference was mathematically refuted by the
synthetic example; it was not silently weakened into a success flag.

## 8. Next mathematical target

The next invariant should be the moving critical value, not merely a vector of
fixed-point spectral observations. For each actual quadratic Euler core:

1. Construct the critical-point continuation with an explicit local radius.
2. Compute the motion-corrected critical-value coefficients.
3. Bound every higher spectral layer and the critical-point substitution error.
4. Prove a strict valuation gap for the actual Euler coefficients, or identify an
   exact critical zero if the gap fails.

The spectral escape theorem guarantees that the packet decomposition contains
detectable information. It does not guarantee that this information is
transverse to motion along the repeated-root locus. That is the unresolved bridge.

## Sources and dependencies

The substantive inherited mathematical source is the v22 archive retained in
`history`. The baseline replay rechecks it in the current pinned environment.
The classical Vandermonde identity and moment-injectivity theorem are imported
from `Mathlib/LinearAlgebra/Vandermonde.lean`, pinned at mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
Current API documentation: https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Vandermonde.html

The exact source, axiom, command, and compiled-output receipts take precedence
over prose counts. See `PROVENANCE.json`, `RELEASE_STATUS.json`, and `evidence`.
