# Twenty-three worked algebraic-kernel examples

Author: Komorebi P.

Each example gives its defining sequence, generating function, first terms,
and a worked calculation. We write \(G(x)=\sum_{n\ge0}a_nx^n\),
and the auxiliary series \(T\) is the unique solution of its stated equation
with \(T(0)=0\). The same convention applies to the indexed auxiliary series
in Example 23. The square root of a series with constant term one is taken
to have constant term one. Each displayed list begins at \(n=0\) and
continues across its line breaks. The examples specialize the coefficient
transfer identity and the block formulas proved in the main manuscript.

## Example 1. The binomial theorem

For arbitrary complex \(q,r\), take
\(\Phi(t)=1+qt\) and \(F(t)=1/(1+rt)\). Then

\[
\begin{aligned}
a_n&=\sum_{k=0}^{n}\binom nk q^k(-r)^{n-k}\\
&=(q-r)^n.
\end{aligned}
\]

The auxiliary equation is \(T=x(1+qT)\), so

\[
\begin{aligned}
T&=\frac{x}{1-qx},\\
G(x)&=\frac{1}{1-(q-r)x}.
\end{aligned}
\]

For \((q,r)=(3,1)\), the first terms are

\[
\begin{gathered}
1,\ 2,\ 4,\ 8,\ 16,\ 32,\ 64,\\
128,\ 256,\ 512,\ldots
\end{gathered}
\]

For example,

\[
\begin{aligned}
a_3={}&-1+9\\
&-27+27\\
={}&8.
\end{aligned}
\]

This is the block theorem at \(d=1\), where its algebraic expression is rational.

## Example 2. Central binomial coefficients

Take \(\Phi(t)=(1+t)^2\) and \(F(t)=1\). The defining coefficient is

\[
a_n=[t^n](1+t)^{2n}=\binom{2n}{n}.
\]

With \(T=x(1+T)^2\), the transfer identity gives

\[
G(x)=\frac{1+T}{1-T}=\frac{1}{\sqrt{1-4x}}.
\]

The first terms are

\[
\begin{gathered}
1,\ 2,\ 6,\ 20,\ 70,\ 252,\ 924,\\
3432,\ 12870,\ 48620,\ldots
\end{gathered}
\]

For example, \(a_4=\binom84=70\). This recovers a classical generating
function from the coefficient transfer identity.

## Example 3. Varying the upper binomial index

Let \(h\) be a positive integer. Use
\(\Phi(t)=(1+t)^h\), \(F(t)=1\), and

\[
a_n=[t^n](1+t)^{hn}=\binom{hn}{n}.
\]

Then

\[
\begin{aligned}
T&=x(1+T)^h,\\
G(x)&=\frac{1+T}{1-(h-1)T}.
\end{aligned}
\]

For \(h=3\), the first terms are

\[
\begin{gathered}
1,\ 3,\ 15,\ 84,\ 495,\ 3003,\\
18564,\ 116280,\ 735471,\\
4686825,\ldots
\end{gathered}
\]

For example, \(a_3=\binom93=84\). Here the integer \(h\) changes the
coefficient kernel itself, instead of changing a residue weight.

## Example 4. Central trinomial coefficients

Choose \(\Phi(t)=1+t+t^2\) and \(F(t)=1\). Then

\[
\begin{aligned}
a_n&=[t^n](1+t+t^2)^n\\
&=\sum_{j=0}^{\lfloor n/2\rfloor}
\frac{n!}{(j!)^2(n-2j)!}.
\end{aligned}
\]

The auxiliary equation and generating function are

\[
\begin{aligned}
T&=x(1+T+T^2),\\
G(x)&=\frac{1+T+T^2}{1-T^2}\\
&=\frac{1}{\sqrt{1-2x-3x^2}}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 3,\ 7,\ 19,\ 51,\ 141,\\
393,\ 1107,\ 3139,\ldots
\end{gathered}
\]

At \(n=4\), the three terms of the sum give \(1+12+6=19\). This shows how
multinomial coefficients enter the same construction.

## Example 5. Two different step sizes in one kernel

Take \(\Phi(t)=1+t^2+t^3\) and \(F(t)=1\). Expanding the kernel gives

\[
\begin{aligned}
a_n&=[t^n](1+t^2+t^3)^n\\
&=\sum_{\substack{a,b\ge0\\2a+3b=n}}
\frac{n!}{a!b!(n-a-b)!}.
\end{aligned}
\]

Then

\[
\begin{aligned}
T&=x(1+T^2+T^3),\\
G(x)&=\frac{1+T^2+T^3}{1-T^2-2T^3}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 0,\ 2,\ 3,\ 6,\ 20,\ 35,\ 105,\\
238,\ 588,\ldots
\end{gathered}
\]

At \(n=8\), the allowed pairs are \((a,b)=(4,0),(1,2)\), so

\[
\begin{aligned}
a_8&=\frac{8!}{4!4!}+\frac{8!}{1!2!5!}\\
&=70+168\\
&=238.
\end{aligned}
\]

This kernel combines steps of sizes two and three within the same
coefficient transfer identity.

## Example 6. Changing the numerator independently

Keep \(\Phi(t)=1+t+t^2\), but take \(F(t)=1/(1-t)\). Now

\[
a_n=[t^n]\frac{(1+t+t^2)^n}{1-t}.
\]

For \(T=x(1+T+T^2)\),

\[
G(x)=\frac{1}{(1-T)(1-x(1+2T))}.
\]

The first terms are

\[
\begin{gathered}
1,\ 2,\ 6,\ 17,\ 50,\ 147,\ 435,\\
1290,\ 3834,\ 11411,\ldots
\end{gathered}
\]

The coefficients of \((1+t+t^2)^3\) through degree three are
\(1,3,6,7\). Thus

\[
\begin{aligned}
a_3&=1+3+6+7\\
&=17.
\end{aligned}
\]

The numerator \(F\) controls a separate weighting while the auxiliary equation
stays unchanged.

## Example 7. The original family with symbolic r

For every complex \(r\), define

\[
\begin{aligned}
c_{n,k}&=\binom n{\lfloor k/2\rfloor},\\
a_n(r)&=\sum_{k=0}^{n}c_{n,k}(-r)^{n-k}.
\end{aligned}
\]

Set \(T=x(1+T^2)\) and \(S=\sqrt{1-4x^2}\). Then

\[
G_r(x)=\frac{1+T}{S(1+rT)}.
\]

The first five polynomials are

\[
\begin{aligned}
a_0&=1,\\
a_1&=1-r,\\
a_2&=r^2-r+2,\\
a_3&=-r^3+r^2-3r+3,\\
a_4&=r^4-r^3+4r^2-4r+6.
\end{aligned}
\]

For example, substituting \(r=3\) gives

\[
\begin{aligned}
a_3(3)={}&-27+9\\
&-9+3\\
={}&-24.
\end{aligned}
\]

The four-term recurrence in the main manuscript is an identity between these
polynomials and holds for every complex value of the parameter.

## Example 8. The rational specialization r=-1

At \(r=-1\), the original defining sum becomes

\[
a_n=\sum_{k=0}^{n}\binom n{\lfloor k/2\rfloor}.
\]

The same equation \(T=x(1+T^2)\) applies, but the generating function
simplifies to

\[
G(x)=\frac{1}{1-2x},\qquad a_n=2^n.
\]

The first terms are

\[
\begin{gathered}
1,\ 2,\ 4,\ 8,\ 16,\ 32,\ 64,\\
128,\ 256,\ 512,\ldots
\end{gathered}
\]

For instance,

\[
\begin{aligned}
a_4={}&1+1+4\\
&+4+6\\
={}&16.
\end{aligned}
\]

A special parameter can reduce the algebraic degree of the generating function.

## Example 9. Even central binomial coefficients at r=1

Here

\[
a_n=\sum_{k=0}^{n}\binom n{\lfloor k/2\rfloor}(-1)^{n-k}.
\]

With \(T=x(1+T^2)\), the common factor \(1+T\) cancels, giving

\[
\begin{aligned}
G(x)&=\frac{1}{\sqrt{1-4x^2}},\\
a_{2m}&=\binom{2m}{m},\\
a_{2m+1}&=0.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 0,\ 2,\ 0,\ 6,\ 0,\ 20,\ 0,\\
70,\ 0,\ldots
\end{gathered}
\]

For example,

\[
\begin{aligned}
a_4={}&1-1+4\\
&-4+6\\
={}&6.
\end{aligned}
\]

The zeros at odd indices are a consequence of the even generating function.

## Example 10. The r=2 recurrence

Take \(a_n=a_n(2)\) from Example 7. Its generating function is

\[
\begin{aligned}
T&=x(1+T^2),\\
S&=\sqrt{1-4x^2},\\
G(x)&=\frac{1+T}{S(1+2T)}.
\end{aligned}
\]

For \(n\ge3\),

\[
\begin{aligned}
0={}&2n a_n+(5n-4)a_{n-1}\\
&-(8n-6)a_{n-2}\\
&-20(n-2)a_{n-3}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ -1,\ 4,\ -7,\ 22,\ -46,\ 130,\\
-295,\ 790,\ -1870,\ldots
\end{gathered}
\]

At \(n=4\), the defining sum gives

\[
\begin{aligned}
a_4={}&16-8+16\\
&-8+6\\
={}&22.
\end{aligned}
\]

Easwar proves this recurrence in Theorem 7.1 of
[arXiv:2608.22053v2](https://arxiv.org/html/2608.22053v2#S7).
The main theorem on this page treats \(r\) as a free parameter.

## Example 11. The r=4 recurrence

Take \(a_n=a_n(4)\) from Example 7. Then

\[
\begin{aligned}
T&=x(1+T^2),\\
S&=\sqrt{1-4x^2},\\
G(x)&=\frac{1+T}{S(1+4T)}.
\end{aligned}
\]

For \(n\ge3\),

\[
\begin{aligned}
0={}&4n a_n+(17n-8)a_{n-1}\\
&-(16n+2)a_{n-2}\\
&-68(n-2)a_{n-3}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ -3,\ 14,\ -57,\ 246,\ -1038,\\
4424,\ -18777,\ 79846,\\
-339258,\ldots
\end{gathered}
\]

For example,

\[
\begin{aligned}
a_4={}&256-64\\
&+64-16+6\\
={}&246.
\end{aligned}
\]

The uniform proof verifies this recurrence. An equivalent recurrence is
recorded for the sign-changed sequence in
[OEIS A133444](https://oeis.org/A133444). The attribution section explains
its correspondence with [A127363](https://oeis.org/A127363).

## Example 12. Opposite signs on the two residue classes

Use \(d=2\), \(r=0\), \(q=1\), and \((w_0,w_1)=(1,-1)\).
The defining sum reduces to

\[
\begin{aligned}
a_{2m}&=\binom{2m}{m},\\
a_{2m+1}&=-\binom{2m+1}{m}.
\end{aligned}
\]

For \(T=x(1+T^2)\),

\[
\begin{aligned}
G(x)&=\frac{(1+T^2)(1-T)}{1-T^2}\\
&=\frac{1+T^2}{1+T}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ -1,\ 2,\ -3,\ 6,\ -10,\ 20,\\
-35,\ 70,\ -126,\ldots
\end{gathered}
\]

For example, \(a_7=-\binom73=-35\). The two residue weights give
independent control of the even and odd terms.

## Example 13. Geometric weights on two-position blocks

Choose \(d=2\), \(r=0\), \(q=2\), and \(w_0=w_1=1\). Then

\[
a_n=2^{\lfloor n/2\rfloor}\binom n{\lfloor n/2\rfloor}.
\]

The generating function is

\[
\begin{aligned}
T&=x(1+2T^2),\\
G(x)&=\frac{1+T}{\sqrt{1-8x^2}}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 4,\ 6,\ 24,\ 40,\ 160,\\
280,\ 1120,\ 2016,\ldots
\end{gathered}
\]

For example,

\[
\begin{aligned}
a_8&=2^4\binom84\\
&=16\cdot70\\
&=1120.
\end{aligned}
\]

The parameter \(q\) weights the block index, while \(r\) weights the
complementary exponent \(n-k\).

## Example 14. Three-position blocks

Set \(d=3\), \(r=0\), \(q=1\), and \(w_0=w_1=w_2=1\). Then

\[
a_n=\binom n{\lfloor n/3\rfloor}.
\]

With \(T=x(1+T^3)\), put \(W(T)=1+T+T^2\). The generating
function is

\[
G(x)=\frac{(1+T^3)W(T)}{1-2T^3}.
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 1,\ 3,\ 4,\ 5,\ 15,\ 21,\\
28,\ 84,\ldots
\end{gathered}
\]

For example, \(a_9=\binom93=84\). The recurrence on each residue class
in the main manuscript advances the index by three.

## Example 15. Three-position blocks with r=1

Set \(m_k=\lfloor k/3\rfloor\) and define

\[
a_n=\sum_{k=0}^{n}\binom n{m_k}(-1)^{n-k}.
\]

Use \(T=x(1+T^3)\) and \(W(T)=1+T+T^2\). Then

\[
G(x)=\frac{(1+T^3)W(T)}{(1-2T^3)(1+T)}.
\]

The first terms are

\[
\begin{gathered}
1,\ 0,\ 1,\ 2,\ 1,\ 4,\ 10,\ 6,\\
21,\ 56,\ldots
\end{gathered}
\]

The sum at \(n=4\) gives

\[
\begin{aligned}
a_4={}&1-1+1\\
&-4+4\\
={}&1.
\end{aligned}
\]

In this calculation, several positions contribute to the same coefficient.

## Example 16. A three-residue contrast at r=2

Take \(d=3\), \(q=1\), \(r=2\), and \(\mathbf w=(1,0,-1)\).
With \(m_k=\lfloor k/3\rfloor\),

\[
a_n=\sum_{k=0}^{n}w_{k\bmod3}\binom n{m_k}(-2)^{n-k}.
\]

Then

\[
\begin{aligned}
T&=x(1+T^3),\\
G(x)&=\frac{(1+T^3)(1-T^2)}{(1-2T^3)(1+2T)}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ -2,\ 3,\ -3,\ 4,\ -9,\ 27,\\
-54,\ 84,\ -84,\ldots
\end{gathered}
\]

Only the residue classes zero and two contribute:

\[
\begin{aligned}
a_5={}&-32+8\\
&+20-5\\
={}&-9.
\end{aligned}
\]

Zero weights can remove entire classes from the defining sum.

## Example 17. Four-position blocks

Take \(d=4\), \(r=0\), and \(q=1\), with all four residue weights equal to one.
Then

\[
a_n=\binom n{\lfloor n/4\rfloor}.
\]

Use

\[
\begin{aligned}
T&=x(1+T^4),\\
W(T)&=1+T+T^2+T^3,\\
G(x)&=\frac{(1+T^4)W(T)}{1-3T^4}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 1,\ 1,\ 4,\ 5,\ 6,\ 7,\ 28,\\
36,\ldots
\end{gathered}
\]

For example, \(a_{12}=\binom{12}{3}=220\). The defining auxiliary
polynomial now has degree four.

## Example 18. Selecting indices divisible by four

Keep \(d=4\), \(r=0\), and \(q=1\), but choose
\(\mathbf w=(1,0,0,0)\). The coefficients are

\[
\begin{aligned}
a_{4m}&=\binom{4m}{m},\\
a_{4m+j}&=0\quad(1\le j\le3).
\end{aligned}
\]

Then

\[
\begin{aligned}
T&=x(1+T^4),\\
G(x)&=\frac{1+T^4}{1-3T^4}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 0,\ 0,\ 0,\ 4,\ 0,\ 0,\ 0,\ 28,\\
0,\ldots
\end{gathered}
\]

For example, \(a_8=\binom82=28\) but \(a_9=0\).
This is an exact residue filter.

## Example 19. Five-position blocks weighted by powers of two

Let \(m=\lfloor n/5\rfloor\) and set

\[
a_n=2^m\binom nm.
\]

The relevant block parameters are \(d=5\), \(r=0\), \(q=2\), with
all residue weights equal to one. Put

\[
\begin{aligned}
T&=x(1+2T^5),\\
W(T)&=1+T+T^2+T^3+T^4,\\
G(x)&=\frac{(1+2T^5)W(T)}{1-8T^5}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 1,\ 1,\ 1,\ 10,\ 12,\ 14,\\
16,\ 18,\ldots
\end{gathered}
\]

At the next index,

\[
\begin{aligned}
a_{10}&=2^2\binom{10}{2}\\
&=4\cdot45\\
&=180.
\end{aligned}
\]

The construction works for arbitrary positive block lengths, with no restriction
to square roots.

## Example 20. All the block parameters active

Take \(d=3\), \(q=2\), \(r=1\), and \(\mathbf w=(1,2,3)\).
Writing \(m_k=\lfloor k/3\rfloor\), define

\[
\begin{aligned}
c_{n,k}&=w_{k\bmod3}2^{m_k}\binom n{m_k},\\
a_n&=\sum_{k=0}^{n}c_{n,k}(-1)^{n-k}.
\end{aligned}
\]

Use

\[
\begin{aligned}
T&=x(1+2T^3),\\
W(T)&=1+2T+3T^2,\\
G(x)&=\frac{(1+2T^3)W(T)}{(1-4T^3)(1+T)}.
\end{aligned}
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 2,\ 4,\ 10,\ 18,\ 38,\\
110,\ 194,\ 418,\ldots
\end{gathered}
\]

For example,

\[
\begin{aligned}
a_4={}&1-2+3\\
&-8+16\\
={}&10.
\end{aligned}
\]

This combines a block weight, unequal residue weights, and a nonzero value of \(r\).

## Example 21. Three-position blocks weighted by m+1

Let \(m=\lfloor n/3\rfloor\) and consider

\[
a_n=(m+1)\binom nm.
\]

Applying \(1+q\partial_q\) to the corresponding three-position block
generating function and then setting \(q=1\) gives the following expression.
Use \(T=x(1+T^3)\), put \(v=T^3\), and define the auxiliary polynomial

\[
\begin{aligned}
P(T)={}&1-v+4v^2\\
&+T(1+2v^2)\\
&+T^2(1+v).
\end{aligned}
\]

Then

\[
G(x)=\frac{(1+v)P(T)}{(1-2v)^3}.
\]

The first terms are

\[
\begin{gathered}
1,\ 1,\ 1,\ 6,\ 8,\ 10,\ 45,\ 63,\\
84,\ 336,\ldots
\end{gathered}
\]

For example, \(a_9=4\binom93=336\). Polynomial weights in the block
index arise from differentiation with respect to \(q\), including its effect
on the implicit series \(T\).

## Example 22. Two-position blocks weighted by m

Let \(m=\lfloor n/2\rfloor\) and define

\[
a_n=m\binom nm.
\]

With \(T=x(1+T^2)\), define the auxiliary polynomial \(P(T)=2+3T-T^3\).
Applying \(q\partial_q\) to the corresponding two-position block generating
function and then setting \(q=1\) gives

\[
G(x)=\frac{T^2(1+T^2)P(T)}{(1-T^2)^3}.
\]

The first terms are

\[
\begin{gathered}
0,\ 0,\ 2,\ 3,\ 12,\ 20,\ 60,\\
105,\ 280,\ 504,\ldots
\end{gathered}
\]

For example, \(a_8=4\binom84=280\). The multiplier depends on the
block index, so fixed residue weights alone cannot produce this weighting.

## Example 23. Fibonacci weights on the block index

Let \(F_0=0\), \(F_1=1\), and \(F_{m+2}=F_{m+1}+F_m\).
Put \(m=\lfloor n/3\rfloor\) and define

\[
a_n=F_m\binom nm.
\]

For any \(\lambda\), let

\[
\begin{aligned}
T_\lambda&=x(1+\lambda T_\lambda^3),\\
W(T)&=1+T+T^2,\\
H_\lambda(x)&=\frac{(1+\lambda T_\lambda^3)W(T_\lambda)}
{1-2\lambda T_\lambda^3}.
\end{aligned}
\]

Set \(\varphi=(1+\sqrt5)/2\) and \(\psi=(1-\sqrt5)/2\).
Binet's formula gives

\[
G(x)=\frac{H_\varphi(x)-H_\psi(x)}{\sqrt5}.
\]

The first terms are

\[
\begin{gathered}
0,\ 0,\ 0,\ 3,\ 4,\ 5,\ 15,\ 21,\\
28,\ 168,\ldots
\end{gathered}
\]

For example,

\[
\begin{aligned}
a_{12}&=F_4\binom{12}{4}\\
&=3\cdot495\\
&=1485.
\end{aligned}
\]

This generating function is algebraic because it is a finite linear
combination of algebraic series. The degree bound for a single block weight
does not automatically apply to this combination.
