# Weighted binomial sums and algebraic generating functions

Author: Komorebi P.
Date: 19 November 2026.
Edition: Final reading edition.

**Abstract.** We prove a uniform recurrence for an established family of
binomial row polynomials, valid for every complex parameter. We then derive
algebraic generating functions for arbitrary block lengths, geometric block
weights, and independent weights within each block. Polynomial weights and
weight sequences satisfying linear recurrences with constant coefficients
give further algebraic families. The proofs include degenerate parameters
and zero weights. Thirty-two worked examples illustrate the formulas.

Sections 1 through 5 prove and explain the original recurrence. Section 6
records the historical context, and Section 7 gives the reproduction commands.
Sections 8 through 10 develop the larger family from classical Lagrange
inversion. The worked examples follow the article. All generating functions
are interpreted as formal power series, so the arguments require no analytic
convergence assumptions.

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

**Theorem (uniform recurrence).** Put \(Q=r^2+1\) and write
\(a_j=a_j(r)\). For every
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

For each \(n\ge3\), this is an identity in \(\mathbb Z[r]\). It therefore
specializes to every complex parameter.
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

Let \(C(z)\) be the Catalan series. The expression below has constant term
one and satisfies the Catalan functional equation:

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
specializations use \(x=-r\) in our notation. Six specializations are:

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

Taking \(g(t)=(1+t)/(1+rt)\) gives the expression in Section 4, which
supplies its uniform derivation.

Rohun Easwar proves the \(r=2\) recurrence in
[Theorem 7.1](https://arxiv.org/html/2608.22053v2#S7) of the paper listed in
Section 11. That theorem concerns the fixed parameter \(r=2\).
The recurrence in Section 1 holds uniformly in \(r\).

A127363 records the \(r=4\) recurrence as a conjecture and
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
already recorded under a different sign convention. Sections 2 and 3
provide a proof as a specialization of the uniform recurrence.

The coefficient-transfer identity in Section 8 is classical Lagrange
inversion. It appears as
[equations (2.1.4) and (2.1.6) in Gessel's survey](https://arxiv.org/html/1609.05988v1#S2.SS1).
Gessel's symbols \(\psi,R,f\)
correspond to \(F,\Phi,T\) below.

**Scope.** This article proves the uniform recurrence and derives the block
and weighted formulas as explicit applications of classical coefficient
transfer. The examples include classical sequences and specializations of
these identities. Historical priority for the generalizations has not been
established, and no first-discovery or first-proof claim is made. In particular,
a conjecture label in one OEIS entry does not establish that a statement is
historically unresolved.

## 7. Exact computation and reproduction

The defining finite sum and the inhomogeneous recurrence are implemented
independently. At \(r=0\), the generator uses the direct central binomial
formula. The four-term identity is checked separately. Exact polynomial
coefficient checks and the written proof cover different obligations: a finite
test verifies its stated range, while Sections 2 through 4 prove the identity
for every parameter and every admissible index.

Python 3.10 or later is required. The Python programs use only the standard
library. The JavaScript arithmetic check uses Node.js 24.

From the repository or the extracted formula source bundle, run:

```bash
python -B -m unittest discover -s tools -p 'test_sequence_closed_forms_central.py' -v
python -B -m unittest discover -s tools -p 'test_sequence_algebraic_kernel_examples.py' -v
node --test tools/test_sequence_closed_forms_core.mjs
python -B -m unittest discover -s tools -p 'test_sequence_closed_form_handoffs.py' -v
python tools/sequence_formula_catalogue.py --id KFOR-CF-CB-4
```

The catalogue command exports the exact record as JSON. The source bundle
includes both manuscripts, the generators, the tests, and the browser
arithmetic. The six integer specializations listed in Section 6 have 24 stored
terms beginning at index zero. Their OEIS comparisons use the
retained snapshot and report finite agreement separately from the source
identifications above.

The block-example checks compare the defining finite sums with independently
expanded formal generating functions. They include nonzero and zero weights,
negative and rational parameters, and the polynomial weights in Examples 21
and 22. Each of Examples 24 through 32 is checked through \(n=23\),
including its twelve printed initial terms and worked calculations.
The example source and exact arithmetic are included in the same downloadable
source bundle as the original recurrence.

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

**Theorem (classical coefficient transfer).**

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
\begin{gathered}
\left[x^n\right]R(x)\\
=\operatorname{Res}_{x=0}\frac{R(x)}{x^{n+1}}\,dx\\
=\operatorname{Res}_{t=0}
\frac{F(t)\Phi(t)^n}{t^{n+1}}\,dt\\
=[t^n]F(t)\Phi(t)^n.
\end{gathered}
\]

This proves the generating-function identity, including its constant term
\(c_0=F(0)\). The inverse series \(T\) is algebraic when \(\Phi\) is
algebraic. Algebraic series are closed under differentiation, composition
with a series of zero constant term, and rational operations. These facts
give the stated algebraicity of \(G\). No analytic convergence assumption
is used.

## 9. Arbitrary block lengths and residue weights

### Reading the parameters

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

The indices have different roles:

- \(n\) is the output index. The sum for \(A_n\) has \(n+1\) terms, indexed by \(k\).
- \(m_k=\lfloor k/d\rfloor\) is the block number of the current summand, starting at zero.
- \(j=k-dm_k\) is its position within the block, with \(0\le j<d\).
- \(q^{m_k}\) multiplies the whole block. The separate factor \(w_j\) chooses or weights a position within it.
- \((-r)^{n-k}\) weights the distance from \(k\) to the output index \(n\).

The block number depends on \(k\), not just on \(n\). When \(r=0\),
every term except \(k=n\) vanishes, so the remaining block number is
\(\lfloor n/d\rfloor\).

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

**Theorem (weighted blocks).**

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

### Using the formula

**Step 1. Choose the weights.** Fix \(d,r,q\) and the \(d\) numbers
\(w_0,\ldots,w_{d-1}\). Form the polynomial \(W\) from those residue
weights. Zero weights simply omit the corresponding positions.

**Step 2. Determine the auxiliary series.** Solve
\(T=x(1+qT^d)\) as a formal series with constant term zero. To compute
coefficients through \(A_N\), start with \(T=0\), repeatedly substitute
into the right side, and discard powers above \(x^N\) after each step.
Each substitution fixes at least one further coefficient, so this process
terminates to the requested precision.

**Step 3. Substitute and expand.** Put \(V=qT^d\) into the boxed
formula. The coefficient of \(x^n\) is \(A_n\). The factors in the
denominator have constant term one, so formal series division is defined.

For a concrete choice, take \(d=3\), \(q=2\), \(r=1\), and
\(\mathbf w=(1,2,3)\). Then

\[
\begin{aligned}
W(t)&=1+2t+3t^2,\\
T&=x(1+2T^3),\\
T&=x+2x^4+12x^7\\
&\quad+96x^{10}+O(x^{13}).
\end{aligned}
\]

The formula gives

\[
\begin{aligned}
G(x)&=\frac{(1+2T^3)W(T)}
{(1-4T^3)(1+T)},\\
G(x)&=1+x+2x^2+4x^3\\
&\quad+10x^4+18x^5+O(x^6).
\end{aligned}
\]

Here is the complete finite-sum calculation of \(A_4\). In the last
column, \(c_k\) denotes the contribution of index \(k\):

\[
\begin{array}{c|c|c|r}
k&m_k&j&c_k\\\hline
0&0&0&1\\
1&0&1&-2\\
2&0&2&3\\
3&1&0&-8\\
4&1&1&16
\end{array}
\]

The first block contributes all three positions. The second contributes
only positions zero and one, because the sum stops at \(k=4\).
For instance, the last two contributions are

\[
\begin{aligned}
c_3&=1\cdot2\cdot\binom41\cdot(-1)\\
&=-8,\\
c_4&=2\cdot2\cdot\binom41=16.
\end{aligned}
\]

Adding all five contributions gives

\[
\begin{aligned}
A_4&=1-2+3\\
&\quad-8+16\\
&=10.
\end{aligned}
\]

This agrees with the coefficient of \(x^4\) in \(G\).
Example 20 continues this sequence. The computation
shows exactly where the block weight, residue weight, binomial coefficient,
and sign enter.

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

The geometric weight \(q^m\) changes by the same factor whenever the
block number increases by one. A weight defined by a recurrence can depend
on several preceding block values. This allows polynomial multiples,
Fibonacci and Pell numbers, periodic choices, and finite initial corrections.
The weight can also be chosen independently for each position in a block.

### Polynomial weights

Let \(P\) be a polynomial with complex coefficients. Replacing a block
weight \(q^m\) with
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
\(P(m)=m+1\) and \(P(m)=m\). The later examples include higher
polynomial weights and combinations with nonzero \(r\).

For example, \(s_m=(m+1)q^m\) satisfies

\[
\begin{aligned}
s_{m+2}&=2q\,s_{m+1}-q^2s_m,\\
s_0&=1,\qquad s_1=2q.
\end{aligned}
\]

It is obtained by applying \(1+D_q\) to the geometric-weight generating
function. This gives a direct connection between polynomial weights and the
recurrence formulation below, including the degenerate case \(q=0\).

### Weights satisfying a constant-coefficient recurrence

Fix a positive integer \(d\) and \(r\in\mathbb C\). For each
\(0\le j<d\), let \(s_j(m)\), \(m\ge0\), be a sequence of complex
numbers satisfying a homogeneous linear recurrence with constant
coefficients. Explicitly, for some integer \(h_j\ge1\) and constants
\(c_{j,0},\ldots,c_{j,h_j-1}\), assume

\[
\begin{gathered}
s_j(m+h_j)\\
=\sum_{\ell=0}^{h_j-1}c_{j,\ell}s_j(m+\ell),\\
m\ge0.
\end{gathered}
\]

Replace the entire weight \(w_jq^m\) from Section 9 by \(s_j(m)\).
Define

\[
\begin{aligned}
m_k&=\lfloor k/d\rfloor,\\
\sigma_k&=s_{k\bmod d}(m_k),\\
A_n^{\mathbf s}&=\sum_{k=0}^n
\sigma_k\binom n{m_k}(-r)^{n-k},\\
G_{\mathbf s}(x)&=\sum_{n\ge0}A_n^{\mathbf s}x^n.
\end{aligned}
\]

**Corollary (recurrence weights).** The generating function
\(G_{\mathbf s}\) is algebraic over \(\mathbb C(x)\). Its constant
term is \(s_0(0)\).

**Proof.** Over \(\mathbb C\), a sequence satisfying such a recurrence
is a finite sum of terms
\(P(m)\lambda^m\), together with a possible finitely supported part.
The nonzero characteristic roots give the exponential terms. Zero roots
account for finite initial corrections.

Each exponential-polynomial term in residue \(j\) is handled by the
preceding construction with \(W(t)=t^j\), followed by the specialization
\(q=\lambda\). A finite-support correction also gives a rational
generating function: for each fixed block index \(m\) and residue \(j\),
the contribution is a scalar multiple of

\[
x^{dm+j}\sum_{\ell\ge0}
\binom{dm+j+\ell}{m}(-rx)^\ell.
\]

The binomial coefficient is a polynomial in \(\ell\), so this series is
rational. At \(r=0\), it is a single monomial. A finite sum of algebraic
series is algebraic, which proves the corollary. The constant term follows
directly from the defining sum at \(n=0\).

Finite support here refers to the weight sequence. When \(r\ne0\),
even finitely many nonzero weights can contribute to infinitely many output
terms. Example 29 shows this distinction through an explicit rational
generating function and an alternating linear tail.

### Fibonacci weights

Let the Fibonacci numbers be defined by

\[
\begin{aligned}
F_0&=0,\qquad F_1=1,\\
F_{m+2}&=F_{m+1}+F_m,\qquad m\ge0.
\end{aligned}
\]

Their closed form is

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

### Polynomial recurrences from algebraicity

Every algebraic generating function constructed above has coefficients
satisfying a nontrivial linear recurrence with polynomial coefficients for
all sufficiently large indices. The following argument proves this
consequence directly.

Let \(G(x)=\sum_{n\ge0}A_nx^n\) be algebraic over \(\mathbb C(x)\).
The field \(E=\mathbb C(x,G)\) has finite degree
\(e=[E:\mathbb C(x)]\). Let \(M(x,y)\) be the irreducible minimal
polynomial of \(G\) over \(\mathbb C(x)\). Characteristic zero implies
\(M_y(x,G)\ne0\), where subscripts denote partial derivatives.
Differentiating \(M(x,G)=0\) gives

\[
G'=-\frac{M_x(x,G)}{M_y(x,G)}\in E.
\]

Differentiating a rational expression in \(x\) and \(G\) therefore stays
in \(E\). The \(e+1\) elements
\(G,G',\ldots,G^{(e)}\) are linearly dependent over \(\mathbb C(x)\).
After clearing denominators, this gives

\[
\sum_{j=0}^{e}p_j(x)G^{(j)}(x)=0,
\]

where the \(p_j\) are polynomials, not all zero. Let \(L\) be the largest
degree among the nonzero \(p_j\). For \(n\ge L\) and
\(0\le\ell\le L\),

\[
\begin{gathered}
\left[x^n\right]x^\ell G^{(j)}(x)\\
=\left(\prod_{h=1}^{j}(n-\ell+h)\right)
A_{n-\ell+j}.
\end{gathered}
\]

An empty product has value one. Expanding each \(p_j\) and comparing
coefficients therefore gives a polynomial recurrence. It is nontrivial:
for a fixed shift \(j-\ell\), terms with different \(j\) have different
polynomial degrees in \(n\), so the leading nonzero term cannot cancel
identically.

This establishes existence for every family proved algebraic in this
article. The explicit coefficients and the order of the recurrence depend
on the family. The bound \(e\) on the differential equation's order does
not by itself bound the number of consecutive coefficient indices in the
resulting recurrence. The four-term recurrence in Section 1 is one explicit
instance.

## 11. References

- Ira M. Gessel. [Lagrange Inversion](https://arxiv.org/abs/1609.05988v1). arXiv:1609.05988v1, 20 September 2016. Equations (2.1.4) and (2.1.6).
- Rohun Easwar. [An application of Jacobi's residue formula and proofs of some other conjectures on binomial coefficients](https://arxiv.org/abs/2608.22053v2). arXiv:2608.22053v2, 25 August 2026. Theorem 7.1.
- The On-Line Encyclopedia of Integer Sequences. [A107430](https://oeis.org/A107430), [A000079](https://oeis.org/A000079), [A001405](https://oeis.org/A001405), [A126869](https://oeis.org/A126869), [A127361](https://oeis.org/A127361), [A127362](https://oeis.org/A127362), [A127363](https://oeis.org/A127363), and [A133444](https://oeis.org/A133444). Accessed 19 November 2026. The recurrence attributions and the change of sign are detailed in Section 6.
