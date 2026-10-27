# Paper IX completion review

Author of the mathematical project: Komorebi P.

This continuation checks the exact `PRSC_IX_v0.11.0_Nishibuchi_Completion`
release identified by the supplied completion audit. Its archive SHA-256 is
`1f02400e73da1d9b6c90a06dcdb5a45c6fd20a4e2addca2a9e638db872cbc721`.

## The external theorem

Let (p) be prime, (m>0), (m\mid p-1) or (m=2), and

\[
N=mp,\qquad 0\le j<N,\qquad q=\operatorname{lcm}(2,p-1).
\]

Use the original coefficients defined by

\[
\sum_{d\ge0}E_d^{(N,j)}\frac{t^d}{d!}
=\left(\sum_{n\ge0}\frac{t^{Nn}}{(Nn+j)!}\right)^{-1}.
\]

The release's capstone proves that every packet coefficient

\[
E_{Nn}^{(N,j)}\in\mathbb Z_p\quad(n\ge0)
\]

is integral and that

\[
E_{Nn+qp^r}^{(N,j)}\equiv E_{Nn}^{(N,j)}\pmod{p^r}
\quad(r\ge1,\ n\ge r).
\]

The threshold (n_0=r) is positive and satisfies the bound suggested immediately
after Conjecture 3.9. The original source and this theorem use positive (r).
The exceptional dyadic case is (p=2,m=2), and every (j<4) is included.

The inspected primary source is Yuta Nishibuchi,
[*p-adic Congruences of Generalized Euler Numbers and Relations to Even Zeta Values*](https://arxiv.org/pdf/2605.10677),
arXiv:2605.10677v2, 1 June 2026. The original PDF's version stamp, Definition 2.1,
Notation 3.2, and Conjecture 3.9 were checked. `EXTERNAL_STATEMENT_AUDIT.md`
records the exact correspondence and proof obligations.

## What completion means

The external Nishibuchi conjecture and Paper IX's native Conjectures 13.2 and
13.3 are different claims. The baseline has 24 of 24 entries from its
manuscript-proved register covered. Its 836 named theorem declarations include
supporting lemmas and examples. Neither number counts the two native conjectures
as proved.

The continuation studies precise forms of the native conjectures. A finite
linear obstruction criterion, a classical finite-presentation specialization,
and a boundary on global reconstruction are separate results. They do not
supply definitions missing from the original universal claims by fiat.

The attached historical audit is preserved as historical evidence. Fresh replay
results are separately dated and recorded. The compiled Mathlib dependency is
the pinned cache used by the baseline. It is not a fresh Mathlib source build.
The independent agent reviews are not external human peer review or a different
proof kernel.

No least-period, earliest-threshold, pointwise-optimal-exponent, or historical
priority claim is made. The new continuation does not rewrite the full original
Paper IX manuscript or rerun Papers I through VIII.
