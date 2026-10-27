# AVOC v0.29.0 — minimum-width affine certificates and paid selection

## Model and scope

Column vectors, fields R, arbitrary natural input/output dimensions n,m in the theorems. Runtime: exact GF(5), dimensions 0..8. A map has coefficients (A,b), with A of shape m by n, and evaluates x -> A x + b. `compose g f` executes f first.

## 1. Two independent witnesses

An untrusted candidate supplies intermediate width r, affine maps f:R^n -> R^r and g:R^r -> R^m, and matrices U (r by m), V (n by r).

The executable gate checks

\[
  g\circ f=(A,b),\qquad U A V=I_r.
\]

The first equality checks both linear coefficients and affine offsets. It proves exact execution and rank(A)<=r. The second proves r<=rank(A), using the standard matrix-rank product inequalities in pinned mathlib. Thus rank(A)=r.

For every exact two-stage affine factorization through any dimension k, rank(A)<=k. Therefore r<=k. This is not a finite candidate comparison: the checked lower bound quantifies over every exact two-stage affine factorization over the field.

Key declarations: `Factorization.checked_optimal`, `width_minimal`, `valid_rank_exact`.

## 2. Minimum intermediate width implies minimum declared two-stage cost

Inherited dense tariff: D(n,m)=m(2n+1). A two-dense-map plan through k costs

\[
 F(n,m,k)=k(2n+1)+m(2k+1).
\]

This is strictly increasing in k. Hence a valid width-r certificate proves minimum F among ALL exact two-stage dense affine implementations, including nonzero first and second offsets.

It does not prove minimum physical runtime, sparse arithmetic, shared-subexpression circuits, arbitrary multi-stage programs, or identity-aware primitive algorithms.

## 3. Keep the current plan as an option

The selector compares the original typed program, its one-dense-map normal form, and the checked rank factorization. It prefers the incumbent on ties. The selected plan is exactly equivalent and no more expensive per call than the original or either candidate. It is no more expensive than any exact two-stage dense factorization.

This protects an identity program with zero declared cost and a pre-existing cheap bottleneck. Semantic normalization does not force densification.

## 4. Search and checking are not free

Let G be the metered proposer charge, N the reference normalization tariff, and K the certificate-check tariff. U=N+G+K remains charged regardless of whether a factor, fused normal form, or original is selected.

For T future calls and selected per-call cost c', the modeled campaign total is U+T c'. Because c'<=c, the exact break-even condition is

\[
 U+T c'\le T c\quad\Longleftrightarrow\quad U\le T(c-c').
\]

No saved call cost means no positive campaign gain. No claim is made that running the search is optimal before its result is known. The lower-bound gate is resource checked, but the direct wire's G is a declared external meter input. The protected Python configuration does not allow users to replace its generated meter result.

The nominal K is `composeCost n r m + 2*r*m*n + 2*r*n*r + m*(n+1) + r*r`: composing the two affine maps, checking the lower witness, and comparing coefficients. It is not an exhaustive tally of all operations in the Lean runtime. In particular duplicate normalizations/evaluation, parser work, copying, allocation, serialization, process startup, and arithmetic bit complexity are not all counted.

## 5. Candidate generation

The Python proposer performs row reduction with tracked row operations over GF(5): R=T A. Pivot columns of A form C; nonzero rows of R form D; the same rows of T form U; V selects the pivot columns. It returns f(x)=D x and g(y)=C y+b. Thus proposed identities are C D=A and U A V=I_r.

This generator is NOT trusted for acceptance. Lean recalculates the original AST semantics and the two identities. Theorems certify every accepted candidate even if a future proposer uses a different method. Universal correctness/completeness or asymptotic complexity of this Python implementation is not formally proved here.

The generator is interrupted before any metered operation that would exceed its allowance. Both its own normalization and the later Lean reference-normalization tariff are accounted separately. Budgets limit declared operations, not all physical work.

## 6. Concrete outcomes

The all-ones 4x4 map with offset (1,2,3,4) gets width 1, with 36 -> 21 per-call tariff. Proposer charge is 91, certificate charge 105, so total setup is 196. At 13 calls the net is -1; at 14 calls it is 14; at 1,000 calls it is 14,804. At one call the net is -181.

A constant 2->3 map gets width zero and 15 -> 3 per-call tariff. An identity AST retains cost zero. The inherited 2->3->2 full-rank example selects dense fusion (29 -> 10), not its 20-unit two-stage factor. The inherited 4->1->4 bottleneck retains its original 21-unit implementation and reports the sunk search loss.

The positive library separately proves rejected wrong-bias and invalid rank-lower-witness cases. An equivalent padded factorization is not automatically a minimum-width certificate. Conversely, distinct valid U,V witnesses are permitted: changing a witness in a nullspace can preserve U A V=I.

## Attribution

Matrix rank and Gaussian/rank factorization are established linear algebra. The contribution here is an AVOC certificate interface, proof-carrying selection, explicit accounting, and execution evidence. See pinned `Mathlib.LinearAlgebra.Matrix.Rank` and its `rank_mul_le_left`, `rank_mul_le_right`, `rank_one`, `rank_le_width` declarations. No historical novelty claim is made for those algebraic facts.
