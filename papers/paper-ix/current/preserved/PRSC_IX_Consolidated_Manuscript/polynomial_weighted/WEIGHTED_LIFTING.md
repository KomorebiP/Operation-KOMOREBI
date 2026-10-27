# Paper IX: weighted nonlinear lifting

**Komorebi P. — 8 September 2026.**

## The theorem

Let \(p\) be prime, \(R=\mathbb Z_p\), \(K=\mathbb Q_p\), and \(d,s,r\in\mathbb N\).
Let \(F=(F_1,\ldots,F_d)\in R[X_1,\ldots,X_d]^d\), \(a\in R^d\), and let
\[
J=DF(a)=\bigl(\partial_jF_i(a)\bigr)_{i,j}.
\]
Assume
\[
J\in\operatorname{GL}_d(K),\qquad p^sJ^{-1}\in M_d(R),\qquad
F(a)\in p^rR^d,\qquad r>2s.
\]
Then
\[
\boxed{\exists!\,b\in a+p^{s+1}R^d:\ F(b)=0,}
\qquad
\boxed{b-a\in p^{r-s}R^d.}
\]
All vector divisibility assertions are coordinatewise. The uniqueness predicate is the
entire ball of depth \(s+1\): competitors need not be assumed to have depth \(r-s\).
The theorem permits arbitrary integral p-adic coefficients and centers, every prime
including two, and dimension zero. It retains the supplied inverse-denominator
exponent \(s\); there is no replacement by a determinant valuation. Integrality of
\(p^sJ^{-1}\) is expressed in Lean by existence of an integral matrix with exactly that
image under the coefficient inclusion \(R\hookrightarrow K\).

## Proof

Write \(A=p^sJ^{-1}\in M_d(R)\). Then
\[
AJ=JA=p^sI.
\]
The formal matrix bridge proves the equivalence with the stated fraction-field
hypotheses, including nonsingularity. In particular, multiplication by \(A\) is
injective, since multiplication by \(J\) sends \(Av=0\) to \(p^sv=0\).

Put \(G=AF\), \(t=p^{s+1}\), and \(k=r-(2s+1)\). Taylor expansion of the
actual preconditioned polynomials gives one polynomial system \(Q\) such that
\[
G(a+tu)=G(a)+p^{2s+1}u+p^{2s+2}Q(u),\qquad Q(0)=0.
\]
This expansion is proved first over every commutative ring. Its remainder is a
polynomial valid for every \(u\), not a pointwise quotient depending on \(u\).
Since \(G(a)\in p^rR^d\), it can be written \(p^{2s+1}C\) with \(C\in p^kR^d\).
Thus
\[
G(a+tu)=p^{2s+1}\bigl(C+u+pQ(u)\bigr).
\]

Integral polynomial evaluation is 1-Lipschitz in the supremum p-adic metric.
Consequently \(T(u)=-C-pQ(u)\) has contraction constant \(|p|_p<1\) on the
complete space \(R^d\), and has exactly one fixed point \(u\).

For completeness, the sharp precision is additional to this fixed-point existence.
Inductively, if \(u\in p^nR^d\), then polynomial congruence and \(Q(0)=0\) imply
\(Q(u)\in p^nR^d\). For \(n<k\), the equation \(u=-C-pQ(u)\) therefore gives
\(u\in p^{n+1}R^d\). Starting at \(n=0\), this proves \(u\in p^kR^d\).
Hence \(b=a+tu\) satisfies
\[
b-a\in p^{s+1+k}R^d=p^{r-s}R^d.
\]
The normalization and injectivity of \(A\) give \(F(b)=0\).

Every other \(z\in a+p^{s+1}R^d\) has the form \(a+tw\). If \(F(z)=0\),
the same normalization, with cancellation of the nonzero scalar \(p^{2s+1}\),
gives \(w=T(w)\). Fixed-point uniqueness implies \(w=u\), hence \(z=b\).

## Boundary and sharpness

The strict inequality cannot in general be weakened to \(r\ge2s\): for \(p=2\),
\(F(X)=X^2+3\), and \(a=1\), we have \(F(a)=4\), \(DF(a)=2\), and may take
\(s=1,r=2\). Yet no root exists in \(\mathbb Z_2\), since there is none modulo eight.
The auxiliary Lean controls prove this obstruction and the exact residual depth.

The displacement exponent cannot uniformly be increased by one. For
\(F(X)=p^sX+p^r\) at \(a=0\), with \(r>2s\), its root is
\(b=-p^{r-s}\), which is not divisible by \(p^{r-s+1}\). The controls prove the
linear root and the absence of that extra digit for all primes.

## Formal statement map

| Module | Verified role |
|---|---|
| `PolynomialTaylorRing.lean` | Polynomial Taylor remainder over any commutative ring; remainder vanishes at zero; evaluation congruences. |
| `PolynomialPadicContraction.lean` | Actual polynomial evaluation is 1-Lipschitz; unique fixed point for \(c+pH\); inheritance of arbitrary constant precision when \(H(0)=0\). |
| `PolynomialWeightedInverse.lean` | Actual Jacobian and preconditioning; exact equivalence of the rational inverse bound and the integral certificate; preservation of roots. |
| `PolynomialWeightedNormalization.lean` | Derives \(AF(a+p^{s+1}u)=p^{2s+1}(C+u+pQ(u))\) from the actual system. |
| `PolynomialWeightedLift.lean` | Full lifting theorem, integral-certificate version, rational-inverse version, and full-ball unique-existence version. |

The principal entry points are
`Komorebi.PolynomialWeightedLift.exists_weighted_root` and
`Komorebi.PolynomialWeightedLift.exists_unique_weighted_root`.
The five new mathematical modules contain 37 theorems and seven definitions.
They use the pinned Lean 4.34.0-rc2 / Mathlib environment of the previous release.
The fresh report, external statement contracts, axiom audit, and independent
proof review accompany this note. Compilation failures during development are
retained with their corrections; they are not represented as successful runs.

## What this closes and what remains

This closes the written weighted lifting theorem for square systems with Jacobian
invertible over the fraction field, including those singular modulo \(p\).
The previous continuous rectangular charts remain available with their recorded
integer-coefficient and integer-center interfaces. Those chart interfaces are
not automatically generalized by this square theorem.

The next formalization is weighted perturbation and its first-order estimate.
Starting with \(F(a)=0\), \(G=F+p^MH\), \(M>2s\), and the same bound on
\(DF(a)^{-1}\), the written target is a unique nearby root \(b\) with
\[
b-a=-p^MDF(a)^{-1}H(a)+\varepsilon,
\qquad \varepsilon\in p^{2M-3s}R^d.
\]
The new lifting theorem by itself does not provide this expansion: the next proof
must either control the perturbed Jacobian with the same inverse bound or solve
the perturbed equation using the original preconditioner, and must estimate the
nonlinear and coefficient-variation terms. First-order motion remains written,
not Lean-certified, in this release.

Rationally rank-deficient systems, higher obstructions, analyticity, native
presentation invariance, and global/completed descent remain separate obligations.
No new external novelty claim is made here.
