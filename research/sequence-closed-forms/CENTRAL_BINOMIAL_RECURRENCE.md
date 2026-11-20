# A uniform recurrence for weighted binomial rows

Author: Komorebi P.
Date: 19 November 2026.

This note gives a uniform derivation for an established family of binomial
row polynomials. The parameter is arbitrary. The written proof is algebraic
and does not depend on testing a finite set of parameters or indices.

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

**Theorem.** For every \(r\in\mathbb C\) and every integer \(n\ge3\),

\[
\boxed{
\begin{aligned}
0={}&rn\,a_n(r)\\
&+\bigl((r^2+1)n-2r\bigr)a_{n-1}(r)\\
&-\bigl(4r(n-2)+2(r^2+1)\bigr)a_{n-2}(r)\\
&-4(r^2+1)(n-2)a_{n-3}(r).
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
r a_n(r)+(r^2+1)a_{n-1}(r)=(r+1)b_{n-1},\qquad n\ge1.
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
G_r(x)=\sum_{n\ge0}a_n(r)x^n,\qquad
B(x)=\sum_{j\ge0}b_jx^j,\qquad
S(x)=\sqrt{1-4x^2}.
\]

The square root is the unique formal series with constant term one whose
square is \(1-4x^2\). The central binomial expansion is
\(S(x)^{-1}=\sum_{m\ge0}\binom{2m}{m}x^{2m}\).
Its coefficients follow directly from
\((m+1)\binom{2m+2}{m+1}=2(2m+1)\binom{2m}{m}\).
Separating the even and odd indices gives

\[
H(x):=\frac{1+2x}{S(x)}=1+2xB(x).
\]

Indeed, the coefficient of \(x^{2m}\), for \(m\ge1\), is
\(\binom{2m}{m}=2\binom{2m-1}{m-1}\), while the coefficient of
\(x^{2m+1}\) is \(2\binom{2m}{m}\).

Set \(q=r^2+1\) and \(D(x)=r+qx\). Summing the inhomogeneous relation
from Section 2 gives

\[
r\bigl(G_r(x)-1\bigr)+qxG_r(x)=(r+1)xB(x).
\]

Equivalently,

\[
\boxed{2D(x)G_r(x)-(r-1)=(r+1)H(x).}
\]

Direct formal differentiation gives \((1-4x^2)H'(x)=2H(x)\).
Apply the operator \((1-4x^2)\frac{d}{dx}-2\) to the boxed relation.
After division by the nonzero scalar two, the result is

\[
(1-4x^2)\bigl(D(x)G_r'(x)+qG_r(x)\bigr)
-2D(x)G_r(x)+(r-1)=0.
\]

For \(n\ge3\), the coefficient of \(x^{n-1}\) is

\[
rn a_n+(qn-2r)a_{n-1}
-\bigl(4r(n-2)+2q\bigr)a_{n-2}
-4q(n-2)a_{n-3}=0.
\]

Substituting \(q=r^2+1\) proves the theorem. The argument never divides
by \(r\), \(r+1\), or \(r^2+1\).

The first two coefficient equations are separate boundary identities:

\[
\begin{aligned}
0&=r a_1+(q-2r)a_0+(r-1),\\
0&=2r a_2+(2q-2r)a_1-2q a_0.
\end{aligned}
\]

They hold for the stated initial polynomials. In particular, the homogeneous
four-term formula is not asserted at \(n=1\).

## 4. The Catalan generating function

Let \(C(z)\) be the Catalan series, defined without a singular constant term by

\[
C(z)=\frac{2}{1+\sqrt{1-4z}},\qquad C(z)=1+zC(z)^2.
\]

Then the generating function has the uniform expression

\[
\boxed{
G_r(x)=\frac{1+xC(x^2)}
{\sqrt{1-4x^2}\bigl(1+rxC(x^2)\bigr)}.
}
\]

Every denominator in this expression has constant term one, for every
\(r\in\mathbb C\). To verify it from the preceding proof, put
\(t=xC(x^2)\). The Catalan equation gives

\[
x=\frac{t}{1+t^2},\qquad
S=\frac{1-t^2}{1+t^2},\qquad
D=\frac{(r+t)(1+rt)}{1+t^2}.
\]

The proposed series \(F=(1+t)/(S(1+rt))\) therefore satisfies

\[
\begin{aligned}
2DF-(r-1)
&=\frac{2(r+t)}{1-t}-(r-1)\\
&=(r+1)\frac{1+t}{1-t}\\
&=(r+1)H.
\end{aligned}
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
1,-3,14,-57,246,-1038,4424,-18777,79846,-339258.
\]

The \(r=4\) recurrence is

\[
\boxed{
4n a_n+(17n-8)a_{n-1}-(16n+2)a_{n-2}
-68(n-2)a_{n-3}=0,\qquad n\ge3.
}
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

This note provides a written uniform proof for the family and recovers those
recorded specializations. The conjecture label in one entry does not establish
that the identity was historically unresolved. Historical priority for the
general parameter formula has not been assessed exhaustively. These source
and notation checks were made on 19 November 2026, America/Chicago.

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
node --test tools/test_sequence_closed_forms_core.mjs
python -B -m unittest discover -s tools -p 'test_sequence_closed_form_handoffs.py' -v
python tools/sequence_formula_catalogue.py --id KFOR-CF-CB-4
```

The catalogue command exports the exact record as JSON. The source bundle
includes the proof, generator, tests, and browser arithmetic. Integer records
have 24 stored terms beginning at index zero. Their OEIS comparisons use the
retained snapshot and report finite agreement separately from the source
identifications above.
