# Separate self-review

Author: Komorebi P.
Checkpoint: SEQ-DH-2026-11-20-001.
Review provenance: **self-review, not independent review**.
This publication carries the source-level proofs and portable verifiers.
The earlier local checkpoint and its retained inputs are identified by
SEQ-DH-2026-11-20-001. Publication checks and exact output records are under
verification/sequence-library/rational-hankel/.

Primary verdict: **proved as written**, for Theorems A--F in
RATIONAL_HANKEL_TAILS.md and LINEAR_WEIGHT_RECURRENCE.md, with Theorem F
using the explicitly bounded, complete polynomial-identity computation.
This verdict is not a Lean certificate or a historical-novelty assessment.

## Claim cards and dependency graph

- A: characteristic-zero polynomial P and finite constant-coefficient
  differential operator; every fixed-parameter Hankel determinant sequence has
  a rational OGF. Zero inputs and M=0 have separate formulas. For M>=1 the
  stated general annihilator bound is binom(8M,4M), from index 8M+1.
- C: for nonzero actual degree/order inputs, maximum separated Chebyshev
  rank is exactly 2(D+r); the balanced separated minor product is (5).
- D--E: noncancellation at both quadratic branch points, algebraic degree
  exactly two, and the common rational kernel Phi(t)=1+t^2 for all moments.
- F: the explicit order-nine recurrence and numerator for every linear
  weight; recurrence begins at n=1; minimal order nine is asserted at a=b=1
  and generically, not at all parameters.

Dependencies:

    monomial functional -> Chebyshev derivative products -> E,O
      -> exact Hankel/Toeplitz/corner decomposition
        -> boundary-safe banding -> stationary signed states -> A
      -> leading coefficient -> parity Vandermonde factors -> C
    algebraic moment numerator iteration -> endpoint noncancellation -> D
      -> formal quadratic parametrization/coefficient transfer -> E
    fixed M=1 transfer + degree bounds + full vector certificates -> F
      -> early direct determinant certificates -> starting index n=1
      -> numerator coefficients + exact Bezout identity -> sample minimality

The primary literature comparison is adjacent attribution, not a load-bearing
replacement for the proof's explicit signed transfer.

## Obligation matrix

| Obligation | Outcome | Decisive check |
|---|---|---|
| Object and coefficient domain | passed | Characteristic-zero polynomial functionals; executable specialization is Q |
| Chebyshev endpoint | passed | C_0=2, det G_N=4W_N for N>=1 only |
| Polynomial branch degree and top coefficient | passed | Constant-term derivation and weight ladder below |
| Entire boundary is banded | passed | Full row stencil annihilates both terms for i>j+4M; corner support is finite |
| Stationary starting row | passed | i>=8M+1 forces every in-band column >=4M+1 |
| Finite sections are coherent | passed | Lower triangular Q uses only earlier indices |
| Transfer path set | passed | Exactly w occupied sliding positions; acceptance means a permutation of columns 0,...,N-1 |
| Determinant signs | passed | New inversions equal occupied positions greater than the selected position |
| All singular minors | passed | State transitions use multiplication/addition, never pivot division |
| Rationality, not merely D-finiteness | passed | Finite constant resolvent in equation (4) |
| Rank lower bound | passed | Both coefficient matrices are triangular and invertible; all balanced Vandermonde factors nonzero |
| Branch poles and rational amplitude | passed | Endpoint values in (6) nonzero; no hidden cancellation |
| Uniform linear-weight certificate | passed | Degree-18 complete vector residual; 19 distinct evaluations |
| Early indices for Theorem F | passed | Degrees 10 through 17; direct monomial determinants through size 17 |
| Minimality scope | passed | Explicit Bezout identity at one parameter; nonzero resultant gives generic assertion |
| Historical originality | out of scope | Partial source check does not establish priority |
| Efficient general recurrence extraction | not addressed | General state bound is exponential; M=2 extraction timed out |
| Independent review / Lean | out of scope | Not performed |

## Reconstruction of the retained algebraic leaf

The arcsine functional is algebraic: F_0[f] is the constant term of
f(t+t^{-1}). Thus no analytic measure hypothesis is needed over a general
characteristic-zero field.

The Chebyshev generating series is
(2-xz)/(1-xz+z^2) = 1+(1-z^2)/(1-xz+z^2).
Its k-th x derivative for k>=1 is
k! z^k (1-z^2)/(1-xz+z^2)^(k+1).
Substituting x=t+t^{-1}, taking the constant term, and comparing z^(k+2q)
gives

    k! [binom(k+q,q)^2-binom(k+q-1,q-1)^2]
      = (k+2q)(k-1)! binom(k+q-1,k-1)^2.

This recovers the positive-index derivative formula, with zero coefficients
at the excluded parity or n<k. For k=0 the unperturbed positive-index
Chebyshev moments vanish.

The functional identities

    F_(d+1)[f] = F_d[x f']/2 - d F_d[f],
    F_d[(4-x^2) f'] = (1-2d) F_d[x f]

follow on monomials by the central-binomial ratio and the falling-factorial
identity, including the initial zeros, and hence on every polynomial.
Apply them to the k-times differentiated Chebyshev ODE to obtain the
weight-raising ladder. At its excluded d=k=0 endpoint, direct constant-term
extraction gives F_1[C_n]=n for positive even n and zero for odd n.
The stated product for k=0,d>=1 follows. Every total-(d+k) branch has top
coefficient 1/[4^(d+k-1)(d+k-1)!]. The unique top aggregate term is a_D c_r.
This verifies the precise leaf used for rank and banding.

## Adversarial failures retained

1. The smaller stencil (1-E^2)^M leaves infinite boundary tails. Its explicit
   residual 4 at P=1,D=1+partial is preserved; the proof uses the larger
   stencil instead.
2. A finite matching scalar prefix would not certify an infinite recurrence.
   The implementation verifies the complete transfer vector.
3. The initial certificate verifier accepted the all-zero coefficient list
   as a vacuous vector relation. Shape/nontriviality checks were added before
   the final run, and 30 malformed certificate cases now fail as required.
   No theorem or valid constructed certificate changed.
4. The 60-second M=2 full-state elimination timed out with 12,740 active
   coordinates. It is resource inconclusiveness, not a failure of A.
5. A zero coefficient in a characteristic polynomial does not justify
   reducing its forward order or moving its starting index. The proof uses
   the monic forward characteristic and checks all early indices separately.

## Executed evidence and freshness

- Published baseline: 14 existing tests passed before continuation edits.
- Original general verifier: computation sequence-differential-continuation-002,
  completed, 3,830 exact checks at the local checkpoint.
- Original uniform certificate: computation sequence-differential-linear-002,
  completed, 19 full vector identities, 152 early identities, 342 direct
  determinants, 115 additional checks, and a checked Bezout identity.
- Earlier -001 successes are historical and superseded by the -002 runs.
  The mixed-001 timeout is retained with its original hashes and is not a
  current proof dependency.

For this publication, tools/verify_sequence_rational_hankel.py and
tools/verify_sequence_linear_hankel.py rerun those checks from the portable
source tree. The linear numerator implementation is additionally compared
with direct determinants and a separately implemented BigInt calculator.
The source bundle contains all required modules and verification scripts.

No mathematical implication in A--F remains dependent on the timed-out
experiment. Practical small-order extraction for genuinely mixed higher
degree/order inputs remains open for a later phase.

## Proofreading

Scope: both new proof notes and this review. Routine edits: none required.
Mathematical-token changes during the separate proofreading pass: none.
The proofs distinguish moments from determinants, actual degree from degree
bounds, finite evidence from the uniform reduction, and eventual from initial
recurrences. New displays, indices, table coefficients, and local references
were checked. Existing published prose was not edited.
