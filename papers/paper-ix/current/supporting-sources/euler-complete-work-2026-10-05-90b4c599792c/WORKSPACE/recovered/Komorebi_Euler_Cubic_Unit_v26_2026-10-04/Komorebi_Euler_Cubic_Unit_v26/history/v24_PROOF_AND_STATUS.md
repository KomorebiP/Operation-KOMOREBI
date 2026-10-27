# Euler XXIV: the actual critical point and exact stationary precision

**Operation Komorebi — 4 October 2026 (UTC)**

## Status and boundary

Five new mathematical Lean modules add 42 named theorem/lemma declarations.
The cumulative project has 878 declarations in 96 modules. Counts include helper
lemmas and negative controls, not separately novel results. All 91 inherited
mathematical modules are unchanged. The complete v23 baseline and two fresh
v24 builds passed, including every transitive-axiom audit.

This release closes a specific gap in the quadratic case. The critical point
is constructed for an actual infinite restricted series, its displacement is
controlled, and its critical value has an exact motion-corrected expression.
Even more strongly, the error in evaluating that critical value at a trial point
is exactly the square of the observable half-slope norm.

The construction applies directly to the one-neighbor Euler core already
constructed in v22, with an even linear coefficient. With an odd linear
coefficient there is no critical point. The Euler-specific assertion that the
remaining critical scalar never vanishes is NOT proved. No complete new
terminal family, numerical coverage extension, or universal simplicity theorem
is claimed. Cubic cores and multiple-lower-residue cases retain their previous
boundaries. No historical-priority claim is made.

## 1. Actual analytic inputs

D is the genuine ring Z_2 and K is Q_2. Let R be an integral restricted series,
let a,b be in D, and let u be a unit in D. Define

\[
F(X)=a+2bX+uX^2+4X^3R(X).
\]

In this document b is HALF THE LINEAR COEFFICIENT. It is not the odd multiplier
of a terminal Euler wall. The actual-index examples use the name B for that
multiplier instead.

Define an integral series, without division in D,

\[
Q(X)=b+uX+2X^2(3R(X)+X R'(X)).
\]

Lean constructs both series, proves restrictedness and their evaluation formulas,
and proves that the genuine analytic derivative satisfies F'(x)=2Q(x).
The complete coefficient reduction is

\[
\bar Q=X+\bar b.
\]

The inherited restricted-series affine atlas therefore constructs a unique
c in Z_2 with

\[
F'(x)=0\iff x=c,
\qquad |c|_2=|b|_2,
\qquad |Q(x)|_2=|x-c|_2.
\]

No critical point is an input hypothesis. It is defined from the proved
existence-and-uniqueness theorem.

**Lean:** `QuadraticCriticalSeries.lean`, `QuadraticCriticalValue.lean`.

## 2. Exact critical-point motion and value

Put

\[
S(x)=3R(x)+xR'(x),\qquad \mathcal C=F(c).
\]

The critical equation is b+uc+2c^2S(c)=0. Lean proves the exact motion identity

\[
c+u^{-1}b=-2u^{-1}c^2S(c).
\]

Completing the square while retaining this motion gives

\[
\boxed{
\mathcal C=a-u^{-1}b^2+
4c^3\bigl(R(c)+u^{-1}cS(c)^2\bigr).
}
\]

Since every factor inside the last parentheses is integral,

\[
\boxed{
|\mathcal C-(a-u^{-1}b^2)|_2\le\frac14|b|_2^3.
}
\]

The exact critical-zero condition is

\[
(\exists x\in\mathbf Z_2:F(x)=F'(x)=0)\iff\mathcal C=0.
\]

Thus the strict certificate

\[
\boxed{|a-u^{-1}b^2|_2>\tfrac14|b|_2^3}
\]

rules out a repeated root everywhere on the normalized quadratic disc. For
nonzero b this can be written

\[
v_2(a-u^{-1}b^2)<2+3v_2(b).
\]

The norm statement includes b=0 and zero quantities without relying on the
implementation convention for the integer-valued valuation of zero.

**Lean:** `quadraticCriticalPoint_motion`, `quadraticCriticalValue_exact`,
`quadraticCriticalValue_error`, `quadraticCriticalValue_zero_iff`,
`quadraticCore_no_critical_of_gap`.

## 3. Exact stationary value precision

A stronger theorem holds at EVERY trial point x in Z_2:

\[
|F(x)-\mathcal C-u(x-c)^2|_2\le\tfrac14|x-c|_2^2.
\]

To prove it, apply the inherited first-order restricted-series remainder theorem
to X^3 R(X). The critical equation cancels the linear contribution exactly.
The remaining nonquadratic term is four times an integral second-order error.
Because u is a unit, strict ultrametric dominance gives

\[
\boxed{|F(x)-\mathcal C|_2=|x-c|_2^2=|Q(x)|_2^2.}
\]

Equivalently,

\[
|F(x)-\mathcal C|_2=4|F'(x)|_2^2.
\]

This is an exact norm identity, not an asymptotic expansion. It holds at c too,
where both sides are zero.

A certified half-slope residual Q(x) divisible by 2^k determines the critical
value from F(x) to precision 2^(2k). The evaluation of F(x) itself must have
that certified precision; a finite sampled equality is not a replacement.

In particular, if at ONE trial point

\[
\boxed{|F(x)|_2\ne |Q(x)|_2^2,}
\]

then the critical scalar is nonzero, and there is no critical zero anywhere
in the disc. Equality is inconclusive, not evidence of a double root.

When the exact scalar is zero, the converse geometric law is

\[
|F(x)|_2=|x-c|_2^2.
\]

This supplies an effective finite certificate once the value and slope norms
are known. It does not prove that every Euler instance passes the certificate.

**Lean:** `StationaryValuePrecision.lean`, especially
`quadraticStationary_value_distance`, `quadraticStationary_value_slope`,
`quadraticCore_no_critical_of_norm_mismatch`.

## 4. A quantified perturbation theorem, with the necessary relative scale

Let epsilon=4e, with e in Z_2. Let c0,c1,b1 be arbitrary integral values and let
R be any integral restricted series. Set

\[
a=4e c_0+16e^2c_1,\qquad b=2e b_1.
\]

The quadratic coefficient u remains an arbitrary unit. Thus

\[
F_e(x)=4e c_0+16e^2c_1+4e b_1x+ux^2+4x^3R(x).
\]

For the constructed actual critical point c_e, Lean proves

\[
\boxed{|F_e(c_e)-4e c_0|_2\le\tfrac14|e|_2^2
=4|\epsilon|_2^2.}
\]

If e is nonzero and |e|_2<|c0|_2, the leading critical value strictly dominates
all quadratic-motion and infinite-tail corrections. Consequently F_e has no
critical zero on Z_2.

In valuation notation the sufficient condition is

\[
\boxed{\epsilon\ne0,\quad v_2(\epsilon)>v_2(c_0)+2.}
\]

This is a pointwise universal theorem for any normalized integral tail. It does
not assert an analytic parameterization of every Euler wall. Before applying it
to an undepletion family, the exact normalization, the relative first-defect
bound and the integral remainder hypotheses must be established.

**Lean:** `quadraticPerturbation_critical_error`,
`quadraticPerturbation_no_critical`.

## 5. Why strictness is indispensable

The exact synthetic polynomial

\[
F_c(x)=(x-c)^2(1+4x)
\]

has a double root at c. It lies in the permitted core class:

\[
F_c(x)=c^2+2(2c^2-c)x+(1-8c)x^2+4x^3.
\]

With a=c^2, b=2c^2-c, u=1-8c,

\[
ua-b^2=-4c^3(1+c).
\]

For nonzero even c, v_2(b)=v_2(c), u is odd, and

\[
v_2(a-u^{-1}b^2)=2+3v_2(b).
\]

This is exactly the excluded boundary of the new strict-gap theorem.
The algebraic identities are checked in Lean; the finite exact audit checks
several such nonzero even c. This is a synthetic example, not an Euler
counterexample. The earlier v23 moving-root counterexample is preserved.

## 6. The actual one-neighbor Euler connection

Take the actual Euler-normalized residual, with j=j_r>=4. Let i<j be a
one-neighbor candidate center, with wall distance delta=d_i, and let F be its
constructed equal-slope half-core. The inherited exact identity is

\[
G_r(i+2^{k_i}Y)=2^{t_i+1}F(Y).
\]

The existing Euler coefficient theorem gives, for every n>=0,

\[
F_{n+2}=4^n\bigl(2(E_{n+1}+T_{n+1})+\varepsilon E_n\bigr),
\qquad E_0\text{ odd},\quad\varepsilon=\pm1.
\]

In particular, F_2 is odd and F_{n+3}=4\cdot4^n w_n for integral w_n.
If F_1 is even, Lean constructs its integral half b, the unit u=F_2, and

\[
R(X)=\sum_{n\ge0}4^nw_nX^n.
\]

It proves restrictedness and exact equality

\[
F(X)=F_0+2bX+uX^2+4X^3R(X).
\]

Thus the new critical point is defined for the actual Euler core. The theorem
`eulerOneNeighbor_movingCriticalValue` records the exact representation,
unique critical point, and equivalence of a critical zero with scalar zero.

If F_1 is odd instead, its derivative has complete reduction one and norm one
everywhere. There is no critical point. Combining the alternatives proves that
an actual one-neighbor core has at most ONE critical point, independently of
whether its critical value is zero.

A separate end-to-end chart theorem transports the strict norm-gap condition
to the original Euler residual with the power-of-two scaling retained. It is
conditional on that arithmetic gap, not an assertion that all gaps hold.

The same generic quadratic theorems apply on a further refined quadratic
frontier whenever its exact coefficient class is independently certified. The
new direct Euler construction above concerns one-neighbor equal-slope cores;
it does not automatically dispose of a two-neighbor cubic core.

**Lean:** `EulerCriticalValueBridge.lean`.

## 7. Fresh bounded arithmetic checks

The main standard-library audit checks 160 random integral polynomial tails
with fixed seed 20261004, 60 normalized perturbation cases, and 6 exact-double
negative controls. It also checks the finite Bernoulli evaluator against exact
rational Bernoulli numbers, and the constructed source against exact integer
values. The initial generic run passed 24,332 registered checks.

The extended run passed 25,102 registered checks. This total INCLUDES the
same generic tests; it is not 24,332 plus 25,102 independent checks. It includes
526 scalar-valuation comparisons, four actual terminal-index checks and eight
original finite-packet value comparisons.

Two preliminary terminal-17 probes on the ball 3+16Z_2 did not have the
anticipated content 16: their computed content was 14. They were retained as
rejected core selections and no moving-critical theorem or root conclusion
was assigned to them. They are not mathematical counterexamples.

Two actual terminal-129 representatives do produce the required quadratic
class. Their original indices are r=B*2^515-129 and their argument balls are:

| B | Argument ball | Removed content | v2(critical value) | v2(a-b^2/u) | Remainder lower bound |
|---:|---|---:|---:|---:|---:|
| 4045 | 7528+2^15 Z_2 | 147 | 2 | 2 | 11 |
| 44797 | 2920+2^15 Z_2 | 147 | 0 | 0 | 2 |

They were constructed from the original Bernoulli and source packet formulas
at 224-bit global precision. The positive gap confirms nondegeneracy in these
two normalized examples. These representatives were already covered by earlier
numerical work; this is a cross-check of the new invariant, not a new parameter
family classification.

A second implementation reconstructed both at 256-bit global precision, with
109 normalized coefficient bits and 108 critical-point bits. It used:

- a logarithmic source rather than the Newton-source construction;
- a Pochhammer rising-factorial packet scalar rather than a paired-factorial ratio;
- the opposite polynomial translation/localization algorithms;
- Newton critical-point lifting rather than bitwise Hensel lifting.

All full-coefficient and shared-precision comparisons passed: 1,808 separate
comparisons are recorded. The modular Bernoulli evaluator and generic polynomial
convolution are shared components. This is not fully independent Bernoulli
implementation. The original low-order Bernoulli tests do use exact rational
recurrence values.

The saved critical points are RESIDUES, not exact ordinary integers. A zero at
finite precision is never promoted to an exact zero. These numerical coefficient
certificates have not themselves been reconstructed inside Lean.

## 8. Formal execution and reproducibility

Input: `history/Komorebi_Euler_Spectral_Audit_v23_2026-10-04.zip`.
All 420 entries of its original manifest matched. Its full 836-declaration
baseline was recompiled and axiom-audited before the new development.

All 91 inherited mathematical modules are byte-for-byte unchanged. The five new
modules contain 602 lines including comments and formatting. The total count of
new named theorem/lemma declarations is 42.

Two clean v24 replays passed. Replay B used a separate source-tree copy and a
separate output directory. Both audited all 878 declarations. All 98 compiled
.olean outputs and all source hashes agree.

| Run | Seconds | Status |
|---|---:|---|
| Incoming v23 baseline | 254.377983 | PASS |
| v24 A | 273.212911 | PASS |
| v24 B, separate source copy | 275.898753 | PASS |

The two final replays ran concurrently; each Lean compiler process used one
worker and warnings-as-errors. Times exclude portable-runtime restoration and
reuse the pinned dependency cache. The compiler and mathlib were not rebuilt.

The transitive axiom union was exactly

```
Classical.choice
Quot.sound
propext
```

No custom mathematical axiom, unfinished proof, or native-evaluation proof axiom
appears. Source checks also reject those constructs before compilation.

Development diagnostics include an early missing-baseline-import failure,
proof-search timeouts in an overgeneral restriction tactic, API/coercion and
unused-simplifier errors, and a parenthesization correction around a conjunction
and an equivalence. All were repaired before both final clean replays. No failed
or interrupted development run is counted as a completed replay.

The generic count is not added twice. The secondary reconstruction count is
reported separately. Refer to `evidence/v24_*` for the new evidence; other
inherited evidence is retained with its original provenance in the source archive.

## 9. Remaining mathematical boundary

Closed in this release:

1. Construction of the actual critical point in the 4-divisible quadratic class.
2. Exact nonlinear critical-point displacement and critical-value formula.
3. Exact trial-value error in terms of the observable half-slope.
4. A quantitative perturbation nonvanishing theorem with explicit relative scale.
5. Construction of that class from actual one-neighbor Euler coefficients.

Still not proved:

1. The exact critical scalar is nonzero for EVERY admitted Euler instance.
2. The needed arithmetic gap in the remaining terminal-129 or terminal-161
   progressions, including after arbitrarily deep normalization.
3. A universal moving-critical-value analysis for all cubic or multiple-lower-root
   cases.
4. The full infinite undepletion resolvent with all parameter/derivative
   interchanges as a new formal theorem.
5. Universal dyadic Euler simplicity or algebraic squarefreeness.

The useful new reduction is quantitative: a trial point now supplies an exact
critical-value error through its half-slope. The remaining task is to establish
a nonzero value with a certified strict margin, not merely to detect spectral
information at a fixed point.
