# Euler Lean XXI: lower-root charts, slope matching, and finite collision localization

**Operation Komorebi — 3 October 2026 — continuation v21**

## Status and exact scope

This release extends the actual Euler atlas beyond pointwise-odd lower residuals.
It constructs normalized analytic lower charts at every relevant skeleton center,
proves the nonresonant simple-root laws when the lower and skeleton slopes differ,
excludes equal-slope balls with odd alignment, and constructs the remaining exact
restricted collision core when the alignment is even.

The capstone is a necessary-condition theorem for every critical zero of the
ACTUAL carry-normalized Euler residual, under the explicit hypothesis that the
carry-defined lower residue polynomial has only simple binary roots. Every such
zero lies in an aligned skeleton ball with equal slopes and one additional bit
of center divisibility. The set of these candidate balls is a constructed finite
type of cardinality at most two for each FIXED actual residual.

There are 74 new theorem/lemma declarations in nine modules. With the 70 unchanged
incoming mathematical modules, the project contains 727 declarations in 79 modules.
Counts include helper lemmas; they are not counts of novel mathematical results.

This is not a new all-label simplicity theorem. No candidate is asserted to contain
a repeated root. The equal-slope/even-alignment core is not asserted to have any
particular degree in this release. No all-multiplier/all-distance stability of
lower-root addresses, nearest-neighbor Euler factorization, closed-disc preparation,
critical-scalar nonvanishing, or new manuscript coverage bound is claimed.

## 1. Actual objects and inherited localization

Use the actual dyadic integers D = Z_2 and field K = Q_2. A `Series` has coefficients
in D. `Restricted f` says those coefficients tend to zero. `reval`, evaluated Hasse
jets, `qeval`, and analytic `deriv` are the constructed convergent operations.

For a positive first omitted depth r, let j be its last global minimizing packet,
mu its minimum, and delta its canonical nonnegative wall distance. The inherited
identity, on EVERY dyadic argument, is

\[
G_r(x)=P_j(x)U_r(x-j)+2^\delta V_r(x).
\]

Here U_r and V_r are the ACTUAL restricted upper continuation and lower prefix
constructed from Bernoulli/source packets. The complete reduction of U_r is one.
The lower polynomial is the sum of falling factorials over the lower carry minima.
No convenient model polynomial or favorable terminal index replaces these objects.

For j>=2 and 0<=i<j, put

\[
k_i=1+\lfloor\log_2\max(i,j-1-i)\rfloor,
\quad d_i=v_2(i!)+v_2((j-1-i)!),\quad t_i=k_i+d_i.
\]

The inherited skeleton balls B_i=i+2^{k_i}Z_2 are disjoint and cover Z_2. Their
constructed upper charts satisfy

\[
P_j(i+2^{k_i}Y)U_r(i+2^{k_i}Y-j)
=2^{t_i}Y A_i(Y),\qquad\overline A_i=1.
\]

All ordinary derivative norms below refer to the ORIGINAL x coordinate unless
specified otherwise. Additive valuation expressions use v_2(0)=infinity in the
mathematical exposition; the unconditional Lean statements use norm identities.

## 2. The lower-root chart is built from Hasse coefficients

Let f be an integral restricted series, a in D, k>0, and suppose

\[
f(a)=2^s w,\qquad s\le k.
\]

Define

\[
T_{f,a,k}(Y)=\sum_{n\ge0}2^{kn}J_{n+1}(f,a)Y^n,
\]

and

\[
L_{f,a,k,s,w}(Y)=w+2^{k-s}Y T_{f,a,k}(Y).
\]

The coefficients of T decay geometrically. The series is therefore restricted,
and Lean proves the exact identity

\[
f(a+2^kY)=2^sL_{f,a,k,s,w}(Y).
\]

The proof compares the Hasse-defined affine coefficients; it does not use an
undefined formal substitution at a nonzero constant or divide an arbitrary
formal series by an unproved common factor.

If s<k and w is odd, the entire normalized chart reduces to the constant one.
If s=k and J_1(f,a) is odd, the chart reduces to

\[
Y+\bar w.
\]

The inherited infinite-series affine Hensel theorem constructs its unique root,
unit normalized derivative, and exact root-distance law. Applied to the actual
V_r, this proves the existence of a lower root in the ball whenever V_r(i) is
divisible by 2^{k_i} and the lower derivative there is odd.

The chart is constructed at the center. A factorization around a hypothetical
lower root is NOT assumed in order to obtain that root.

## 3. Every shallower lower value is completely classified

Suppose the center has exact finite content

\[
V_r(i)=2^s w,\qquad s<k_i,\qquad w\text{ odd}.
\]

The normalized lower chart is a unit. The two terms of G have contents t_i and
delta+s. After normalizing the WHOLE local function, the reduction is exactly
1, Y+1, or Y. Lean proves:

\[
v_2G_r(x)=
\begin{cases}
\delta+s,&\delta+s<t_i,\quad x\in B_i,\\
d_i+v_2(x-\alpha_i),&\delta+s\ge t_i,\quad x\in B_i.
\end{cases}
\]

The first case is root-free. The second has a unique simple root alpha_i with
original derivative norm 2^{-d_i}. No lower-derivative hypothesis is required
for this shallower case.

The implementation also constructs s and the odd w whenever the center is NOT
divisible by 2^{k_i}, using the actual dyadic valuation and unit coefficient.
The global localization theorem does not ask the caller to guess them.

## 4. Root-containing balls: unequal slopes cannot produce a critical zero

Suppose

\[
V_r(i)=2^{k_i}w,\qquad J_1(V_r,i)\text{ odd}.
\]

Write k=k_i and d=d_i. The actual chart identity is

\[
G_r(i+2^kY)=2^{k+d}Y A_i(Y)+2^{k+\delta}L_i(Y),
\quad \overline A_i=1,\quad\overline L_i=Y+\bar w.
\]

When delta<d, remove 2^{k+delta}. The result reduces to Y+bar(w).
When d<delta, remove 2^{k+d}. The result reduces to Y.

Thus whenever delta!=d there is exactly one root alpha in B_i, and

\[
\boxed{v_2G_r(x)=\min(\delta,d)+v_2(x-\alpha),}
\]

\[
\boxed{|G_r'(\alpha)|_2=2^{-\min(\delta,d)}.}
\]

These are actual restricted-series root statements, including existence,
uniqueness on the whole ball, and the analytic derivative. The `SimpleBallAtlas`
definition merely bundles these proved conclusions for reuse; it is not supplied
as an assumed root atlas in the Euler slope theorems.

The chain rule retains both scales. If G(i+2^kY)=2^cF(Y), it yields
2^k G'(i+2^kY)=2^c F'(Y). Therefore the derivative order is c-k, not c.

## 5. Equality has an exact extra-bit decision and an honest remaining core

When delta=d, the normalized chart after removing 2^{t_i} has reduction bar(w).

If w is odd, the whole ball is root-free and its valuation is exactly t_i.

If w is even, Lean CONSTRUCTS a restricted series F with

\[
\boxed{G_r(i+2^{k_i}Y)=2^{t_i+1}F(Y).}
\]

The integral half is produced from the full zero residue by coefficientwise
divisibility. Restrictedness is then proved from the norm scaling. It is not an
arbitrary formal half of a series that may lack integral coefficients.

A genuine analytic chain-rule theorem gives

\[
\boxed{
G_r(i+2^{k_i}y)=G_r'(i+2^{k_i}y)=0
\iff F(y)=F'(y)=0.
}
\]

No simplicity or degree bound is inferred for F. Deriving its nearest-neighbor
factors and applying the existing conditional quadratic/cubic results are still
subsequent obligations.

## 6. Global Euler collision localization

Define the arithmetic hypothesis directly from the carry-defined polynomial:

\[
\operatorname{LowerResidueSimple}(j):\quad
\forall e\in\mathbf F_2,\quad
\bar V_j(e)=0\ \Longrightarrow\ \bar V_j'(e)\ne0.
\]

The complete coefficient certificate for V_r, combined with the inherited jet
soundness theorem, derives the odd actual derivative at every zero-residue center.
It is not assumed independently as a property of the infinite function.

For actual r>0, j>=2, and this simple-lower-residue hypothesis, Lean proves

\[
\boxed{
G_r(x)=G_r'(x)=0\ \Longrightarrow\
\exists i<j:\quad
x\in B_i,\quad\delta=d_i,\quad
V_r(i)\equiv0\pmod{2^{k_i+1}}.
}
\]

The proof covers ALL skeleton balls. If the center is shallower than the radius,
Section 3 excludes a critical zero. Otherwise Section 4 excludes unequal slopes,
and Section 5 excludes the odd alignment. The covering theorem supplies the ball
for every x in Z_2.

A corresponding sufficient theorem excludes all actual critical zeros whenever
no center passes both the slope-equality and additional-divisibility tests.

## 7. At most two candidate balls for each fixed residual

`LowerAlignedSkeleton r hr` is the finite subtype of skeleton centers satisfying
V_r(i)=0 modulo 2^{k_i}. Each such ball has an ACTUAL lower root by Section 2.

Under LowerResidueSimple, two lower roots of the same parity are equal. This is
proved using the isometry on a simple residue class. Pairwise disjoint skeleton
balls therefore cannot correspond to the same binary root.

Lean constructs the injective parity map and proves

\[
\#\operatorname{LowerAlignedSkeleton}(r)\le2.
\]

`SlopeCandidate r hr` adds the conditions delta=d_i and the extra zero bit.
Consequently

\[
\boxed{\#\operatorname{SlopeCandidate}(r)\le2,}
\]

and every actual critical zero belongs to one of those constructed candidate balls.

This counts BALLS, not critical points inside each ball. It is a statement for a
FIXED actual r. The cross-multiplier/cross-distance stability theorem needed to
freeze the candidate set throughout an entire terminal family is not proved in
this release. Nor does this theorem apply when a lower binary root is multiple.

## 8. The row law and an actual irregular-wall example

A local simple atlas of slope nu transports through the already-identified Euler
error exactly:

\[
\boxed{
|E_{2N}-T_{r-1,N}|_2
=2^{-(4r-1+\mu_r+\nu)}
\left|\binom Nr\right|_2\,|N-r-\alpha|_2,
}
\]

for N>=r and the indicated offset ball. In the nonresonant lower-root case,
nu=min(delta,d_i). The norm theorem includes zero errors without assigning a
false finite value to the integer-valued Lean valuation at zero.

For terminal label 17, a kernel-checked finite carry calculation plus algebraic
polynomial identities prove

\[
\bar V_{17}=X+1,
\qquad11\le d_i\le15\quad(0\le i<17).
\]

Thus EVERY actual depth with terminal index 17 and delta<11 or delta>15 has no
critical zero. The interval is a conservative formal exclusion; this release
does not claim a full terminal-17 phase table.

A separately defined explicit first omitted depth is

\[
r=2^{63}-17=9223372036854775791.
\]

Lean verifies its actual global minimizer j=17 and wall distance delta=10 using
the proved finite search bound. It then proves that every dyadic root of this
actual infinite Euler residual has nonzero derivative. This is an irregular,
non-pointwise-unit application, not a synthetic polynomial. No root count for
this example is claimed by this module.

The optimal uniform Euler exponent 4M+3 and the broader manuscript coverage
numbers are unchanged.

## 9. Modules

| Module | Declarations | Role |
|---|---:|---|
| NormalizedLowerChart | 9 | Constructed center-content chart from convergent Hasse jets |
| SlopeChartSeries | 10 | Integral before/after sums and exact even division |
| EulerSlopeCharts | 10 | Actual Euler lower/slope chart constructions and identities |
| EulerSlopeAtlas | 8 | Nonresonant simple roots, equal odd exclusion, equal even core |
| EulerShallowLower | 11 | Complete atlas for center content below the radius |
| EulerSlopeLocalization | 7 | Actual content witnesses and global slope/alignment criterion |
| EulerSlopeCandidates | 7 | Finite candidate types, parity injection and cardinality bound |
| EulerSlopeExamples | 8 | Carry-defined terminal-17 example and noncritical actual depth |
| EulerSlopeRows | 4 | Critical-core equivalence and original Euler-error transport |

## 10. Remaining formal and mathematical obligations

1. Derive the exact nearest-neighbor 1+/-2Y and 1-4Y^2 factors on the surviving
   Euler-defined equal-slope cores. The generic coefficient/analytic core theorems
   are inherited, but their full actual Euler factorization is not supplied here.
2. Prove low-precision lower-coefficient stability across admissible multipliers
   and wall distances, then derive the manuscript's all-family routing theorem.
   A fixed-residual two-ball bound is not a substitute for that additional step.
3. Formalize the complete defect-address and regular-complement theorems and the
   stored high-precision arithmetic coefficient certificates.
4. Construct any further closed-disc preparation and critical coordinate charts
   needed at persistent multiple residues.
5. Prove Euler-specific critical-scalar/Wronskian nonvanishing, or classify an
   actual zero, in the unresolved progressions. That is still mathematical
   research, not an obligation automatically discharged by Lean compilation.

No universal Euler nondegeneracy, algebraic squarefreeness, new irregular-family
classification, or larger terminal-degree/binary-complexity scope is asserted.

## 11. Verification and trust boundary

See RELEASE_STATUS.json for exact replay times, source and object hash comparisons,
and the successful transitive-axiom reports. Each final replay compiles every module
from an empty project-output directory. The second starts from a separate source
copy. Both reuse the same pinned dependency cache: Lean and all mathlib are not
bootstrapped from source in these replays.

All 727 indexed theorem/lemma declarations are included in the compiler's `#print
axioms` audit. The permitted union is only Classical.choice, Quot.sound and propext.
The lexical indexer is a project utility rather than an independent Lean parser;
its list is compared with the compiler's actual axiom output. The incoming 70
mathematical modules are unchanged and their hashes are recorded separately.

The supplementary standard-library audit passes 25,657 registered finite checks.
It compares direct binomial localization with product charts on 527 skeleton balls,
checks 10,484 complete root-containing reductions and 8,402 shallow-center reductions,
300 eight-bit simple-root lifts, candidate-cardinality tests and affine coefficient
error bounds. It retains the permitted exact double-root negative control G=X^2
with V=X^2-P_2, as well as independent digit-sum/carry-increment checks of the
explicit r=2^63-17 example. Synthetic polynomials are NOT Euler-family certificates;
finite modular lifts are NOT reported as exact root constructions. Universal
conclusions come from the Lean proofs.

### Development failures and recovery

Development compilations rejected several API-name, coercion, residue-characteristic
and rewrite mismatches. A direct compile invocation was interrupted by the outer
command budget and rerun separately; no incomplete invocation is counted as a pass.
A row-error specialization reached Lean's deterministic heartbeat limit because its
minimum was being elaborated through an integer cast. Giving the natural minimum
and its cast explicitly resolved it without weakening the statement or raising
the heartbeat budget. The corrected module compiled in under two seconds during
development. Failed diagnostics are preserved under evidence/development.

An early concrete polynomial kernel-evaluation attempt did not reduce. It was
replaced by kernel-checked finite carry data plus explicit algebraic polynomial
identities, not by untrusted native proof evaluation. Source scans and complete
transitive audits reject unfinished proofs and custom/native proof axioms.

The verified runtime archive hash is inherited and was checked before extraction.
Runtime binaries, compiled project objects, dependency caches and fonts are not
included in this source release. The original incoming v20 archive is preserved
unchanged in history/v20.

## 12. Reproduction and provenance

Use Python 3.10+, the pinned Lean 4.34.0-rc2 runtime, and mathlib revision
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_slope_localization.py --max-j 32 --output /path/to/NEW_slope_check.json
```

Fresh evidence paths are required; the scripts refuse to overwrite retained outputs.
The actual pinned mathlib source supplies the p-adic residue/valuation APIs, analytic
chain rule and cardinality principles. The inherited project supplies the complete
Euler construction, affine localization and infinite-series Hensel theorem.
Source and input hashes are in PROVENANCE.json. The mathematical slope formulas
were developed in the earlier research record; this continuation formalizes their
fixed-residual construction and implications. No historical-priority claim is made.

## Final clean replay record

The incoming manifest verified 548 entries, and the inherited 653-declaration project passed a fresh baseline replay in 147.034097 seconds. All 70 incoming mathematical modules remain unchanged.

| Replay | Audited declarations | Seconds |
|---|---:|---:|
| 1: fresh output | 727 | 161.845191 |
| 2: separate source copy and fresh output | 727 | 162.620814 |

All 81 compiled .olean outputs have identical SHA-256 hashes between replays. The transitive axiom union is exactly Classical.choice, Quot.sound, propext. Runtime restoration is excluded from these compilation/audit times. The new modules contain 1075 lines; all mathematical modules contain 8885 lines, including definitions and comments.
