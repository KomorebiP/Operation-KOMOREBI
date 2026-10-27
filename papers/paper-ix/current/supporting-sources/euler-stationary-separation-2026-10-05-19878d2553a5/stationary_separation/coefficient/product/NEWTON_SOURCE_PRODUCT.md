# Exact Newton source product and the beta cubic

Scope: the actual source transform and the full coefficient identity for the
Bernoulli kernel. This note establishes the product algebra, the exact cubic
it transports, and the cancellation of its first shifted linear term. It
does not assert critical-value nonvanishing or rule out further arguments
using the full recurrence.

## 1. The exact source product comes from operator composition

Write

\[
P_n(s)=2^{-n}(2s)_{\underline{2n}},\qquad
A(s)=\frac{9^{s+1}-1}{8(s+1)(2s+1)},\qquad
\mathcal T(k)(s)=\sum_{n\ge0}8^nk_nP_n(s)A(s-n)
\]

for a kernel \(k(w)=\sum k_nw^n\). Let

\[
(T_kh)(s)=\sum_{n\ge0}8^nk_nP_n(s)h(s-n),\qquad
\mathcal T(k)=T_kA.                                     \tag{1}
\]

The factorization \(P_i(s)P_j(s-i)=P_{i+j}(s)\) proves

\[
T_aT_b=T_{ab}.                                          \tag{2}
\]

This holds for polynomial kernels and for the convergent kernel/operator
compositions used here. The source transform is injective: at an ordinary
integer \(s=N\), all packets with index greater than \(N\) vanish, and the
diagonal coefficient is \(8^NP_N(N)A(0)=4^N(2N)!\ne0\).
The values at successive nonnegative integers therefore recover the
kernel coefficients recursively. We can define a bilinear product on its
image unambiguously by

\[
\mathcal T(a)\star\mathcal T(b)=\mathcal T(ab).            \tag{3}
\]

Its identity element is \(A=\mathcal T(1)\), not the constant function 1.
By (2), if \(F=\mathcal T(a)\) and \(G=\mathcal T(b)\), then

\[
(F\star G)(s)=\sum_{n\ge0}8^na_nP_n(s)G(s-n).             \tag{4}
\]

Formula (4) is symmetric despite its asymmetric appearance. It is the
correct meaning of transforming a kernel square. It retains all shifted
values; evaluation at one argument is not a homomorphism for this product.

## 2. The Euler operator is not the ordinary argument derivative

Set \(D=w\,d/dw\), and define \(\delta\) only as the transported
coefficient derivation on the source image:

\[
\delta\mathcal T(k)=\mathcal T(Dk),\qquad
\delta\mathcal T(k)(s)=\sum_{n\ge0}n\,8^nk_nP_n(s)A(s-n).
                                                               \tag{5}
\]

This is a derivation for \(\star\), by the coefficient product rule for
\(D\). It is not ordinary argument differentiation: for example
\(\delta A=0\), whereas \(A'\) is not zero. Also, with
\(LF(s)=8P_1(s)F(s-1)\), equation (2) gives
\(\mathcal T(wk)=L\mathcal T(k)\). No expression for \(\delta\)
in terms of a half shift and a source correction is asserted here.

For comparison only, the separate unsourced Newton map
\(\mathcal U(z^m)(y)=(y)_{\underline m}\) has the polynomial product

\[
(F\odot G)(y)=\sum_{j\ge0}\frac{(-1)^j(y)_{\underline j}}{j!}
(\Delta^jF)(y-j)(\Delta^jG)(y-j),\quad
\Delta F(y)=F(y+1)-F(y).
\]

Its proof uses the formal generating functions \((1+a)^y,(1+b)^y\):
the displayed sum equals \(((1+a)(1+b)-ab)^y=(1+a+b)^y\).
This finite polynomial identity does not identify the actual source
transform with multiplication by its exponential generating function
followed by \(\mathcal U\).

## 3. The full beta cubic and its first cancellation

For the actual Bernoulli kernel

\[
f(w)=\left(\frac{\sqrt w}{\sinh\sqrt w}\right)^2,
\quad g(w)=\sqrt w\coth\sqrt w,
\qquad Df=f(1-g),\qquad g^2=f+w,
\]

eliminating \(g\) gives the exact identity

\[
(Df)^2-2fDf+(1-w)f^2-f^3=0.                              \tag{6}
\]

Thus, for \(E=\mathcal T(f)=\mathcal E\), its full transformed form is

\[
(\delta E)\star(\delta E)-2E\star\delta E
+E\star E-L(E\star E)-E\star E\star E=0.                 \tag{7}
\]

Replacing stars by pointwise products, or replacing \(\delta\) by ordinary
argument differentiation, changes the equation.

There is a concrete cancellation before any point is evaluated. For a
prefix \(p=f_{<r}\), the linearization of the left side of (6) at \(p\)
in an increment \(u\) is

\[
A_pDu+B_pu,
\quad A_p=2(Dp-p),\quad
B_p=-2Dp+2(1-w)p-3p^2.                                  \tag{8}
\]

Since \(f=1-w/3+w^2/15+O(w^3)\), for every \(r\ge3\),

\[
A_p=-2+\frac{2}{15}w^2+O(w^3),\qquad
B_p=-1-\frac15w^2+O(w^3).                               \tag{9}
\]

Both coefficients of \(w^1\) vanish exactly. Writing \(u=w^rB\),
the divided linearization is

\[
A_pDB+(rA_p+B_p)B,
\qquad
rA_p+B_p=-(2r+1)+\frac{2r-3}{15}w^2+O(w^3).              \tag{10}
\]

Thus two separately nonzero first-shift contributions cannot be retained
as a forcing term of this full recurrence: they cancel in the complete
linearized coefficient equation. The coefficient of \(w^2\) in the
second operator is a dyadic unit. Its evaluation still involves shifted
tail values and the other exact terms, including the finite prefix defect.
No dominance conclusion follows from that coefficient alone.

## 4. What local quadratic information does and does not determine

An argument using only the value and ordinary first derivative at \(s_0\)
could evaluate transformed products from those data only if the ideal

\[
I_{s_0}^2=\{F:F(s_0)=F'(s_0)=0\}
\]

were an ideal for \(\star\) on the admissible source image. It is not.
The failure can be checked with this actual source, rather than with an
unrelated transform. Take the rational polynomial kernel

\[
h(w)=1-\frac5{24}w+\frac3{128}w^2+\frac{35}{1024}w^3,
\qquad H=\mathcal T(h).
\]

Writing \(\ell=\log9\), the value and derivative of the first four
source packets \(b_n=8^nP_nA(s-n)\) at \(s=1\) are

| \(n\) | \(b_n(1)\) | \(b_n'(1)\) |
|---|---:|---:|
| 0 | \(5/3\) | \(27\ell/16-35/18\) |
| 1 | \(8\) | \(9\ell\) |
| 2 | \(0\) | \(8\ell\) |
| 3 | \(0\) | \(512/9\) |

Consequently \(H(1)=H'(1)=0\) exactly. But the first two coefficients
of \(h^2\) are \(1,-5/12\), so

\[
\boxed{(H\star H)(1)=\mathcal T(h^2)(1)=-\frac53\ne0.}   \tag{11}
\]

This example has a nondegenerate quadratic zero. Direct expansion gives

\[
[u^2]H(1+u)=\frac{395}{108}-\frac{475}{288}\ell,
\quad
v_2([u^2]H(1+u))=-1,                                   \tag{12}
\]

because \(\ell/8\equiv5\pmod8\) and four times the coefficient in
(12) is congruent to \(2\pmod8\). In a sufficiently small dyadic chart,
scaling this function therefore gives a unit quadratic leading term and
higher terms of strictly larger valuation. Knowing a nondegenerate local
quadratic chart does not repair the missing product rule.

Example (11) is a structural counterexample, not an actual Bernoulli tail
or a counterexample to the desired Euler theorem. For an actual tail,
formula (4) identifies precisely the additional data required: shifted
values, and after ordinary differentiation their shifted first derivatives
and the derivative of the Newton factors. On a chart of radius \(2^{-15}\),
the shifts by 1 and 2 already leave that chart. Estimates confined to its
local quadratic model do not estimate those values.

The actual coefficient square and its fixed-valuation evaluations are
handled separately in the parent coefficient note. They are compatible
with an arbitrarily small original critical value. To turn the full cubic
into a contradiction, one must compare all its prescribed shifted terms
and the prefix defect; neither the local two-jet nor the isolated square
supplies that comparison.

## Evidence boundary

All assertions in this note have the displayed algebraic proofs. No index
search, numerical stationary lift, finite-range extrapolation, external
theorem, or Lean compilation is used. The polynomial source example is
exact and tests only the validity of a proposed local product reduction.
