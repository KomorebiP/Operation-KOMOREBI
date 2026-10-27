# Euler Lean XVII: constructed residuals, exact carry normalization, and row factorization

**Operation Komorebi — 3 October 2026 — continuation v17**

## Status and boundary

This release constructs the actual infinite Euler residual H_r and its integral,
carry-normalized series G_r. The previously established independent Euler error
now factors through these objects. The packet scalar valuation, finite global
minimum, last minimizing packet, complete residue polynomial, and last odd
coefficient are derived in Lean from the original definitions. No coefficient
valuation or convergent residual is supplied as an assumed structure field.

There are 138 new theorem/lemma declarations in 14 modules. Together with the
unchanged 28 incoming mathematical modules, the project has 417 declarations in
42 modules. Counts include auxiliary lemmas and are not counts of novel results.

The mathematical research boundaries are unchanged. No new irregular terminal
family is classified. There is no new terminal-degree or binary-complexity bound,
no universal Euler nondegeneracy theorem, and no proof of nonvanishing of the
remaining critical scalars. The terminal wall arithmetic, nearest-neighbor
factorizations from the original Euler objects, local high-precision certificates,
and additional closed-disc preparation still require further Lean work.

The first simple actual residual cases are now end-to-end too: terminal index
zero is pointwise a unit; terminal index one has a unique simple dyadic root.
The exact Euler error valuation for all positive r with at most three binary
one-bits follows from the constructed normalized residual, not an abstract model.

## 1. Conventions and inherited objects

D denotes the actual dyadic integer ring Z_2, implemented as `ℤ_[2]`. Its field is
`ℚ_[2]`. A restricted series has integral Taylor coefficients tending to zero.
`reval` is its genuine convergent evaluation, while `qeval` is the corresponding
field-valued sum. First derivatives use Lean's `HasDerivAt` and `deriv`.

The inherited signed Euler sequence is independently defined from the inverse
of the rational formal cosh series. The v16 theorem identifies it with

    E_(2N) = sum_(m=0..N) kappa_m choose(2N,2m) A(N-m),

where

    kappa_m = -2^(4m)(2m-1) B_(2m),
    A(n) = (9^(n+1)-1)/(8(n+1)(2n+1)).

The source is an actual restricted Newton-series construction. The source/kernel
alignment and optimal uniform Euler modulus 2^(4M+3) are inherited unchanged.
All exact error statements here require N>=r>=1, with M=r-1. Empty original
tails remain covered by the earlier exact-equality theorems.

## 2. The actual beta coefficient and an integral numerator

Define over Q and then embed into D

    beta_m = kappa_m / (4^m (2m)!).

Lean proves beta_0=1, every beta_m is nonzero, and beta_m is dyadically integral.
For m>0 the checked valuation is first obtained as

    v_2(beta_m) = 2m-1-v_2((2m)!).

Legendre's theorem then gives the exact binary form

    v_2(beta_m) = s_2(m)-1,

where `binaryDigitSum m` is defined by the sum of the actual base-two digits.
No binary-complexity function is characterized only by desired properties.

H_r need not have integral coefficients. We therefore construct its numerator

    J_r(X) = beta_r H_r(X)

first. The qth scalar of J_r is

    a_(r,q) = 8^q beta_(r+q),

and Lean proves the uniform norm bound

    |a_(r,q)|_2 <= 8^(-q).

This does not lose the arithmetic content: division by the proved nonzero beta_r
is retained exactly in the later definition of H_r.

## 3. Analytic translations of the actual source

A formal substitution at a nonzero constant is not automatically defined for
an arbitrary formal power series. The new translation construction instead
uses convergent coefficient sums.

Lean proves from the Newton source that its nth Taylor coefficient is divisible
by 2^n. Write A(X)=sum_n 2^n w_n X^n with w_n in D. For a in D, define

    b_n(a) = sum_(m>=0) 2^m choose(n+m,n) w_(n+m) a^m,
    Shift_a A(X) = sum_n 2^n b_n(a) X^n.

The double-summability bounds justify regrouping the binomial expansion, giving

    reval(Shift_a A,x) = reval(A,x+a)

at EVERY dyadic x,a. The translated coefficients still satisfy

    |[X^n] Shift_a A|_2 <= 2^(-n).

The same module proves multiplicativity of `reval` on restricted series. These
are actual evaluation theorems, not formal-composition shorthand.

## 4. The infinite packet series is constructed and converges

Use the actual polynomial

    P_q(X) = product_(i=0..q-1) (X-i)(2X-2i-1).

Its ordinary polynomial degree is at most 2q. Define

    F_(r,q)(X) = 8^q beta_(r+q) P_q(X) A(X-q),

where A(X-q) is the convergent translated series from Section 3.

Lean proves BOTH coefficient bounds, uniformly in r:

    |[X^n] F_(r,q)|_2 <= 8^(-q),
    |[X^n] F_(r,q)|_2 <= 2^(-(n+q)).

The second bound follows because a coefficient in the polynomial factor has
index at most 2q, leaving source degree at least n-2q. It is strong enough for
ordinary absolute double summability, so no informal exchange of two infinite
sums is needed.

Define

    J_r = PowerSeries.mk (n |-> sum_(q>=0) [X^n]F_(r,q)).

Then

    |[X^n]J_r|_2 <= 2^(-n),

and `eulerResidualNumerator_restricted` proves that J_r is restricted. Evaluation
is proved to commute with the complete packet sum:

    J_r(x) = sum_(q>=0) 8^q beta_(r+q) P_q(x) A(x-q).

At a nonnegative integer n, P_q(n)=0 for q>n. Thus the evaluation terminates
EXACTLY, not merely to finite precision.

## 5. H_r is an actual restricted series over Q_2

Define

    H_r(x) = J_r(x)/beta_r.

`eulerResidualSeries` is the field-valued Taylor series obtained by the same
scalar multiplication. Lean proves restricted convergence on the unit disc,
its equality with the packet formula, and genuine differentiability:

    H_r'(x) = J_1(J_r,x)/beta_r.

It also proves

    J_r(0)=beta_r,     H_r(0)=1.

There is no assertion that H_r is always integral. The numerator J_r and the
later normalized series G_r have that property by separate proofs.

## 6. Exact factorization of the identified Euler error

The factorial-lane identity is established for every individual original term.
For N=r+n and 0<=q<=n,

    kappa_(r+q) choose(2(r+n),2(r+q)) A(n-q)
      = 4^r (2(r+n))^underlined(2r)
          * 8^q beta_(r+q) P_q(n) A(n-q).

Reindexing the finite Euler tail gives

    T_(r-1)(r+n)
      = 4^r (2(r+n))^underlined(2r) J_r(n).

Using kappa_r=4^r(2r)! beta_r and the definition of H_r yields the capstone

    E_(2N) - retained_(r-1,N)
      = kappa_r choose(2N,2r) H_r(N-r)                 (1)

for EVERY N>=r>=1, in the actual dyadic field.

The factor kappa_r choose(2N,2r) is proved nonzero. Therefore exact zero of the
original Euler error is equivalent to zero of the constructed residual at the
original integer offset.

## 7. Exact transport recurrence and finite packet precision

The proved packet multiplication law and convergent summation give

    J_r(x) = sum_(q<a) 8^q beta_(r+q) P_q(x) A(x-q)
             + 8^a P_a(x) J_(r+a)(x-a)

for every a,r>=0 and x in D. In particular,

    J_r(x) = beta_r A(x) + 8x(2x-1)J_(r+1)(x-1),

and

    H_r(x) = A(x) + 8 beta_(r+1)/beta_r
                       * x(2x-1)H_(r+1)(x-1).        (2)

Equation (2) is now an identity of the constructed infinite functions.

For the finite packet truncation J_(r,<Q), whose retained source factors remain
exact infinite series, Lean proves

    |[X^n](J_r-J_(r,<Q))|_2 <= 8^(-Q)      for EVERY n,
    |J_r(x)-J_(r,<Q)(x)|_2 <= 8^(-Q)       for EVERY x in D.

In particular, P<=3Q gives full coefficientwise and value agreement modulo2^P.
Division by beta_r has the explicit error norm cost 1/|beta_r|_2. These results
are numerator cutoffs; they are not relabelled as the sharper carry-normalized
cutoff from the mathematical research record.

## 8. The carry cost and its minimum are derived, not assumed

For r>0, define the actual rational H_r scalar

    alpha_(r,q)=8^q beta_(r+q)/beta_r.

The formal valuation theorem is

    v_2(alpha_(r,q)) = lambda_r(q),
    lambda_r(q)=3q+s_2(r+q)-s_2(r).                   (3)

It is an integer-valued cost and can be negative. Its lower bound is

    lambda_r(q) >= 3q+1-s_2(r).

Since lambda_r(0)=0, every nonpositive cost lies in

    0<=q<=floor((s_2(r)-1)/3).

The code defines mu_r as the minimum over precisely this finite set, and proves
that it is the GLOBAL minimum over every q>=0. It then constructs the finite
set J_r^min of all minimizing packets and its largest element j_r. (The symbol
J_r^min denotes an index set here, not the numerator J_r.)

    mu_r<=0,
    lambda_r(j_r)=mu_r,
    q>j_r => lambda_r(q)>mu_r,
    j_r<=floor((s_2(r)-1)/3).

No caller supplies a hypothetical minimizer or a favorable finite cutoff.

## 9. G_r is constructed with its exact normalized residue

Set gamma_(r,q)=2^(-mu_r) alpha_(r,q). Equation (3) and the global minimum prove

    v_2(gamma_(r,q))=lambda_r(q)-mu_r>=0.

Hence every normalized packet scalar lies in D. The new proof bounds the scaled
numerator coefficients using the convergent sums of those integral packets.
It constructs

    G_r = (2^(-mu_r)/beta_r) J_r

as an actual series with coefficients in D, proves restrictedness, and proves

    G_r(x)=2^(-mu_r)H_r(x).                           (4)

The full binary coefficient reduction is also proved:

    bar G_r(X) = sum_(q in J_r^min) X^underlined(q).   (5)

The source translates reduce to one; gamma reduces to one exactly at a minimum
and to zero elsewhere; the paired packet reduces to its falling factorial.
The complete infinite coefficient sum is sent through the continuous residue
map, with the nonminimum terms proved to vanish.

The largest term of (5) is monic of degree j_r and every other term has smaller
degree. Therefore Lean proves

    LastOdd(G_r,j_r),     G_r!=0.

This verifies the ACTUAL coefficient normalization, not only an integral bound.
The closed-disc Weierstrass factorization G_r=W_r U_r is not constructed in this
release. `LastOdd` means the last odd Taylor coefficient, not a substituted
formal-power-series order at the origin.

## 10. Exact normalized row law and first end-to-end root cases

Combining (1) and (4),

    E_(2N)-retained_(r-1,N)
      = kappa_r choose(2N,2r) 2^mu_r G_r(N-r).        (6)

Lean proves that doubling both binomial indices preserves their dyadic
valuation, using the actual binary-digit form of Kummer's theorem. The resulting
UNCONDITIONAL norm identity is

    |E_(2N)-retained|_2
      = 2^(-(4r-1+mu_r)) |choose(N,r)|_2 |G_r(N-r)|_2.

This remains correct if the error is zero. The additive valuation theorem has
an explicit hypothesis G_r(N-r)!=0, because Lean's integer-valued padic
valuation uses zero at the zero argument:

    v_2(error)=4r-1+v_2 choose(N,r)+mu_r+v_2 G_r(N-r).

The zero-error equivalence is separately proved without that hypothesis.

Two actual normalized residual classes now connect directly to the inherited
infinite-series Hensel bridge:

* j_r=0: G_r has unit values everywhere, so it has no dyadic root and mu_r=0.
* j_r=1: G_r has a complete affine binary coefficient certificate. It has one
  and only one dyadic root, and its actual analytic derivative is nonzero there.

In particular, s_2(r)<=3 implies j_r=0 and gives, for EVERY N>=r>0,

    |E_(2N)-retained|_2 = 2^(-(4r-1)) |choose(N,r)|_2.

This small formal scope is not a retraction of the larger manuscript scope.
It identifies which root/row classifications now follow end-to-end from the
original Euler definitions in the Lean project. The larger manuscript atlases
have not all been transported into Lean.

## 11. New modules

| Module | Declarations | Main role |
|---|---:|---|
| ResidualScalars | 10 | Actual beta definition, nonvanishing, integrality and numerator tap bound |
| WeightedTranslation | 9 | Restricted analytic translation via convergent coefficient sums |
| SourceTranslation | 11 | Geometric source coefficients, translation, multiplicative evaluation |
| ResidualSeries | 12 | Actual infinite numerator, double-sum convergence, finite integer evaluation |
| ResidualEvaluation | 11 | Field residual H_r, derivatives, packet formula and value at zero |
| ResidualRows | 10 | Factorial cancellation and exact Euler-tail factorization |
| ResidualTruncation | 9 | Complete numerator packet cutoff and explicit division cost |
| ResidualRecurrence | 7 | Exact block and first-order residual transport |
| ResidualCarry | 15 | Actual digit sums, beta valuation, scalar cost and finite search bound |
| ResidualMinimum | 12 | Constructed global minimum, minimizer set and last minimizer |
| ResidualNormalization | 10 | Integral convergent G_r and exact scaling identity |
| ResidualReduction | 11 | Complete binary residue and actual last odd coefficient |
| ResidualError | 5 | Doubled-binomial valuation, exact norm/valuation/zero-error laws |
| ResidualSimpleCases | 6 | Actual terminal-zero/one cases and sparse exact row law |

These 14 modules have 1,541 source lines including comments and definitions.
The complete 42 mathematical modules have 4,619 lines. All 28 inherited
mathematical modules are byte-for-byte unchanged.

## 12. Remaining formal and mathematical obligations

1. Formalize the terminal arithmetic r=b2^L-j and the full normal form
   G_r=P_j U+2^delta V, including the regular-complement and address theorems.
2. Derive the exact local nearest-neighbor factorization and the numerical
   residue certificates from the newly constructed Euler residuals, with all
   translation, rescaling and omitted-packet precision losses accounted for.
3. Formalize the further closed-disc preparation and coordinate constructions
   needed at persistent multiple-residue branches. The residue and Hensel
   framework already applies once the exact local coefficient identities are
   supplied, but it does not establish those identities by itself.
4. Resolve exact critical-value nonvanishing or classify an actual zero in the
   remaining arithmetic progressions. This remains mathematical research,
   not an obligation automatically discharged by kernel checking.

No new irregular-family atlas or larger research coverage bound is asserted.
No universal Euler simplicity, algebraic squarefreeness, or priority claim is made.

## 13. Execution and trust boundary

See RELEASE_STATUS.json, THEOREM_INDEX.json and evidence/v17_replay*/run.json.
The source index includes all 417 theorem/lemma declarations. Every one is checked
by the compiled `#print axioms` audit. Only `Classical.choice`, `Quot.sound` and
`propext` are permitted. There are no custom mathematical axioms, unfinished
proofs, or native-evaluation proof axioms in the accepted project.

The exact incoming v16 manifest verifies 448 entries. A fresh replay of all 279
incoming declarations passed before development. The final release is checked
in two empty output directories, the second from a separate source-tree copy.
Both use the pinned cached mathlib dependencies. Lean and the entire mathlib
library were not bootstrapped from source here.

The independent exact-rational audit checks r=1..32 and offsets0..24 against
independently generated Euler numbers. It passes 23,660 registered checks,
including 800 whole-error factorizations, 4,320 block identities, and 11,200
numerator packet-tail bounds. These finite checks corroborate the Lean theorems;
they do not supply their universal quantifiers.

### Failures and recovery

The first runtime extraction exceeded the outer tool budget and left one partial
cached dependency. That file was removed and re-extracted from the verified
archive. Resumed extraction completed successfully. The first direct baseline
replay was interrupted by the outer tool timeout after 13 module results; its
raw report is retained as incomplete. A separately launched complete baseline
replay passed all 279 declarations. No incomplete replay is counted as passed.

Development builds rejected coercion/type mismatches, incorrect library names,
small algebraic rewrite scripts, and unused/deprecated tactic syntax. Each was
corrected before the complete clean replays. Diagnostic logs are preserved in
evidence/v17_development and are not mathematical source modules. The temporary
probe file is not part of the release. Verification status is reported from the
final clean replay records, not from these development attempts.

## 14. Reproduction and provenance

Pinned Lean: 4.34.0-rc2.
Pinned mathlib revision: aeb72f1e9981b6d35b426b16dca7759be3e7ba06.

    python3 scripts/verify_manifest.py
    python3 scripts/replay.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --evidence /path/to/NEW_replay
    python3 scripts/check_residual_alignment.py --max-r 32 --max-offset 24 --output /path/to/NEW_check.json

Use new output paths: the tools refuse to overwrite retained evidence. Runtime
binaries and dependency caches are not included in this source release. The
original v16 archive is preserved under history/v16.

The formal summability, restricted-series, p-adic norm/valuation, factorial and
digit-sum APIs used here are the actual pinned mathlib sources. Relevant source
hashes are recorded in PROVENANCE.json. This is an extension of the formal Euler
proof chain, not a historical-priority claim about the classical identities.
