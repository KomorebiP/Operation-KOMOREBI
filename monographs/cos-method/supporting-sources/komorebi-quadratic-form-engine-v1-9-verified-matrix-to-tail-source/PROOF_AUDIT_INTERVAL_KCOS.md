# Directed-rounding K-COS enclosure audit — v1.4

Date: 2026-09-24

## Scope

This block establishes a first end-to-end **numerical enclosure** for the
positive central quadratic-form tail when the positive spectrum itself is
supplied as exact decimal input.

The backend uses `mpmath.iv` interval arithmetic.  The local implementation
constructs interval endpoints with downward/upward rounding in mpmath's
`libmp` interval layer.  The mathematical guarantee is therefore conditional
on the correctness of that interval-library implementation, as is standard
for software-assisted interval numerics.

This block does **not** yet certify the preceding eigensolver that may have
produced an arbitrary floating-point spectrum.  Matrix-to-spectrum
certification remains a separate layer.

## Setup

Let

\[
Q=\sum_{j=1}^r \lambda_j Z_j^2,
\qquad
\lambda_j>0,
\]

and choose any

\[
0<\theta<\frac{1}{2\lambda_{\max}}.
\]

No exact saddlepoint is required for correctness.

Under exponential tilting,

\[
P(Q\ge q)
=
e^{K(\theta)-\theta q}
S_\theta(q),
\]

where

\[
S_\theta(q)
=
E_\theta[
e^{-\theta(Q-q)}
1_{\{Q\ge q\}}
].
\]

The implementation encloses the prefactor and a finite COS approximation to
\(S_\theta(q)\) by directed rounding, then enlarges that interval by analytic
support/alias and omitted-mode bounds.

## Lemma 1 — tilted characteristic-function decay

Define

\[
a_j=\frac{2\lambda_j}{1-2\theta\lambda_j}.
\]

The normalized tilted characteristic function satisfies

\[
|\phi_\theta(t)|
=
\prod_{j=1}^r
\left(1+(a_jt)^2\right)^{-1/4}.
\]

Since

\[
1+(a_jt)^2\ge(a_jt)^2,
\]

for \(t>0\),

\[
\boxed{
|\phi_\theta(t)|
\le
C_\theta t^{-r/2},
\qquad
C_\theta=
\prod_j a_j^{-1/2}.
}
\]

Verdict: proved.

## Lemma 2 — payoff coefficient bound

For

\[
I_k
=
\int_q^U
e^{-\theta(x-q)}
\cos(k\pi x/U)\,dx,
\]

\[
|I_k|
\le
\int_q^U e^{-\theta(x-q)}\,dx
\le
\frac{1}{\theta}.
\]

Verdict: proved.

## Theorem 1 — omitted COS-mode bound

Let

\[
p=\frac r2>1.
\]

For modes \(k\ge K\),

\[
u_k=\frac{k\pi}{U}.
\]

Combining Lemmas 1 and 2 gives

\[
|R_K|
\le
\frac{2}{U\theta}
C_\theta
\left(\frac{U}{\pi}\right)^p
\sum_{k=K}^\infty k^{-p}.
\]

Using

\[
\sum_{k=K}^\infty k^{-p}
\le
K^{-p}
+
\frac{K^{1-p}}{p-1},
\]

we obtain the implemented bound

\[
\boxed{
|R_K|
\le
\frac{2C_\theta}{U\theta}
\left(\frac{U}{\pi}\right)^p
\left(
K^{-p}+\frac{K^{1-p}}{p-1}
\right).
}
\]

Verdict: proved for \(r>2\).

## Theorem 2 — support and periodization alias bound

Choose any

\[
\theta<\eta<\frac{1}{2\lambda_{\max}}.
\]

Chernoff under the tilted measure gives

\[
P_\theta(Q>U)
\le
\exp\{
K(\eta)-K(\theta)-(\eta-\theta)U
\}.
\]

The infinite cosine series formed from the full characteristic function is
the cosine periodization of the tilted density on \([0,U]\).  Because the
original quadratic form has support on \([0,\infty)\), the total positive-tail
mass aliased back into one fundamental interval is at most
\(P_\theta(Q>U)\).

The actual omitted payoff above \(U\) is at most

\[
e^{-\theta(U-q)}P_\theta(Q>U).
\]

Hence

\[
\boxed{
E_{\rm support+alias}
\le
P_\theta(Q>U)
\left(
1+e^{-\theta(U-q)}
\right).
}
\]

Verdict: proved.

## Theorem 3 — final interval enclosure

Let \(\boldsymbol S_K\) be the directed-rounding interval enclosure of the
finite \(K\)-mode tilted COS sum and let

\[
E=E_{\rm support+alias}+E_{\rm series}.
\]

Then

\[
S_\theta(q)
\in
\boldsymbol S_K+[-E,E].
\]

If the resulting lower endpoint is positive, directed rounding of

\[
K(\theta)-\theta q+\log S_\theta(q)
\]

gives an interval

\[
\boxed{
\log p\in[\ell_-,\ell_+]
}
\]

and therefore

\[
\boxed{
\log_{10}p
\in
[d_-,d_+].
}
\]

The multiplicative uncertainty ratio obeys

\[
\frac{p_+}{p_-}
\le
10^{d_+-d_-}.
\]

Verdict: proved, conditional on correctness of the interval arithmetic
implementation.

## Independent exact control

For

\[
Q=c\chi^2_\nu
\]

with even \(\nu=2n\),

\[
P(Q\ge q)
=
e^{-x}
\sum_{k=0}^{n-1}
\frac{x^k}{k!},
\qquad
x=\frac{q}{2c}.
\]

This finite expression was evaluated independently using the same
directed-rounding interval primitives, without K-COS.

For

\[
Q=0.02\chi^2_{80}
\]

the K-COS enclosure and the exact finite-sum enclosure overlap at all three
tested depths:

\[
10^{-100},\qquad
10^{-1000},\qquad
10^{-5000}.
\]

With \(K=128\) and 90 interval decimal digits, the K-COS widths were
approximately

\[
8.95\times10^{-13},
\quad
6.94\times10^{-12},
\quad
3.37\times10^{-11}
\]

decades respectively.

At \(10^{-5000}\), the last width corresponds to a multiplicative uncertainty
of approximately

\[
7.75\times10^{-11}.
\]

## Arithmetic versus analytic width

At the \(10^{-5000}\) control, increasing interval precision from 40 to 120
decimal digits changed the total certified width negligibly:

\[
3.34247\times10^{-11}\text{ decades}.
\]

Over the same sweep, the arithmetic-only interval width contracted from about

\[
7.5\times10^{-37}
\]

to

\[
6.3\times10^{-117}
\]

decades.

Thus the current rigorous enclosure is controlled by the explicit analytic
support/series remainder, not by interval-rounding uncertainty.

## Strongest safe statement

For exact positive decimal spectra of rank greater than two, the v1.4 backend
returns a directed-rounding logarithmic probability enclosure enlarged by
proved analytic support/alias and omitted-COS-mode error bounds.

The tested scaled-chi-square controls rigorously overlap their independently
interval-evaluated exact tails through \(10^{-5000}\).

## Remaining boundary

A fully end-to-end guarantee starting from an arbitrary floating-point matrix
still requires a certified matrix-to-spectrum layer or exact residual
completion with rigorously enclosed linear algebra.

The current packetized compression layer has not yet been ported to interval
arithmetic; v1.4's first rigorous backend uses the exact supplied spectrum.
