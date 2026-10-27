# Contracting Arithmetic Torsion and Theta Transport in the Pure Cubic Hilbert 12 Test

**Author:** Komorebi P.

**Status:** Exact arithmetic, finite group, and analytic distribution identities. The required elliptic-gamma to class-field comparison remains open.

## Abstract

The inverse cubic unit acting on the full seventh-torsion reduction of the original period lattice has order 21, although its distinguished eigenline has order three. The seven-point packet therefore omits the unipotent extension needed to retain the perfect dual pairing with the complementary torsion direction. An explicit 343-point ambient packet restores that data. Its action has one fixed point, two three-cycles, and sixteen twenty-one-cycles. Exact integer period carries are obtained for every point, yielding a theta-valued contracting transport for the full packet. Independently, a three-direction elliptic-gamma distribution formula is proved by roots-of-unity filtering. In the conductor-three specialization its untwisted seventh norm cancels the distinguished gamma value, identifying a precise limitation of scalar norms. The remaining mathematical problem is a normalized, character-sensitive analytic-to-arithmetic comparison.

## 1. Fixed setting

Let

\[
\omega^2+\omega+1=0,\quad \beta^3=7,\quad
\varepsilon=2-\beta,\quad \rho=\varepsilon^{-1}=\beta^2+2\beta+4.
\]

Choose the complex embedding \(\beta=7^{1/3}\omega^2\), so \(|\rho|<1\). Put

\[
\tau=\frac{\beta^2+2\beta}{15},\qquad
\sigma=-\frac{\beta+2}{15},\qquad t=-\tau,
\quad z_0=\frac13.
\]

The analytic function is the fifth-smoothed elliptic gamma

\[
F(z)=\frac{\Gamma_{\mathrm{ell}}(z;\tau,\sigma)^5}
{\Gamma_{\mathrm{ell}}(5z;5\tau,5\sigma)},\qquad U_\Gamma=F(z_0).
\]

The inherited exact functional equations are

\[
F(z+1)=F(z),\qquad
F(z+\tau)=q_\sigma(z)F(z),\qquad
F(z+\sigma)=q_t(z)^{-1}F(z),
\]

where

\[
q_a(z)=\frac{\theta_0(z;a)^5}{\theta_0(5z;5a)}.
\]

The previously established zero-anchor normalization is \(F(0)=\varepsilon^2\ne0\). The divisor support is contained in
\(\Lambda_5=\mathbb Z\tau+\mathbb Z\sigma+\tfrac15\mathbb Z\). These analytic facts are inherited inputs, not freshly formalized in Lean here.

The arithmetic lattice is \(\Lambda=\mathbb Z\tau+\mathbb Z\sigma+\mathbb Z\). Multiplication by \(\varepsilon\) on its ordered basis is

\[
M=\begin{pmatrix}0&1&0\\-4&2&15\\-1&0&4\end{pmatrix},\qquad
R=M^{-1}=\begin{pmatrix}8&-4&15\\1&0&0\\2&-1&4\end{pmatrix}.
\]

We use \(R\) for the integral matrix and \(\rho\) for the corresponding scalar multiplication.

## 2. Semisimple and unipotent actions at seven

Let \(N=M-2I\pmod7\). Then \(N^3=0\) and \(N^2\ne0\). Define

\[
u=(1,2,4)^T,\quad v=(0,1,2)^T,\quad w=(0,0,1)^T.
\]

Modulo seven they give the complete Jordan chain

\[
Nu=0,\qquad Nv=u,\qquad Nw=v.
\]

The matrix with columns \(u,v,w\) has determinant one. Consequently the three vectors form an integral basis.

In characteristic seven,

\[
R=(2I+N)^{-1}=4I+5N+N^2.
\]

Cubing and taking seventh powers gives

\[
R^3-I=2N+5N^2\pmod7,\qquad
R^7=4I\pmod7,\qquad R^{21}=I\pmod7.
\]

Because \(R^3-I\ne0\), the order of \(R\) in \(\mathrm{GL}_3(\mathbb F_7)\) is exactly 21. Its one-dimensional eigenline has scalar action \(4\), of order three. Thus the order-three torsion packet is the semisimple slice of a nonsemisimple order-21 arithmetic operator.

For reference, the codifferent pairing from the earlier study has Gram matrix

\[
H=\begin{pmatrix}4&-4&15\\-4&1&0\\15&0&0\end{pmatrix},\qquad
M^T H=HM,
\]

and, in the ordered basis \(u,v,w\), its reduction is

\[
\begin{pmatrix}0&0&1\\0&1&0\\1&0&0\end{pmatrix}\pmod7.
\]

The essential duality is \(\langle u,w\rangle_H=1\) while \(\langle u,u\rangle_H=\langle u,v\rangle_H=0\) modulo seven. A stable linear subspace containing \(w\) also contains \(v=Nw\) and \(u=N^2w\). Thus both the full unit action and this nontrivial socle-to-top pairing require the complete three-dimensional module.

## 3. Three levels of torsion packets

Put

\[
\delta=\frac{\tau+2\sigma+4}{7},\qquad
\eta=\frac{\sigma+2}{7},\qquad
\xi=\frac17.
\]

The seven-point packet has arguments \(z_0+k\delta\). The first refinement consists of \(z_0+k\delta+\ell\eta\), with 49 labels. The full ambient packet is

\[
\boxed{z_{k,\ell,j}=z_0+k\delta+\ell\eta+j\xi,\qquad
k,\ell,j\in\{0,\ldots,6\}.}
\]

Since \(\delta,\eta,\xi\) are the images of \(u/7,v/7,w/7\), and \(\det[u\ v\ w]=1\), the 343 labels represent all of \(\tfrac17\Lambda/\Lambda\). Here this is torsion of the rank-three lattice quotient, not a claim that the nondiscrete rank-three quotient is an ordinary elliptic curve.

The three generator transport equations are exact:

\[
\begin{aligned}
\rho z_0&=z_0+5\tau+1,\\
\rho\delta&=4\delta+8\tau-\sigma,\\
\rho\eta&=5\delta+4\eta+3\tau-2\sigma-3,\\
\rho\xi&=\delta+5\eta+4\xi+2\tau-\sigma-2.
\end{aligned}
\]

Hence the induced action on finite labels is

\[
\boxed{T(k,\ell,j)=(4k+5\ell+j,\ 4\ell+5j,\ 4j)\pmod7.}
\]

The complete orbit decomposition is

\[
\boxed{343=1+2\cdot3+16\cdot21.}
\]

Restricting to \(j=0\) gives \(49=1+2\cdot3+2\cdot21\). Restricting again to \(\ell=j=0\) gives \(7=1+2\cdot3\). All orbit decompositions were enumerated exactly. The quotient action, not a heuristic spectral analogy, produces these numbers.

### The explicit 343 carry formula

For \((k,\ell,j)\), set

\[
A_0=4k+5\ell+j,\qquad B_0=4\ell+5j,\qquad C_0=4j,
\]

and let

\[
q_1=\lfloor A_0/7\rfloor,\quad
q_2=\lfloor B_0/7\rfloor,\quad
q_3=\lfloor C_0/7\rfloor.
\]

Write \((k',\ell',j')=(A_0,B_0,C_0)\bmod7\). Then

\[
\boxed{
\rho z_{k,\ell,j}=
 z_{k',\ell',j'}+a\tau+b\sigma+c
}
\]

with the **integer** carries

\[
\begin{aligned}
a&=5+8k+3\ell+2j+q_1,\\
b&=-k-2\ell-j+2q_1+q_2,\\
c&=1-3\ell-2j+4q_1+2q_2+q_3.
\end{aligned}
\]

These identities were checked symbolically for every one of the 343 labels. They are also immediate by substituting the four generator equations above and reducing each generator modulo its seventh period.

### Divisor avoidance

No \(z_{k,\ell,j}\) lies in \(\Lambda_5\). To see this, compare the rationally independent coefficients of \(\tau,\sigma,1\). The coefficient of \(\tau\) forces \(k=0\), that of \(\sigma\) then forces \(\ell=0\), while \(1/3+j/7\) is never in \(\tfrac15\mathbb Z\). The unit \(\rho\) preserves \(\Lambda_5\) since

\[
\rho\tau=8\tau+\sigma+2,\qquad
\rho\sigma=-4\tau-1,\qquad
\rho/5=3\tau+4/5,
\]

and the inverse \(\varepsilon\) also preserves \(\Lambda_5\). Thus every contracting orbit avoids the divisor of \(F\).

## 4. An exact theta-valued contracting transport

Let \(x=(k,\ell,j)\in V=(\mathbb Z/7)^3\) and \(z_x=z_{k,\ell,j}\). Define

\[
f_x^{(m)}=F(\rho^m z_x),\qquad m\ge0.
\]

Let \(d_x=(a_x,b_x,c_x)^T\) be the integer carry vector from Section 3. At stage \(m\), the carry is \(d_{x,m}=R^{m-1}d_x\in\mathbb Z^3\). Set \(W_{x,m}=\rho^{m-1}z_{T x}\). By the arithmetic transport formula,

\[
\rho^m z_x=W_{x,m}+a_{x,m}\tau+b_{x,m}\sigma+c_{x,m}.
\]

For an integer \(n\), define the oriented finite product

\[
\mathcal P(g;n,w,h)=
\begin{cases}
\prod_{r=0}^{n-1}g(w+rh),&n>0,\\
1,&n=0,\\
\prod_{r=n}^{-1}g(w+rh)^{-1},&n<0.
\end{cases}
\]

The multiplier is the explicit theta product

\[
\boxed{
C_x^{(m)}=
\mathcal P(q_t^{-1};b_{x,m},W_{x,m},\sigma)\,
\mathcal P(q_\sigma;a_{x,m},W_{x,m}+b_{x,m}\sigma,\tau).
}
\]

It follows solely from the gamma shift identities that

\[
\boxed{f_x^{(m)}=C_x^{(m)} f_{T x}^{(m-1)}.}
\]

As \(\rho^m z_x\to0\), all \(f_x^{(m)}\to F(0)=\varepsilon^2\). Every multiplier is nonzero at the chosen arguments, and
\(C_x^{(m)}=1+O(|\rho|^{m-1})\).

Thus the finite telescope has an absolutely convergent infinite limit:

\[
\boxed{
F(z_x)=\varepsilon^2
\prod_{m=1}^{\infty}
\left(C_{T^{-m}x}^{(m)}\right)^{-1}.
}
\]

This exact expression is branch-free: it uses only ordinary meromorphic theta quotients and their products. For the seven-point eigenline \(T^{-m}k=2^m k\bmod7\), recovering the previous seven-packet identity. The full 343-point form also transports all unipotent directions.

This is a normalized *analytic* realization. No conclusion that its special values belong to the cubic class field is drawn.

## 5. A complete three-direction distribution identity

The absolutely convergent logarithm of our fifth-smoothed gamma on a suitable strip is

\[
L_{t,\sigma}(z)=-5\sum_{\substack{m\ge1\\5\nmid m}}
\frac{P^m e^{2\pi imz}-Q^m e^{-2\pi imz}}
{m(1-P^m)(1-Q^m)},\qquad
P=e^{2\pi it},\ Q=e^{2\pi i\sigma}.
\]

For \(n\ge1\), define the complete rank-three distribution

\[
\mathcal N_n F(z)=
\prod_{u=1-n}^{0}\prod_{v=0}^{n-1}\prod_{j=0}^{n-1}
F\left(z+\frac{ut+v\sigma+j}{n}\right).
\]

**Distribution theorem.** As meromorphic functions,

\[
\boxed{
\mathcal N_nF(z)=
\begin{cases}F(nz),&5\nmid n,\\1,&5\mid n.\end{cases}
}
\]

**Proof.** Work first where all logarithmic series converge normally, which includes real \(z\) in the fixed upper half-plane conventions. Summing over \(j\) gives zero unless the Fourier index is divisible by \(n\). For Fourier index \(nq\), the two other finite geometric series yield

\[
\sum_{u=1-n}^{0}P^{qu}
=P^{-(n-1)q}\frac{1-P^{nq}}{1-P^q},\qquad
\sum_{v=0}^{n-1}Q^{qv}
=\frac{1-Q^{nq}}{1-Q^q}.
\]

The analogous inverse sums in the negative part cancel its denominators in the same way. Thus the total logarithm is

\[
-5\sum_{\substack{q\ge1\\5\nmid nq}}
\frac{P^q e^{2\pi i nq z}-Q^q e^{-2\pi i nq z}}
{q(1-P^q)(1-Q^q)}.
\]

When \(5\nmid n\), the condition \(5\nmid nq\) is exactly \(5\nmid q\), giving \(L_{t,\sigma}(nz)\). When \(5\mid n\), no terms remain and the logarithm is zero. Exponentiating proves the equality in the convergence region. Meromorphic continuation gives the stated identities. \(\square\)

At \(n=7\) and \(z_0=1/3\), period-one invariance gives

\[
\boxed{\mathcal N_7F(1/3)=F(7/3)=F(1/3)=U_\Gamma.}
\]

The chosen shifts \((ut+v\sigma+j)/7\) represent the same full 343-element torsion module as \(k\delta+\ell\eta+j\xi\), but their selected representatives differ by integer periods, which introduces explicit theta factors. In the canonical distribution representatives the fixed, zero-shift factor is \(U_\Gamma\). Removing it gives the exact 342-factor identity

\[
\boxed{
\prod_{(u,v,j)\ne(0,0,0)}
F\left(\frac13+\frac{ut+v\sigma+j}{7}\right)=1.
}
\]

**Interpretation.** The untwisted complete norm cannot determine the arithmetic phase of \(U_\Gamma\), because that factor cancels. Extra finite torsion alone does not remove the need for an oriented or character-sensitive comparison.

## 6. The dual-character target

In the integral Jordan basis \(u,v,w\), the perfect codifferent pairing modulo seven has matrix

\[
G_H=\begin{pmatrix}0&0&1\\0&1&0\\1&0&0\end{pmatrix}.
\]

Fix the oriented seventh-root phase \(\zeta_7=e^{2\pi i/7}\). The additive character against the top dual direction is

\[
\boxed{\psi_w(k,\ell,j)=\zeta_7^{3k}.}
\]

Under inverse-unit transport, its exponent changes as

\[
\boxed{\psi_w(T(k,\ell,j))=\zeta_7^{3(4k+5\ell+j)}.}
\]

So the dual character is sensitive to all levels of the Jordan chain after transport, unlike its restriction to the seven-point eigenline. This explicitly identifies the missing extension data.

One must not form arbitrary complex-character powers of the gamma values and call the result a single-valued meromorphic function. The earlier primitive-sector residue obstruction rules that out. A valid comparison should use integral monomial coordinates, a geometric theta/gerbe lift, or a coherently normalized logarithmic/cocycle construction.

A successful next theorem would compute a character-sensitive, correctly based analytic transport and prove that its arithmetic evaluation agrees with the oriented Gauss/Jacobi coordinate \(J=2+3\omega\). The fixed desired scalar identity remains

\[
\operatorname{Im}(C_{\mathrm{pol}}U_\Gamma^3)=0
\]

with the already established modulus and separately specified branch conditions. None of the present identities establishes this equality.

## 7. Character transport in the full Fourier space

Let \(V=(\mathbb Z/7)^3\), \(\zeta=\exp(2\pi i/7)\), and let \(\mathcal F\) be the ordinary finite Fourier transform

\[
\widehat f(a)=\sum_{x\in V}\zeta^{a\cdot x}f(x),\qquad a\in V.
\]

It uses no multivalued powers of the function values. For the actual theta-return vector, the preceding theorem gives

\[
f_m(x)=C_m(x)f_{m-1}(Tx),\qquad x\in V.
\]

Fourier inversion and a change of variables give the **exact dual transfer formula**

\[
\boxed{
\widehat f_m(a)=\frac1{343}\sum_{b\in V}
\widehat C_m(a-b)\,\widehat f_{m-1}(T^{-T}b).
}
\]

Thus the arithmetic operation sends each dual character to its inverse-transpose transport, while multiplication by the analytic theta multiplier produces convolution in Fourier space. This retains precisely the mode coupling that disappears if one diagonalizes only the cubic permutation and drops its theta carries.

In the basis \(u,v,w\), the dual transport matrix is

\[
T^{-T}=\begin{pmatrix}2&0&0\\1&2&0\\0&1&2\end{pmatrix}\pmod7.
\]

The covector \(a_0=(1,0,0)^T\), corresponding to the oriented complementary pairing with \(w\), has an orbit of length **21** under this matrix. Its first three iterates are

\[
(2,1,0)^T,\qquad (4,4,1)^T,\qquad(1,5,6)^T.
\]

A primitive dual character therefore does not close under a single order-three Fourier eigenvalue. Even before analytic theta mixing, it generates a twenty-one-term arithmetic orbit. The missing phase comparison should respect this full dual transport and its prescribed orientation.

The displayed Fourier formula is finite linear algebra and is proved independently of the unproved arithmetic evaluation. It supplies an exact, single-valued computational target, not a claim that any weighted gamma sum is already algebraic.

## 8. Verification record and boundaries

The accompanying verifier checks 343 exact carries, the full orbit classification, the order-21 reduction, the length-three pairing, the two lower-level packets, and the arithmetic support argument. The seven-packet companion checks the rank-two monomial action and first-step theta formulas.

An independent numerical distribution test covers \(n=2,3,5,7\) with 38-digit arithmetic and finite truncation. The absolute logarithmic residual in the n=7 test was approximately \(10^{-37}\). These are regression tests and not directed interval certificates. The multiplication theorem itself is the exact Fourier-series proof above.

**Not proved:** the BCG elliptic-gamma algebraicity and reciprocity conjectures, the exact polarized phase, the Eisenstein deck descent/gerbe identification, or the general Hilbert 12 problem. No new Lean compilation was performed for this checkpoint.

## Source foundations

- *Cubic Divisor Transport and Reconstruction*, Komorebi P.
- *An Ambient Cyclic Cubic and the Elliptic Gamma Fourier Obstruction*, Komorebi P.
- *An ambient dual slice for the pure cubic Hilbert 12 experiment*, Komorebi P.
- *Holomorphic descent, complementary gerbe torsion, and the oriented Gauss character*, Komorebi P.
- Bergeron, Charollois and García, *Elliptic Units for Complex Cubic Fields*. The algebraicity and complex reciprocity claims remain conjectural in the source material.

The results above are mathematical continuations under the inherited analytic conventions. The algebraic identities are self-contained, and every claim beyond their scope is explicitly separated from them.
