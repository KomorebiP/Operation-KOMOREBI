# Global radical counting route

Checkpoint ABC-20261025-RR2. The base checkpoint is the archive
`ABC_Square_Kernel_Reverse_Realization_2026-10-25.zip`, SHA-256
`f9e5f22f454acf335f7267e6b69d0ee7c06394bf8744c3c3652fb9dec8ac9b59`.

## Target contract

For each real epsilon > 0, prove that only finitely many ordered positive
integer triples (a,b,c), with a+b=c and gcd(a,b)=1, satisfy
c > rad(abc)^(1+epsilon). This is the full target. No effective bound on the
finite set is required. Equivalently one may prove a uniform bound
c <= K_epsilon rad(abc)^(1+epsilon), for every epsilon > 0. A bound for
one fixed exponent, or a sparse exceptional set, does not complete this target.

## A direct count retaining every prime in the radical

For delta > 0 and positive integer k set

    C(k,delta) = product over primes p of (1 + k/[p(p^delta-1)]).

This product is finite. Indeed,

    1/[p(p^delta-1)]
      <= p^(-1-delta)/(1-2^(-delta)),

and the sum of the right side over primes is at most its convergent sum
over integers n >= 2. The local geometric series gives

    sum over n >= 1 of k^omega(n)/(rad(n) n^delta) = C(k,delta).

The passage to the infinite product is justified by nonnegative terms and
the proved convergence. For real Z,Y >= 1, multiplying the indicator
rad(n) <= Y by Y/rad(n), and using n^delta <= Z^delta, therefore gives

    sum over 1 <= n <= Z, rad(n) <= Y of k^omega(n)
      <= C(k,delta) Y Z^delta.                         (G1)

For k=1 this is a direct bound on integers of small radical. It retains
rad(n), rather than replacing it with the squarefree kernel modulo squares.

## A global count for primitive abc triples

Let B(X,Y) count ordered positive integer triples with a+b=c <= X,
gcd(a,b)=1, and rad(abc) <= Y. Assume X >= 2 and Y >= 1. Pairwise
coprimality implies that each prime power in n=abc is allocated wholly to
one of a,b,c. Thus the number of ordered pairwise coprime factorizations
n=abc is exactly 3^omega(n). The additive condition selects a subset of
these factorizations. Moreover abc <= X^3. Hence (G1) proves

    B(X,Y) <= C(3,delta) Y X^(3 delta).                (G2)

This uses neither independence of prime factors nor a theorem on primes
in arithmetic progressions. The overcount includes factor allocations
that fail a+b=c, which is allowed for an upper bound.

Put s=1/(1+epsilon). Every target exception with c <= X has
rad(abc) < c^s <= X^s. Choosing delta=eta/3 gives, for each eta > 0,

    #{target exceptions with c <= X}
       <= C(3,eta/3) X^(s+eta).                       (G3)

In particular choose eta < 1-s to obtain a sublinear bound in X for the
number of these ordered exceptional triples. This is an unconditional
counting statement covering the full primitive abc family. Historical
originality has not been assessed or asserted.

## Executed attempt and first unresolved implication

The attempted inference was to combine (G3) across dyadic height intervals
and force finitely many exceptions. This inference fails: the upper bounds
grow with the interval height and are not summable. Even a hypothetical
bound X^o(1) would permit infinitely many heights such as 2^(2^j).
Thus no finiteness conclusion follows from this counting route.

The missing ingredient is an estimate using a+b=c strongly enough to
exclude all sufficiently high exceptional allocations. The proof of (G2)
discards that equation after obtaining the size bound on abc. It supplies
no such estimate. Rewriting (G3) as a coherence or realization statement
does not add one.

## Route status and continuation

Outcome: a proved elementary global sparse-count bound, subject to proof
review. Target abc remains unproved. The route is open for an additive
arithmetic refinement. The current positive Euler-product/union-bound
mechanism alone does not imply finiteness. An untried continuation is to
bound only the prime-power allocations satisfying a+b=c, with constants
uniform as the prime support grows. That continuation is deferred because
no estimate supplying the necessary height saving has been established.
The next executable task is to formulate a noncircular additive saving
and test it against known high-quality triples before using it.

## Finite check contract

The accompanying standard-library verifier checks (i) primitive triples
at c <= 600, (ii) exact quality c^10 > R^11, (iii) 3^omega(n) against an
independent enumeration of coprime factor allocations for n <= 500, and
(iv) the local Dirichlet factor at delta=1 by exact rational geometric
partial sums. The universal inequalities are proved above. The finite
run checks implementation and conventions, not the abc conjecture.
