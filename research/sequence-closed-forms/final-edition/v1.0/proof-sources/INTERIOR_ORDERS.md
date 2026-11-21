# Exact minimal orders for every nonzero mixed parameter

Author: Komorebi P. Checkpoint: SEQ-DH-2026-11-21-005.
Parent publication: 5ab2d295a36c16fe54b85773ae0a3390aab3a81f.
Review status: proved as written in separate project self-review;
independent review, historical novelty and Lean formalization are unassessed.

## 1. A finite algebraic classification

Work over a characteristic-zero field. Use the moments and empty determinant
of [Theorem M](EXCEPTIONAL_ORDERS.md):
\[
 \begin{aligned}
 \mu_{2m}&=u(a+bm)\binom{2m}{m},\\
 \mu_{2m+1}&=v(2m+1)(a+bm)\binom{2m}{m},\\
 W_N&=\det(\mu_{i+j})_{0\le i,j<N},\\
 W_0&=1.
 \end{aligned}
\]
Suppose \(abuv\ne0\), and put
\[
 t=b/a,\qquad w=v/u,\qquad q=w^2.
\]
Dividing the functional by \(au\) scales \(W_N\) by \((au)^{-N}\),
which preserves its minimal eventual scalar constant-coefficient order.
The normalized quartic from [Theorem L](UNIFORM_MIXED_RECURRENCE.md) is
\[
 \begin{aligned}
 R(x)={}&x^4+wx^3+(2t-8)x^2\\
       &+w(6t-4)x+16-8t.
 \end{aligned}                                                   \tag{N1}
\]

The following polynomials make the answer computable without choosing roots.
Set \(C_0(x)=2\), \(C_1(x)=x\),
\(C_k=xC_{k-1}-C_{k-2}\), and define
\[
 \begin{aligned}
 T_k&=\operatorname{Res}_x(R,C_k)\quad(1\le k\le8),\\
 c_0&=1,\qquad
 c_j=-\frac1j\sum_{k=1}^j c_{j-k}T_k\quad(1\le j\le8),\\
 F(Y)&=c_8Y^8+\sum_{j=0}^7c_j(Y^{16-j}+Y^j).
 \end{aligned}                                                   \tag{N2}
\]
Every \(c_j\) is a polynomial in \(t,q\). The source package retains their
exact sparse coefficient lists, as well as a separate replay of this definition.
Define also
\[
 \begin{aligned}
 H(Z)={}&q^2Z^4+q^2Z^3+q(2t-8)Z^2\\
       &+q(6t-4)Z+16-8t,\\
 G&=\operatorname{monic\ gcd}(H,H'),\qquad g=\deg G,\\
 h&=\deg\left(F/\gcd(F,F')\right),\\
 B(t,q)&=q^2+(36t^2-16t+32)q+64(t-2)^2,\\
 \delta&=\begin{cases}1,&B(t,q)=0,\\0,&B(t,q)\ne0.\end{cases}
 \end{aligned}                                                   \tag{N3}
\]
Primes denote derivatives in the displayed polynomial's variable. Constant
monic gcds are one. Since \(q\ne0\), \(H(Z)=R(wZ)\) has degree four
and has exactly the root multiplicities of \(R\).

**Theorem N.** The minimal eventual order is given by this exhaustive table:

| Exact condition | Root multiplicities of \(R\) | Minimal order |
|---|---|---|
| \(g=0\) | \(1+1+1+1\) | \(7h-\delta\) |
| \(g=1\) | \(2+1+1\) | \(7h+4-\delta\) |
| \(g=2,\ \gcd(G,G')=1\) | \(2+2\) | 69 |
| \(g=2,\ \deg\gcd(G,G')=1\) | \(3+1\) | 64 |

The case \(g=3\) cannot occur. In the last two rows, respectively,
\((h,\delta)=(9,0)\) and \((8,0)\). Every minimal recurrence holds
from index one; the separate value \(W_0=1\) cannot be included in that
minimal recurrence. All polynomial gcds are over the original field.

This is an exact finite algebraic decision rule: two polynomial gcds, of
degrees at most four and sixteen, determine the order, with one quadratic
gcd distinguishing the last two rows. Together with Theorem M, it covers every
parameter of the mixed linear-weight, first-order-operator family.

## 2. The sixteen bases and their leading coefficients

Let the roots of \(R\), counted with multiplicity, be \(x_i\), and choose
\(z_i\) with \(x_i=z_i+z_i^{-1}\) in an algebraic extension.
For distinct roots, Theorem L gives the exponential polynomial
\[
 \widehat W_N=\frac{2^N}{4608N(N-1)\Delta(x)}
               \det(P_{N+j}(x_i))_{1\le i\le4,\ 0\le j<4},          \tag{N4}
\]
where \(P_n(x_i)=z_i^n\ell_n(z_i)+z_i^{-n}\ell_n(z_i^{-1})\) and
\[
 \ell_n(z)=(n-3)(n-4)-2n(n-4)z^{-2}+n(n-1)z^{-4}.
\]
Its sixteen labeled normalized bases are \(\prod_i z_i^{\epsilon_i}\),
\(\epsilon_i\in\{-1,1\}\); the actual bases are \(2au\) times these.
Their power sums are \(T_k\), and their multiset is closed under inversion.
Thus their monic characteristic polynomial is exactly \(F\) in (N2).
Replacing \(w\) by \(-w\) negates all four roots and leaves these power
sums unchanged. This proves the asserted polynomial dependence on \(t,q\).

For a rowwise choice \(v_i\in\{z_i,z_i^{-1}\}\), define
\[
 Q_n(v)=\det(v_i^j\ell_{n+j}(v_i))_{1\le i\le4,\ 0\le j<4}.
\]
It is divisible by \(n(n-1)\), as in Theorem L. Every coefficient in \(n\)
is alternating in the \(v_i\), so it is also divisible by \(\Delta(v)\)
in the Laurent polynomial ring. These two factors are coprime. Consequently
\[
 L_n(v)=Q_n(v)/(n(n-1)\Delta(v))
\]
is a Laurent polynomial whose degree in \(n\) is at most six. This fact
controls the lower coefficients as well as the leading one; it excludes
additional poles when roots merge.

Since
\(x_j-x_i=(v_j-v_i)(1-(v_iv_j)^{-1})\), the coefficient of this branch
has leading term \(A(v)n^6/4608\), where
\[
 A(v)=\frac{\prod_i(1-v_i^{-2})^2}
             {\prod_{i<j}(1-(v_iv_j)^{-1})}.                       \tag{N5}
\]
For distinct nonendpoint roots it is nonzero. The next coefficient, divided
by the leading one, is
\[
 -15-6S(v),\qquad S(v)=\sum_i\frac1{v_i^2-1}.                      \tag{N6}
\]
To check (N6), write
\(\ell_{n+j}(v)=A_0(v)n^2+(2jA_0(v)+B_0(v))n+\cdots\), where
\[
 A_0(v)=(1-v^{-2})^2,\qquad
 B_0(v)/A_0(v)=-7-6/(v^2-1).
\]
Multilinearity gives the coefficient ratio
\(2\sum_{j=0}^3j+\sum_iB_0(v_i)/A_0(v_i)\) at degree seven before
division by \(n(n-1)\). That division adds one to the ratio, giving (N6).

## 3. All collisions with simple roots

The nonzero hypotheses give
\[
 R(2)=12tw,\qquad R(-2)=-12tw.                                  \tag{N7}
\]
No two distinct roots of \(R\) can be opposites. Indeed, if \(r,-r\)
were roots with \(r\ne0\), the even and odd parts of (N1), with
\(\sigma=r^2-4\), would give
\(\sigma(\sigma+2t)=0\) and \(\sigma+6t=0\). Their combination is
\(24t^2=0\), a contradiction. A zero root occurs only at \(t=2\);
its derivative is \(8w\ne0\), so it is always simple.

Two sign vertices at Hamming distance one can collide only if some
\(z_i^2=1\), contradicting (N7). At distance two, the condition is
\((z_i^{\epsilon_i}z_j^{\epsilon_j})^2=1\), which would give equal
or opposite roots. Thus a collision has distance three or four.
There cannot be a cluster of three vertices: relative to one vertex, two
distinct flip sets of sizes at least three have symmetric difference of
size at most two. Every cluster therefore has size at most two.

For a distance-three pair put \(v_1v_2v_3=e\), \(e\in\{1,-1\}\).
Inverting these three branches changes the ratio of (N5) by
\[
 \frac{A(v_1^{-1},v_2^{-1},v_3^{-1},v_4)}{A(v)}
 =-\frac{\prod_{i=1}^3(v_4v_i-1)}{e\prod_{i=1}^3(v_4-v_i)}.
\]
If the two leading coefficients canceled, subtraction of these cubic
products would give
\[
 e\prod_{i=1}^3(v_i-e)\,v_4(v_4+e)=0.
\]
Every factor is nonzero: a zero factor would be a zero branch or an endpoint
root. Thus the aggregate coefficient still has degree six.

For distance four, put \(V=\prod_i v_i\). Directly from (N5),
\(A(v^{-1})=VA(v)\). At a positive full collision, \(V=1\), the
leading terms add. At a negative full collision, \(V=-1\), they cancel.
Since \(S(v^{-1})=-4-S(v)\), (N6) gives the retained degree-five
coefficient
\[
 -12A(v)(2+S(v))/4608.                                         \tag{N8}
\]
It is nonzero in this mixed family. Here are the necessary details.
Let \(s_j\) be the elementary symmetric functions of the four \(v_i\)
with \(s_4=-1\), and let \(J(z)=\prod_i(z-v_i)\). Then
\[
 2+S(v)=\frac{s_1^2-s_3^2-4s_2}{J(1)J(-1)}.
\]
The root identities from (N1) give
\[
 \begin{aligned}
 s_1-s_3&=-w,\\
 s_1s_3&=4-2t,\\
 s_2(s_1+s_3)&=6tw.
 \end{aligned}
\]
If the numerator vanished, these equations would force
\(q+16t+16=0\). The coefficientwise identity
\[
 B(t,-16(t+1))=-576t^3
\]
rules this out at a negative full collision, because
\[
 F(1)=q^2(q+36t^2)^2,\qquad F(-1)=B(t,q)^2.                    \tag{N9}
\]
Both identities in (N9) are checked over \(\mathbb Q[t,q]\).
There is exactly one cluster at the negative base when it occurs. Every
other distinct base contributes order seven, and that one contributes six.
This proves \(7h-\delta\) for simple roots, including every intersection
of their collision conditions.

## 4. What confluence does to a coefficient degree

Suppose a root of multiplicity \(m\) is split formally as
\(r+e_1,\ldots,r+e_m\), and choose a local branch \(z\), with
\(r=z+z^{-1}\). Its logarithmic derivative is
\(\alpha=1/(z-z^{-1})\ne0\). Choose \(k\) of the plus branches and
\(m-k\) inverse branches. In the denominator following (N5), exactly the
\(k(m-k)\) cross-branch factors vanish. Each has linear part
\(\alpha(e_i-e_j)\), with \(i\) in the plus set and \(j\) outside it.
All other factors have nonzero limits.

Group the choices of the plus set before taking the confluent divided
difference. This grouped numerator is alternating in the root variables,
so division by their Vandermonde is regular. Every coefficient of \(L_n\)
is Laurent polynomial, and hence has no further poles. Consequently the
coefficient degree can increase by at most \(d=k(m-k)\).

The leading coefficient increases by exactly \(d\). To see that it does not
cancel, take the leading degree-six term and expand its exponential factor.
Up to a common nonzero factor, the required local limit is
\[
 \sum_{\substack{I\subseteq\{1,\ldots,m\}\\ \#I=k}}
 \frac{\exp(\tau\sum_{i\in I}e_i)}
      {\prod_{i\in I,\ j\notin I}(e_i-e_j)},
 \qquad \tau=2\alpha n.
\]
For the multiplicities needed here, its value at all \(e_i=0\) is

| \((m,k)\) | Local value |
|---|---|
| \((2,1)\) | \(\tau\) |
| \((3,1)\) | \(\tau^2/2\) |
| \((3,2)\) | \(\tau^2/2\) |

These identities are algebraic divided differences. The first is
\((e^{\tau e_1}-e^{\tau e_2})/(e_1-e_2)\). The second is its second
divided difference, whose coincident value is the quadratic Taylor coefficient
\(\tau^2/2\). For the third, use the complement of the two-element set;
the expression becomes \(e^{\tau\sum e_i}\) times the second divided
difference of \(e^{-\tau x}\), with the same value. This uses only finite
Taylor coefficients over a characteristic-zero field. It does not use an
analytic limit or an assumption about positive measures.

All common factors are nonzero, including \(\alpha\) and the nonvanishing
factors of (N5). Lower powers of \(n\) have the same pole bound and cannot
cancel this highest power. Thus the exact degree of this grouped coefficient is
\[
 6+k(m-k).
\]
For several repeated roots the contributions add; in particular two double
roots give degree \(6+k_1(2-k_1)+k_2(2-k_2)\).

After this confluence, the coefficient functions are regular whenever the
distinct root groups stay distinct and avoid the endpoints. Further spectral
collisions therefore combine finite coefficient polynomials; they do not create
another degree increase.

## 5. A double root and every collision on its locus

Let the roots be \(r,r,s,t_0\). The double root is nonzero, by (N7) and
the zero-root derivative calculation. There are eight modes in which its two
branches have the same sign; call these the A modes. They have degree six and
their leading coefficients are the regular repeated-entry values of (N5).
The four mixed-sign modes from that double root, the B modes, have bases
\(2au\,z_s^{\pm1}z_{t_0}^{\pm1}\) and degree seven.

The four B bases are distinct and none is \(\pm2au\): otherwise the two
simple roots would be equal or opposite, or an endpoint would occur.
A collision involving B and one or more A modes retains degree seven,
because only one B mode belongs to each such cluster.

An A-only cluster has at most two modes. Regard an A sign vector as a
four-bit vector with its first two bits equal. A distance-two collision that
flips those first two bits would require \(z_r^4=1\), hence
\(r\in\{0,2,-2\}\), all excluded. The other distance-one and distance-two
collisions were already excluded in section 3. The same binary-code argument
therefore applies. Distance-three pairs retain degree six; the calculation
in section 3 permits repeated entries in (N5). A positive full pair also
retains degree six. The negative full pair has exact degree five by (N8);
the symmetric identities proving its nonvanishing also permit repeated entries.

Exactly four of the \(h\) clusters contain B modes. Their contributions
are eight each, and the others contribute seven, except for the one possible
negative full pair. Thus the order is
\[
 4\cdot8+(h-4)\cdot7-\delta=7h+4-\delta.
\]
This includes intersections of confluence with every spectral collision,
without assuming that the discriminant locus is smooth.

## 6. The two remaining multiplicity types

For two double roots, write \(R=(x^2+sx+p)^2\). Coefficient comparison gives
\[
 2s=w,\quad p=6t-4,\quad s^2+2p=2t-8,\quad p^2=16-8t.
\]
Since \(t\ne0\), these imply
\[
 t=10/9,\qquad q=-400/9,\qquad
 R=(x^2+wx/2+8/3)^2.                                         \tag{N10}
\]
At this exact rational \((t,q)\), the coefficientwise characteristic replay
and exact polynomial gcd give \(h=9\). There are at most nine confluent
bases, indexed by \((k_1,k_2)\in\{0,1,2\}^2\), so this check proves
that all nine are distinct. Four have degree six, four have degree seven,
and the central mode has degree eight. Their order is
\(4\cdot7+4\cdot8+9=69\). The check also gives \(\delta=0\).
This is exhaustive for this root type because (N10) is forced, not inferred
from a sample.

For a triple root, write \(R=(x-r)^3(x-s)\), with \(y=r^2\).
Matching the two lower coefficients, after using the upper coefficients to
eliminate \(t,w\), gives
\[
 \begin{aligned}
 26r^3+33r^2s+9rs^2+60r+20s&=0,\\
 r^3s+12r^2+12rs+16&=0.
 \end{aligned}
\]
Here \(r\ne0\), and \(y+12\ne0\), since the second equation would
otherwise be \(-128=0\). Therefore
\[
 \begin{aligned}
 s&=-\frac{4(3y+4)}{r(y+12)},\\
 P(y)&=13y^4+144y^3+480y^2+1280y-768=0,\\
 t&=\frac{3y^2+8y+48}{2(y+12)},\\
 q&=\frac{(3y^2+24y-16)^2}{y(y+12)^2}.
 \end{aligned}                                                \tag{N11}
\]
Substitution into the first equation, multiplied by \(r(y+12)^2\), gives
exactly \(2P(y)\); the replay checks every coefficient of this identity.

The eight potential bases are \(2au\,z_r^{2k-3}z_s^{\epsilon}\),
\(k=0,1,2,3\), \(\epsilon\in\{-1,1\}\). Within a fixed sign of
\(\epsilon\), a collision would require \(y\in\{0,1,4\}\).
Between the two signs, it would require
\(s=\pm C_j(r)\), \(j=0,1,2,3\).
Put
\[
 D(y)=y(y+12)^2,\qquad M(y)=16(3y+4)^2,
 \qquad s^2=M(y)/D(y).
\]
The certificate supplies exact Bezout identities between \(P\) and each of
\[
 \begin{aligned}
 &y(y-1)(y-4),\quad M-yD,\quad M-4D,\\
 &M-(y-2)^2D,\quad M-y(y-3)^2D,\\
 &y(y+12),\quad 3y^2+8y+48,\quad 3y^2+24y-16.
 \end{aligned}                                                \tag{N12}
\]
Each identity has the form \(UP+VQ=1\) over \(\mathbb Q[y]\), checked
coefficientwise by the separate replay. The first five exclude every listed
collision, and the remaining ones verify the denominators and nonzero
parameters in (N11). All eight bases are therefore distinct, over every
characteristic-zero field. Four coefficients have degree six and four have
degree eight, giving order \(4\cdot7+4\cdot9=64\). Their distinctness
also gives \(h=8\) and \(\delta=0\).

Finally, a quadruple root \(R=(x-r)^4\) would have \(r\ne0\) and,
with \(y=r^2\), would require
\[
 17y+20=0,\qquad y^2+24y+16=0.
\]
The latter's remainder modulo the former is \(-3136/289\ne0\).
Thus no further multiplicity type exists in this nonzero family.

## 7. Minimality, coefficient field, and initial index

An exponential polynomial \(\lambda^N p(N)\), with \(\lambda\ne0\)
and \(\deg p=d\), has a generating-function pole of exact order \(d+1\)
at \(z=\lambda^{-1}\). Its leading pole coefficient contains the nonzero
factor \(d!\) times the leading coefficient of \(p\). Distinct bases give
distinct poles. Hence the minimal eventual recurrence order is exactly the
sum of these \(d+1\), after combining equal bases. This proves the lower
bounds as well as the annihilators counted above.

The calculations can be made in a finite splitting field. Permuting roots
or inverting the chosen lifts permutes the summands. Consequently the monic
minimal annihilator is invariant under the splitting field's Galois group,
so it lies in the original field. Its order is unchanged by that extension.
Likewise, the gcd degrees in (N3) are unchanged by field extension.

For repeated roots, (N4) uses the rows of derivatives divided by their
factorials and the confluent Vandermonde
\(\prod_{i<j}(r_j-r_i)^{m_im_j}\). The low-index boundary identities of
Theorem L are polynomial identities in the quartic coefficients, so they
remain valid under this confluence. Equivalently, the initial coefficient
determinants are unchanged when evaluations are replaced by these normalized
jets. Thus the exponential polynomial gives the actual \(W_N\) for every
\(N\ge1\). Its continuation at zero is still \(1/2\), by the same
degree-three boundary determinant as in Theorem L.

Every base is nonzero. The minimal annihilator therefore has nonzero constant
coefficient, and its residual at zero is half that coefficient, since the actual
empty determinant is one. The recurrence cannot be extended to index zero
without increasing its order. This completes the stated classification.

## 8. Exact examples and reproduction

These examples use \(a=u=1\), \(b=t\), and \(v^2=q\). Negative or
nonsquare \(q\) can be interpreted in the corresponding quadratic extension.

| \(t\) | \(q\) | Root type | \(h\) | \(\delta\) | Minimal order |
|---|---|---|---|---|---|
| 1 | 4 | \(1+1+1+1\) | 16 | 0 | 112 |
| 1 | 1 | \(1+1+1+1\) | 14 | 0 | 98 |
| 1 | -36 | \(1+1+1+1\) | 15 | 0 | 105 |
| \(8/9\) | \(-16/9\) | \(1+1+1+1\) | 15 | 1 | 104 |
| 2 | -144 | \(1+1+1+1\) | 14 | 1 | 97 |
| 2 | \(-36/5\) | \(1+1+1+1\) | 12 | 0 | 84 |
| \(2/15\) | \(8/3\) | \(2+1+1\) | 12 | 0 | 88 |
| \(10/9\) | \(1/54\) | \(2+1+1\) | 12 | 0 | 88 |
| \(10/9\) | \(-400/9\) | \(2+2\) | 9 | 0 | 69 |
| \(40/27\) | \(-400/81\) | \(2+1+1\) | 12 | 0 | 88 |

An order-64 example is given exactly by (N11), taking the unique positive
root of \(P(y)\). It lies between \(49/100\) and \(1/2\): the endpoint
values have opposite signs and \(P'(y)>0\) for \(y>0\).

For rational \(t,q\), the defining determinants can be calculated without
choosing a square root. Divide moment number \(j\) by \(w^j\). The new
even and odd moments are respectively
\[
 \frac{(1+tm)\binom{2m}{m}}{q^m},\qquad
 \frac{(2m+1)(1+tm)\binom{2m}{m}}{q^m}.
\]
The determinant of these rational moments, multiplied by
\(q^{N(N-1)/2}\), is the normalized \(W_N\). This follows from the
diagonal row and column basis change, including singular minors.

The separate standard-library replay verifies the nine characteristic
coefficient lists on 45 degree-complete parameter nodes. At coefficient
index \(j\le8\), homogeneity gives degree at most \(j\) in \(t\)
and at most \(j\) in \(w\); evenness in \(w\) gives degree at most
\(\lfloor j/2\rfloor\) in \(q\). The 9-by-5 grid therefore proves
coefficient coverage; reciprocal symmetry supplies the other coefficients.
It also verifies (N9), (N12), the triple-root elimination, and the two-double
support calculation.

The ten sample GFs are reconstructed under Theorem L's all-index bound and
have exact cross-multiplication and degree-preserving modular Bezout
certificates. Their parameter interpolation uses 57 distinct squared nodes,
covering the proved degree at most 56 in \(q\) through \(W_{112}\).
The finite confluence regressions independently use rational lifted roots,
polynomial jets, and actual monomial determinants. Those regression quartics
need not belong to the mixed family; their orders are checks of the mechanism.

Finite samples alone do not prove this theorem. Universal coverage follows
the collision and confluence arguments above and the coefficientwise leaves
with their proved bounds. Review provenance is project self-review;
independent review, historical novelty and Lean formalization are unassessed.
Pointwise quadratic-weight orders and higher-degree or higher-order mixed
families remain separate research targets.
