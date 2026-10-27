# Lehmer residual attempt: exact identities and failed transfer hypotheses

26 September 2026. **Status: Lehmer's conjecture is not proved.**

This is a standalone audit of the formulas in the current discussion. It is not a replacement for, or a verified continuation of, any earlier Euler research archive. No historical-priority claim or Lean-verification claim is made.

## 1. What the proposed four-layer lemma actually asserts

Write

\[
S_j(p)=\sum_{k=1}^{p-1}k^j\sigma(k)\sigma(p-k).
\]

For prime p, the exact convolution identity is

\[
\tau(p)=p^4 C(p)-840 S_4(p),\qquad
C(p)=85-49p-84p^2+50p^3.
\]

For p>7, 840 is invertible modulo p^4. Consequently

\[
p^4\mid S_4(p)\iff p^4\mid\tau(p).
\]

Thus the proposed lemma p^4 does not divide S_4(p) demands that v_p(tau(p)) <=3. This is a stronger sufficient assertion than nonvanishing. Merely renaming the coefficient as a convolution does not prove that valuation bound.

Deligne's estimate gives |tau(p)| <=2 p^(11/2)<p^6 for p>=5. Therefore

\[
\tau(p)=0\iff\tau(p)\equiv0\pmod{p^6}.
\]

For p>7, this is equivalent to

\[
S_4(p)\equiv p^4 C(p)/840\pmod{p^6}.
\]

When p^4 divides S_4, the last condition is

\[
840\,S_4(p)/p^4\equiv85-49p\pmod{p^2}.
\]

These are exact reductions, not a proof that the forbidden residue never occurs.

## 2. Complete differential extraction of the residual

Let D=q d/dq, A=sum sigma(n)q^n, and B=sum sigma_3(n)q^n. Thus E2=1-24A and E4=1+240B.

Use the classical Ramanujan relations

\[
DE_2=(E_2^2-E_4)/12,\quad
DE_4=(E_2E_4-E_6)/3,\quad
DE_6=(E_2E_6-E_4^2)/2.
\]

In Q[E2,E4,E6], exact differentiation gives

\[
E_2D^2E_2=4D^3E_2+\frac3{10}D^2E_4
\]

and

\[
E_2D^4E_2=\frac{12}{5}D^5E_2+\frac17D^4E_4-\frac{24}{35}\Delta.
\]

Here Delta=(E4^3-E6^2)/1728. The same differential relations give DDelta=E2 Delta. Since its leading term is q, this identifies it with q product_(n>=1)(1-q^n)^24: both solve this first-order formal differential equation with the same leading coefficient.

Substituting A and B yields the full generating-series identity

\[
\boxed{\Delta=50D^4B+35D^4A-84D^5A-840A D^4A.}
\]

Therefore, for every n>=1,

\[
840\sum_{k=1}^{n-1}k^4\sigma(k)\sigma(n-k)
=n^4[50\sigma_3(n)+(35-84n)\sigma(n)]-\tau(n).
\]

The cusp contribution survives with coefficient -1/840. For p>7 this is a p-adic unit. Eliminating the divisor-sum part therefore leaves the original unknown coefficient without an automatic extra power of p.

`check_differential_projector.py` verifies these as zero polynomial remainders and checks the resulting second- and fourth-moment identities for every 1<=n<=512 against independently generated tau coefficients.

## 3. The independent triangular inversion

Define

\[
s_{2j}(p)=\frac12\sum_{|t|<2\sqrt p}t^{2j}H(4p-t^2).
\]

The Eichler-Selberg trace identities give

\[
\sum_{j=0}^r(-1)^{r-j}\binom{r+j}{r-j}p^{r-j}s_{2j}(p)
=-1-\operatorname{tr}T_{2r+2}(p),\quad r\ge1.
\]

Together with s0(p)=p, this is a unit lower triangular system. Its inverse coefficients are

\[
\left[\binom{2r}{r-j}-\binom{2r}{r-j-1}\right]p^{r-j}.
\]

This Catalan inversion is classical, not a new result of this attempt. The trace vanishes at weights 4,6,8,10 and equals tau(p) at weight 12. In particular

\[
s_{10}(p)=42p^6-90p^4-75p^3-35p^2-9p-1-\tau(p).
\]

The inverse's last diagonal entry is one. Hence the cusp coefficient again survives. Setting that coefficient formally equal to zero does not contradict the linear system. Actual nonvanishing requires an additional arithmetic property of the Hurwitz sums, not just inversion.

The audit checked both inverse products through a 32 by 32 matrix and independently enumerated reduced positive definite binary quadratic forms for all primes through 499 and p=2411. All 96 prime rows matched the tau coefficients generated from the Jacobi series.

## 4. Exact counterexample to the proposed integral dyadic model

Consider the proposed interpolation F(u)=tau(2^14 u-1)/2^14 at prime arguments. Take

\[
(u_1,p_1)=(15,245759),\quad (u_2,p_2)=(47,770047).
\]

Both indices are prime. Exact integer calculations give

\[
\tau(245759)=77900595298037436891536424960,
\]

\[
\tau(770047)=-379872617393156753656047295381504.
\]

The respective dyadic valuations are 17 and 14. Modulo 2^19, the residues are 393216 and 147456. Thus

\[
F(15)\equiv24\pmod{32},\quad F(47)\equiv9\pmod{32},
\]

whereas 47-15=32. In particular

\[
v_2(F(47)-F(15))=0<5=v_2(47-15).
\]

Every power series in Z2< u > is 1-Lipschitz: subtracting its values factors by x-y with an integral convergent quotient. Therefore no single integral restricted power series can match this F on all prime arguments. This refutes the exact Euler-style integral interpolation being proposed.

It does NOT refute finer residue-class models, models with denominators, models retaining additional arithmetic variables, or Lehmer's conjecture. Different valuations on their own would not disprove analyticity. The actual obstruction is the displayed failure of the required divided-difference integrality.

The large-index calculation was independently checked from the defining q-series using integer number-theoretic transforms modulo two odd primes, CRT reconstruction under a verified bound, and reduction modulo 2^19. No floating-point approximation was used.

## 5. A classical obstruction to a fixed-modulus proof

Serre proves that for every fixed M>=1, the set of primes p with tau(p)=0 modulo M has positive density. This is explicitly stated in Section 1, example 3, printed page 20-02 of his 1974/75 seminar paper.

Thus no fixed finite modulus can be used to show that the tau residue is nonzero at every prime. This includes any fixed power of 2 or any product of finitely many fixed prime powers. A Frobenius explanation is that complex conjugation supplies a trace-zero conjugacy class in the finite Galois quotient, and Chebotarev supplies primes with that class.

This does not imply an exact zero: the primes may change with M. Nor does it invalidate the index-dependent p^6 criterion. It specifically excludes the idea that a fixed congruence depth alone eventually removes all prime candidates.

## 6. Actual finite evidence

- Exact tau coefficients through n=20000, with a separate direct product check through n=128.
- All five divisor moments and both tau convolution formulas checked at all 2262 primes <=20000.
- The p^4 divisibility equivalence checked at every prime >7 in that range.
- Exact large-prime convolution checks at 12 selected indices through 1032191.
- 19 independent q-series residue comparisons modulo 2^19, including both interpolation counterexample indices.
- 1056 entries checked in both products for a 32 by 32 Catalan inverse.
- 96 independent Hurwitz-moment prime rows.
- Four symbolic differential identities and 1024 coefficient checks.

At p=2411, the exact data are

\[
\tau(p)=4542041100095889012,\quad S_4(p)=28168797627693083506845.
\]

Both valuations are one. Their normalized residues are tau(p)/p=150 modulo p and S4(p)/p=947 modulo p, satisfying -840*947=150 modulo p.

These tests validate the finite computations and exhibit the interpolation counterexample. They do not prove the desired all-prime nonvanishing statement.

## 7. Remaining proof obligation

The exact remaining target can be retained without strengthening it:

\[
\boxed{840S_4(p)\not\equiv p^4C(p)\pmod{p^6}\quad(p>7).}
\]

The three formulas above express it as a divisor convolution, a differential cusp residual, or a Hurwitz moment residual. No independent uniform inequality or nonzero residue proving this has been established here.

A sufficient stronger target is p^4 not dividing tau(p), but it must not be presented as though the convolution reformulation has proved or made that bound automatic.
