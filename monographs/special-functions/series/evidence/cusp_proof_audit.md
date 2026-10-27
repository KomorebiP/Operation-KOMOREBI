# Independent audit of the principal Abelian cusp

Audit date: 2026-10-07.

This is a separate mathematical review of the local Abelian implication used for Volume III, “Principal edge cusp.” It records an exact argument and its scope. The manuscript was consulted read-only; this audit does not independently re-establish the upstream squarefree counting law or source energy asymptotic.

## Exact claim and hypotheses

Let \(c_k\) be finite nonnegative real numbers for \(k\ge0\), and assume

\[
c_k\sim A k^{-3/2}\quad(k\to\infty),\qquad A>0.
\]

Define \(F(z)=\sum_{k\ge0}c_kz^k\). Then \(F(1)<\infty\), and

\[
F(1)-F(z)\sim 2\sqrt{\pi}\,A\sqrt{1-z}
\qquad(z\uparrow1\text{ through real values}).
\]

The coefficient hypothesis implies summability because its tail is bounded by a constant times \(k^{-3/2}\). Thus the value at \(z=1\) and the termwise difference below are well-defined. The coefficient \(c_0\) cancels from that difference.

## Exact model sum and the integral bridge

For \(0<z<1\), put \(t=-\log z>0\). Define

\[
S(t)=\sum_{k\ge1}k^{-3/2}(1-e^{-tk}),\qquad
f(u)=u^{-3/2}(1-e^{-u}).
\]

Then

\[
\frac{S(t)}{\sqrt t}=t\sum_{k\ge1}f(tk).
\]

The representation

\[
f(u)=u^{-1/2}\int_0^1e^{-su}\,ds
\]

shows that \(f\) is positive and decreasing. Also
\(f(u)\le u^{-1/2}\) and \(f(u)\le u^{-3/2}\), so it is integrable at zero and infinity. Comparing each sampled value with the integrals over its adjacent intervals gives

\[
\int_t^\infty f(u)\,du
\le t\sum_{k\ge1}f(tk)
\le\int_0^\infty f(u)\,du.
\]

These inequalities justify the improper Riemann-sum limit, including both endpoint tails. Integrability alone would not justify such a sampling limit for an arbitrary integrable function; the monotonicity argument is the relevant additional control here.

Integration by parts gives

\[
\int_0^\infty u^{-3/2}(1-e^{-u})\,du
=2\int_0^\infty u^{-1/2}e^{-u}\,du
=2\Gamma(1/2)=2\sqrt\pi.
\]

The boundary term vanishes: \(u^{-1/2}(1-e^{-u})\to0\) at both endpoints. Moreover,

\[
0\le2\sqrt\pi\sqrt t-S(t)
\le\sqrt t\int_0^t f(u)\,du
\le2t.
\]

Hence the model estimate is
\(S(t)=2\sqrt\pi\sqrt t+O(t)\).

## Passage from the coefficient asymptotic

For \(k\ge1\), set \(r_k=c_k-Ak^{-3/2}\). Given \(\varepsilon>0\), choose \(K\) so that \(|r_k|\le\varepsilon k^{-3/2}\) for all \(k\ge K\). Since \(1-e^{-tk}\le tk\),

\[
\left|F(1)-F(e^{-t})-AS(t)\right|
\le t\sum_{1\le k<K}k|r_k|+\varepsilon S(t).
\]

For each fixed \(\varepsilon\), the first sum is finite and contributes \(O(t)\). Divide by \(\sqrt t\), take \(t\downarrow0\), and then take \(\varepsilon\downarrow0\). This proves

\[
F(1)-F(e^{-t})
=2\sqrt\pi A\sqrt t+o(\sqrt t).
\]

Finally, \(-\log z\sim1-z\), so the asserted real cusp follows.

## Remainder distinction

The model sequence \(k^{-3/2}\) has the quantitative \(O(t)\) remainder proved above. The assumption \(c_k\sim Ak^{-3/2}\) alone gives only an \(o(\sqrt t)\) remainder for the actual coefficient sequence. Accordingly, the justified conclusion in the original variable is

\[
F(1)-F(z)=2\sqrt\pi A\sqrt{1-z}+o(\sqrt{1-z}),
\]

with no \(O(1-z)\) remainder supplied by the stated hypotheses.

## Dependency on the source energy law

The arithmetic application sets

\[
c_k=E_{2,2,1}(k),\qquad
E_{a,\beta,q}(k)=\sum_{\substack{n\ge1\\(n,q)=1}}
\mu(n)^2n^{-2a}(1-n^{-\beta})^{2k}.
\]

The source energy law used in the manuscript is

\[
E_{a,\beta,q}(k)\sim
\frac{\delta_q}{\beta}\Gamma(\alpha)(2k)^{-\alpha},
\qquad \alpha=\frac{2a-1}{\beta},
\qquad
\delta_q=\frac1{\zeta(2)}\prod_{p\mid q}\frac p{p+1}.
\]

Its stated upstream counting input is

\[
\sum_{\substack{n\le X\\(n,q)=1}}\mu(n)^2
=\delta_qX+O_q(\sqrt X).
\]

That counting input and its reduction to the source energy law are external dependencies of this local cusp audit. They have not been independently re-proved by this review.

For \(a=\beta=2\), \(q=1\), the source law gives \(\alpha=3/2\), \(\delta_1=6/\pi^2\), and

\[
A=\frac{\delta_1}{2}\Gamma(3/2)2^{-3/2}
=\frac{3}{2^{5/2}\pi^{3/2}}.
\]

The audited Abelian passage therefore yields

\[
\mathcal E(1)-\mathcal E(z)
\sim\frac{3}{2^{3/2}\pi}\sqrt{1-z}.
\]

## Bounded audit conclusion

The generic Abelian lemma is valid under its exact stated hypotheses, and the principal constant is algebraically correct. The monotone integral comparison closes the improper Riemann-sum bridge without an unproved endpoint interchange. The arithmetic cusp follows conditional on the source energy asymptotic and its squarefree counting dependency. This audit establishes that local implication; it does not establish the upstream arithmetic input, a stronger remainder, or a signed Möbius cancellation result.
