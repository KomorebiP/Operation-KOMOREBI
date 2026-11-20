# Weighted binomial sums and algebraic generating functions

Author: Komorebi P.
Date: 19 November 2026.

This note proves a recurrence for every complex parameter in an established
family of binomial row polynomials. It then derives an algebraic generating
function for arbitrary block lengths, residue weights, and a second scalar
weight. Polynomial and Fibonacci weights give further applications.

Sections 1 through 5 prove and explain the original recurrence. Section 6
identifies the prior results precisely. Sections 8 through 10 develop the
larger family from classical Lagrange inversion. The worked-example gallery
following this note contains 23 complete specializations.

The written arguments establish identities for all admissible parameters
and indices. Finite computations are additional checks. An identity derived
here is not, by that fact alone, a claim of historical priority.

## 1. Definition and universal recurrence

For every integer \(n\ge0\), define the polynomial

\[
a_n(r)=\sum_{k=0}^{n}
\binom{n}{\lfloor k/2\rfloor}(-r)^{n-k}.
\]

Here \(\lfloor k/2\rfloor\) is the greatest integer at most \(k/2\).
The factor \((-r)^0\) is evaluated as the constant polynomial one,
including at \(r=0\). The first polynomials are

\[
\begin{aligned}
a_0(r)&=1,\\
a_1(r)&=1-r,\\
a_2(r)&=r^2-r+2,\\
a_3(r)&=-r^3+r^2-3r+3.
\end{aligned}
\]

**Theorem.** Put \(Q=r^2+1\) and write \(a_j=a_j(r)\). For every
\(r\in\mathbb C\) and every integer \(n\ge3\),

\[
\boxed{
\begin{aligned}
0={}&rn\,a_n\\
&+(Qn-2r)a_{n-1}\\
&-\bigl[4r(n-2)+2Q\bigr]a_{n-2}\\
&-4Q(n-2)a_{n-3}.
\end{aligned}
}
\]

For each \(n\), this is an identity in \(\mathbb Z[r]\). It therefore
specializes to every complex parameter, rather than only integer examples.
At \(r\ne0\), the displayed recurrence and the first three values determine
the sequence forward. At \(r=0\), the coefficient of \(a_n\) vanishes.
The identity still holds, and the defining sum gives the values directly.

## 2. An elementary relation from Pascal's identity

Write

\[
b_j=\binom{j}{\lfloor j/2\rfloor},\qquad j\ge0.
\]

We first prove the simpler inhomogeneous relation

\[
\boxed{
\begin{aligned}
r a_n+Q a_{n-1}&=(r+1)b_{n-1},\\
&n\ge1.
\end{aligned}
}
\]

Apply Pascal's identity to every summand of \(a_n\), with binomial
coefficients outside their usual range interpreted as zero. The first part is

\[
\begin{aligned}
U_n&=\sum_{k=0}^{n}\binom{n-1}{\lfloor k/2\rfloor}(-r)^{n-k}\\
&=\binom{n-1}{\lfloor n/2\rfloor}-r a_{n-1}(r).
\end{aligned}
\]

The second part begins at \(k=2\):

\[
V_n=\sum_{k=2}^{n}\binom{n-1}{\lfloor k/2\rfloor-1}(-r)^{n-k}.
\]

Multiplication by \(-r\) and reindexing \(j=k-2\) give the polynomial
identity

\[
\begin{aligned}
-rV_n
&=\sum_{j=0}^{n-2}\binom{n-1}{\lfloor j/2\rfloor}(-r)^{n-1-j}\\
&=a_{n-1}(r)-b_{n-1}.
\end{aligned}
\]

For \(n=1\), the sum is empty and both sides are zero. No division by
\(r\) has been used. Binomial symmetry, separately for even and odd
\(n\), gives

\[
\binom{n-1}{\lfloor n/2\rfloor}=b_{n-1}.
\]

Since \(a_n=U_n+V_n\), multiplication by \(r\) now yields the boxed
inhomogeneous relation, including \(r=0\).

## 3. Formal generating functions and the recurrence proof

All series below are formal power series. Put

\[
\begin{aligned}
G_r(x)&=\sum_{n\ge0}a_n(r)x^n,\\
B(x)&=\sum_{j\ge0}b_jx^j,\\
S(x)&=\sqrt{1-4x^2}.
\end{aligned}
\]

The square root is the unique formal series with constant term one whose
square is \(1-4x^2\). The central binomial expansion is
\(S(x)^{-1}=\sum_{m\ge0}\binom{2m}{m}x^{2m}\).
Its coefficients follow directly from

\[
\begin{gathered}
(m+1)\binom{2m+2}{m+1}\\
=2(2m+1)\binom{2m}{m}.
\end{gathered}
\]

Separating the even and odd indices gives

\[
H(x):=\frac{1+2x}{S(x)}=1+2xB(x).
\]

Indeed, the coefficient of \(x^{2m}\), for \(m\ge1\), is
\(\binom{2m}{m}=2\binom{2m-1}{m-1}\), while the coefficient of
\(x^{2m+1}\) is \(2\binom{2m}{m}\).

Set \(Q=r^2+1\) and \(D(x)=r+Qx\). Summing the inhomogeneous relation
from Section 2 gives

\[
\begin{aligned}
r(G_r-1)+QxG_r\\
=(r+1)xB.
\end{aligned}
\]

Equivalently,

\[
\boxed{
\begin{gathered}
2DG_r-(r-1)\\
=(r+1)H.
\end{gathered}
}
\]

Direct formal differentiation gives \((1-4x^2)H'(x)=2H(x)\).
Apply the operator \((1-4x^2)\frac{d}{dx}-2\) to the boxed relation.
After division by the nonzero scalar two, the result is

\[
\begin{aligned}
0={}&(1-4x^2)(DG_r'+QG_r)\\
&-2DG_r+(r-1).
\end{aligned}
\]

For \(n\ge3\), the coefficient of \(x^{n-1}\) is

\[
\begin{aligned}
0={}&rn a_n+(Qn-2r)a_{n-1}\\
&-\bigl[4r(n-2)+2Q\bigr]a_{n-2}\\
&-4Q(n-2)a_{n-3}.
\end{aligned}
\]

Substituting \(Q=r^2+1\) proves the theorem. The argument never divides
by \(r\), \(r+1\), or \(r^2+1\).

The first two coefficient equations are separate boundary identities:

\[
\begin{aligned}
0&=r a_1+(Q-2r)a_0+(r-1),\\
0&=2r a_2+(2Q-2r)a_1-2Q a_0.
\end{aligned}
\]

They hold for the stated initial polynomials. In particular, the homogeneous
four-term formula is not asserted at \(n=1\).

## 4. The Catalan generating function

Let \(C(z)\) be the Catalan series, defined without a singular constant term by

\[
\begin{aligned}
C(z)&=\frac{2}{1+\sqrt{1-4z}},\\
C(z)&=1+zC(z)^2.
\end{aligned}
\]

Then the generating function has the uniform expression

\[
\boxed{
\begin{gathered}
t=xC(x^2),\qquad S=\sqrt{1-4x^2},\\
G_r(x)=\frac{1+t}{S(1+rt)}.
\end{gathered}
}
\]

Every denominator in this expression has constant term one, for every
\(r\in\mathbb C\). To verify it from the preceding proof, put
\(t=xC(x^2)\). The Catalan equation gives

\[
\begin{aligned}
x&=\frac{t}{1+t^2},\\
S&=\frac{1-t^2}{1+t^2},\\
D&=\frac{(r+t)(1+rt)}{1+t^2}.
\end{aligned}
\]

The proposed series \(F=(1+t)/(S(1+rt))\) therefore satisfies

\[
\begin{gathered}
2DF-(r-1)\\
=\frac{2(r+t)}{1-t}-(r-1)\\
=(r+1)\frac{1+t}{1-t}\\
=(r+1)H.
\end{gathered}
\]

Thus \(D(G_r-F)=0\). For any fixed complex \(r\), the series \(D\)
is nonzero: if \(r=0\), it is \(x\). Cancellation in the integral domain
\(\mathbb C[[x]]\) gives \(G_r=F\). This is cancellation of a nonzero
factor, not division by a series with zero constant term.

## 5. Special parameters and worked values

- At \(r=-1\), \(G_{-1}(x)=1/(1-2x)\), so \(a_n(-1)=2^n\).
- At \(r=0\), \(a_n(0)=\binom n{\lfloor n/2\rfloor}\). The universal identity holds even though it cannot be solved directly for \(a_n\) by dividing by \(rn\).
- At \(r=1\), \(G_1(x)=1/\sqrt{1-4x^2}\). Hence \(a_{2m}(1)=\binom{2m}{m}\) and \(a_{2m+1}(1)=0\).
- At \(r=\pm i\), \(r^2+1=0\). The definition gives \(a_0(r)=1\), and the inhomogeneous relation gives \(a_n(r)=(1-r)\binom{n-1}{\lfloor(n-1)/2\rfloor}\) for \(n\ge1\). The third lag disappears from the universal recurrence.

The \(r=2\) values begin \(1,-1,4,-7,22,-46\). At \(r=3\), they
begin \(1,-2,8,-24,84,-272\). At \(r=4\), they begin

\[
\begin{gathered}
1,-3,14,-57,246,\\
-1038,4424,-18777,\\
79846,-339258,\ldots.
\end{gathered}
\]

The \(r=4\) recurrence is

\[
\boxed{
\begin{aligned}
0={}&4n a_n+(17n-8)a_{n-1}\\
&-(16n+2)a_{n-2}\\
&-68(n-2)a_{n-3},\qquad n\ge3.
\end{aligned}
}
\]

For a direct example, the five summands at \(n=4,r=4\) are

\[
\begin{aligned}
a_4(4)&=256-64+64-16+6\\
&=246.
\end{aligned}
\]

The simpler recurrence gives the same value using only the preceding term:

\[
\begin{gathered}
4a_4+17(-57)\\
=5\binom31,\\
4a_4=984,\\
a_4=246.
\end{gathered}
\]

The browser calculator evaluates integer parameters from \(-12\) through
\(12\), with indices through \(160\). The written theorem has no such
parameter or index bound. The Python source supports exact integer and
rational parameters and supplies the coefficient polynomial in \(r\).

## 6. OEIS connections and attribution

The established triangle [OEIS A107430](https://oeis.org/A107430) has
\(T(n,k)=\binom n{\lfloor k/2\rfloor}\). Its recorded row-polynomial
specializations use \(x=-r\) in our notation. The six stored examples are:

- \(r=-1\): [A000079](https://oeis.org/A000079).
- \(r=0\): [A001405](https://oeis.org/A001405).
- \(r=1\): [A126869](https://oeis.org/A126869).
- \(r=2\): [A127361](https://oeis.org/A127361).
- \(r=3\): [A127362](https://oeis.org/A127362).
- \(r=4\): [A127363](https://oeis.org/A127363).

The floor-binomial family and its Catalan/Chebyshev generating-function
framework are established in the OEIS entries associated with Paul Barry.
A127361 and A127363 print the corresponding generating functions for their
fixed parameters and describe the transformation

\[
\begin{gathered}
t=xC(x^2),\qquad S=\sqrt{1-4x^2},\\
g(x)\longmapsto \frac{g(t)}{S}.
\end{gathered}
\]

Taking \(g(t)=(1+t)/(1+rt)\) gives the expression in Section 4. This page
supplies its uniform derivation. The entry author dates do not date every
formula subsequently added to those entries.

Rohun Easwar proves the \(r=2\) recurrence in Theorem 7.1 of
[An application of Jacobi's residue formula and proofs of some other conjectures on binomial coefficients](https://arxiv.org/html/2608.22053v2#S7),
arXiv:2608.22053v2, 25 August 2026. That theorem concerns the fixed parameter
\(r=2\). The present note derives the displayed recurrence uniformly in
\(r\).

The retrieved A127363 entry labels the \(r=4\) recurrence a conjecture and
credits R. J. Mathar, 24 November 2012. An equivalent recurrence was already
recorded for [A133444](https://oeis.org/A133444), credited to Vaclav Kotesovec,
20 October 2012. Its terms are \(c_n=(-1)^n a_n(4)\). Substituting this sign
change into that recorded recurrence gives exactly the boxed \(r=4\) formula.

To see the equivalence explicitly, the recurrence recorded for A133444 is

\[
\begin{aligned}
4n c_n={}&(17n-8)c_{n-1}\\
&+(16n+2)c_{n-2}\\
&-68(n-2)c_{n-3}.
\end{aligned}
\]

Substitute \(c_j=(-1)^j a_j(4)\) and divide by \((-1)^n\). Bringing all
terms to the left gives the recurrence in Section 5. Thus the statement was
already recorded under a different sign convention. The proof here verifies
it without asserting that this is its first proof.

The coefficient-transfer identity in Section 8 is classical Lagrange
inversion. It appears as equations (2.1.4) and (2.1.6) of
[Ira M. Gessel, Lagrange Inversion](https://arxiv.org/html/1609.05988v1#S2.SS1),
arXiv:1609.05988v1, 20 September 2016. Gessel's symbols \(\psi,R,f\)
correspond to \(F,\Phi,T\) below.

**What is established here.** The all-\(r\) recurrence has a written proof.
The block formula is an explicit consequence of classical Lagrange inversion.
The polynomial and Fibonacci weight formulas are further applications.
The 23 examples include classical sequences and specializations of these
identities. They are not 23 claims of new discoveries.

**What has not been established.** No exhaustive priority search has been
completed for the all-\(r\) recurrence or the block and weighted formulas.
A conjecture label in one OEIS entry does not establish that a statement is
historically unresolved. These source and notation checks were made on
19 November 2026, America/Chicago.

## 7. Exact computation and reproduction

The defining finite sum and the inhomogeneous recurrence are implemented
independently. At \(r=0\), the generator uses the direct central binomial
formula. The four-term identity is checked separately. Exact polynomial
coefficient checks and the written proof cover different obligations: a finite
test verifies its stated range, while Sections 2 through 4 prove the identity
for every parameter and every admissible index.

From the repository or the extracted formula source bundle, run:

```bash
python -B -m unittest discover -s tools -p 'test_sequence_closed_forms_central.py' -v
python -B -m unittest discover -s tools -p 'test_sequence_algebraic_kernel_examples.py' -v
node --test tools/test_sequence_closed_forms_core.mjs
python -B -m unittest discover -s tools -p 'test_sequence_closed_form_handoffs.py' -v
python tools/sequence_formula_catalogue.py --id KFOR-CF-CB-4
```

The catalogue command exports the exact record as JSON. The source bundle
includes the proof, generator, tests, and browser arithmetic. Integer records
have 24 stored terms beginning at index zero. Their OEIS comparisons use the
retained snapshot and report finite agreement separately from the source
identifications above.


The block-example checks compare the defining finite sums with independently
expanded formal generating functions. They include nonzero and zero weights,
negative and rational parameters, and the polynomial weights in Examples 21
and 22. The example source and exact arithmetic are included in the same
downloadable source bundle as the original recurrence.

## 8. Classical coefficient transfer

This section states the form of Lagrange inversion used in the larger
family. It is included with a proof so the derivation can be read on its own.

Work over a field \(K\) of characteristic zero. Let
\(F(t),\Phi(t)\in K[[t]]\) and assume \(\Phi(0)\ne0\). The notation
\([t^n]P(t)\) means the coefficient of \(t^n\) in a formal series. Define

\[
\begin{aligned}
c_n&=[t^n]F(t)\Phi(t)^n,\\
G(x)&=\sum_{n\ge0}c_nx^n.
\end{aligned}
\]

There is a unique formal series \(T(x)\), with \(T(0)=0\), satisfying

\[
T=x\Phi(T).
\]

**Classical identity.**

\[
\boxed{G(x)=\frac{F(T)}{1-x\Phi'(T)}.}
\]

If \(F\) and \(\Phi\) are algebraic over \(K(t)\), then \(G\) is
algebraic over \(K(x)\). Here algebraic means that the series satisfies a
nonzero polynomial equation with coefficients in the indicated rational
function field. It does not mean that the general coefficient has an
expression involving only radicals or factorials.

**Proof.** The series \(x=t/\Phi(t)\) has nonzero linear coefficient,
so it has a compositional inverse \(t=T(x)\). Under this substitution,

\[
\begin{aligned}
\frac{dx}{dt}
&=\frac{\Phi(t)-t\Phi'(t)}{\Phi(t)^2},\\
1-x\Phi'(T)
&=\frac{\Phi(t)-t\Phi'(t)}{\Phi(t)}.
\end{aligned}
\]

Let \(R(x)=F(T)/(1-x\Phi'(T))\). The formal residue, denoted by
\(\operatorname{Res}\), is the coefficient of the power \(-1\).
Changing variables in that residue cancels the common derivative factor:

\[
\begin{aligned}
[x^n]R(x)
&=\operatorname{Res}_{x=0}\frac{R(x)}{x^{n+1}}\,dx\\
&=\operatorname{Res}_{t=0}
\frac{F(t)\Phi(t)^n}{t^{n+1}}\,dt\\
&=[t^n]F(t)\Phi(t)^n.
\end{aligned}
\]

This proves the generating-function identity, including its constant term
\(c_0=F(0)\). The inverse series \(T\) is algebraic when \(\Phi\) is
algebraic. Algebraic series are closed under differentiation, composition
with a series of zero constant term, and rational operations. These facts
give the stated algebraicity of \(G\). No analytic convergence assumption
is used.

## 9. Arbitrary block lengths and residue weights

Choose a positive integer \(d\), complex parameters \(r,q\), and complex
weights \(w_0,\ldots,w_{d-1}\). The index \(k\bmod d\) is the remainder
in \(\{0,\ldots,d-1\}\). Define

\[
\begin{aligned}
m_k&=\lfloor k/d\rfloor,\\
\omega_k&=w_{k\bmod d}\,q^{m_k},\\
A_n&=\sum_{k=0}^n
\omega_k\binom n{m_k}(-r)^{n-k}.
\end{aligned}
\]

Thus \(d\) changes the number of consecutive indices sharing a binomial
coefficient, \(q\) weights the block index, and \(w_j\) weights the
position within each block. The original family has
\(d=2,q=1,w_0=w_1=1\). The new block weight \(q\) is distinct from
\(Q=r^2+1\) in the original recurrence.

Put

\[
\begin{aligned}
W(t)&=\sum_{j=0}^{d-1}w_jt^j,\\
T&=x(1+qT^d),\\
T(0)&=0,\\
V&=qT^d,\\
G(x)&=\sum_{n\ge0}A_nx^n.
\end{aligned}
\]

The polynomial \(W\) has degree at most \(d-1\). The notation includes
the zero polynomial. All powers with exponent zero have value one, including
when the base is zero.

**Block theorem.**

\[
\boxed{
G(x)=\frac{(1+V)W(T)}
{(1-(d-1)V)(1+rT)}.
}
\]

Every denominator here has constant term one. The formula therefore holds
for all the stated complex parameters, including \(r=0\) and \(q=0\).
Its constant term is \(A_0=w_0\), which need not be one.

**Proof.** Group the defining sum by \(k=dm+j\), where \(0\le j<d\).
Then

\[
A_n=[t^n]\frac{W(t)}{1+rt}(1+qt^d)^n.
\]

In the product on the right, the exponents selected from the three factors
satisfy \(n=dm+j+\ell\). Their contribution is precisely
\(w_jq^m\binom nm(-r)^\ell\), the corresponding summand on the left.
Apply Section 8 with \(F(t)=W(t)/(1+rt)\) and
\(\Phi(t)=1+qt^d\). Since \(x=T/(1+qT^d)\),

\[
\begin{aligned}
1-x\Phi'(T)&=1-dqxT^{d-1}\\
&=\frac{1-(d-1)V}{1+V}.
\end{aligned}
\]

Substitution gives the theorem.

**Algebraic degree.** The equation \(T-x-qxT^d=0\) has degree at most
\(d\) in \(T\). Since \(G\) is a rational function of \(T\), its
algebraic degree over \(\mathbb C(x)\) is at most \(d\). This is an
upper bound. Cancellation and special parameter values can lower the degree.

An explicit polynomial equation for \(G\) can be obtained by eliminating
\(T\) from the two equations below. Write \(y=G(x)\):

\[
\begin{gathered}
T-x(1+qT^d)=0,\\
y(1-(d-1)V)(1+rT)\\
=(1+V)W(T).
\end{gathered}
\]

This also explains why an auxiliary algebraic series is a closed form:
the branch is specified exactly by \(T(0)=0\), and no numerical root
selection is required.

### Boundary cases

- If \(d=1\), then \(A_n=w_0(q-r)^n\).
- If \(q=0\), then \(T=x\) and \(G(x)=W(x)/(1+rx)\).
- If \(r=0\), then only the term \(k=n\) remains. For \(0\le j<d\), this gives \(A_{dm+j}=w_jq^m\binom{dm+j}{m}\).
- If a residue weight vanishes, the formula still applies. For example, at \(r=0,d=4,W(t)=1\), only indices divisible by four can have nonzero values.

### A first-order recurrence on each residue class

For \(r=0\), fix \(j\in\{0,\ldots,d-1\}\) and set
\(B_m=A_{dm+j}\). Write \(N=dm+j\) and \(M=N-m\), and define

\[
\begin{aligned}
L_{m,j}&=(m+1)\prod_{h=1}^{d-1}
(M+h),\\
R_{m,j}&=q\prod_{h=1}^{d}(N+h).
\end{aligned}
\]

Then, for every \(m\ge0\),

\[
\boxed{L_{m,j}B_{m+1}=R_{m,j}B_m.}
\]

This follows by cancelling factorials between
\(\binom{dm+d+j}{m+1}\) and \(\binom{dm+j}{m}\), then multiplying by
\(w_jq^{m+1}\). The displayed identity does not divide by \(q\) or
\(w_j\), so zero weights are included. An empty product has value one,
which covers \(d=1\). This is a recurrence along one residue class. It is
not a claim about the minimal order of a recurrence using consecutive indices.

## 10. Polynomial weights and recurrence weights

Let \(P\) be any polynomial. Replacing a block weight \(q^m\) with
\(P(m)q^m\) corresponds to the differential operator

\[
\begin{aligned}
D_q&=q\frac{\partial}{\partial q},\\
P(D_q)q^m&=P(m)q^m.
\end{aligned}
\]

Here the differentiation is at fixed \(x\), before a numerical value is
assigned to \(q\). Apply \(P(D_q)\) to the generating function in
Section 9. Its coefficient of \(x^n\) is exactly the finite sum with the
additional factor \(P(\lfloor k/d\rfloor)\).

Differentiating the equation for \(T\) gives

\[
\boxed{D_qT=\frac{qT^{d+1}}{1-(d-1)qT^d}.}
\]

Consequently, every fixed polynomial weight still gives a rational function
of \(T\). Its generating function is algebraic and retains the degree
bound of at most \(d\). Examples 21 and 22 write out the results for
\(P(m)=m+1\) and \(P(m)=m\).

More generally, each residue can have its own weight sequence \(s_j(m)\)
satisfying a linear recurrence with constant coefficients. Over
\(\mathbb C\), such a sequence is a finite sum of terms
\(P(m)\lambda^m\), together with a possible finitely supported part.
The nonzero characteristic roots give the exponential terms. Zero roots
account for finite initial corrections.

Each exponential-polynomial term is handled by the preceding construction
with \(q=\lambda\). A finite-support correction also gives a rational
generating function: for each fixed block index \(m\) and residue \(j\), the contribution is a
scalar multiple of

\[
x^{dm+j}\sum_{\ell\ge0}
\binom{dm+j+\ell}{m}(-rx)^\ell.
\]

The binomial coefficient is a polynomial in \(\ell\), so this series is
rational. At \(r=0\), it is a single monomial. A finite sum of algebraic
series is algebraic. This proves the claimed extension.

**Fibonacci example.** Write

\[
\begin{aligned}
\varphi&=(1+\sqrt5)/2,\\
\psi&=(1-\sqrt5)/2,\\
F_m&=(\varphi^m-\psi^m)/\sqrt5.
\end{aligned}
\]

For ternary blocks with \(r=0\) and all residue weights one, let
\(G_\lambda\) denote the Section 9 series with \(q=\lambda\). Then

\[
\begin{aligned}
A_n&=F_{\lfloor n/3\rfloor}
\binom n{\lfloor n/3\rfloor},\\
G(x)&=\frac{G_\varphi(x)-G_\psi(x)}{\sqrt5}.
\end{aligned}
\]

This is an algebraic generating function, with two different auxiliary
series. The single-parameter degree bound \(d\) does not automatically
apply to this combination. Example 23 gives the complete specialization.

Finally, algebraic generating functions have coefficient sequences satisfying
linear recurrences with polynomial coefficients. The construction proves
that such a recurrence exists. Determining a useful explicit recurrence,
its minimal order, or a new determinant identity requires a separate
calculation or proof. The four-term recurrence in Section 1 is one explicit
instance, not a universal order claim for all the weighted families.
