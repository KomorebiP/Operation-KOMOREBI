# Proof audit — trace/moment residual certificate and exact residual completion

Date: 2026-09-23

## Claim A — exact residual decomposition

Let `U` have orthonormal columns and define

\[
B=U^\top A,
\qquad
F=(I-UU^\top)A.
\]

Then

\[
A=UB+F,
\qquad
U^\top F=0,
\]

and hence

\[
\boxed{A^\top A=B^\top B+F^\top F.}
\]

### Audit

The cross terms in

\[
(UB+F)^\top(UB+F)
\]

are `B^T U^T F` and its transpose. Both vanish because `U^T F=0`.
Therefore the unresolved spectral component

\[
R=F^\top F
\]

is positive semidefinite rather than an arbitrary perturbation.

**Verdict:** proved as written.

---

## Claim B — exact residual moments

For

\[
R=F^\top F\succeq0,
\]

define

\[
t=\operatorname{tr}R,
\qquad
v=\operatorname{tr}(R^2),
\qquad
\rho=\|R\|_2.
\]

Then

\[
\boxed{t=\|F\|_F^2,}
\]

\[
\boxed{v=\|FF^\top\|_F^2,}
\]

and

\[
\boxed{\rho=\|F\|_2^2.}
\]

These are direct trace/singular-value identities.

**Verdict:** proved as written.

---

## Claim C — trace–Frobenius–cap MGF envelope

Let

\[
C=B^\top B,
\qquad
H=C+R,
\qquad
c=\lambda_{\max}(C).
\]

For

\[
0<2\theta(c+\rho)<1,
\qquad
\alpha=(1-2\theta c)^{-1},
\]

define the exact Gaussian quadratic-form log MGF

\[
K_H(\theta)
=-\frac12\log\det(I-2\theta H).
\]

Then

\[
\boxed{
K_H(\theta)
\le
K_C(\theta)
+
\theta\alpha t
+
\frac{\theta^2\alpha^2v}
     {1-2\theta\alpha\rho}.
}
\]

### Audit

Factor

\[
I-2\theta(C+R)
=
(I-2\theta C)^{1/2}
(I-2\theta T)
(I-2\theta C)^{1/2},
\]

where

\[
T=(I-2\theta C)^{-1/2}
  R
  (I-2\theta C)^{-1/2}.
\]

Because

\[
\|(I-2\theta C)^{-1/2}\|_2^2=\alpha,
\]

we have

\[
\operatorname{tr}T\le\alpha t,
\]

\[
\operatorname{tr}(T^2)
=\|T\|_F^2
\le\alpha^2v,
\]

and

\[
\|T\|_2\le\alpha\rho.
\]

For every eigenvalue `x` of `T`, with `0 <= x <= alpha rho`,

\[
-\frac12\log(1-2\theta x)
\le
\theta x
+
\frac{\theta^2x^2}
     {1-2\theta\alpha\rho}.
\]

This follows by expanding `-log(1-u)` and bounding every term of degree at
least two by the corresponding geometric series with denominator
`1-2 theta alpha rho`. Summing over the eigenvalues of `T` gives the result.

**Verdict:** proved as written.

---

## Claim D — certified upper tail

For

\[
Q=Z^\top HZ,
\qquad
Z\sim N(0,I),
\]

Chernoff's inequality gives

\[
\boxed{
\Pr(Q\ge q)
\le
\inf_{\theta>0}
\exp\{\widehat K_H(\theta)-\theta q\},
}
\]

where `Khat_H` is the MGF envelope in Claim C and the infimum is restricted to
`2 theta(c+rho)<1`.

Since `H=C+R >= C` in Loewner order,

\[
Z^\top HZ\ge Z^\top CZ
\]

for the same Gaussian vector. Therefore

\[
\boxed{
\Pr(Z^\top CZ\ge q)
\le
\Pr(Z^\top HZ\ge q).
}
\]

This yields a certified two-sided interval when the lower endpoint is evaluated
from the core spectrum and the upper endpoint from the trace/moment Chernoff
envelope.

**Verdict:** proved as written.

---

## Claim E — residual-rank bounds

Let

\[
s=\operatorname{rank}F=\operatorname{rank}R.
\]

If the nonzero eigenvalues of `R` are `r_i`, then

\[
t=\sum_{i=1}^s r_i,
\qquad
v=\sum_{i=1}^s r_i^2,
\qquad
r_i\le\rho.
\]

Hence

\[
\boxed{
s\ge \frac{t}{\rho}}
\]

and by Cauchy-Schwarz

\[
\boxed{
s\ge \frac{t^2}{v}.}
\]

Because every column of `F` lies in the orthogonal complement of `U`,

\[
\boxed{s\le n-\dim U.}
\]

Therefore

\[
\boxed{
\left\lceil
\max\left\{
\frac{t}{\rho},
\frac{t^2}{v}
\right\}
\right\rceil
\le s\le n-\dim U.
}
\]

When the integer lower bound equals the upper bound, the residual rank is
certified exactly.

**Verdict:** proved as written.

---

## Claim F — exact residual completion

Let a compact QR or SVD factorization of the residual be

\[
F=WD,
\]

where `W` has orthonormal columns. Since `F` lies in `U^perp`,

\[
U^\top W=0.
\]

Therefore

\[
\boxed{
A=[U\;W]
\begin{bmatrix}
B\\D
\end{bmatrix}.
}
\]

The left factor `[U W]` is orthonormal, so the nonzero singular values of `A`
are exactly the singular values of the stacked core.

The same identity supports a column-streamed implementation: process residual
blocks, orthogonalize each against the accumulated residual basis, append only
new directions, and pad earlier residual-core blocks with zeros. Future new
basis directions are orthogonal to all earlier residual blocks by construction.

**Verdict:** proved as written.

---

## Computational audits

### Random MGF sweep

- 120 random factor/range cases.
- Four admissible positive tilt values per case.
- 480 total MGF comparisons.
- Both the trace/cap and trace–Frobenius–cap MGF envelopes dominated the exact
  log MGF in every tested case.
- The trace–Frobenius–cap envelope was at least as tight as the trace/cap
  envelope in about 83.5% of the comparisons.

This is finite implementation evidence, not the proof of Claim C.

### Full-rank 50-dimensional stress case

At a true tail probability of `1e-8`, the old coefficient-wise Weyl range-core
interval had widths of approximately:

- depth 4: 90,097 decades;
- depth 5: 16,511 decades;
- depth 6: 3,747 decades;
- depth 7: 2,275 decades;
- depth 8: 1,165 decades.

The trace/moment interval reduced those widths to approximately:

- depth 4: 11.86 decades;
- depth 5: 9.76 decades;
- depth 6: 7.67 decades;
- depth 7: 5.70 decades;
- depth 8: 3.39 decades.

All intervals still contained the exact K-COS probability.

### Exact completion audit

For depths 2 through 8, completing the residual range recovered the full
singular spectrum with relative error between approximately `2e-16` and
`6e-16`. The resulting `1e-8` tail differed from the full-spectrum reference by
less than `1e-14` decades.

At depth 8, the candidate basis had dimension 48 and the moment bounds gave

\[
1.985\lesssim\operatorname{rank}F\le2,
\]

with the second-moment bound equal to two to numerical precision. Thus the
missing rank was certified as exactly two, and two residual directions closed
the spectrum.

---

## Claim boundary

The trace/moment certificate is a rigorous replacement for the gross
coefficient-wise Weyl inflation, but it is still a worst-case orientation
bound. It does not promise a narrow two-sided deep-tail interval while a large
residual subspace remains.

The exact residual-completion theorem is the correct fallback once the missing
range is small enough to capture economically. The production rule supported by
this block is therefore hybrid:

1. continue pruned/streamed Krylov while the residual range is large;
2. monitor residual trace, square-trace, and spectral cap;
3. when the residual rank upper bound is affordable, finish by streamed
   residual completion rather than additional approximate tail bounding.

**Primary verdict:** the theorem chain is proved as written; the numerical
performance claims are computationally verified only in the stated finite
experiments.
