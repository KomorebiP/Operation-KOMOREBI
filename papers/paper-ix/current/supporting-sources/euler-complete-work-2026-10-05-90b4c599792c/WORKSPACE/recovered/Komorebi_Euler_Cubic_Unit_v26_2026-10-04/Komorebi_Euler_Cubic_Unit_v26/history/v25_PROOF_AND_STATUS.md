# Euler XXV: cubic critical values from an inflection-centered jet

**Operation Komorebi — 4 October 2026 (UTC)**

## Status and exact boundary

This continuation adds 45 named theorem/lemma declarations in eight mathematical
Lean modules. The cumulative project contains 923 declarations in 104 modules.
The counts include helper lemmas and negative controls, not separately novel
results. All 96 incoming mathematical modules are byte-for-byte unchanged.
The 878-declaration baseline and two clean full 923-declaration replays passed.

The new result is a quantitative criterion for the ACTUAL infinite cubic class,
including the two-neighbor Euler cores constructed in v22. A unique inflection
point is constructed, and exact norm identities relate its value and slope to
every possible critical point. One norm mismatch at the inflection point rules
out all critical zeros on the core disc. A finite trial-jet version avoids
knowing the inflection point exactly.

This is a sufficient nondegeneracy test, NOT proof that every Euler instance
passes it. No new infinite multiplier family, terminal-degree coverage bound,
binary-complexity bound, or universal simplicity theorem is claimed. No
historical-priority assessment was performed.

## 1. Infinite cubic class and actual derivatives

Let D=Z_2, K=Q_2, and let R be an integral restricted series. Put

\[
F(X)=a+bX+cX^2+uX^3+4X^4R(X),
\qquad a,b,c\in D,\quad u\in D^\times.
\]

Letters a,b,c here are Taylor coefficients, not the integer multiplier of a
terminal wall. The numerical examples use B for that multiplier.

Lean constructs F as an actual restricted series, proves its evaluation formula,
and computes its first derivative. With

\[
S=4R+XR',
\]

its derivative is exactly

\[
F'(X)=b+2cX+3uX^2+4X^3S(X).
\]

S is integral restricted, and 3u is a unit. Therefore F' lies in the quadratic
class formalized in v24. All derivatives below are genuine analytic derivatives
over Q_2 evaluated at dyadic integers, not finite-difference substitutes.

**Lean:** `CubicCriticalSeries.lean`.

## 2. Generic integral remainder lemmas

For an arbitrary integral restricted series f, write J_d(f,x) for its evaluated
Hasse jet. The new proofs establish

\[
|f(y)-f(x)-(y-x)J_1(f,x)-(y-x)^2J_2(f,x)|_2
\le |y-x|_2^3,
\]

and

\[
|2(f(y)-f(x))-(y-x)(J_1(f,x)+J_1(f,y))|_2
\le |y-x|_2^3.
\]

The proofs first construct exact monomial remainders divisible by (y-x)^3.
The coefficients are integral; no division by a factorial is used to assert
integrality. The inherited summability results permit convergent summation of
these monomial identities. J_1 is already identified with the analytic derivative.

**Lean:** `SecondOrderRemainder.lean`, `TrapezoidRemainder.lean`.

## 3. Exact cubic trapezoid identity

For the cubic class in section 1, the stronger equality holds:

\[
\boxed{
|2(F(y)-F(x))-(y-x)(F'(x)+F'(y))|_2=|y-x|_2^3.
}
\]

The degree-zero through degree-two terms cancel. The cubic term is
-u(y-x)^3. The remaining term is four times an integral trapezoid error, of norm
at most one quarter of |y-x|_2^3. It cannot cancel the unit cubic contribution.
The zero-distance case is handled separately.

If x and y are both critical points, this gives

\[
\boxed{|F(y)-F(x)|_2=2|y-x|_2^3.}
\]

For distinct critical points,

\[
v_2(F(y)-F(x))=3v_2(y-x)-1.
\]

In particular, two different critical points cannot both be zeros of F. The
cubic core has AT MOST ONE critical zero, not necessarily zero critical zeros.

**Lean:** `cubicCore_trapezoid_norm`,
`cubicCore_critical_value_separation`, `cubicCore_critical_zero_unique`.

## 4. The unique inflection point is constructed

Apply the v24 quadratic critical-point theorem to F'. This constructs a unique
rho in Z_2 such that

\[
\boxed{F''(x)=0\iff x=\rho,\qquad |\rho|_2=|c|_2.}
\]

It is not a point supplied as an extra hypothesis. Define the exact inflection
data

\[
A=F'(\rho),\qquad C=F(\rho).
\]

The quadratic stationary-precision theorem, applied to F', yields

\[
\boxed{|F'(x)-A|_2=|x-\rho|_2^2.}
\]

The observable second Hasse jet measures distance to the same center:

\[
\boxed{|J_2(F,x)|_2=|x-\rho|_2.}
\]

Here J_2(F,x)=F''(x)/2. The division-free Hasse series is the formal object;
its equality to the scaled ordinary derivative is proved.

**Lean:** `CubicInflection.lean`, `cubicInflection_halfSecond_distance`.

## 5. Every possible critical value has a fixed norm relative to C

At any critical point alpha, write h=alpha-rho. The exact identities are

\[
\boxed{|A|_2=|h|_2^2,}
\qquad
\boxed{|F(\alpha)-C|_2=\tfrac12|h|_2^3.}
\]

For the second statement, set T=X^4 R and write the first- and second-order
Taylor errors of T as e1,e2. The equations F'(alpha)=0 and F''(rho)=0 give

\[
F(\alpha)-F(\rho)=-2u h^3+4(e_2-h e_1),
\]

with |e1|<=|h|^2 and |e2|<=|h|^3. Therefore the remainder has norm at most
one quarter of |h|^3, whereas the first term has norm one half of |h|^3.
This proves the exact equality, including h=0.

If a critical point is a zero, it follows necessarily that

\[
\boxed{|C|_2^2=\tfrac14|A|_2^3.}
\]

Consequently the checked sufficient certificate is

\[
\boxed{
|C|_2^2\ne\tfrac14|A|_2^3
\Longrightarrow
\forall x\in Z_2,\ \neg(F(x)=F'(x)=0).
}
\]

When A and C are nonzero, this is equivalently

\[
\boxed{2v_2(C)\ne2+3v_2(A).}
\]

The norm statement also handles zero quantities; it does not use Lean's
integer-valued valuation convention at zero as though it were infinity.

If A=0, the slope-distance identity shows that rho is the only critical point.
Lean also proves the exact triple-jet equivalence

\[
\boxed{
(\exists x:F(x)=F'(x)=F''(x)=0)\iff C=A=0.
}
\]

**Lean:** `CubicCriticalValues.lean`.

## 6. A finite trial point can certify the exact inflection test

Let x be a trial point and put eta=|J_2(F,x)|_2. Then eta=|x-rho|_2, and

\[
|F'(x)-A|_2=\eta^2,
\]

\[
\boxed{
|F(x)-C|_2\le\max\{\eta|F'(x)|_2,\eta^3\}.
}
\]

Thus the three conditions

\[
\eta^2<|F'(x)|_2,
\]
\[
\max\{\eta|F'(x)|_2,\eta^3\}<|F(x)|_2,
\]
\[
|F(x)|_2^2\ne\tfrac14|F'(x)|_2^3
\]

imply that the exact inflection criterion holds and F has no critical zero
anywhere on its disc.

This is a certificate using three evaluated jets. The first two inequalities
certify that trial value/slope norms equal the exact inflection value/slope
norms. The third excludes the required balance. Finite evaluation errors must
be below the claimed norms; a sampled numerical equality is not a proof.

Unlike the quadratic stationary center, an inflection point need not have zero
first derivative. Its trial-value error therefore includes a first-order term.
It would be incorrect to reuse quadratic precision-doubling without that term.

**Lean:** `CubicTrialJets.lean`.

## 7. Exact connection to the two-neighbor Euler core

The inherited Euler construction supplies an equal-slope half-core F0. In the
two-neighbor case, if its constant and linear coefficients also vanish modulo
two, exactly one further division gives K, with last odd index three.

Its existing all-order coefficient identity gives

\[
[X^{n+4}]K=4\cdot4^n w_n,\qquad w_n\in Z_2,
\]

and [X^3]K is odd. Define

\[
R(X)=\sum_{n\ge0}4^n w_nX^n.
\]

This is restricted, and Lean proves the exact identity

\[
K(X)=K_0+K_1X+K_2X^2+uX^3+4X^4R(X).
\]

Thus the cubic class is derived from the ACTUAL Euler nearest-neighbor
coefficients. It is not just assumed for an unrelated polynomial.

`eulerTwoNeighbor_criticalZero_unique` transfers the uniqueness of a critical
zero to that core. The checked chart theorem transfers the inflection norm
mismatch through the exact relation

\[
G_r(i+2^{k_i}Y)=2^{t_i+2}K(Y)
\]

to absence of a critical zero of the original Euler residual on that ball.
The original coordinate and value scalings are retained.

The exact chart relation and the arithmetic mismatch are explicit hypotheses of
the final transport theorem. The source derives the cubic representation from
the inherited core identities, but does not assert that every Euler core passes
the arithmetic test.

**Lean:** `EulerCubicCriticalBridge.lean`.

## 8. Sharp controls: equality is inconclusive

The synthetic polynomial

\[
F_s(x)=x^3-3s^2x+2s^3=(x-s)^2(x+2s)
\]

has an exact critical zero at x=s. For s nonzero, it is exactly double. Its
inflection point is zero and its data satisfy

\[
A=-3s^2,\qquad C=2s^3,\qquad
2v_2(C)=2+3v_2(A).
\]

Lean checks the factorization, the actual critical zero, and the zero reduced
discriminant. These are NOT Euler counterexamples.

Conversely x^3+3x+2 lies on the same norm-equality boundary, but its reduced
polynomial discriminant obstruction is 216, not zero. That nonzero arithmetic
identity is checked too. Together with the inherited polynomial discriminant
theorem, it rules out a repeated root of that polynomial.

Thus equality in the norm test is neither a proof of degeneracy nor a proof of
nondegeneracy. The odd-unit information and higher exact coefficients still
matter on the boundary.

**Lean:** `CubicSharpControls.lean`.

## 9. Bounded actual-index checks

Four original terminal-161 residuals were reconstructed at global precision
224 with

\[
r=B2^{640}-161,\qquad B\in\{3,7,11,15\},
\quad j_r=161,\quad\mu_r=-154.
\]

On x=90+128Y their coefficient content is 162. The normalized cubic core is
therefore known coefficientwise modulo 2^62. Its infinite high coefficients
are controlled by the inherited packet cutoff and actual Euler-core theorem,
not by assuming the written polynomial is exact.

| B | v_2(C) | v_2(A) | Norm mismatch | Conclusion from this test |
|---:|---:|---:|---|---|
| 3 | 1 | 0 | No | Inconclusive |
| 7 | 4 | 1 | Yes | No critical zero on the fixed core |
| 11 | 1 | 0 | No | Inconclusive |
| 15 | 2 | 2 | Yes | No critical zero on the fixed core |

All displayed valuations are strictly below the available precision and hence
are exact for the corresponding values. A zero residue is never promoted to an
exact dyadic zero. Inflection coordinates in the JSON files are residues, not
exact ordinary integers.

A small trial point Y=6 independently passes the finite three-jet test for the
two positive cases:

| B | v_2(F(6)) | v_2(F'(6)) | v_2(J_2(F,6)) | Guaranteed value-error order |
|---:|---:|---:|---:|---:|
| 7 | 4 | 1 | 6 | 7 |
| 15 | 2 | 2 | 6 | 8 |

The slope-error order is 12 in both. All error margins are strict.

A second implementation recomputed all four functions at 256 global bits,
leaving 94 normalized bits. It used a logarithmic source instead of the Newton
source, rising-factorial rather than paired-factorial packet scalars, and Horner
rather than direct-binomial localization. Inflection residues were computed by
both binary lifting and Newton iteration. Every shared coefficient and critical
datum agreed. There were also 32 terminating original-packet value comparisons.

Shared components remain: the modular Bernoulli evaluator and polynomial
multiplication. This is not a fully independent Bernoulli implementation.
Low Bernoulli values are checked against an exact rational recurrence by the
inherited routines. No general Euler parameter congruence class is inferred
from these four integers; they test the new invariant on actual inputs already
studied in the previous project.

The new finite coefficient records have NOT themselves been re-created inside
Lean. The universal analytic implications are kernel-checked; these arithmetic
instances are separately checked exact/modular computations.

## 10. Execution record and limitations

Input archive: `history/Komorebi_Euler_Critical_Value_v24_2026-10-04.zip`.
All 746 tracked entries matched. Its full 878-declaration baseline was compiled
and transitive-axiom-audited successfully in 217.034680 seconds.
All 96 inherited mathematical modules are unchanged.

The eight new modules have 728 source lines including comments and formatting.
They contain 45 named theorem/lemma declarations. The full project has 923 such
declarations across 104 mathematical modules.

Two full clean replays passed:

| Replay | Seconds | Audited declarations |
|---|---:|---:|
| A, fresh project output | 231.263185 | 923 |
| B, separate source copy and fresh output | 230.970205 | 923 |

All 106 compiled .olean files match byte-for-byte, as do the axiom audits and
mathematical source hashes. The transitive axiom union is exactly

```
Classical.choice
Quot.sound
propext
```

The compiler and pinned dependency cache were reused, not rebuilt or independently
bootstrapped. Both replays ran concurrently, with one worker per compiler process,
warnings-as-errors, and a 120-second timeout per module. Timings exclude portable
runtime restoration.

The generic exact/modular audit passed 25,826 registered checks over 147 finite
synthetic examples, including 60 examples with two independently planted exact
integer critical points. The 4 original-index runs recorded 82 checks apiece
(328 total). The alternative reconstruction recorded 1,528 comparisons. The
small four-record trial certificate is reported separately, not added as another
large test count. These finite tests corroborate the proofs; they do not supply
their universal quantifiers.

Development compilations encountered project-module search-path shadowing and
ordinary API, coercion, rewrite and linter failures. They were corrected before
both final clean replays. Development logs were overwritten during repair; a
failure summary is retained rather than claiming complete raw diagnostics exist.
No final replay or retained mathematical computation was interrupted or failed.

## 11. Remaining boundary

Closed here:

1. Construction of the inflection point for the infinite 4-divisible cubic class.
2. Exact derivative and curvature distances from that center.
3. Exact critical-value separation, and at most one critical zero per cubic core.
4. A single inflection value/slope norm-mismatch certificate for nondegeneracy.
5. A finite three-jet version with explicit error margins.
6. Derivation of the permitted cubic representation from actual Euler cores.

Still open:

1. Euler-specific arithmetic on the norm-equality boundary.
2. Exact critical-scalar nonvanishing in the remaining terminal-129 and terminal-161
   progressions; no multiplier-family completion is claimed here.
3. General treatment of lower residues that already have multiple binary roots.
4. Universal Euler simplicity, closed-disc algebraic squarefreeness, and the full
   all-parameter undepletion/critical-point continuation problem.

The useful new target is smaller: in a cubic core, first test the two exact data
A=F'(rho), C=F(rho) at its uniquely constructed inflection point. Only the exact
balance |C|^2=|A|^3/4 can still contain a repeated zero. There is no need to locate
two moving critical points before running this sufficient test.
