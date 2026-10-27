# Komorebi Hilbert 12 Program — Consolidated Working State

**Date:** 2026-10-02  
**Current test case:** \(K=\mathbf Q(\beta)\), \(\beta^3=7\), with the fixed complex embedding
\[
\beta=7^{1/3}e^{-2\pi i/3}.
\]

## 0. Status in one sentence

For the Bergeron–Charollois–García pure cubic example we now have an explicit arithmetic ray-field model, a Jacobi/Kummer coordinate, an unramified cubic model, a three-isogeny interpretation, a classical CM seven-torsion realization, an exact theta-return formula for the elliptic-gamma value, and an explicit Stark-type algebraic predecessor \(W\). The remaining gap is still the analytic-to-arithmetic comparison proving that the actual elliptic-gamma special value equals the explicit algebraic unit.

This is **not** a solution of Hilbert's twelfth problem in general, nor yet a proof of the BCG algebraicity conjecture even for this example.

---

# 1. Original analytic target

Define
\[
\tau=\frac{\beta^2+2\beta}{15},\qquad
\sigma=-\frac{\beta+2}{15},
\]
and
\[
U_\Gamma=
\frac{\Gamma_{\rm ell}(1/3;\tau,\sigma)^5}
     {\Gamma_{\rm ell}(5/3;5\tau,5\sigma)}.
\]

The conjectured algebraic value is a root of the reciprocal sextic
\[
\begin{aligned}
Q(X)={}&X^6+(6\beta^2-14\beta+2)X^5+(4\beta^2-6\beta+2)X^4\\
&+(106\beta^2-152\beta-103)X^3\\
&+(4\beta^2-6\beta+2)X^2+(6\beta^2-14\beta+2)X+1.
\end{aligned}
\]

Writing \(Y=X+X^{-1}\),
\[
Q(X)=X^3R(Y),
\]
where
\[
R(Y)=Y^3+(6\beta^2-14\beta+2)Y^2
 +(4\beta^2-6\beta-1)Y
 +(94\beta^2-124\beta-107).
\]

Thus an exact proof that
\[
R(U_\Gamma+U_\Gamma^{-1})=0
\]
already puts \(U_\Gamma\) among the six algebraic candidates. The rigorous numerical separation established in the earlier audit then selects the intended branch.

---

# 2. Stage I — Jacobi/Kummer reconstruction

Let \(\omega^2+\omega+1=0\). For the cubic character modulo \(7\), the finite Jacobi sum is
\[
J=2+3\omega.
\]

The associated Gauss sum satisfies
\[
G^3=7J.
\]
With
\[
\eta=G/\beta,
\]
we obtain
\[
\eta^3=J=2+3\omega.
\]

For a real seventh-cyclotomic coordinate \(t=\zeta+\zeta^{-1}\),
\[
t^3+t^2-2t-1=0,
\]
and Fourier inversion gives
\[
t=\frac{-1+\beta\eta+\beta^2/\eta}{3}.
\]

An explicit quadratic map \(Y(t)\) sends the three conjugates of \(t\) to the three roots of \(R\), and an explicit \(Z(Y)\) satisfies
\[
Y^2-4=-3Z(Y)^2.
\]
Therefore
\[
U_{\rm alg}=\frac{Y-(1+2\omega)Z(Y)}{2}
\]
is a root of \(Q\), and
\[
K(U_{\rm alg})=K(\omega,\eta)
\]
has degree six over \(K\).

The primitive cubic Lagrange resolvent has exact scale
\[
Y_0+\omega Y_1+\omega^2Y_2=c(\beta,\omega)G,
\]
where
\[
c(\beta,\omega)
=
\frac{(8\beta^2-18\beta+7)\omega+(19\beta^2-41\beta+7)}7.
\]
Hence
\[
\left(
\frac{Y_0+\omega Y_1+\omega^2Y_2}
{\beta c(\beta,\omega)}
\right)^3
=2+3\omega.
\]

This was our first precise analytic Fourier-resolvent target.

---

# 3. Stage II — Eta anchor and torsion selector

Put \(t=-\tau\) and \(\epsilon=2-\beta\). For
\[
F(z)=
\frac{\Gamma_{\rm ell}(z;-t,\sigma)^5}
     {\Gamma_{\rm ell}(5z;-5t,5\sigma)},
\]
the target is \(F(1/3)=U_\Gamma\).

Using exact eta transformations,
\[
F(0)=\epsilon^2=(2-\beta)^2.
\]

A control calculation at \(z=1/2\) gives a nonconstant eta quotient at an algebraic non-CM parameter. Schneider's theorem then shows
\[
F(1/2)\ \text{is transcendental}.
\]
This proves that rational torsion by itself is not enough to force algebraicity.

Multiplication by \(\epsilon\) in the arithmetic lattice is represented by
\[
M=
\begin{pmatrix}
0&1&0\\
-4&2&15\\
-1&0&4
\end{pmatrix}.
\]

The Smith normal form of \(M-I\) is \(\operatorname{diag}(1,1,6)\), so the unit-fixed torsion group is cyclic of order six.

A convenient generator is
\[
g=\left(-\frac12,\frac12,-\frac16\right)\pmod{\mathbf Z^3},
\]
because
\[
(M-I)g=(1,0,0)^T.
\]
It satisfies
\[
2g\equiv(0,0,-1/3),\qquad
3g\equiv(1/2,1/2,1/2)\pmod{\mathbf Z^3}.
\]

So the conductor-three target occurs naturally inside the order-six fixed-torsion geometry. However, the raw scalar \(F(z)\) does **not** descend to this quotient: pure period shifts can introduce transcendental multipliers. The six ray-class special values therefore must be treated as coherently transported geometric gamma data, not as evaluations of one raw \(F\) at the six multiples of \(g\).

---

# 4. Stage III — Contracting unit return and Jacobi determinant

Let
\[
r=\epsilon^{-1}=\beta^2+2\beta+4.
\]
The inverse unit matrix
\[
N=M^{-1}
=
\begin{pmatrix}
8&-4&15\\
1&0&0\\
2&-1&4
\end{pmatrix}
\]
satisfies
\[
(\tau,\sigma,1)N=r(\tau,\sigma,1).
\]

Starting from \(z_0=1/3\), integer return coordinates \(a_m\) satisfy
\[
z_0+a_m\tau+a_{m-1}\sigma+d_m=r^m/3
\]
and
\[
a_{m+3}=12a_{m+2}-6a_{m+1}+a_m.
\]

With
\[
\Theta(z;v)=\frac{\theta_0(z;v)^5}{\theta_0(5z;5v)},
\]
one proves the exact period exchange
\[
\Theta(z_0+j\tau;\sigma)=\Theta(z_0+j\sigma;t).
\]

Define
\[
P_m=
\prod_{j=a_{m-1}}^{a_m-1}\Theta(z_0+j\sigma;t).
\]
Then for every finite \(m\),
\[
P_m=\frac{F(r^m/3)}{F(1/3)}.
\]
Therefore
\[
\boxed{
\lim_{m\to\infty}P_m=\frac{\epsilon^2}{U_\Gamma}.
}
\]

This is an exact analytic realization of the target, with a rigorous convergence bound.

Now set
\[
h(X)=\det(I-XM)=1-6X+12X^2-X^3.
\]
The integer filter
\[
A_m=
\frac{P_mP_{m+2}^{12}}{P_{m+1}^6P_{m+3}}
\]
cancels the linear return error and converges quadratically to
\[
\left(\frac{\epsilon^2}{U_\Gamma}\right)^6.
\]

The same matrix gives
\[
\det(I-M)=6,
\qquad
\frac{\det(\omega M-I)}{\det(I-M)}
=2+3\omega=J.
\]

Thus the **same finite unit matrix** controls both:
1. the contracting analytic return, and
2. the cubic Jacobi/Kummer radicand.

What remains missing is the theorem comparing these two realizations.

---

# 5. Stage IV — Integral unramified cubic

Let
\[
\theta=\zeta_7+\zeta_7^{-1},\qquad
\nu=\frac{\theta-2}{\beta}.
\]
Then
\[
\nu^3+\beta^2\nu^2+2\beta\nu+1=0,
\]
whose relative discriminant over \(K\) is exactly
\[
1.
\]

Trace-duality calculations identify the full relative integer ring. This produces an explicit everywhere-unramified cyclic cubic extension \(H/K\), and in this example it is the Hilbert class field.

A smaller integral generator
\[
v=-\beta^2\nu-2\nu^2
\]
satisfies
\[
\boxed{v^3-\beta v^2+1=0.}
\]

This cubic is the central arithmetic coordinate in the later geometric interpretation.

---

# 6. Stage V — Three-isogeny fiber and class-field Frobenius

Consider
\[
E_0:y^2+y=x^3,
\qquad
E_1:Y^2+Y=X^3-7.
\]

There is an explicit degree-three isogeny
\[
\varphi(x,y)=
\left(
x+x^{-2},
\ y-(2y+1)x^{-3}
\right).
\]

The point
\[
P=(\beta,0)\in E_1(K)
\]
has a three-point fiber under \(\varphi\). One point is
\[
Q=(v,q(v)),
\]
with \(v^3-\beta v^2+1=0\), and
\[
\varphi(Q)=P.
\]

The cubic class-field automorphism acts as translation by rational 3-torsion:
\[
\sigma(Q)=Q+T,\qquad T=(0,0).
\]

The descent function
\[
\Xi_{\rm geo}(x,y)=\frac{y+1+\omega}{x}
\]
satisfies the universal identity
\[
\Xi_{\rm geo}(x,y)^3
=
\varphi_Y(x,y)+2+3\omega.
\]
At the fiber above \(P\),
\[
\Xi_{\rm geo}(Q)^3=2+3\omega.
\]

Thus the Jacobi sum is simultaneously:
- a finite cubic-character sum,
- a Kummer radicand,
- and a three-isogeny descent value.

For the analytic value define
\[
Y_\Gamma=U_\Gamma+U_\Gamma^{-1}.
\]
Locally invert the algebraic quadratic \(Y(v)\) to get \(v_\Gamma\), and then define a local analytic point \(Q_\Gamma\in E_0\).

The original conjecture is then equivalent to the concrete geometric target
\[
\boxed{\varphi(Q_\Gamma)=P.}
\]
Its \(x\)-coordinate residual is
\[
\varphi_X(Q_\Gamma)-\beta
=
\frac{v_\Gamma^3-\beta v_\Gamma^2+1}{v_\Gamma^2}.
\]

---

# 7. Stage VI — Genuine seven-torsion and a classical CM target

The same Kummer coordinate has a second, different geometric realization.

On the equianharmonic curve \(E_0\), if
\[
x^3=\frac1J,
\qquad J=2+3\omega,
\]
then the corresponding point is a genuine point of order seven. In particular,
\[
\Xi=\frac1{x(R)}
\]
for a CM seven-torsion point \(R\).

With the equianharmonic lattice
\[
\Lambda_0=\mathbf Z+\mathbf Z\omega
\]
and the standard period normalization
\[
\Omega=
e^{\pi i/6}\frac{\Gamma_{\rm Euler}(1/3)^3}{2\pi},
\]
one obtains the exact classical CM identity
\[
\boxed{
\frac{\Omega^2}{\wp_{\Lambda_0}(1/J)}
=
\frac1\beta
\sum_{a=1}^6\chi(a)e^{6\pi ia/7}.
}
\]

The branch is selected by a rigorous lattice estimate rather than numerical fitting.

Consequently the algebraic candidate can be reconstructed from a fully classical CM theta/Weierstrass value:
\[
U_{\rm alg}
=
R_{\beta,\omega}
\left(
\frac{\Omega^2}{\wp_{\Lambda_0}(1/J)}
\right).
\]

So the unresolved comparison can also be written
\[
U_\Gamma
\stackrel{?}{=}
R_{\beta,\omega}
\left(
\frac{\Omega^2}{\wp_{\Lambda_0}(1/J)}
\right).
\]

A naive global unbranched elliptic lift cannot work: the raw gamma function has odd-order poles incompatible with such a global map. Any successful comparison must therefore be a special-value identity, a coherently branched construction, or a geometric/cocycle comparison that keeps the full arithmetic trivialization.

---

# 8. Stage VII — Explicit pre-smoothing unit and abelian radical

Inside the degree-six ray field
\[
E=\mathbf Q(\beta,v,\omega),
\]
define
\[
\begin{aligned}
A={}&(21\beta-42)v^2+(-15\beta^2+30\beta)v-\beta^2-4\beta+11,\\
B={}&3\beta^2v^2+(18\beta-42)v-11\beta^2+13\beta+7,
\end{aligned}
\]
and
\[
W=\frac{A+\omega B}{3}.
\]

Exact reduction gives
\[
W\iota(W)=1
\]
and, most importantly,
\[
\boxed{
W^5=\sigma(W)\,U_{\rm alg}^6,
}
\]
or
\[
\boxed{
W^{5-\sigma}=U_{\rm alg}^6.
}
\]

Thus \(W\) has exactly the algebraic smoothing shape expected of the Stark-type predecessor.

If \(t^6=W\), then
\[
E(t)/K
\]
is an abelian extension of degree \(36\), with
\[
\operatorname{Gal}(E(t)/K)\cong C_2\times C_{18}.
\]

This proves a strong algebraic compatibility condition. It does **not** prove that \(W\) satisfies the required Stark logarithmic formula, and it does not prove \(U_\Gamma=U_{\rm alg}\).

The same \(W\) gives norm-11 and norm-19 algebraic smoothing values whose independently computed elliptic-gamma analogues agree numerically to roughly 127–129 decimal digits, with the predicted residual sixth-root phases exposed.

A conditional two-smoothing rigidity theorem shows that exact norm-5 and norm-19 analytic smoothing comparisons would force any remaining multiplicative discrepancy into \(\mu_6\). The exact residual kernel is therefore finite.

---

# 9. New continuation — the three-sector polyphase closure

The previous work suggested using the full six ray-class values instead of attacking one scalar in isolation.

BCG's pure-cubic example gives three elliptic-gamma parameter pairs, each accompanied by its reciprocal value. Reindex them to match the algebraic cubic orbit as follows:
\[
(\tau_0,\sigma_0)
=
\left(
\frac{\beta^2+2\beta}{15},
-\frac{\beta+2}{15}
\right),
\]
\[
(\tau_1,\sigma_1)
=
\left(
\frac{\beta^2+2\beta+15}{150},
-\frac{\beta-43}{150}
\right),
\]
\[
(\tau_2,\sigma_2)
=
\left(
\frac{\beta^2+2\beta+75}{345},
-\frac{\beta+32}{345}
\right).
\]

Define
\[
U_j^\Gamma
=
\frac{\Gamma_{\rm ell}(1/3;\tau_j,\sigma_j)^5}
     {\Gamma_{\rm ell}(5/3;5\tau_j,5\sigma_j)},
\qquad
Y_j^\Gamma=U_j^\Gamma+(U_j^\Gamma)^{-1}.
\]

Now perform the \(C_3\) discrete Fourier transform:
\[
S_0=Y_0^\Gamma+Y_1^\Gamma+Y_2^\Gamma,
\]
\[
S_1=Y_0^\Gamma+\omega Y_1^\Gamma+\omega^2Y_2^\Gamma,
\]
\[
S_2=Y_0^\Gamma+\omega^2Y_1^\Gamma+\omega Y_2^\Gamma.
\]

## 9.1 Exact polyphase closure lemma

For arbitrary \(Y_0,Y_1,Y_2\),
\[
S_1S_2=S_0^2-3e_2,
\]
where
\[
e_2=Y_0Y_1+Y_1Y_2+Y_2Y_0.
\]

Also,
\[
\boxed{
S_0^3+S_1^3+S_2^3-3S_0S_1S_2=27e_3,
}
\]
where
\[
e_3=Y_0Y_1Y_2.
\]

Therefore the unordered cubic packet is determined by
\[
S_0,\qquad P=S_1S_2,\qquad C=S_1^3+S_2^3.
\]

For the algebraic packet the exact targets are
\[
\boxed{
S_0=-6\beta^2+14\beta-2,
}
\]
\[
\boxed{
P=208\beta^2+214\beta-1169,
}
\]
and
\[
\boxed{
C=3(5636\beta^2-15734\beta+9473).
}
\]

Indeed,
\[
e_2=\frac{S_0^2-P}{3}
=4\beta^2-6\beta-1,
\]
and
\[
e_3=
\frac{S_0^3+C-3S_0P}{27}
=
-94\beta^2+124\beta+107.
\]

Thus
\[
T^3-e_1T^2+e_2T-e_3
=
R(T).
\]

### Consequence

If the analytic packet satisfies these three identities, then
\[
R(Y_j^\Gamma)=0
\quad\text{for all }j.
\]

In particular,
\[
R(U_\Gamma+U_\Gamma^{-1})=0,
\]
which places the original elliptic-gamma value among the six roots of \(Q\). The existing rigorous branch separation then selects \(U_{\rm alg}\).

So the original single-value conjecture has been reduced to **three explicit \(C_3\)-sector identities for a coherent analytic packet**.

## 9.2 Stronger character-oriented target

The primitive sector can be sharpened using the Jacobi/Kummer coordinate:
\[
\boxed{
S_1^3=(\beta c(\beta,\omega))^3(2+3\omega),
}
\]
with
\[
c(\beta,\omega)=
\frac{(8\beta^2-18\beta+7)\omega+(19\beta^2-41\beta+7)}7.
\]

Together with
\[
S_1S_2=208\beta^2+214\beta-1169,
\]
this determines \(S_2^3\) automatically.

The cube-root ambiguity
\[
S_1\mapsto\omega S_1,\qquad
S_2\mapsto\omega^2S_2
\]
only cyclically permutes \(Y_0,Y_1,Y_2\). It therefore does not affect polynomial membership. This removes a branch nuisance that was present when attacking one conjugate at a time.

---

# 10. New numerical audit of the polyphase target

The attached `polyphase_audit.py` evaluates the three gamma values independently from their convergent smoothed logarithmic series. It does not reconstruct them from the algebraic polynomial.

The numerical ordering is
\[
(\text{original pair},\ \text{150-pair},\ \text{345-pair})
\leftrightarrow
(t_0,t_1,t_2).
\]

At the chosen precision/truncation, the independent computation gives approximately:

- \(S_0\) target error: \(5.3\times10^{-61}\)
- \(S_1S_2\) target error: \(1.7\times10^{-59}\)
- \(S_1^3\) target error: \(3.1\times10^{-57}\)
- \(S_1^3+S_2^3\) target error: \(4.1\times10^{-57}\)

Relative errors are around \(10^{-62}\).

These are **regression tests, not proofs**. Their value is that the full three-sector closure target was not fitted to these three gamma values: its constants come from the previously established algebraic Jacobi/Kummer model.

---

# 11. What is now genuinely closed

For this cubic example, the following pieces are established by ordinary exact arguments, with computational checks where noted:

1. The explicit degree-six algebraic candidate and its reciprocal sextic.
2. The Jacobi sum \(J=2+3\omega\) and the normalized Gauss/Kummer coordinate \(\eta^3=J\).
3. An explicit integral unramified cubic model of the Hilbert class field.
4. A degree-three isogeny fiber realizing the cyclic cubic and its Frobenius action.
5. A universal descent function whose cube is the Jacobi radicand.
6. A genuine seven-torsion CM realization of the same Kummer coordinate.
7. An exact classical Weierstrass/theta evaluation of that Kummer coordinate.
8. The eta anchor \(F(0)=(2-\beta)^2\).
9. The exact contracting theta-return formula
   \[
   \lim P_m=(2-\beta)^2/U_\Gamma.
   \]
10. The exact finite unit-matrix determinant
    \[
    -h(\omega)/h(1)=2+3\omega.
    \]
11. The explicit algebraic pre-smoothing unit
    \[
    W^{5-\sigma}=U_{\rm alg}^6.
    \]
12. The degree-36 abelian radical extension generated by a sixth root of \(W\).
13. Exact norm-11 and norm-19 algebraic smoothing identities.
14. A finite two-smoothing rigidity theorem reducing a future analytic discrepancy to \(\mu_6\).
15. The new exact polyphase closure lemma reducing the original cubic membership problem to three Fourier-sector identities.

---

# 12. What remains open

The principal unresolved theorem is still one analytic-to-arithmetic comparison. Equivalent or near-equivalent forms include:

\[
U_\Gamma=U_{\rm alg},
\]

\[
R(U_\Gamma+U_\Gamma^{-1})=0,
\]

\[
\varphi(Q_\Gamma)=(\beta,0),
\]

\[
\lim P_m=(2-\beta)^2/U_{\rm alg},
\]

or the new coherent-packet identities
\[
S_0=-6\beta^2+14\beta-2,
\]
\[
S_1S_2=208\beta^2+214\beta-1169,
\]
\[
S_1^3=(\beta c)^3(2+3\omega).
\]

A separate unresolved theorem is the exact Stark logarithmic/partial-zeta characterization of the explicit \(W\). Proving that would give another route to identifying the analytic and algebraic realizations.

---

# 13. Most promising next attack

The strongest next target is no longer a naked equality of one transcendental-looking number.

We should work with the **coherent three-value gamma packet** and try to prove its Fourier invariants from the geometric \(\mathrm{SL}_3(\mathbf Z)\) structure.

The work should proceed in this order:

1. **Build exact transport matrices** connecting the three BCG lattices/ideal representatives.
2. **Write each \(Y_j^\Gamma\)** in a common geometric-gamma trivialization so raw period-shift multipliers are not confused with Artin transport.
3. **Derive the trivial sector \(S_0\)** first. This is the missing normalization mode that nontrivial cocycle/Walsh arguments lose.
4. **Derive the cross-sector norm \(S_1S_2\)**. This is \(K\)-valued and avoids choosing a cubic character branch.
5. **Derive the primitive cubic sector \(S_1^3\)** and compare it to
   \[
   (\beta c)^3\,\frac{\det(\omega M-I)}{\det(I-M)}.
   \]
6. Once these are exact, invoke the polyphase closure lemma and the existing rigorous branch separation.

Conceptually, this isolates the missing theorem more sharply:

> The determinant calculation already captures the primitive \(C_3\) obstruction.  
> What was missing was the trivial character normalization and the coupling between the two primitive sectors.

That is why earlier cocycle-only arguments could not close the proof.

---

# 14. Trust boundary

- Exact polynomial, field, isogeny, determinant, and finite-group identities are distinct from numerical tests.
- High-precision agreement of gamma values with algebraic candidates is not used as a proof of algebraicity.
- The BCG algebraicity and reciprocity statements remain conjectural in the cited literature.
- Morain's 2026 work strengthens the geometric/cocycle framework but likewise does not supply the missing algebraicity theorem used here.
- No Lean proof of this Hilbert-12 cubic program is currently claimed.
- No claim is made that this solves Hilbert's twelfth problem for arbitrary number fields.

---

# 15. Included predecessor notes

The archive contains the seven retained proof stages:

1. `PROOF(20261002-121503).md` — Jacobi/Kummer audit
2. `PROOF(20261002-123422).md` — eta anchor and torsion selection
3. `PROOF(20261002-131052).md` — unit return and Jacobi determinant
4. `PROOF(20261002-134353).md` — unramified cubic and primitive-sector correction
5. `PROOF(20261002-141429).md` — isogeny fiber and Jacobi descent
6. `PROOF(20261002-154405).md` — seven-torsion and CM theta target
7. `PROOF(20261002-162814).md` — norm-five descent and abelian radical

The new file `polyphase_audit.py` reproduces the current three-sector numerical audit.


---

# 16. Continuation after consolidation: exact Hecke/polyphase transport

A further exact block is recorded in `PROOF(20261002-POLYPHASE_TRANSPORT).md`.

The key new facts are:

\[
(\tau_{10},\sigma_{10})=((\tau+1)/10,(\sigma+3)/10),
\]
\[
(\tau_{23},\sigma_{23})=((\tau+5)/23,(\sigma-2)/23),
\]

with exact index-10 and index-23 unit-stable lattice inclusions. A finite-grid
distribution formula rewrites both additional BCG gamma values as finite
products of the original smoothed function. The corresponding grids are
preserved by the unit action. Their exact orbit decompositions are

\[
100=1+3+8\cdot12,
\qquad
529=1+528.
\]

The index-23 grid therefore has only the arithmetic fixed point \(1/3\) and one
single nontrivial orbit of length \(23^2-1\). This is now the cleanest target
for a fixed-point/orbit localization proof of the missing analytic comparison.
