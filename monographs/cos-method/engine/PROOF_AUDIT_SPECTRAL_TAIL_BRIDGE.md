# Proof audit — spectral and tail bridge

Date: 2026-09-23

## Claim A — block-norm domination

Let \(E\) be a self-adjoint operator partitioned by orthogonal phase
projectors \(P_h\), and define

\[
C_{hg}=\|P_hEP_g\|_2.
\]

Then

\[
\boxed{\|E\|_2\le\|C\|_2.}
\]

### Audit

For any \(x\), put \(r_g=\|P_gx\|_2\). Then

\[
\|P_hEx\|_2
\le
\sum_g C_{hg}r_g.
\]

Orthogonality of the phase projectors gives

\[
\|Ex\|_2^2
=
\sum_h\|P_hEx\|_2^2
\le
\|Cr\|_2^2
\le
\|C\|_2^2\|r\|_2^2
=
\|C\|_2^2\|x\|_2^2.
\]

Taking the supremum over unit \(x\) proves the claim.

**Verdict:** proved as written.

---

## Claim B — eigenvalue enclosure after pruning

Let \(H\succeq0\) and let \(H_0=H-E\) be self-adjoint. If
\(\|E\|_2\le\varepsilon\), and the eigenvalues are ordered decreasingly,

\[
\lambda_i(H),\qquad \mu_i(H_0),
\]

then Weyl's inequality gives

\[
|\lambda_i-\mu_i|\le\varepsilon.
\]

Since \(\lambda_i\ge0\),

\[
\boxed{
\max(0,\mu_i-\varepsilon)
\le
\lambda_i
\le
\max(0,\mu_i+\varepsilon).
}
\]

**Verdict:** proved as written.

---

## Claim C — positive quadratic-form tail bracket

Let

\[
\ell_i\le\lambda_i\le u_i,\qquad \ell_i,u_i\ge0,
\]

and let \(Z_i\) be independent standard normals. Define

\[
Q_-=\sum_i\ell_iZ_i^2,\quad
Q=\sum_i\lambda_iZ_i^2,\quad
Q_+=\sum_i u_iZ_i^2.
\]

Using the same \(Z_i\) on one probability space,

\[
Q_-\le Q\le Q_+
\]

almost surely. Therefore for every threshold \(q\),

\[
\boxed{
P(Q_-\ge q)
\le
P(Q\ge q)
\le
P(Q_+\ge q).
}
\]

**Verdict:** proved as written.

---

## Claim D — range-core singular-value enclosure

Let \(U\) have orthonormal columns,

\[
B=U^\top A,\qquad
F=(I-UU^\top)A,
\qquad
\delta=\|F\|_2.
\]

Then

\[
A=UB+F
\]

and \(\|A-UB\|_2=\delta\). The singular values of \(UB\) are the singular
values of \(B\), padded by zeros. Singular-value perturbation therefore gives

\[
\boxed{
|\sigma_i(A)-\widetilde\sigma_i(B)|\le\delta.
}
\]

Squaring the nonnegative endpoints gives valid generalized-\(\chi^2\)
coefficient intervals.

**Verdict:** proved as written.

---

## Important limitation found by computation

The range-core theorem is correct but can be useless for deep-tail
certification when the range residual is not already small.

In the full-rank 50-dimensional stress test, Krylov dimensions 12 through 48
left residual norms approximately \(0.87\)–\(0.99\) relative to the top
singular value. The induced \(10^{-8}\) tail brackets were therefore
vacuous or thousands of decades wide. At dimension 50 the residual fell to
about \(1.2\times10^{-15}\), and the bracket collapsed to the exact
probability.

This is not a theorem failure. It identifies the correct role of the range
certificate: use it as a stopping/certification test, not as a promise that
a very incomplete basis yields a useful full-spectrum tail interval.

---

## Strongest safe statement

A phase-pruned operator can be connected to the final SKAT tail in two
certified ways:

1. Direct route:
   block-norm operator bound -> Weyl coefficient intervals -> stochastic
   generalized-\(\chi^2\) tail bracket.

2. Certify-after-prune route:
   use the pruned operator to generate a candidate range, then evaluate the
   exact factor residual and accept the spectral/tail result only when the
   residual certificate is sufficiently small.

The first route is immediately useful under a small operator-norm budget.
The second route is exact but may require near-complete range capture for
full-spectrum deep-tail guarantees.
