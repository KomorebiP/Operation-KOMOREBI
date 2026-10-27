# Euler Lean XX: exact skeleton localization and an end-to-end pointwise-unit atlas

**Operation Komorebi — 3 October 2026 — continuation v20**

## Status and exact scope

This continuation constructs the canonical separated skeleton balls and their
normalized local series, proves that those balls are disjoint and cover the
whole dyadic unit disc, and derives actual Euler root/derivative/row-error
statements from the v19 wall identity. The resulting all-distance atlas covers
EVERY actual terminal wall with terminal degree j>=2 whose lower residual is
pointwise odd. The inherited arithmetic criterion discharges that condition
when E_j=0 and e_j(1)!=E_j. In particular every regular actual terminal wall of
degree at least two is covered without a degree or multiplier bound.

The project contains 653 theorem/lemma declarations in 70 mathematical modules,
87 declarations and 12 modules more than v19. Counts include technical lemmas
and are not counts of historically novel results. All 58 inherited mathematical
modules are unchanged.

These are genuine Euler-defined residuals, not unidentified polynomials. The
local root theorems use the inherited convergent evaluation, analytic derivative,
and contraction/Hensel results. No Weierstrass preparation or hypothetical
polynomial root is substituted for the actual infinite function.

The argument does NOT classify a ball whose lower residual vanishes modulo two.
It does not prove the slope-matching or nearest-neighbor quadratic/cubic theorems
for those remaining Euler balls. The full defect-address classification,
regular-complement theorem at a lower address, critical-scalar nonvanishing,
and persistent multiple-residue charts remain further obligations. No broader
manuscript numerical coverage bound is increased, and no historical-priority
claim is made.

## 1. Actual objects inherited unchanged

D is mathlib's actual `ℤ_[2]`, with field `ℚ_[2]`. The signed Euler sequence is
independently defined by the inverse rational cosh series. Its reconstruction,
sharp error bound, infinite packet residual, normalization and terminal form
are the previously compiled constructions.

For an actual r>0, let j be the last global minimizing carry packet, let mu_r
be its minimum, and let delta be the constructed nonnegative wall distance.
The exact identity is

    G_r(x) = P_j(x) U_r(x-j) + 2^delta V_r(x),
    P_j(x) = product_(0<=l<j) (x-l)(2x-2l-1).

Both U_r and V_r are integral restricted series. The ENTIRE coefficient
reduction of U_r is one. The lower reduction is the sum of falling-factorial
polynomials over all lower carry minima, including the constant tie.

For every N>=r,

    |E_(2N)-retained_(r-1,N)|_2
      = 2^(-(4r-1+mu_r)) |choose(N,r)|_2 |G_r(N-r)|_2.       (1)

Every norm identity includes the zero case. We do not treat mathlib's
integer-valued valuation at zero as positive infinity.

## 2. Convergent affine localization, not arbitrary formal composition

For an integral series f and a,s in D define

    Aff(f,a,s)_n = s^n J_n(f,a),

where J_n is the actual evaluated Hasse jet. For |s|<1 the resulting series
is restricted. When f is restricted, Lean proves

    reval(Aff(f,a,s),y) = reval(f,a+s*y)                    (2)

for every dyadic y. The proof uses a nonarchimedean double-summability estimate
and binomial regrouping. In particular it does not make an undefined formal
substitution at a nonzero constant.

The full coefficient bounds are

    |coeff_n Aff(f,a,s)| <= |s|^n,

and, if restricted f,g have identical COMPLETE coefficient residues modulo 2^P,

    |coeff_n(Aff(f,a,s)-Aff(g,a,s))| <= |s|^n 2^(-P).       (3)

For s=2^k this is the coefficient error slope P+kn. Removing content 2^c then
has the exact stated precision cost c.

If red(s)=0, the entire chart reduction is the constant red(f(a)). Thus a
pointwise unit at the center becomes a coefficientwise unit on a proper
integral affine ball. This is why the pointwise-unit lower condition suffices.

The genuine analytic chain rule is also proved:

    deriv(qeval(Aff(f,a,s)))(y) = deriv(qeval f)(a+s*y)*s.   (4)

A second transport theorem differentiates an exact chart equality
f(a+s*y)=c*g(y) and retains BOTH scalars s and c. The equality is established
on an open field neighborhood of each dyadic point before differentiating.

## 3. Canonical skeleton scales and the exact unit polynomial

For 0<=i<j put

    k_i = floor(log_2(max(i,j-1-i)))+1,
    d_i = v_2(i!) + v_2((j-1-i)!),
    t_i = k_i+d_i.                                       (5)

The full-domain partition theorem assumes j>=2. The algebraic factorization
also makes sense for its indicated individual indices at smaller j.

Let v(n)=v_2(n) and u(n)=n/2^v(n), implemented by Nat.divMaxPow rather than an
assumed odd-part operation. Define the finite polynomial

    Q_(j,i)(Y)
      = product_(1<=n<=i) [u(n)+2^(k_i-v(n))*Y]
        * product_(1<=n<=j-1-i) [-u(n)+2^(k_i-v(n))*Y]
        * product_(0<=l<j) [2i-2l-1+2^(k_i+1)*Y].          (6)

Each n in the first two products is strictly below 2^k_i. Its valuation is
therefore strictly smaller than k_i; every nonconstant factor coefficient is
even and every constant factor is odd. Lean proves coefficientwise

    Q_(j,i) mod 2 = 1.

An exact finite-product rearrangement, using the factorial valuation sums, gives

    P_j(i+2^k_i*y) = 2^t_i * y * Q_(j,i)(y)               (7)

for every dyadic y. There is no division by a polynomial that might vanish.
Every power of two is extracted using a positive integer factor and its proved
odd part.

Combining Q_(j,i) with the convergent affine localization of the ACTUAL U_r
constructs a restricted series A_i with full reduction one and

    P_j(i+2^k_i*y) U_r(i+2^k_i*y-j)
      = 2^t_i * y * A_i(y).                              (8)

## 4. The balls form a proved finite partition

Define a dyadic ball as the RANGE of its affine chart:

    Ball(a,k) = {a+2^k*y : y in D}.

Lean proves equivalence with the exact residue condition

    x in Ball(a,k) iff redPow(k,x)=redPow(k,a).

For every j>=2, the j canonical balls Ball(i,k_i), 0<=i<j, are pairwise disjoint
and cover D. The proof is arithmetic, not a sampling or measure argument.

For covering, use the residue of x modulo 2^(m+1), m=floor(log_2(j-1)). If that
representative is below j, it provides a center directly. Otherwise subtract
2^m to reach a center with a shorter separating scale. All index and depth
inequalities are proved. For disjointness, two distinct skeleton centers have
positive ordinary separation smaller than BOTH relevant powers of two. A
shared point would make that difference divisible by the smaller power, a
contradiction.

## 5. Normalize the WHOLE local Euler function

Suppose V_r(i) is odd. Define the two local restricted series directly from
U_r,V_r and (8):

    Before_i(Y)
      = 2^(t_i-delta) Y A_i(Y) + V_r(i+2^k_i*Y),

    After_i(Y)
      = Y A_i(Y) + 2^(delta-t_i) V_r(i+2^k_i*Y).

The natural-number subtractions are used only under the correct order
hypotheses. Lean proves

    G_r(i+2^k_i*y) = 2^delta Before_i(y)   when delta<=t_i,
    G_r(i+2^k_i*y) = 2^t_i After_i(y)     when t_i<=delta. (9)

The complete binary reductions are

    delta<t_i:  Before_i = 1 mod 2,
    delta=t_i:  After_i  = Y+1 mod 2,
    delta>t_i:  After_i  = Y mod 2.                       (10)

The normalizations and all coefficient residues are derived from the actual
Euler wall, including its infinite source, not supplied as a standalone model.

## 6. Local actual root, derivative, and displacement theorem

When delta<t_i, the entire ball is root-free and

    |G_r(x)| = 2^(-delta).

When delta>=t_i, it contains exactly one actual dyadic root alpha_i, with

    |G_r'(alpha_i)| = 2^(-d_i),
    |G_r(x)| = 2^(-d_i) |x-alpha_i|,
    |alpha_i-i| = 2^(-(delta-d_i)).                       (11)

Lean proves existence and uniqueness with the inherited INFINITE-series Hensel
bridge. The derivative is the genuine field derivative. The chart scaling
2^k_i is retained explicitly: a unit derivative of the normalized chart is
not falsely reported as a unit derivative of G_r in the original coordinate.

The root-distance statements are unconditional norm identities. At the root
both sides are zero. Away from the root their usual additive-valuation form is

    v_2 G_r(x) = d_i + v_2(x-alpha_i).

These conclusions require only the single local hypothesis red(V_r(i))=1.

## 7. Complete pointwise-unit class, derived from the Euler carry costs

Suppose j>=2 and V_r(x) is odd for every dyadic x. The partition and local
results then give a full atlas on D.

Define the finite type of active skeleton centers by

    ActiveSkeleton(r) = {i:Fin j : t_i<=delta}.

The release constructs an actual equivalence

    ActiveSkeleton(r) equiv {x:D : G_r(x)=0}.             (12)

Injectivity follows from disjoint balls; surjectivity follows from covering
and exclusion of every subthreshold ball. Thus the exact root count is

    #{dyadic roots of G_r} = #{0<=i<j : t_i<=delta}.       (13)

Every root has nonzero analytic derivative.

The pointwise-unit hypothesis is discharged by the INHERITED proved arithmetic
criterion

    E_j=0 and e_j(1)!=E_j.                               (14)

The new end-to-end theorem `eulerCarry_unit_no_critical` and root-count theorem
therefore require only the actual arithmetic conditions (14), not a hypothetical
normal form or an assumed root atlas. In particular the regular lower-cost
inequalities imply them, giving `eulerRegular_no_critical` for every actual
regular terminal wall of degree at least two.

This formally covers the pointwise-unit class, including irregular members
once their finite lower-cost condition is supplied. This release does not add
new individual arithmetic address certificates such as terminal 258; the
all-label defect-address and regular-complement proofs remain further work.

The restriction j>=2 cannot simply be discarded in the generic pointwise-unit
argument. At j=1, U=1 and V=1+3x-x^2 have pointwise odd V, but

    P_1(x)+V(x) = (x+1)^2.

This synthetic negative control is included in the exact audit. Actual Euler
terminal-one residuals are already covered by their stronger inherited theorem.

## 8. Original Euler row laws

Combining (11) with the independently identified Euler-error theorem gives,
on an active skeleton ball,

    |E_(2N)-retained_(r-1,N)|
      = 2^(-(4r-1+mu_r+d_i)) |choose(N,r)|
        * |(N-r)-alpha_i|,                               (15)

for every N>=r with its offset in that ball. The code constructs alpha_i and
proves the original row equality criterion: the error vanishes precisely when
the integer offset is that root.

On a subthreshold ball the exact norm is

    2^(-(4r-1+E_j)) |choose(N,r)|.                        (16)

For the global pointwise-unit class E_j=0, so this is exactly the previously
known worst-case coefficient order plus the binomial factor. No uniform
truncation exponent is increased.

## 9. The complete terminal-two class and an actual two-root example

The release proves for every actual r>0 with j_r=2,

    number of dyadic roots = 0 if delta_r=0, otherwise 2,

and every existing root is simple. These are whole-function conclusions for
the constructed Euler residual, not finite residue tests alone.

A concrete kernel-evaluated carry witness gives

    r=510=2^9-2,
    (lambda(0),lambda(1),lambda(2))=(0,4,-1),
    j_r=2, mu_r=-1, delta_r=1.

The proved global cutoff excludes all later competitors. Each of the two
parity balls contains exactly one root, with original-coordinate derivative
norm one. For i=0,1 and the corresponding root alpha_i, Lean proves for EVERY
N>=510 with N-510 in i+2Z_2,

    |E_(2N)-retained_(509,N)|
      = 2^(-2038) |choose(N,510)| |N-510-alpha_i|.         (17)

This is a genuine nonconstant, multi-root end-to-end Euler example. It is not
a new broader manuscript coverage result.

## 10. Modules and proof boundaries

| New module | Declarations | Role |
|---|---:|---|
| RestrictedAffine | 8 | Convergent affine translation, evaluation and coefficient precision |
| SkeletonArithmetic | 6 | Canonical scales, factorial sums and actual odd parts |
| SkeletonLocalPolynomial | 11 | Exact finite skeleton factorization and full unit reduction |
| LocalAnalyticTools | 4 | Analytic chain rule and global affine Hensel atlas |
| SkeletonLocalSeries | 9 | Actual upper chart and before/after series |
| SkeletonLocalEvaluation | 5 | Exact normalization and differentiated chart equality |
| LocalRootTransport | 4 | Root existence, uniqueness, norm and derivative scaling |
| SkeletonPartition | 7 | Residue balls, covering and disjointness |
| EulerLocalAtlas | 10 | Localized actual Euler normal forms and simple-root laws |
| EulerPointwiseAtlas | 7 | Root-type equivalence, exact count and carry/regular simplicity |
| EulerLocalRows | 5 | Exact error laws for the original independent Euler numbers |
| EulerSkeletonExamples | 11 | Terminal-two family and the r=510 actual application |

Remaining work:

1. Handle skeleton balls where the lower function has a root. The construction
   here makes V pointwise odd on the ball; it does not establish the more general
   slope-match theorem for zero-containing lower balls.
2. Formalize the nearest-neighbor 1+/-2Y and 1-4Y^2 factorizations and connect them
   to the existing quadratic/cubic core results at those slope matches.
3. Formalize the complete defect-address and largest-active-address regular
   complement, and supply the high-precision Euler-specific certificates.
4. Construct any further closed-disc preparation and critical charts needed when
   a multiple residue survives. No origin-adic preparation theorem is silently
   substituted for a last-odd-coefficient statement.
5. Resolve the exact Euler critical scalar/Wronskian nonvanishing question or
   classify an actual zero in the remaining arithmetic progressions. This is a
   mathematical research obligation, not something compilation provides.

The current result does not prove universal Euler simplicity or algebraic
squarefreeness. It formalizes a broad previously derived atlas exactly from the
Euler definitions. No manuscript degree/digit-sum scope number is increased.

## 11. Verification and reproduction

The exact incoming v19 archive passed its 282-entry manifest. Its 566-declaration
project was recompiled and axiom-audited before development. The portable runtime
was restored from the locally available five-part compact archive, whose combined
SHA-256 matched the inherited pin. Lean is 4.34.0-rc2 and mathlib is pinned at
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

See RELEASE_STATUS.json for the TWO completed final clean replay records and
compiled-output comparisons. Each replay starts with an empty project output
directory, and the second uses a separate mathematical source-tree copy. All
653 indexed declarations are inspected with `#print axioms`. The permitted
transitive union is only Classical.choice, Quot.sound and propext. No native
proof evaluation, unfinished proof, or custom mathematical axiom is accepted.
The source indexer is a lexical project utility; coverage is compared against
the compiler's actual axiom-report output.

The supplementary standard-library audit passes 5,098 registered checks at
32-bit normalized coefficient precision. It verifies full finite polynomial
factorizations on 557 skeleton balls, disjoint/complete residue coverings for
all j=2..512, and 897 full local coefficient reductions with synthetic
nonconstant pointwise-unit lower factors. Exact direct derivative products
corroborate the factorial slope. The synthetic examples are explicitly NOT
Euler residuals. Actual small carry data are separately checked at r=254,510,1022.
The universal mathematical conclusions come from Lean, not these samples.

Development compilations rejected API/coercion mismatches, missing Fintype
resolution, a rewrite that expanded an arithmetic example too deeply, and an
initial after-chart statement missing the required t_i<=delta inequality. The
order hypothesis was added explicitly before the statement compiled. All these
failed diagnostics remain in evidence/v20_development; none is counted as a
passed theorem. Both final replays use the corrected sources.

Run with fresh output paths:

```text
python3 scripts/verify_manifest.py
python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
python3 scripts/check_skeleton_localization.py --precision 32 --output /path/to/NEW_check.json
```

Runtime binaries, compiled project objects, dependency caches, and fonts are
not included in the source ZIP. Compiled dependencies are reused during replay;
Lean and all of mathlib are not bootstrapped here. All 58 incoming mathematical
modules and the original v19 archive are preserved unchanged.

## Sources and attribution

The actual pinned mathlib sources supply the p-adic ring/norm/residue structure,
formal and restricted power series, nonarchimedean summation, derivative chain
rule, finite sums/products, factorial valuations, and natural-number logarithms.
Hashes of the directly used source files are in PROVENANCE.json. The inherited
project supplies its checked infinite-series Hensel theorem and original Euler
construction. The polynomial separation and atlas arguments are formalizations
of the earlier manuscript mathematics; no historical-priority claim is made.
