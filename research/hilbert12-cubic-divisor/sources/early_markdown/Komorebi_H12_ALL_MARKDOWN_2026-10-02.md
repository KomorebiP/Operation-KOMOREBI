# Komorebi Hilbert 12 — Complete Markdown Working Archive

**Assembled:** 2026-10-02

This file concatenates every Hilbert 12 Markdown note currently recovered for the pure cubic \(K=\mathbf Q(\beta)\), \(\beta^3=7\) program. The original files are preserved separately in the accompanying ZIP.

## Archive index

1. `H12_MASTER_STATE_2026-10-02.md` — Komorebi Hilbert 12 Program — Consolidated Working State
2. `PROOF(20261002-121503).md` — Komorebi Hilbert 12 cubic test: a Jacobi-sum Kummer coordinate
3. `PROOF(20261002-123422).md` — Komorebi H12 continuation: an eta anchor, a transcendental control, and the arithmetic torsion selector
4. `PROOF(20261002-131052).md` — Komorebi H12 continuation: a cubic-unit return product and its Jacobi determinant
5. `PROOF(20261002-134353).md` — Komorebi H12: an integral unramified cubic and a primitive-sector correction
6. `PROOF(20261002-141429).md` — Komorebi H12: the unramified cubic as an explicit isogeny fiber
7. `PROOF(20261002-154405).md` — Komorebi H12: genuine seven-torsion and an exact CM theta target
8. `PROOF(20261002-162814).md` — Komorebi H12: norm-five descent, a degree-36 abelian radical, and new smoothing tests
9. `PROOF(20261002-POLYPHASE_TRANSPORT).md` — Komorebi H12 continuation — exact Hecke/polyphase transport

## Integrity manifest

| File | Bytes | SHA-256 |
|---|---:|---|
| `H12_MASTER_STATE_2026-10-02.md` | 19706 | `3b01c7b8207bae1fc691a1b16fc70d88218e5a3cf98b7ad41d73315b490e94e8` |
| `PROOF(20261002-121503).md` | 10708 | `a7c1b5aea81d7d3593901ce016acf0a7735f539a6d23baa3b53ddf775cd91471` |
| `PROOF(20261002-123422).md` | 13097 | `0a72f11e52b32e6f3a9e1b89f957064391a9021bed2a2821c6006bf52fbdecec` |
| `PROOF(20261002-131052).md` | 15974 | `5506267f458200228c451c75f601f59c2fa5debcb0a2628c2b7862a6d2612019` |
| `PROOF(20261002-134353).md` | 17782 | `92a4d1770eac99fc1bd70fd4dd14397c39467531fc898ff5b2e8e4571b745c4b` |
| `PROOF(20261002-141429).md` | 13236 | `ee130f1d73e93660fb34afcbe10b2bd438ec2bf9f0623ea7194f076c76d40343` |
| `PROOF(20261002-154405).md` | 15615 | `8eaa42161cd3aaaf50aa1c9a58c3ecd255b174ecbd7e9dc7b9004e5c623424aa` |
| `PROOF(20261002-162814).md` | 18066 | `40aec57747a4b1ca16d5523bda69576c479ff4ec76cdf71e2b143ae040eecf41` |
| `PROOF(20261002-POLYPHASE_TRANSPORT).md` | 9344 | `1f06c41159b328da57888738378c8cbd44c25fbd6d2c7d947fea32a46623bc61` |

---

<!-- BEGIN ORIGINAL FILE: H12_MASTER_STATE_2026-10-02.md -->
# Archive Part 1: `H12_MASTER_STATE_2026-10-02.md`

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

<!-- END ORIGINAL FILE: H12_MASTER_STATE_2026-10-02.md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-121503).md -->
# Archive Part 2: `PROOF(20261002-121503).md`

# Komorebi Hilbert 12 cubic test: a Jacobi-sum Kummer coordinate

## Status

This note proves the algebraic candidate's explicit Kummer description and isolates failures in two previously proposed analytic closing arguments. It does **not** prove algebraicity of the elliptic-gamma special value. The algebraic identities are accompanied by exact rational polynomial reductions. The numerical comparison uses a separate interval calculation with an analytic infinite-series tail bound. No Lean proof or independent formal-kernel audit was performed.

We use only the pure cubic example, beta^3 = 7. The different BCG example beta^3 - beta^2 + 5 beta + 1 = 0 is not used.

## 1. An elementary finite theorem

Let omega be a primitive third root of unity and zeta any primitive seventh root. Define the cubic multiplicative character of F_7 by chi(0)=0 and

    a       1    2      3        4        5    6
    chi(a)  1  omega  omega^2  omega^2  omega  1.

Equivalently, chi(3)=omega^2. Put

\[
G=\sum_{a=1}^{6}\chi(a)\zeta^a,
\qquad J=\sum_{a\in\mathbf F_7}\chi(a)\chi(1-a).
\]

The five nonzero terms of J are omega, 1, omega, 1, omega, so

\[
J=2+3\omega.
\]

Write G_2 for the same Gauss sum with chi replaced by chi^2. Direct finite summation gives

\[
G^2=J G_2,\qquad GG_2=7.
\]

For the first equality, expand the double sum and partition by s=a+b. The s=0 contribution is zero since chi^2 is nontrivial. For s nonzero, substitute a=st and b=s(1-t), obtaining chi(s)^2 times J. For the second, put a=bt in the double sum for GG_2. The inner sum over b is 6 if t=-1 and -1 otherwise. Since the sum of chi is zero and chi(-1)=1, the result is 7.

Consequently

\[
\boxed{G^3=7(2+3\omega).}
\]

Fix beta^3=7 and define eta=G/beta. Then

\[
\boxed{\eta^3=2+3\omega.}
\]

The radicand has norm

\[
(2+3\omega)(2+3\omega^2)=7.
\]

It is a prime element above 7 in the Eisenstein integers, not an algebraic unit. Indeed Z[omega]/(2+3omega) is F_7, with omega mapping to 4. Thus this is a normalized Gauss-sum Kummer coordinate, not an ordinary root of unity.

## 2. Eigenaction and reconstruction

Let

\[
t=\zeta+\zeta^{-1},\quad t_1=\zeta^2+\zeta^{-2}=t^2-2,\quad
t_2=\zeta^4+\zeta^{-4}=-t^2-t+1.
\]

The minimal polynomial is

\[
f(t)=t^3+t^2-2t-1.
\]

Grouping the six Gauss-sum terms into opposite pairs gives

\[
G=t+\omega t_1+\omega^2t_2.
\]

The conjugate resolvent is G_2=t+omega^2 t_1+omega t_2. Since GG_2=7,

\[
G=\beta\eta,\qquad G_2=\frac{\beta^2}{\eta}.
\]

Fourier inversion therefore gives

\[
\boxed{t=\frac{-1+\beta\eta+\beta^2/\eta}{3}.}
\]

The automorphism sigma induced by zeta -> zeta^2, fixing beta and omega, satisfies

\[
\sigma(\eta)=\omega^2\eta.
\]

In particular K(omega,eta)=K(omega,t). This establishes the exact Kummer coordinate for the candidate cubic layer; it is not a statement about the analytic gamma value.

## 3. The original reciprocal sextic

The BCG example uses

\[
\begin{aligned}
Q(X)={}&X^6+(6\beta^2-14\beta+2)X^5+(4\beta^2-6\beta+2)X^4\\
&+(106\beta^2-152\beta-103)X^3+(4\beta^2-6\beta+2)X^2\\
&+(6\beta^2-14\beta+2)X+1.
\end{aligned}
\]

Its inversion quotient is

\[
Q(X)=X^3R(X+X^{-1}),
\]

where

\[
R(Y)=Y^3+(6\beta^2-14\beta+2)Y^2
 +(4\beta^2-6\beta-1)Y+(94\beta^2-124\beta-107).
\]

Define

\[
Y(t)=\frac{7-5\beta+3\beta^2+(-23\beta+11\beta^2)t
                 +(-7+18\beta-8\beta^2)t^2}{7}.
\]

Exact reduction modulo beta^3-7 and f(t) gives R(Y(t))=0. The inverse map is

\[
\begin{aligned}
t={1\over76875}\bigl[&(113076\beta^2+216268\beta+413399)Y^2\\
 &-(182979\beta^2+339097\beta+662921)Y\\
 &+26154\beta^2+53122\beta+127871\bigr].
\end{aligned}
\]

Thus K(Y)=K(t), with actual inverse polynomial maps. The latter extension has degree 3: Q(t)/Q is Galois cyclic of degree 3, and it is not K (the chosen K contains nonreal beta whereas Q(t) is real). Their intersection is Q, and the Galois degree formula gives [K(t):K]=3.

Define

\[
Z(Y)=\frac{-19584+11812\beta+3984\beta^2
 +(109+488\beta+116\beta^2)Y
 -(1346+572\beta+304\beta^2)Y^2}{15375}.
\]

Another exact reduction gives

\[
Y^2-4=-3Z(Y)^2.
\]

With s=1+2omega, so s^2=-3, put

\[
U_{\rm alg}=\frac{Y-sZ(Y)}2,
\qquad U_{\rm alg}^{-1}=\frac{Y+sZ(Y)}2.
\]

Then their product is 1, their sum is Y, and Q(U_alg)=0.

Since K(t) has degree 9 over Q, it cannot contain the quadratic field Q(s). Also Z(Y) is nonzero: otherwise Y=+2 or -2 would contradict degree 3. Therefore s=(Y-2U_alg)/Z(Y) lies in K(U_alg), and

\[
K(U_{\rm alg})=K(t,s)=K(\omega,\eta),\qquad [K(U_{\rm alg}):K]=6.
\]

The field is Galois with group C3 x C2. In particular Q is irreducible over K. Its identification with the specified ray class field additionally uses the arithmetic identification recorded by BCG; no new conductor computation is asserted here.

## 4. Exact scale for the Y-resolvent

Let Y_j=Y(t_j). Set

\[
c(\beta,\omega)=\frac{(8\beta^2-18\beta+7)\omega+(19\beta^2-41\beta+7)}7.
\]

The exact relation is

\[
Y_0+\omega Y_1+\omega^2Y_2=c(\beta,\omega)G.
\]

Consequently the normalized algebraic Y-resolvent has cube

\[
\left(\frac{Y_0+\omega Y_1+\omega^2Y_2}
{\beta c(\beta,\omega)}\right)^3=2+3\omega.
\]

The normalization factor is nonzero; its norm under omega -> omega^2 is

\[
c(\beta,\omega)c(\beta,\omega^2)
=\frac{208\beta^2+214\beta-1169}{7}\ne0.
\]

This is a concrete target for an analytic Fourier-resolvent comparison. Defining the analytic orbit and proving this comparison are not supplied by the algebraic calculation.

## 5. Why the previous cocycle argument does not close the analytic gap

Morain's denominator-one result at smoothing index 5 and rank 3 concerns a multiplicative coboundary. Under its full hypotheses, it gives an exact cocycle law. It does not give uniqueness of a cocycle or of its value at a unit.

For example, on C3 the nontrivial character c(g^j)=omega^j has multiplicative coboundary identically 1. An exact cocycle can therefore retain a nontrivial root-of-unity value. On the infinite cyclic group, c(n)=a^n is a cocycle for every nonzero complex a.

Nor does commutation with the order-two action force the phase to square to 1. In the actual Kummer model,

\[
\sigma:\eta\mapsto\omega^2\eta,\quad\omega\mapsto\omega,
\]

while

\[
\iota:\eta\mapsto\beta/\eta,\quad\omega\mapsto\omega^2.
\]

Both fix beta. Direct substitution shows sigma^3=iota^2=1 and sigma*iota=iota*sigma. The order-two operation acts nontrivially on the coefficient root omega; it is semilinear over K(omega). Ignoring this action invalidates the previous inference delta=delta^{-1}.

Finally, a nontrivial multiplicative Walsh component loses a constant normalization. If chi is a nontrivial sign character on (Z/2)^3,

\[
\mathcal W_\chi(cF)=\prod_v[cF(v)]^{\chi(v)}
=c^{\sum_v\chi(v)}\mathcal W_\chi(F)=\mathcal W_\chi(F).
\]

Thus identification of all selected nontrivial Walsh components alone cannot recover the absolute value of F at an arithmetic point. Extra arithmetic descent and normalization data are necessary. These observations do not refute the gamma conjecture; they refute the particular proposed deductions that claimed to finish it from cocycle consistency alone.

## 6. Numerical evaluation with an explicit tail enclosure

Choose beta=7^(1/3) exp(-2*pi*i/3), tau=(2beta+beta^2)/15 and sigma=-(2+beta)/15. The original tau has negative imaginary part. Use the BCG sign-change continuation before using a convergent logarithmic series.

Set

\[
p=e^{-2\pi i\tau},\quad q=e^{2\pi i\sigma},
\quad x=e^{2\pi i(1/3-\tau)}.
\]

The gamma product implies exactly

\[
U_\Gamma=\exp\left(-5\sum_{\substack{n\ge1\\5\nmid n}}
 \frac{x^n-(pq/x)^n}{n(1-p^n)(1-q^n)}\right).
\]

This is not a fitted formula. It follows by subtracting the logarithmic series at (x^5,p^5,q^5) from five copies at (x,p,q), together with the sign-change rule. Terms divisible by 5 cancel.

The interval computation verifies |p|,|x|<r=19/20 and |q|,|pq/x|<s=3/5. For truncation at N,

\[
E_N\le\frac{5}{(N+1)(1-r^{N+1})(1-s^{N+1})}
\left(\frac{r^{N+1}}{1-r}+\frac{s^{N+1}}{1-s}\right)
\]

bounds the absolute error in the exponent. For N=6000, this is less than 3.48*10^(-136). The calculation retains 4800 terms.

Using mpmath.iv with 170 decimal digits, an explicit rectangular exponent error of radius 10^(-135), and the algebraic branch t=2cos(6pi/7), s=i sqrt(3), the computed enclosure gives

\[
|U_\Gamma-U_{\rm alg}|<10^{-130}.
\]

All six algebraic candidate roots are pairwise more than 0.2 apart in this embedding. The same interval computation excludes the other five candidates. **This isolates the only compatible algebraic branch; it does not prove the gamma value belongs to that finite set.** An interval containing zero is not a proof that its enclosed number is zero.

The interval implementation is software evidence, not a proof-assistant certificate. mpmath documents its interval support as experimental. The independent mathematical tail bound is given explicitly above so the calculation can be reproduced in another enclosure library.

## 7. What is closed and what remains

Closed here: the candidate field's explicit Gauss-sum/Kummer coordinate, its exact radicand 2+3omega, reconstruction of its cubic and sextic coordinates, and a narrow numerical enclosure for the prescribed analytic value.

Still required for the requested analytic-to-algebraic theorem: an exact argument that the actual gamma value satisfies R(U_gamma+U_gamma^(-1))=0, or an independent analytic-to-arithmetic comparison strong enough to imply it. The finite Hecke orbit, root-of-unity eigenaction, difference equations, and zero coboundary do not alone put their invariant scalar in K.

A productive next comparison target is the fully normalized analytic Fourier resolvent against the explicit finite Gauss sum in section 4, together with its trivial character coordinate. That target is an equality to prove, not an available premise.

## Sources consulted

- Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields*, arXiv:2311.04110v2, Introduction (1.1)-(1.3), section 2.3, and section 5.2.
- Morain, *Geometric families of multiple elliptic Gamma functions and arithmetic applications, II*, arXiv:2602.06561v1, main theorem and section 4.
- Morain, *Computations of higher elliptic units in optimal settings*, arXiv:2601.11961v2 (July 2026). Its formulation continues to distinguish conjectural algebraic units from the established functional identities.
- mpmath 1.3.0 documentation, *Contexts*, interval arithmetic.

The sources supply their own definitions and results. The finite algebraic normal-form calculations and the explicit obstruction counterexamples in this note are deductions checked in the attached scripts, not claims quoted from those sources.

<!-- END ORIGINAL FILE: PROOF(20261002-121503).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-123422).md -->
# Archive Part 3: `PROOF(20261002-123422).md`

# Komorebi H12 continuation: an eta anchor, a transcendental control, and the arithmetic torsion selector

## Status and scope

This is an ordinary mathematical derivation using the elliptic-gamma product and continuation, the classical Dedekind eta transformation formula, the eta-quotient modularity criterion, and Schneider's theorem. Exact symbolic and numerical tests accompany it. There is no Lean proof, no claim of a new proof of those background theorems, and no independent human review.

The target U = F(1/3) is NOT proved algebraic or equal to the Jacobi--Kummer candidate. This continuation proves F(0) algebraic and F(1/2) transcendental, and isolates a character-twisted series whose exponential would have to equal the square of that candidate.

The half-point is deliberately not the admissible BCG torsion point. Its transcendence does not contradict the BCG conjecture.

## 1. Fixed conventions

Choose beta = 7^(1/3) exp(-2*pi*i/3), and put

    tau = (beta^2+2*beta)/15,
    t = -tau,
    sigma = -(beta+2)/15,
    epsilon = 2-beta.

Both t and sigma have positive imaginary parts. Define the meromorphic function

    F(z) = Gamma(z; -t, sigma)^5 / Gamma(5*z; -5*t, 5*sigma).

The gamma function uses BCG's convention

    Gamma(z; -t, sigma) = 1/Gamma(z+t; t, sigma).

The original target is exactly U = F(1/3).

Use the notation

    p = exp(2*pi*i*t), q = exp(2*pi*i*sigma),
    D(r) = product_{n>=1} (1-r^n),
    H(v) = eta(5*v)/eta(v)^5.

Since D(exp(2*pi*i*v)) = exp(-pi*i*v/12) eta(v), the exponential factors cancel in H:

    H(v) = D(exp(2*pi*i*5*v))/D(exp(2*pi*i*v))^5.

## 2. Two telescoping evaluations of the gamma product

In multiplicative notation, for |p|,|q|<1,

    Gamma_mult(x;p,q) = product_{j,k>=0}
       (1-p^(j+1)q^(k+1)/x)/(1-p^j q^k x).

Absolute convergence at x=p and x=-p permits cancellation of the common interior factors. The boundary products give

    Gamma_mult(p;p,q) = D(q)/D(p),
    Gamma_mult(-p;p,q) = D_plus(q)/D_plus(p),

where D_plus(r) = product_{n>=1}(1+r^n) = D(r^2)/D(r).

Applying the negative-period continuation yields

    Gamma(0;-t,sigma) = D(p)/D(q),
    Gamma(1/2;-t,sigma) = D_plus(p)/D_plus(q).

In particular F is finite and nonzero at both points. Consequently,

    F(0) = H(sigma)/H(t),                                      (2.1)
    F(1/2) = [H(2*sigma)/H(2*t)]/[H(sigma)/H(t)].              (2.2)

These are identities of actual products, not fits to special-value numerics.

## 3. Exact algebraic normalization at zero

Let delta = 15*t-4. Reduction modulo beta^3-7 proves

    sigma = (-4*t+1)/(15*t-4),
    delta*epsilon = -1.

The associated SL2(Z) matrices are

    A  = [-4,1; 15,-4],
    A5 = [-4,5;  3,-4].

They satisfy sigma=A(t) and 5*sigma=A5(5*t). The factor c*t+d is delta in both transformations.

For c>0 use the eta formula with the principal square root:

    eta((a*v+b)/(c*v+d))
      = exp(pi*i*k(a,d,c)) (c*v+d)^(1/2) eta(v),

    k(a,d,c) = (a+d)/(12*c) - s(d,c) - 1/4,

where s is the Dedekind sum. Exact rational summation gives

    s(-4,15) = -19/90,   k(-4,-4,15) = -1/12,
    s(-4, 3) =  -1/18,  k(-4,-4, 3) = -5/12.

Thus the multiplier in H(sigma)/H(t) is

    exp(pi*i*(-5/12-5*(-1/12))) = 1.

The two square-root factors combine to delta^(-2). Therefore

    F(0) = delta^(-2) = epsilon^2 = (2-beta)^2.                (3.1)

The eta-transform part holds for any t in the upper half-plane with sigma=A(t). The cubic equation is used only for delta*epsilon=-1.

This is an algebraic base-point normalization. It does not propagate algebraicity to other arguments z without a further arithmetic theorem.

## 4. Exact half-point identity

Put u=t/2. Then

    2*sigma = (-8*u+1)/(15*u-2).

Use the matrices

    B  = [-8,1; 15,-2],
    B5 = [-8,5;  3,-2].

The common square-root argument is 15*u-2=delta/2. Exact sums give

    s(-2,15) = -7/18,   k(-8,-2,15) = 1/12,
    s(-2, 3) =  1/18,  k(-8,-2, 3) = -7/12.

The smoothed multiplier is now

    exp(pi*i*(-7/12-5/12)) = -1.

Consequently

    H(2*sigma) = -4*delta^(-2)*H(t/2).

Substitute this and (3.1) into (2.2):

    F(1/2) = -4*H(t/2)/H(2*t)
           = -4*h(u),                                      (4.1)

where

    h(u) = eta(5*u)*eta(4*u)^5 / (eta(u)^5*eta(20*u)).

The minus sign is necessary. The exact Dedekind-sum calculation detects it.

## 5. The half-point value is transcendental

The eta exponents of h at level 20 are

    r_1=-5, r_4=5, r_5=1, r_20=-1.

They satisfy

    sum r_d = 0,
    sum d*r_d = 0,
    sum (20/d)*r_d = -72 = 0 mod 24,
    product d^(r_d) = 256, a rational square.

The standard eta-quotient criterion therefore makes h a meromorphic modular function on X_0(20) with trivial character. It has rational Fourier coefficients. Direct expansion gives

    h(u) = 1+5*q_u+20*q_u^2+65*q_u^3+185*q_u^4+..., q_u=exp(2*pi*i*u).

Thus h is nonconstant. As a second check, its cusp orders are -3 at denominator 1, +3 at denominator 4, and zero at denominators 2,5,10,20.

Now u=t/2 satisfies

    1800*u^3 - 84*u + 7 = 0.

This polynomial is Eisenstein at 7. Hence u is algebraic of degree 3 and is not imaginary quadratic.

Schneider's theorem says j(u) is transcendental. On the other hand, j is algebraic over Q(h): both belong to the function field Q(X_0(20)), and a nonconstant function h defines a finite map to the projective line. Equivalently, there is a nonzero polynomial relation P(h,j)=0 over Q. Choose its coefficients as polynomials in h with no common factor. At any algebraic h-value they cannot all vanish; therefore a finite algebraic h(u) would make the finite value j(u) algebraic.

This contradicts Schneider. So h(u), and therefore F(1/2), is transcendental.

This is a theorem application, not a numerical transcendence test. The external mathematical inputs are identified explicitly: eta modularity, the Q-model/q-expansion principle for X_0(20), and Schneider's theorem.

## 6. The arithmetic torsion distinction

Use the lattice with basis

    u1=beta^2+2*beta, u2=-(beta+2), gamma=15.

Its basis determinant in (1,beta,beta^2) is 15; the BCG norm-5 smoothing lattice is the intended arithmetic realization. Multiplication by epsilon is

    M = [0,1,0; -4,2,15; -1,0,4].

The point z=1/d in the gamma coordinate corresponds to v_d=(0,0,1/d) modulo Z^3. Its displacement is

    (M-I)v_d = (0,15/d,3/d).

For positive integers d it is fixed modulo the lattice exactly when d divides 3. Thus the target v_3 is fixed, while v_2 is not.

The diagonal half-point (1/2,1/2,1/2) is also fixed. Its gamma argument is

    z_half_diagonal = (1+tau+sigma)/2.

Here Gamma(z_half_diagonal;tau,sigma)=1 directly from the product/reflection identity, and the same is true of the scaled denominator (5 is odd). Hence

    F((1+tau+sigma)/2)=1.

The Smith normal form of M-I has invariant factors 1,1,6. Its full fixed torsion group in Q^3/Z^3 is cyclic of order 6. Unit-fixedness is not asserted to be a sufficient condition for algebraicity of every gamma value; this is a concrete necessary distinction that any proposed arithmetic theorem must preserve.

Summary of established and open point values:

    z=0:                     F(z)=(2-beta)^2, proved.
    z=(1+tau+sigma)/2:        F(z)=1, proved.
    z=1/2:                   F(z) transcendental, proved using Schneider.
    z=1/3:                   F(z)=U_alg conjectural, not proved here.

Therefore a claim that rational torsion plus norm-5 smoothing alone forces algebraicity is false for this very same function.

## 7. Isolate the genuinely remaining odd-character series

For real z, the sign-change continuation and the absolutely convergent logarithmic series give

    F(z)=exp(L(z)),
    L(z)=-5 sum_{n>=1, 5 does not divide n}
          [p^n exp(2*pi*i*n*z)-q^n exp(-2*pi*i*n*z)]
          / [n(1-p^n)(1-q^n)].                               (7.1)

Define the odd Dirichlet character modulo 3 by

    chi_-3(n)=0 if 3|n, +1 if n=1 mod3, -1 if n=2 mod3.

This is distinct from the order-three multiplicative character on F_7 in the preceding Jacobi-sum calculation.

Put

    S = sum_{n>=1, 5 does not divide n}
        chi_-3(n) (p^n+q^n)/[n(1-p^n)(1-q^n)].              (7.2)

Since omega^n-omega^(-n)=i*sqrt(3)*chi_-3(n), subtracting the two convergent series gives exactly

    L(1/3)-L(-1/3) = -5*i*sqrt(3)*S.                         (7.3)

For completeness, the inverse pairing here follows without assuming gamma algebraicity. Set

    Theta5(z;v)=theta0(z;v)^5/theta0(5*z;5*v).

This function is even and periodic with lattice Z+Zv. BCG's theta modularity argument (Lemma 4.8 / equations 4.30--4.32), with smoothing 5 coprime to 6, gives

    Theta5(z;sigma)=Theta5(delta*z;t).

The gamma product and negative-period continuation give

    F(z)F(-z)=Theta5(z;t)/Theta5(z;sigma).

At z=1/3, delta*z=5*t-4/3 is congruent to -1/3 modulo Z+Zt. Evenness makes the ratio one. Hence

    F(1/3)F(2/3)=1.

Combining with (7.3) gives the branch-free exact identity

    U^2 = exp(-5*i*sqrt(3)*S).                               (7.4)

The Jacobi--Kummer checkpoint defines U_alg algebraically from Xi^3=2+3*omega. The precise unproved arithmetic target can therefore be written

    exp(-5*i*sqrt(3)*S) = U_alg^2.                           (7.5)

An equality (7.5), followed by the already available numerical sign separation, would prove U=U_alg. No equality (7.5) is claimed here.

The interval calculation also encloses [L(1/3)+L(2/3)]/(2*pi*i) within 1e-130 of 1. The exact inverse relation makes this quotient an integer, so that interval separates its branch. This auxiliary conclusion depends on the interval implementation. Formula (7.4) and all the ordinary proofs above do not need that numerical branch selection.

The numerical value of S begins

    1.1104141628908685596945079590551171402939
    +0.8634467779055493861707174075676104937155*i.

## 8. Tests and their limits

- exact_checks.py performs 45 exact rational/algebraic checks, including the unit action, Smith form, Eisenstein polynomial, Dedekind sums, all eta-quotient criteria, cusp orders and initial Fourier coefficients.
- numerical_checks.py independently compares the gamma logarithmic series with q-Pochhammer products and the eta formulas at 70 and 110 decimal digits. It also checks the odd-sector identity and the old algebraic candidate numerically.
- interval_checks.py computes simultaneous enclosures at 0,1/2,1/3,2/3 at 170 digits, up to n=6000. It retains 4800 non-smoothed-away terms.

For |p|<r=19/20 and |q|<s=3/5, the uniform real-z tail in (7.1) satisfies

    E_N <= 5/[(N+1)(1-r^(N+1))(1-s^(N+1))]
           *[r^(N+1)/(1-r)+s^(N+1)/(1-s)].

At N=6000 this is less than 3.48e-136. The implementation adds a 1e-135 rectangle radius to each logarithmic sum. Complex powers are reset every 32 steps to control interval wrapping.

The interval output has |U-U_alg|<1e-130 and |exp(-5*i*sqrt(3)*S)-U_alg^2|<1e-128. These are enclosures, not equality proofs. mpmath.iv is experimental upstream and has not been certified in Lean or independently in another interval implementation.

All three new scripts passed their first completed executions. The unavailable HTML rendering of one source was replaced by its public PDF. There were no failed new mathematical test assertions in the completed runs. A separate source-ZIP extraction replay is recorded in REPLAY.json.

## 9. Research consequence

The new anchor fixes an analytic scale once a genuine function comparison has been proved. It does not create the comparison or force its 1/3 value into a number field. The half-point theorem rules out the blanket replacement of arithmetic admissibility by 'torsion plus smoothing'.

The next productive analytic calculation is (7.2)--(7.5): evaluate the odd character-twisted double Lambert series at this unit-fixed cubic torsion datum in terms of the logarithm of the explicit Jacobi--Kummer unit. A purported simplification must preserve the conductor-3 torsion datum and survive the transcendental half-point control.

## Sources used

1. Bergeron--Charollois--Garcia, *Elliptic units for complex cubic fields*, arXiv:2311.04110v2, introduction, section 2.1, Lemma 4.8 and equation (4.32), section 5.2. https://arxiv.org/html/2311.04110v2
2. NIST DLMF 23.18.5--7, Dedekind eta transformation and Dedekind sums. https://dlmf.nist.gov/23.18
3. Kong--Teo, *An Elementary Proof of the Transformation Formula for the Dedekind Eta Function*, arXiv:2302.03280. https://arxiv.org/pdf/2302.03280
4. SageMath official documentation, eta products on modular curves X_0(N), Ligozat criteria. https://doc.sagemath.org/html/en/reference/modfrm/sage/modular/etaproducts.html
5. Choi--Lim, arXiv:1812.01770, Theorem A on page 1 (Schneider's theorem), and the Q-model of X_0(N) on page 2. https://arxiv.org/pdf/1812.01770
6. The predecessor Komorebi_H12_Cubic_Jacobi_Kummer_Audit.zip, SHA256 f37715123979031d13e8115dea3d0648f287db0e699d641490eb01af628f1c0b, for the explicit algebraic U_alg and its exact finite proof.

No claim of literature novelty, independent peer review, or a proof of the BCG algebraicity conjecture is made.

<!-- END ORIGINAL FILE: PROOF(20261002-123422).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-131052).md -->
# Archive Part 4: `PROOF(20261002-131052).md`

# Komorebi H12 continuation: a cubic-unit return product and its Jacobi determinant

## Status

This note contains ordinary mathematical proofs and exact symbolic / high-precision regression tests. It does **not** prove the elliptic-gamma special value algebraic or equal to the previously constructed Jacobi--Kummer unit. There is no Lean proof, no new interval certificate, no independent human review, and no claim of literature novelty.

The new analytic result is an exactly normalized theta-product limit for the original value. The new finite identity identifies the SAME unit matrix's twisted determinant with the Jacobi sum 2+3*omega. The missing theorem is a comparison between these two realizations, not the determinant calculation itself.

## 1. Conventions

Choose beta = 7^(1/3) exp(-2*pi*i/3). Put

    epsilon = 2-beta,
    tau = (beta^2+2*beta)/15,
    t = -tau,
    sigma = -(beta+2)/15,
    r = epsilon^(-1) = beta^2+2*beta+4,
    delta = 15*t-4 = -r,
    z0 = 1/3.

Both t and sigma lie in the upper half-plane. Use the BCG additive elliptic-gamma convention, with Gamma(z;-t,sigma)=1/Gamma(z+t;t,sigma), and define

    F(z) = Gamma(z;tau,sigma)^5 / Gamma(5*z;5*tau,5*sigma),
    U = F(z0).

The prior eta-anchor calculation gives

    F(0) = epsilon^2.

For completeness, let H(v)=eta(5*v)/eta(v)^5. The product telescopes at zero to F(0)=H(sigma)/H(t). The matrices [-4,1;15,-4] and [-4,5;3,-4] take t to sigma and 5*t to 5*sigma. Their exact eta multipliers cancel in the smoothed quotient, so H(sigma)=delta^(-2)H(t). Since delta*epsilon=-1, the anchor follows. This uses the standard eta transformation formula; the predecessor records the Dedekind sums -19/90 and -1/18 and their multiplier exponents -1/12 and -5/12.

## 2. The elliptic theta multiplier and an exact period-exchange identity

Write

    theta0(z;v) = (x;q)_infty (q/x;q)_infty,
    x=exp(2*pi*i*z), q=exp(2*pi*i*v),
    Theta(z;v) = theta0(z;v)^5 / theta0(5*z;5*v).

Theta is an even elliptic function of z, with periods 1 and v. Its divisor on C/(Z+Zv) is four times the origin minus the four nonzero points k/5, k=1,2,3,4. The product also gives

    Theta(z;v) = (2*pi)^4 z^4 / (5 H(v)^2) + O(z^5)

at zero. The displayed leading coefficient, not the unneeded remainder's parity, is used below.

The gamma difference laws imply

    F(z+tau)/F(z) = Theta(z;sigma),
    F(z+sigma)/F(z) = 1/Theta(z;t),
    F(z+1)=F(z).

The second formula retains the negative-period convention; smoothing cancels its elementary exponential factors.

### Theta covariance, including its constant

The arithmetic identities

    sigma = (-4*t+1)/(15*t-4),
    delta^(-1) = -4-15*sigma

show that multiplication by delta identifies the sigma elliptic lattice with the t elliptic lattice. The two functions

    Theta(z;sigma),   Theta(delta*z;t)

have the same divisor: delta^(-1)k/5 is congruent to k/5 modulo Z+Zsigma. Their quotient is constant. Comparing the leading coefficients at zero and using H(sigma)=delta^(-2)H(t) shows the constant is 1. Thus

    Theta(z;sigma) = Theta(delta*z;t).                         (2.1)

This proves the needed covariance from divisors and the eta anchor, without assuming a phase-free cross-lattice gamma identity.

A second, genuinely cubic identity is

    delta*t = sigma-8*t+2.

Since delta*z0 is congruent to -z0 modulo Z+Zt, equation (2.1), periodicity, and evenness yield, for every integer j,

    Theta(z0+j*tau;sigma) = Theta(z0+j*sigma;t).               (2.2)

This period-exchange identity uses BOTH the conductor-three point and the cubic period relation. It fails in general at z=1/2, as the tests demonstrate.

All its sampled factors are finite and nonzero. Indeed 1,tau,sigma are Q-linearly independent. An equality z0+j*tau in (1/5)Z+Zsigma would force j=0 and 1/3 in (1/5)Z, which is impossible.

## 3. The actual unit matrix generates a contracting return

In the lattice basis (beta^2+2*beta, -(beta+2),15), multiplication by epsilon has matrix

    M = [0,1,0; -4,2,15; -1,0,4].

Its inverse is

    N = M^(-1) = [8,-4,15; 1,0,0; 2,-1,4].

The row (tau,sigma,1) satisfies

    (tau,sigma,1) N = r (tau,sigma,1).

Let v0=(0,0,1/3)^T. Since (N-I)v0=(5,0,1)^T is integral, all N^m v0-v0 are integral. Write

    N^m v0-v0 = (a_m, b_m, d_m)^T.

Then b_m=a_(m-1), d_m is an integer, and

    z0 + a_m*tau + a_(m-1)*sigma + d_m = r^m/3.              (3.1)

The first return indices are

    a_0=0, a_1=5, a_2=60, a_3=690, a_4=7925, a_5=91020.

The inverse characteristic polynomial gives the exact recurrence

    a_(m+3) = 12*a_(m+2)-6*a_(m+1)+a_m.                     (3.2)

The indices are strictly increasing for m>=1. For example a_2>=11*a_1, and the recurrence proves a_(m+1)>=11*a_m inductively, since a_m>=11*a_(m-1)>0 gives 12*a_m-6*a_(m-1)+a_(m-2)>11*a_m.

Although these integer coordinates grow, their chosen complex realization contracts. Norm(epsilon)=1 and the real embedding epsilon_R=2-cuberoot(7) lies in (0,0.09). Therefore

    |r|^2=epsilon_R,   |r|<3/10.

Numerically r=0.257415962216125...-0.144242294851258...i and |r|=0.295074257141504....

## 4. An exact theta-only formula for each return

Define the finite products

    P_m = product_{j=a_(m-1)}^(a_m-1) Theta(z0+j*sigma;t),
    m>=1.                                                    (4.1)

They can equivalently be evaluated with the fast-converging sigma nome, replacing each factor by Theta(z0+j*tau;sigma) using (2.2).

To prove their relation to F, first iterate the tau shifts, and then the sigma shifts. Because Theta(z;t) is tau-periodic (tau=-t), the latter factors do not depend on the previous integer tau shift. For nonnegative a,b,

    F(z0+a*tau+b*sigma)/F(z0)
       = [product_{j=0}^{a-1} Theta(z0+j*tau;sigma)]
         /[product_{j=0}^{b-1} Theta(z0+j*sigma;t)].

Use (2.2), take a=a_m, b=a_(m-1), cancel the actual common factors, and use (3.1) and integer periodicity. This proves

    P_m = F(r^m/3)/F(1/3).                                   (4.2)

This is an identity for EACH finite m, not a numerical fit or an asymptotic assumption.

Since F is holomorphic and nonzero near zero,

    C := lim_{m->infty} P_m = epsilon^2/U.                   (4.3)

Equivalently,

    U = epsilon^2 / lim P_m.                                 (4.4)

The scalar normalization is now fixed by the proved anchor. It has not been inferred from a vanishing coboundary.

### Explicit convergence bound

Let p=exp(2*pi*i*t), q=exp(2*pi*i*sigma). On the strip -Im(t)<Im(z)<Im(sigma), the product yields a holomorphic logarithm

    L(z)=-5 sum_{n>=1, 5 does not divide n}
          [(p exp(2*pi*i*z))^n-(q exp(-2*pi*i*z))^n]
          /[n(1-p^n)(1-q^n)],
    F(z)=exp(L(z)).

The elementary bounds |p|<19/20, |q|<3/5 can be proved using 1.91<cuberoot(7)<1.92, sqrt(3)>1.73, and 2*pi>6.28. On |z|<=1/1000, exp(2*pi*|z|)<101/100. Differentiating the absolutely convergent series and bounding its positive geometric majorants gives

    |L'(z)|<40000,    |L''(z)|<6000000.                       (4.5)

The rational comparisons used here are checked exactly by the script. The first derivative is bounded by

    10*pi/[(1-rp)(1-rq)] * [A/(1-A)+B/(1-B)],

and the second by

    20*pi^2/[(1-rp)(1-rq)] * [A/(1-A)^2+B/(1-B)^2],

where rp=19/20, rq=3/5, A=1919/2000, B=303/500.

For m>=5, |r^m/3|<1/1000. Thus

    |P_m/C-1| <= exp((40000/3)*(3/10)^m)-1.                  (4.6)

This analytic inequality is a proof, independent of the floating-point tests.

## 5. A branch-free integer filter accelerates the return

Put

    h(X)=det(I-X*M)=1-6*X+12*X^2-X^3.

Since r is an inverse eigenvalue of M, h(r)=0. Also h(1)=6. Define

    A_m = P_m * P_(m+2)^12 / [P_(m+1)^6 * P_(m+3)].         (5.1)

These are integer powers, so no logarithm or fractional-root convention is required in the definition.

Write L(z)-L(0)=ell_1*z+R(z), with |R(z)|<=3000000*|z|^2 on the small disk. The linear term in the logarithm of A_m/C^6 is

    (ell_1/3) r^m h(r) = 0.

Therefore

    A_m -> C^6,
    |A_m/C^6-1| <= exp(700000*(3/10)^(2*m))-1, m>=5.         (5.2)

For the bound, use sum_{j=0}^3 |h_j|*(3/10)^(2*j)<2. This proves a quadratic improvement in the return error: O(|r|^(2m)), rather than O(|r|^m).

This filter is NOT an algebraicity theorem. The same annihilation calculation works for an arbitrary holomorphic nonzero function with an arbitrary limiting scalar. Its value here is an exact analytic reduction with integer exponents.

## 6. The same finite matrix yields the Jacobi-sum radicand

Let omega^2+omega+1=0. Direct determinant expansion gives

    det(I-M)=6,
    det(omega*M-I)=6*(2+3*omega).

Hence

    J = det(omega*M-I)/det(I-M) = 2+3*omega.                 (6.1)

This is exactly the finite Jacobi sum used in the preceding Kummer construction. With the cubic character on F_7 given by

    chi(1)=1, chi(2)=omega, chi(3)=omega^2,
    chi(4)=omega^2, chi(5)=omega, chi(6)=1, chi(0)=0,

the five nonzero terms in sum chi(a)chi(1-a) are omega,1,omega,1,omega. The sum is J.

For a primitive seventh root zeta and G=sum_{a=1}^6 chi(a)zeta^a, the finite Gauss--Jacobi identities give G^3=7J. Since beta^3=7,

    Xi=G/beta  satisfies  Xi^3=J.

Thus the earlier algebraic eigen-coordinate has the direct unit-matrix presentation

    Xi^3 = det(omega*M-I)/det(I-M).                           (6.2)

The radicand is a prime above 7, NOT a unit or a root of unity. Its norm is 7.

The occurrence of 7 can also be read without choosing omega:

    det(I-M^3)=1512,
    det(I-M^3)/det(I-M)^3 = 1512/216 = 7.                    (6.3)

Indeed det(I-M^3)=det(I-M)det(I-omega*M)det(I-omega^2*M), and the latter two determinants multiply to 36*7.

For additional context, the literal exterior-square matrix in the basis e12,e13,e23 is

    W = [4,0,15; 1,0,4; 2,-1,8].

It has the inverse-unit characteristic polynomial, and

    det(I-omega*M)/det(I-omega*W) = -J/conjugate(J).

These are finite algebraic identities. No analytic determinant comparison, equivariant torsion theorem, or equality of a gamma value with a finite determinant is asserted.

The one polynomial h therefore has three exact roles:

    h(r)=0               -- cancels the first return error,
    h(1)=6               -- produces the sixth-power normalization,
    -h(omega)/h(1)=J      -- gives the Jacobi radicand.

The number 6 also equals the order of the unit-fixed torsion group, as the Smith form of M-I is diag(1,1,6). This identifies common finite data, not the missing analytic realization.

## 7. A further guardrail: a single period shift has a transcendental multiplier

The first theta multiplier is exactly

    T0=Theta(1/3;t)
       = -9 * eta(3*t)^5 * eta(5*t) / [eta(t)^5*eta(15*t)].  (7.1)

To see the -9, use (1-omega)^5/(1-omega^2)=-9 and

    theta0(1/3;v)=(1-omega)D(q^3)/D(q).

The eta quotient in (7.1) has level 15 exponents r1=-5,r3=5,r5=1,r15=-1. Their sum is zero, their two eta congruence sums are 0 and -48, and product d^r_d=81 is a square. The standard eta-quotient criterion makes it a weight-zero modular function with trivial character and rational q-expansion. The quotient without -9 begins

    1+5*q+20*q^2+60*q^3+165*q^4+...

and is nonconstant. It has no zero or pole in the upper half-plane.

Now t satisfies 225*t^3-42*t+7=0, an Eisenstein polynomial at 7. Schneider's theorem implies j(t) is transcendental. A finite algebraic value of the above nonconstant modular function would make j(t) algebraic, since a nonconstant function on the modular curve defines a finite map and j is algebraic over its function field. Therefore T0 is transcendental.

The exact difference law says

    F(1/3+tau)=T0*F(1/3).                                    (7.2)

The two arguments represent the SAME unit-fixed class in C/(Z+Ztau+Zsigma), but their scalar values cannot both be nonzero algebraic numbers. If the conjectured algebraicity of F(1/3) is proved, its unchanged-face tau translate is necessarily transcendental.

This is not a contradiction of BCG: shifting only the argument while holding the geometric realization fixed is not the same as coherently transporting all their admissible data. It proves that a scalar-valued theorem must retain the representative/trivialization data; unit-fixedness alone cannot make this raw F descend to the torsion quotient.

## 8. Precise unresolved arithmetic comparison

Let U_alg be the explicit degree-six algebraic unit in the preceding Jacobi--Kummer note. Nothing in this note proves

    lim P_m = epsilon^2/U_alg,

or the weaker sixth-power equality

    lim A_m = (epsilon^2/U_alg)^6.                            (8.1)

A proof of (8.1), followed by rigorous separation of the six possible root-of-unity factors, would prove the original equality. At present (8.1) is an arithmetic target, not an input used in deriving the theta products.

The new finite determinant (6.2) supplies a concrete candidate on the algebraic side of a prospective determinant/resolvent comparison. It does NOT identify the theta-return scalar C with Xi; they are different quantities, linked on the candidate side by the previously supplied nonlinear reconstruction of U_alg.

The original odd Dirichlet-character series remains equivalent to the target through U^2=exp(-5*i*sqrt(3)*S). The return formula is a different exact realization of the same normalized value, with a specified recurrence and explicit error bounds.

## 9. Verification and limitations

- exact_checks.py checks 130 exact rational / polynomial assertions, including return coordinates through m=20, the recurrence, bound constants, the eta data, the finite Jacobi sum, the twisted determinant, and the complementary Gauss resolvents.
- numerical_checks.py runs independently at 70 and 110 decimal digits. It checks 17 analytic identities at each precision, evaluates actual finite theta products of lengths 5,55,630, and tests the analytic estimates and the filtered convergence.
- The very long indexed products in the asymptotic table are evaluated via the PROVED return identity F(r^m/3)/U, not multiplied term-by-term. This distinction is explicit in the output.
- The evaluator recenters the logarithmic gamma series using a finite number of exact theta difference laws. Its target and zero values are independently checked against an unshifted 6500-term sum.
- No numerical observation is used to prove transcendence or algebraicity. Transcendence in section 7 is an application of eta modularity and Schneider's theorem.
- No new interval-arithmetic certificate is claimed. The universal error bounds are proved separately by majorants. The high-precision computations are regression tests.
- Two exact-script development runs failed: first, a rational expression was passed to a polynomial reduction before putting it over a common denominator; second, structurally different factored/expanded expressions were compared without expanding their difference. The repaired tests retain the same mathematical identities. Snapshots and failure notes are included.

## Sources and inherited inputs

1. Bergeron--Charollois--Garcia, *Elliptic units for complex cubic fields*, arXiv:2311.04110v2. Gamma definitions, functional equations and the original pure-cubic target. https://arxiv.org/html/2311.04110v2
2. NIST DLMF 23.18, eta transformation. https://dlmf.nist.gov/23.18
3. Rouse--Webb, *On spaces of modular forms spanned by eta-quotients*, arXiv:1311.1460v3, printed page 2: eta congruence criteria and the modular-curve model. https://arxiv.org/pdf/1311.1460
4. Choi--Lim, arXiv:1812.01770, Theorem A on page 1: the classical Schneider criterion. https://arxiv.org/pdf/1812.01770
5. The predecessor Torsion Selection and Eta Anchor note supplies the fully recorded F(0) derivation, and the prior Jacobi--Kummer note supplies U_alg. Their archive hashes are preserved in PREDECESSORS.json.

All new statements above are distinguished from these background results. No claimed advance in the general status of Hilbert's twelfth problem is made.

<!-- END ORIGINAL FILE: PROOF(20261002-131052).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-134353).md -->
# Archive Part 5: `PROOF(20261002-134353).md`

# Komorebi H12: an integral unramified cubic and a primitive-sector correction

## Status and scope

This continuation proves an explicit integral model of the Hilbert class field of K = Q(beta), beta^3 = 7, and independently identifies the degree-six ray class field used in the cubic elliptic-gamma experiment. It also tests and repairs a proposed determinant rule under squaring the unit. These are ordinary algebraic-number-theory proofs with exact symbolic checks, not Lean theorems and not a claim of literature novelty.

The original analytic equation U_Gamma = U_alg is NOT proved here. In particular, nothing below makes the theta-return limit algebraic merely because the algebraic comparison field is known. The computational calibration is separated from the proofs.

The current experiment is exclusively beta^3=7. It is not the other BCG cubic beta^3-beta^2+5beta+1=0.

## 1. A discriminant-one relative polynomial

Let theta = zeta_7 + zeta_7^(-1), or any of its three real conjugates. Its polynomial is

    f(T) = T^3 + T^2 - 2T - 1.

It is irreducible over Q: the only possible rational roots are +/-1, neither of which is a root. The other roots are theta^2-2 and -theta^2-theta+1. Thus Q(theta)/Q is cyclic of degree 3.

Set

    nu = (theta-2)/beta.

An exact polynomial expansion gives

    f(2+beta*V) = 7 (V^3 + beta^2 V^2 + 2 beta V + 1).

Consequently nu satisfies

    Phi(V) = V^3 + beta^2 V^2 + 2 beta V + 1 = 0.          (1.1)

Since Q(theta) is Galois and K is a non-Galois cubic, their intersection is Q. Therefore H = K(theta) = K(nu) has degree 3 over K. In particular Phi is irreducible over K.

The discriminant is exactly

    disc(Phi) = 4 beta^6 - 32 beta^3 - 4 beta^6 - 27 + 36 beta^3
              = 4 beta^3 - 27 = 1.                       (1.2)

This is the RELATIVE discriminant over K. It is not an absolute discriminant-one number field over Q.

The norm is

    N_(H/K)(nu) = -1,
    nu^(-1) = -nu^2-beta^2 nu-2 beta.

Thus nu is an actual algebraic unit, unlike the prime-radical coordinate Xi whose cube is 2+3 omega.

## 2. Explicit integral trace duality proves the whole integer ring

The cyclic automorphism sigma is

    sigma(nu) = beta nu^2 + 4nu,
    sigma^2(nu) = -beta nu^2 - 5nu - beta^2.              (2.1)

These formulas follow from theta -> theta^2-2. Direct reduction proves sigma^3=1. They also give

    Tr(nu) = -beta^2,
    Tr(nu^2) = 3 beta,
    Tr(nu^3) = -10,
    Tr(nu^4) = 5 beta^2.

The trace Gram matrix on (1,nu,nu^2) is therefore

          [ 3       -beta^2     3 beta ]
    T  =  [-beta^2   3 beta      -10  ],
          [ 3 beta    -10       5 beta^2]

with the integral inverse

              [ 5      5 beta   beta^2 ]
    T^(-1) =  [5 beta  6 beta^2    9   ].                (2.2)
              [beta^2     9      2 beta]

All entries lie in O_K, and T*T^(-1)=I using beta^3=7.

This proves more than a numerical discriminant identity. Let e_i^* be the trace-dual basis supplied by (2.2). Each e_i^* lies in O_K[nu]. If a is any element of O_H, write a = sum a_i nu^i with a_i in K. Then

    a_i = Tr_(H/K)(a e_i^*) in O_K.

The inclusion follows because the trace of an integral element is integral. Hence

    O_H = O_K[nu],     disc(O_H/O_K) = (1).              (2.3)

The discriminant criterion for ramification now proves H/K unramified at every finite prime [ANT, Theorem 3.35]. At the real place of K, beta and all three theta-conjugates are real, so all extensions of that real place to H are real. There is no infinite ramification either.

For additional explicit control,

    (nu-sigma(nu)) (sigma(nu)-sigma^2(nu)) (sigma^2(nu)-nu) = -1.

Thus each difference between conjugates is itself a unit. The source script verifies this on the original conjugate formulas, not by assuming the discriminant.

## 3. An elementary class-number computation identifies H as the Hilbert class field

### The base integer ring

The polynomial X^3-7 has discriminant -27*49. Only 3 and 7 can divide the index [O_K:Z[beta]]. At 7, the polynomial is Eisenstein. At 3, beta-1 satisfies

    X^3+3X^2+3X-6,

which is Eisenstein at 3. The local uniformizer description gives maximality at these two primes. Equivalently, Dedekind's index criterion has relatively prime correction terms at both primes; the exact script checks those corrections. Therefore

    O_K=Z[beta],       disc(K)=-1323.

### Generators for all ideal classes

The Minkowski bound is

    (4/pi)*(3!/3^3)*sqrt(1323) < (8/27)*37 < 11.

Thus every class has an integral representative of norm at most 10 [ANT, Theorem 4.3]. The relevant prime ideals are

    b=(2,beta-1),                Norm b = 2,
    c=(2,beta^2+beta+1),          Norm c = 4,
    f=(3,beta-1),                Norm f = 3,
    a=(5,beta-3),                Norm a = 5,
    p7=(beta),                  Norm p7 = 7.

These account for all prime ideals of norm at most 10, as is seen by factoring X^3-7 at 2,3,5,7. Norm comparison and the stated residues give

    (2)=b c,
    (beta-1)=b f,
    (beta+2)=a f,
    (beta+1)=b^3.

For the last equality, beta+1 does not lie in c, and its norm is 8. In particular all classes are generated by [b] and [b]^3=1.

The ideal b is not principal. Indeed the actual norm formula is

    N(a+b1 beta+c1 beta^2)
      = a^3+7 b1^3+49 c1^3-21 a b1 c1.

Modulo 7 this is a^3. Cubes modulo 7 are only 0,1,-1, so neither norm 2 nor norm -2 is possible for an algebraic integer. A generator of the norm-two ideal would have one of those norms. Therefore

    Cl(K) = C3, generated by [b].                          (3.1)

The cyclic degree-three extension H/K is unramified everywhere. Since the maximal such abelian extension has degree the class number, (3.1) and class field theory imply

    H = the Hilbert class field of K.                     (3.2)

This derivation does not take BCG's class number or ray-field computation as a proof input. It uses standard Minkowski/discriminant/class-field theorems and the explicit computations above.

## 4. The full narrow ray field and its conductor

Let omega^2+omega+1=0 and put E=H(omega). Since [H:Q]=9, H cannot contain a quadratic field. Thus

    [E:K]=6,     Gal(E/K)=C3 x C2.

Consider the modulus m=f*infinity_R, where f is the unique norm-three prime and infinity_R the unique real place of K.

The ray-class exact sequence [CFT, V.1.7] uses the group

    (O_K/f)^x x {+,-} = F3^x x {+,-}.

For any unit u, its norm is +/-1 and its sign equals the sign at the real embedding, because the product over the complex pair is positive. Modulo 3, multiplication in

    O_K/3O_K = F3[X]/((X-1)^3)

has determinant u_res^3=u_res. Hence the residue of u modulo f agrees with its real sign. The image of the unit group is exactly the two-element diagonal subgroup; -1 supplies its nonidentity element. The ray kernel has size 4/2=2, and (3.1) yields

    |Cl_m(K)|=2*3=6.                                      (4.1)

The quadratic extension K(omega)/K is unramified away from f. At f, K_f has degree 3 over Q_3, while Q_3(omega)/Q_3 has ramification index 2. Their compositum is a ramified quadratic extension of K_f: its absolute ramification index must be divisible by both 3 and 2, and its degree is 6. It is tamely ramified, since the residual characteristic is 3. Its conductor exponent is therefore 1 [CFT, I.1.9]. The real place becomes complex. Its conductor is exactly m.

H/K is unramified everywhere, so E lies in the ray field of modulus m. Comparing its degree 6 with (4.1) proves

    E = K(f*infinity_R) = K(nu,omega).                     (4.2)

This proves the arithmetic ray-field identification independently of the conjectural gamma evaluation.

### Explicit Frobenius

Modulo b=(2,beta-1),

    Phi(V) = V^3+V^2+1 in F2[V],

which is irreducible. In its residue field, the formula sigma(nu)=beta nu^2+4nu reduces to nu -> nu^2. Thus arithmetic Frobenius at b is sigma on H.

It sends omega to omega^2 on the quadratic factor. Hence the full ray-field Frobenius is

    Frob_b(nu)=beta nu^2+4nu,
    Frob_b(omega)=omega^2.                                (4.3)

It has order 6. The script also checks the irreducible reductions and Frobenius formulas at the norm-three prime in H and the norm-five prime: these give sigma^2 and sigma, respectively.

The local implementation at b is particularly explicit. Hensel-lift the odd solution of beta^3=7 modulo 2^k and retain the same monic Phi and formula (2.1). The script verifies preservation of Phi and order three for k=1,2,4,8,16,32,64. These finite checks supplement the global proof; they are not a proof of an analytic-to-p-adic comparison.

## 5. The sextic unit in the small integral basis

The preceding Kummer note defined an inversion-quotient coordinate Y(theta) with a denominator 7. Substituting theta=2+beta nu eliminates that denominator entirely:

    Y(nu) = -3+3 beta-beta^2
          + (-21-4 beta+7 beta^2) nu
          + (18-8 beta-beta^2) nu^2.                      (5.1)

The corresponding quadratic-lift expression becomes

    Z(nu) = 7-beta-beta^2
          + (-3 beta^2+14 beta-15) nu
          + (13 beta^2-14 beta-20) nu^2/3.               (5.2)

Reduction modulo Phi and beta^3-7 gives

    Y^2-4=-3 Z^2.

With s=1+2omega (so s^2=-3), define

    U_alg=(Y-sZ)/2,       U_alg^(-1)=(Y+sZ)/2.             (5.3)

Their product is 1. The value in (5.3) satisfies the ORIGINAL reciprocal sextic

    Q(X)=X^6+(6 beta^2-14 beta+2)X^5
      +(4 beta^2-6 beta+2)X^4
      +(106 beta^2-152 beta-103)X^3
      +(4 beta^2-6 beta+2)X^2
      +(6 beta^2-14 beta+2)X+1.

Thus U_alg is integral and a unit. The inverse polynomial Y -> theta from the preceding proof is verified again. It recovers H from U+U^(-1). Since Z is nonzero, s=(Y-2U)/Z is also recovered. Therefore

    K(U_alg)=E=K(f*infinity_R).                           (5.4)

No assertion about the full integer basis of E is made: (5.2) has a denominator 3, and the quadratic integral model is not being silently identified with O_H[omega]. Integrality of U follows from Q.

The Kummer coordinate and the integral unit are connected by

    Xi^3=2+3omega,
    nu=(Xi+beta/Xi-beta^2)/3.                             (5.5)

Here Xi is the explicit normalized finite Gauss sum from the preceding proof, not an analytically defined gamma value. Formula (5.5) is rechecked algebraically.

## 6. Squaring the unit refutes the raw determinant prescription

The previous continuation found

    M=[0,1,0; -4,2,15; -1,0,4],
    h(X)=det(I-XM)=1-6X+12X^2-X^3,
    J=det(omega M-I)/det(I-M)=2+3omega.

It was important to test whether this formula is compatible with changing the generator from M to M^2. The same raw prescription gives instead

    J2=det(omega M^2-I)/det(I-M^2)=(11+12omega)/10.        (6.1)

Its norm to Q is 133/100=7*19/100. At the Eisenstein prime over 19 with omega=7 modulo 19, the numerator has valuation exactly 1. The denominator is a 19-adic unit. The extension K(omega)/Q(omega) is unramified there: its discriminant can only involve primes over 3 or 7. Thus J2 has valuation 1 at each prime of K(omega) above that Eisenstein prime.

It follows that J2/J^2 is not a cube in K(omega). More strongly, adjoining a cube root of J2 introduces ramification at 19, whereas the desired extension E/K(omega) is unramified there.

This refutes the particular rule “apply the same unfiltered determinant formula to every unit power and obtain the corresponding power of the same Kummer coordinate.” It does not refute the original equality at M, nor every possible arithmetic determinant comparison.

### The extra cyclotomic sector is explicit

Factor the squared operator at omega:

    det(I-omega M^2)=h(omega^2) h(-omega^2),
    det(I-M^2)=h(1) h(-1).

Consequently

    J2 = conjugate(J) * h(-omega^2)/h(-1)
       = conjugate(J) * (-2+3omega)/10.                  (6.2)

The unwanted factor is the additional order-six sector, normalized by the order-two sector. Its norm is 19/100.

After removing this factor, one obtains conjugate(J), which has exactly the correct cube class:

    conjugate(J)/J^2 = 7/J^3 = (beta/J)^3.               (6.3)

So the corrected prescription is compatible with the squared cubic eigencharacter. A compatible radical is beta/Xi, whose cube is conjugate(J), and whose sigma-eigenvalue is omega.

This supplies a precise primitive-sector correction. It does not identify any of these determinants with the theta-return multiplier.

## 7. A small family of discriminant-one models

The rescaling is not peculiar to 7. Suppose

    f_a(T)=T^3-aT^2-(a+3)T-1,
    p=a^2+3a+9

is prime. Choose c in Z with 3c=a modulo p. Since p is not 3, this is possible, and

    f_a(T)=(T-c)^3 modulo p.

Let beta^3=p. Then

    f_a(c+beta V)/p
      = V^3 + A beta^2 V^2 + B beta V + C,

where

    A=(3c-a)/p,
    B=f_a'(c)/p,
    C=f_a(c)/p

are integers. Since disc(f_a)=p^2, the new relative discriminant is

    p^2 / beta^6 = 1.

The polynomial f_a is irreducible (its only possible rational roots are +/-1, with neither a root), has positive square discriminant, and defines a cyclic real cubic. It is disjoint from the non-Galois pure cubic. Hence this again produces an everywhere unramified cyclic cubic over Q(cuberoot(p)), split at the real place. The same discriminant-one trace-duality argument proves the maximal relative order. In particular, the class number is divisible by 3.

Four exact tests are:

| p | Relative polynomial |
|---|---|
| 7 | V^3+beta^2 V^2+2beta V+1 |
| 13 | V^3-beta^2 V^2+4beta V-5 |
| 19 | V^3+beta^2 V^2+6beta V+11 |
| 37 | V^3-beta^2 V^2+12beta V-47 |

Every discriminant is exactly 1. Only the first displayed generator is asserted to be a unit of norm -1. No class-number equality, gamma formula, or full ray-field computation is asserted for the other three fields. This is an explicit calculation in the classical simplest-cubic/genus-field setting, not a claim of a new general Hilbert-12 theorem.

## 8. Connection to the unresolved analytic target

The preceding unit-return proof constructs the ACTUAL analytic limit

    C_Gamma = lim P_m = (2-beta)^2 / U_Gamma.

That is an exact analytic identity, with proved convergence bounds. The present note constructs independently

    C_alg = (2-beta)^2 / U_alg.

We do NOT prove C_Gamma=C_alg.

The integral cubic model suggests a more concrete descent target: extract the same cubic coordinate from the analytic value and prove it satisfies

    Phi(nu_Gamma)=0.

The numerical script uses the explicit inverse quadratic polynomial from Y to theta and then divides theta-2 by beta. At 120 decimal digits its Phi-residual is approximately 3.24e-117. This is only numerical calibration. That inverse quadratic map can have extra preimages away from the algebraic locus, so an exact proof of Phi(nu_Gamma)=0 would still require branch selection or the corresponding inverse-reconstruction identity before concluding Q(U_Gamma)=0. The previous interval enclosure can support branch selection, but does not itself establish the polynomial relation.

The new arithmetic information does not turn the analytic period into an algebraic integer automatically. The remaining task is an arithmetic descent/evaluation theorem for the gamma or theta-return expression. Mere finite-order symmetry, a zero coboundary, or faster convergence still does not establish it.

## 9. Verification actually carried out

- exact_checks.py passed 134 exact rational/finite-ring checks. This includes the discriminant, trace-dual inverse, original conjugates, norm formula, ideal-factorization data, unit residue data, finite Frobenius formulas, the rewritten sextic, Kummer identities, primitive-sector correction, four family examples, and finite 2-adic models through 64 bits.
- numerical_checks.py passed 10 regression comparisons at each of 80 and 120 decimal digits. The gamma value is evaluated independently from its convergent logarithmic series; the algebraic value is built from a real seventh-cyclotomic root.
- Numerical comparison does not prove algebraicity. These runs are not interval certificates.
- The standard number-theory deductions (Minkowski/class field theory/conductor theory) are ordinary mathematical arguments, not assertions that the Python script proves those theories.
- No production test run failed during this continuation. The determinant power-compatibility test is an intentional negative result, not a software failure.
- No Lean compilation and no independent human or second-agent review was performed.
- The release receipt records a separate extraction replay, once actually completed. The manifest authenticates the files, not the mathematical truth of an unproved analytic conclusion.

## Sources

1. Bergeron, Charollois, Garcia, *Elliptic units for complex cubic fields*, arXiv:2311.04110v2, Introduction and section 5.2. Context and the original analytic target. https://arxiv.org/html/2311.04110v2
2. J. S. Milne, *Algebraic Number Theory*, Theorems 3.35 (ramification/discriminant), 4.3 (Minkowski bound), and Remark 4.11 (Hilbert class field); also the local Eisenstein/uniformizer discussion. https://www.jmilne.org/math/CourseNotes/ANT.pdf
3. J. S. Milne, *Class Field Theory*, V.1.7 (ray exact sequence), I.1.9 (tame conductor), and the global reciprocity/existence theorem. https://www.jmilne.org/math/CourseNotes/CFT.pdf
4. The preceding Jacobi--Kummer proof supplies the explicit algebraic Y/Z model and inverse map, all rechecked here.
5. The preceding Unit Return and Jacobi Determinant proof supplies the analytic return identity and its bounds. It is used only with its stated boundary: equality to C_alg remains unproved.

All classical background is used as such. The explicit calculations are distinguished from the source statements and from the remaining analytic conjecture.

<!-- END ORIGINAL FILE: PROOF(20261002-134353).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-141429).md -->
# Archive Part 6: `PROOF(20261002-141429).md`

# Komorebi H12: the unramified cubic as an explicit isogeny fiber

## Status

This continuation proves an explicit algebraic and elliptic-curve realization of the cyclic cubic already constructed for K=Q(beta), beta^3=7. The fiber is that of a degree-three isogeny between two fixed elliptic curves over Q. The class-field Frobenius becomes translation by an actual rational point of order three. The same fiber has a Kummer coordinate whose cube is the previously computed finite Jacobi sum.

This is an ordinary proof, supported by exact symbolic identities and finite-field checks. Standard facts about smooth projective curves, isogenies, and prime-to-residue-characteristic torsion reduction are used as background. No Lean verification is claimed. No novelty priority is claimed for the classical isogeny or descent construction.

The elliptic-gamma equality U_Gamma=U_alg and the theta-return equality C_Gamma=C_alg remain UNPROVED. The numerical isogeny residual is explicitly a coordinate reformulation of the same analytic conjecture, not independent evidence of algebraicity.

## 1. A smaller integral generator

Retain the previous field H=K(nu), where

    Phi(nu)=nu^3+beta^2 nu^2+2 beta nu+1=0.

Define

    v=-beta^2 nu-2nu^2.

Exact substitution gives

    g(v)=v^3-beta v^2+1=0,
    nu=beta v-2v^2.

The two substitutions are mutually inverse in their relative cubic fields. In particular H=K(v) and O_K[nu]=O_K[v]. Also

    disc(g)=4 beta^3-27=1,
    v^(-1)=beta v-v^2,
    N_(H/K)(v)=-1.

The preceding proof identified H as the Hilbert class field and proved O_H=O_K[nu]. Those conclusions therefore hold with v in place of nu. We do not infer the class-field theorem merely from the name of a polynomial.

An independent trace certificate on (1,v,v^2) is

    T=[3,beta,beta^2; beta,beta^2,4; beta^2,4,3 beta],
    T^(-1)=[5,beta^2,-3 beta; beta^2,2 beta,-5; -3 beta,-5,2 beta^2].

Both matrices are integral over O_K and their product is I. The discriminant is relative over K, not over Q.

## 2. Two fixed rational elliptic curves and the isogeny

Let

    E0: y^2+y=x^3,
    E1: Y^2+Y=X^3-7.

Their discriminants are -27 and -3^9, so they are nonsingular in characteristic zero. They both have j=0. Over Q(omega), omega^2+omega+1=0, the automorphism (x,y)->(omega x,y) gives the familiar complex multiplication action.

For x nonzero define

    phi(x,y)=(x+x^(-2), y-(2y+1)x^(-3)).             (2.1)

Direct substitution using y^2+y=x^3 proves that (2.1) lies on E1. At O, (0,0), and (0,-1), the rational map extends to O on E1. The pole orders of its X and Y coordinates are respectively two and three at these points. Thus it is a nonconstant morphism of smooth projective curves sending O to O, and hence an isogeny [Milne, II.1.5]. Its degree is three and

    ker(phi)={O,T,-T},  T=(0,0), -T=(0,-1).

The line y=0 has triple intersection with E0 at T; the chord-and-tangent law gives 3T=O. The kernel is rational over Q.

The normalized differential identity is exact:

    phi^*(dX/(2Y+1))=dx/(2y+1).                    (2.2)

Indeed dX/dx=(x^3-2)/x^3 and 2Y+1=(2y+1)(x^3-2)/x^3.

This is the standard rational three-isogeny in explicit coordinates, not a newly postulated transformation.

## 3. The full preimage of the actual point P=(beta,0)

Since beta^3=7, P=(beta,0) lies on E1(K).

Put

    q(v)=3 beta v^2-beta^2 v-5.

The exact identities in K[v]/(g) are

    q(v)(v^3-2)=1,
    q(v)^2+q(v)=v^3.

Thus Q=(v,q(v)) is an integral point of E0(H). Formula (2.1) gives

    phi_X(Q)=(v^3+1)/v^2=beta,
    phi_Y(Q)=(q(v)(v^3-2)-1)/v^3=0.

Consequently phi(Q)=P.

Conversely, every point above P has x nonzero and x satisfying g(x)=0. Its y coordinate must be 1/(x^3-2). The denominators cannot vanish at a root of g: x=0 contradicts its constant term, and x^3=2 together with g would imply beta x^2=3, hence 28=27 after cubing. There are exactly three points above P.

Since g is irreducible over K, adjoining any one such point gives exactly H. In particular

    H=K(Q),  and  phi^(-1)(P)={Q,Q+T,Q-T}.        (3.1)

This is a concrete torsor: a set of three points on which the three-element kernel acts freely and transitively. It is not the three-torsion subgroup itself.

## 4. Frobenius is actual torsion translation

In the new coordinate the original cubic automorphism is

    sigma(v)=-beta^2 v^2+2v+2 beta,
    sigma^2(v)=beta^2 v^2-3v-beta.

Direct reduction proves that these are the other roots of g and sigma^3=1.

Addition of T=(0,0) on E0 has formula

    (x,y)+T=(-y/x^2,-y/x^3).

It follows by direct substitution that

    sigma(Q)=Q+T.                                 (4.1)

Modulo b=(2,beta-1), the relative polynomial is V^3+V^2+1, irreducible over F2, and sigma(v) reduces to v^2. Because the preceding integral model is unramified, this identifies sigma with arithmetic Frobenius at b. Thus (4.1) is also an explicit class-field reciprocity action on the algebraic cubic fiber.

All this concerns H and Q already known to be algebraic. It is not an Artin action on an unproved algebraic gamma value.

## 5. The Jacobi sum is the isogeny descent value

Let omega^2+omega+1=0 and s=1+2omega. On E0 define

    Xi_geo(x,y)=(y+1+omega)/x.

There is a universal rational identity, not merely an identity on our chosen fiber:

    Xi_geo(x,y)^3=phi_Y(x,y)+2+3omega.              (5.1)

To see this, use y^2+y=x^3 and expand:

    (y+1+omega)^3=(y+2+3omega)x^3-2y-1.

Dividing by x^3 gives (5.1). At phi(Q)=P=(beta,0), it becomes

    Xi_geo(Q)^3=2+3omega.                          (5.2)

The rational kernel translation acts by

    Xi_geo(Q+T)=omega^2 Xi_geo(Q).                 (5.3)

This follows directly from the addition formula. Thus the cyclic field action has been diagonalized by an actual rational function on the elliptic curve.

The previous finite Gauss sum G=sum chi(a) zeta_7^a satisfied G^3=7(2+3omega), so Xi_old=G/beta had the same cube. With the previous conventions theta=zeta_7+zeta_7^(-1), nu=(theta-2)/beta, and the current v=-beta^2 nu-2nu^2, exact reduction gives

    Xi_geo(Q)=omega Xi_old.

The branch factor is stated, not hidden. In fact q(v)=-theta^2-theta+1 is one of the three real seventh-cyclotomic coordinates.

The quantity 2+3omega is therefore simultaneously a five-term Jacobi sum and the value of the cubic descent function at P. We are using a classical three-isogeny/Kummer mechanism in this explicit field.

## 6. Coherent multiplication, without the spurious determinant sector

If m is an integer, then

    phi([m]Q)=[m]P,
    sigma([m]Q)=[m]Q+[m]T.

For gcd(m,3)=1, the three Galois translates of [m]Q are distinct, so K([m]Q)=H. If 3 divides m, the point [m]Q is fixed by sigma and belongs to E0(K).

The dual isogeny is

    phi_hat(X,Y)=((X^3-27)/(9X^2),
                 (2Y+1)(X^3+54)/(54X^3)-1/2).

It satisfies phi_hat phi=[3]. In particular,

    [3]Q=phi_hat(P)=(-20/(9 beta^2), -64/189).

The symbolic script independently computes [3]Q by the group law and verifies these coordinates.

This geometric construction has an honest composition law and stays inside H. It does not introduce a new prime such as the 19 appearing in the previous unfiltered determinant-power test. This is NOT a proof that multiplying a point corresponds to replacing the cubic unit matrix M by M^m in the analytic gamma construction; that comparison has not been established.

## 7. The base point is not torsion

This is a useful limit on a tempting CM shortcut.

On E1 put R=(3 beta,13). In completed-square coordinates (x,Y=y+1/2), direct addition gives

    2R=P=(beta,0),
    x(3R)=57/(4 beta^2),
    Y(3R)=-405/56.

At the prime (beta) above 7, E1 has good reduction since its discriminant is -3^9. The displayed x coordinate has negative valuation, so 3R is a nonidentity point in the kernel of reduction. If it were torsion, its order would be a power of 7: prime-to-7 torsion injects under good reduction [Milne, II.4.2 and II.4.3].

At the norm-five prime (5,beta-3), E1 has good reduction over F5. Exact enumeration gives six points including O. Prime-to-5 torsion injects there, so E1(K) has no nontrivial 7-power torsion.

Thus 3R cannot be torsion. R has infinite order, and so does P=2R. Every Q above P also has infinite order.

We have divided a NON-TORSION algebraic point by an isogeny. The differences of the three choices are torsion, but the choices themselves are not. Consequently a theorem about values at CM torsion points does not directly establish our original gamma equality.

## 8. The exact remaining analytic test

Retain the original BCG analytic value

    U_Gamma=Gamma(1/3,tau,sigma)^5/Gamma(5/3,5tau,5sigma),
    beta=7^(1/3) exp(-2 pi i/3),
    tau=(beta^2+2beta)/15, sigma=-(beta+2)/15.

Let the inversion quotient be Y_Gamma=U_Gamma+U_Gamma^(-1). In the new coordinate the algebraic polynomial is

    Y(v)=A v^2+B v+C,
    A=4 beta^2+beta-14,
    B=11 beta-23,
    C=-beta^2+3beta-3.

The quadratic lift is

    Z(v)=(-2 beta^2+7 beta-8)v^2/3
          +(-10 beta^2+11 beta+17)v/3+7-beta-beta^2,
    U_alg=(Y(v)-(1+2omega)Z(v))/2.

These are exactly the earlier Y/Z formulas after the integral change of generator. The original sextic is checked again.

To avoid the extra-preimage issue in a previous polynomial inverse, define v_Gamma LOCALLY by the equation

    A v_Gamma^2+B v_Gamma+C=Y_Gamma,

on the branch through the chosen algebraic v. This local inverse exists: if 2Av+B vanished at v, then v would be in K, contradicting degree three. Next choose the branch of

    y_Gamma=(-1+sqrt(1+4v_Gamma^3))/2

through q(v), and put Q_Gamma=(v_Gamma,y_Gamma). This is an analytic point on E0 by construction, without assuming arithmetic membership.

The new exact target is

    phi(Q_Gamma)=P.                                  (8.1)

Its X residual is precisely

    phi_X(Q_Gamma)-beta
       =(v_Gamma^3-beta v_Gamma^2+1)/v_Gamma^2.       (8.2)

If (8.1) is proved with these branches, then v_Gamma belongs to the three-point algebraic fiber, hence H; the exact Y reconstruction gives the original reciprocal sextic for U_Gamma. Final local branch separation then selects U_alg rather than its reciprocal or other conjugates.

We have NOT proved (8.1). The numerical test is a reformulation of the same original conjecture, not independent proof. Nor does the mere existence of the isogeny force an arbitrary analytic Q_Gamma into its fiber over P.

The differential identity (2.2) gives a possible analytic route: compare the actual gamma-derived point with the elliptic logarithm of P, including periods and normalization. An identity between those analytic constructions is still missing. The point P is nontorsion, so calling the curve CM does not supply that identity.

## 9. Verification and failures

The exact script verifies the integral change of generator, trace dual, universal isogeny identities, actual kernel translations, Jacobi descent, original sextic, explicit multiples, and good-reduction data. It also exhaustively tests the group-homomorphism formula on all point pairs over each of F_p for p=2,5,7,11,13,17,19,23,29,31. The actual number of checks is recorded in exact_results.json.

The numerical script independently evaluates the original smoothed gamma through its convergent logarithmic series at 80 and 120 decimal digits. It then uses the local quadratic inverse and compares phi(Q_Gamma) with P. Wrong inverse branches and a 10^(-6) multiplicative perturbation are negative controls. These are high-precision regressions, not interval certificates.

One initial exploratory script had an unmatched parenthesis and failed before execution. Its source is retained under evidence. It was fixed before deriving the numerical/symbolic outputs. Both production scripts passed; accepted run logs and separate extraction replay are retained. No failed exploratory execution is counted as a successful test.

## Sources and trust boundary

1. J. S. Milne, Elliptic Curves (second edition), II.1.5 (morphisms preserving the origin are group homomorphisms), II.4.2-4.3 (torsion and reduction, including complete discretely valued fields), and the complex-analytic description of elliptic curves. https://www.jmilne.org/math/Books/EC2.pdf
2. SageMath, Isogenies reference documentation, mathematical definition and rational-map conventions. Sage is NOT installed or run in this package. https://doc.sagemath.org/html/en/reference/arithmetic_curves/sage/schemes/elliptic_curves/ell_curve_isogeny.html
3. Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields, arXiv:2311.04110v2, for the original analytic function, special parameters, proved modulus result, and conjectural algebraicity. https://arxiv.org/html/2311.04110v2
4. The preceding Komorebi H12 Unramified Cubic and Primitive Sector proof, for H/K, O_H, the class-number and ray-field identification. Its exact algebraic maps are rechecked here. The earlier gamma equality remains unproved in both packages.

No published theorem has been silently turned into a Lean proof term. No standalone finite computation certifies a general analytic statement. This package proves the stated ordinary arithmetic/isogeny statements and supplies reproducible tests, not a completed Hilbert-12 special-value proof.

<!-- END ORIGINAL FILE: PROOF(20261002-141429).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-154405).md -->
# Archive Part 7: `PROOF(20261002-154405).md`

# Komorebi H12: genuine seven-torsion and an exact CM theta target

## Status

This continuation proves that the Jacobi--Kummer coordinate already constructed
for the pure cubic example is the reciprocal x-coordinate of an actual point of
order SEVEN on E0: y^2+y=x^3. It also proves an explicitly normalized identity
between that coordinate, a classical Weierstrass/theta value at a CM torsion
point, and the finite Gauss sum. The sign choosing the branch is proved by a
convergent lattice estimate, not by fitting a decimal approximation.

The elliptic-gamma identity U_Gamma=U_alg is STILL UNPROVED. The classical CM
value on the right of the new comparison is algebraic by the proof below; the
original BCG gamma value has not been identified with it. These are ordinary
proofs using standard complex uniformization and theta formulas. They are not
Lean proofs, not an independent human review, and not claims of novelty for
classical complex multiplication, Gauss sums, or elliptic division theory.

The earlier point Q in the THREE-isogeny fiber is non-torsion. It is NOT the
seven-torsion point R in this note. Different points can describe the same
arithmetic coordinate field.

## 1. Fixed notation

omega=exp(2*pi*i/3), J=2+3*omega, Jbar=-1-3*omega, J*Jbar=7.

beta=7^(1/3)*omega^2 is the fixed complex cube root used in the BCG example.
The existing algebraic field is E=K(omega,Xi), K=Q(beta), Xi^3=J.
The preceding arithmetic note proved E is the degree-six ray class field of K
of modulus (3,beta-1)*infinity_R.

When fixing the Gauss branch in this note, zeta=exp(6*pi*i/7), not exp(2*pi*i/7).
The character is chi(0)=0 and

    a        1    2        3        4        5      6
    chi(a)   1   omega  omega^2  omega^2   omega    1.

Write G=sum_{a=1}^6 chi(a)*zeta^a and Xi_G=G/beta. Finite character summation
proves G^3=7J and Xi_G^3=J. The new exact script repeats that finite calculation.

## 2. The Kummer coordinate is a reciprocal seven-torsion coordinate

Use completed-square coordinates Y=y+1/2 on E0, so Y^2=x^3+1/4.
Let x be any nonzero solution of

    x^3=1/J,

and choose either Y with Y^2=x^3+1/4. The denominator Y is nonzero, since
J+4 is nonzero (its norm is 27).

The ordinary duplication formula is

    x([2]R)=x*(x^3-2)/(4*x^3+1),
    Y([2]R)=-Y+(3*x^2/(2*Y))*(x-x([2]R)).

Substitution of x^3=1/J, omega^2+omega+1=0 gives

    [2]R=(omega^2*x,Y)=[omega^2]R.                 (2.1)

Here [omega](x,Y)=(omega*x,Y) is the usual CM automorphism. Applying (2.1)
three times gives [8]R=R, hence [7]R=O. Since R is affine, it is nonzero and
has exact order seven. In particular

    Xi_G=1/x(R)                                    (2.2)

for an actual point R of order seven.

There is also a CM-kernel description. The identity

    2-omega^2=-omega*J

implies [J]R=O. Conversely nonzero points of this CM kernel satisfy (2.1),
and the duplication formula forces x^3=1/J. Conjugating gives the other
CM kernel, whose x-coordinates satisfy x^3=1/Jbar.

As a polynomial cross-check, the standard division-polynomial recurrences give

    psi_7(X)=(7X^6-X^3+1)
      *(X^18+141X^15-363X^12-1924X^9-741X^6-48X^3+1).

Its first factor is

    7X^6-X^3+1=7(X^3-1/J)(X^3-1/Jbar).            (2.3)

Thus the six x-coordinates in the two CM eigenspaces are recognized by a
small polynomial over Q. We do not assert that these six are all 24
x-coordinates of nonzero seven-torsion.

## 3. The ray field is the splitting field of that small division factor

Put x_plus=1/Xi_G and x_minus=Xi_G/beta. Then

    x_plus^3=1/J,   x_minus^3=1/Jbar,
    x_plus*x_minus=1/beta.

It follows that

    Q(omega,x_plus,x_minus)=Q(omega,beta,Xi_G)=E.   (3.1)

All other roots in each cubic group differ by powers of omega. Conversely,
the splitting field of (2.3) contains omega, since J=1/x_plus^3 and
omega=(J-2)/3, and it contains a cube root of 7 through 1/(x_plus*x_minus).
It therefore equals E. The field contains the chosen beta because it also
contains omega. Thus

    E is the splitting field over Q of 7X^6-X^3+1. (3.2)

Its degree is 18 over Q and 6 over the specified K, using the earlier exact
field identification. Over F0=Q(omega), its two cubic Kummer directions are
also seen to be independent from the valuations of J and Jbar.

IMPORTANT: (3.1) is an x-COORDINATE statement. A full point R need not lie in
E. In fact its completed-square ordinate requires

    (2Y)^2=1+4/J.

At a prime above J in E, J has valuation 3: K(omega)/Q(omega) is totally
ramified of degree three there, and the previously constructed Hilbert-class
extension is unramified. Since J+4 is a unit there, 1+4/J has valuation -3.
It is not a square in E. The full point therefore requires a quadratic
extension beyond E. No larger ramified torsion field is being identified with
the requested ray field.

## 4. An exact analytic evaluation at a CM seven-torsion point

Let Lambda0=Z+Z*omega and W(z)=wp(z;Lambda0).
Define

    Omega=exp(pi*i/6)*Gamma_Euler(1/3)^3/(2*pi).

The equianharmonic invariant formula [DLMF 23.5.8], with half-period 1/2,
gives g2(Lambda0)=0 and

    g3(Lambda0)=Gamma_Euler(1/3)^18/(2*pi)^6.

Consequently Lambda=Omega*Lambda0 has g2=0, g3=-1, and

    z mod Lambda -> (wp_Lambda(z), wp'_Lambda(z)/2-1/2)

uniformizes E0. [Milne, Chapter III; DLMF 23.3]

Take z_R=Omega/J. Because 7/J=Jbar belongs to Lambda0 while 1/J does not,
this is an actual nonzero seven-torsion point. Moreover

    2/J-omega^2/J=-omega belongs to Lambda0,

so its duplication is the CM action in (2.1). Therefore

    Xi_CM=Omega^2/W(1/J)

satisfies

    Xi_CM^3=J.                                    (4.1)

This is a proved analytic-to-algebraic evaluation for a CLASSICAL CM elliptic
function, not for the original elliptic gamma.

### A branch proof, rather than a numerical branch choice

We prove that both Xi_CM and Xi_G have negative imaginary part. Because J is
strictly in the first quadrant, its three cube roots have arguments in
(0,pi/6), (2pi/3,5pi/6), and (4pi/3,3pi/2). There is exactly one with
negative imaginary part.

For Xi_G, group opposite Gauss terms:

    G=t0+omega*t1+omega^2*t2,
    t0=2*cos(6*pi/7), t1=2*cos(2*pi/7), t2=2*cos(10*pi/7).

Since beta=7^(1/3)*omega^2,

    Im(Xi_G)=sqrt(3)/(2*7^(1/3))*(t0-t1)<0.

For Xi_CM, put u=1/J, so |u|^2=1/7. On Lambda0 the sixth-root rotations
annihilate every lattice sum G_m except when 6 divides m. The normally
convergent Laurent series [DLMF 23.9] gives

    W(u)-u^(-2)=sum_{k>=1}(6k-1)*G_(6k)*u^(6k-2).

Every nonzero lattice vector has length at least one. The hexagonal shell
max(|a|,|b|,|a-b|)=n contains 6n vectors, each of squared length at least
3n^2/4. Hence

    sum_{lambda!=0}|lambda|^(-6)
      <=(128/9)*sum_{n>=1}n^(-5)<=160/9.

It follows that

    |W(1/J)-J^2|
      <=(160/9)*(1/49)*(5+1/343)/(1-1/343)^2
      =160160/87723 < 2.                           (4.2)

But

    Im(exp(-pi*i/3)*J^2)=4*sqrt(3).

Thus exp(-pi*i/3)*W(1/J) has strictly positive imaginary part. Since
Omega^2 is a positive real multiple of exp(pi*i/3), its reciprocal ratio
Xi_CM has negative imaginary part. We have proved the EXACT branch identity

    Omega^2 / W(1/(2+3omega))
      = (1/beta)*sum_{a=1}^6 chi(a)*exp(6*pi*i*a/7).
                                                        (4.3)

The lattice estimate is a universal analytic bound. The floating-point
calculation is not used to select the branch in (4.3).

### The evaluation can be written entirely with classical theta functions

With q_CM=exp(pi*i*omega), DLMF 23.6.14 gives

    W(u)=pi^2*[ theta1'''(0)/(3 theta1'(0))
                -theta1''(pi*u)/theta1(pi*u)
                +(theta1'(pi*u)/theta1(pi*u))^2 ].        (4.4)

All theta functions in (4.4) have nome q_CM. This is the formula used in the
independent numerical evaluator. Euler Gamma in Omega is not the elliptic
gamma function on the other side of the outstanding conjecture.

## 5. The exact algebraic target reconstructed from this CM value

For a nonzero scalar X define successively

    nu(X)=(X+beta/X-beta^2)/3,
    v(X)=-beta^2*nu(X)-2*nu(X)^2,
    Y(v)=(4beta^2+beta-14)v^2+(11beta-23)v-beta^2+3beta-3,
    Z(v)=((-2beta^2+7beta-8)v^2+(-10beta^2+11beta+17)v)/3
          +7-beta-beta^2,
    R_beta,omega(X)=[Y(v(X))-(1+2omega)Z(v(X))]/2.

On X^3=J these reproduce the original integral cubic, the three-isogeny
fiber, and the reciprocal sextic from the preceding notes. Hence (4.3)
proves, with the same branch throughout,

    U_alg=R_beta,omega( Omega^2/W(1/J) ).            (5.1)

The unresolved gamma equation can now be written as the concrete identity

    Gamma_ell(1/3;tau,sigma)^5 / Gamma_ell(5/3;5tau,5sigma)
       ?= R_beta,omega( Omega^2/W(1/J) ),           (5.2)

where beta, tau=(beta^2+2beta)/15, and sigma=-(beta+2)/15 are unchanged.

The right side of (5.2) is rigorously evaluated and algebraic. The equality
of its LEFT side to its right side has not been proved. This is a more
explicit comparison target, not a discharge of the BCG conjecture.

## 6. Which arithmetic operation corresponds to elliptic doubling?

Let b=(2,beta-1) and c=(2,beta^2+beta+1), so Norm(c)=4. On the cyclotomic
presentation, arithmetic Frobenius at c fixes omega and beta and sends
zeta -> zeta^4. Since chi(4)=omega^2,

    Frob_c(G)=omega*G,
    Frob_c(Xi_G)=omega*Xi_G,
    Frob_c(x_plus)=omega^2*x_plus.                 (6.1)

At the x-coordinate level, (6.1) is exactly elliptic doubling on the
J-kernel. The inverse ideal c^(-1), which appeared in the distinguished
rank-three Hecke superlattice, corresponds instead to x -> omega*x,
which is the x-coordinate of multiplication by 4. This records the
orientation; inverse Frobenius is not silently replaced by Frobenius.

We do not assert a Frobenius formula for the full R without specifying the
larger ordinate field. Nor is any Galois action on an unproved algebraic
gamma value being assumed.

### Literal doubling of the gamma ARGUMENT is a different operation

At the admissible thirds, the exact smoothed inversion law gives
F(2/3)=F(1/3)^(-1). Its inversion quotient F+F^(-1) is unchanged. Therefore
the local inverse used to obtain v_Gamma and y_Gamma from that quotient is
unchanged as well, when the same local branches are used.

The new gamma-derived coordinate is

    x_Gamma=omega*v_Gamma/(y_Gamma+1+omega).

It is thus unchanged by this literal argument doubling. It is not sent to
omega^2*x_Gamma. A norm-four IDEAL correspondence, not the argument change
1/3 -> 2/3, is the relevant candidate for (6.1).

The tests detect the wrong identification with a discrepancy approximately
1.2523074206; it is not a hidden high-precision agreement.

## 7. Why a global unbranched elliptic lift cannot supply the proof

Write t=-tau, with Im(t),Im(sigma)>0. The negative-period rule is

    F(z)=Gamma_ell(5z+5t;5t,5sigma)/Gamma_ell(z+t;t,sigma)^5.

At z_star=tau+1/5=-t+1/5, the numerator has a simple pole (argument 1),
while Gamma_ell(1/5;t,sigma) in the denominator is finite and nonzero.
The defining convergent product proves this directly. Thus F has a simple
pole at z_star, and so does F+F^(-1).

If a single-valued meromorphic v(z) satisfied

    A v(z)^2+B v(z)+C=F(z)+F(z)^(-1),
    A=4beta^2+beta-14 != 0,

on a punctured neighborhood extending meromorphically across z_star,
then any pole on the left would have EVEN order. The right has order one.
This is impossible. In the full elliptic curve, x has pole order two at O,
so A x^2+B x+C has pole order four. A lift through E0 requires ramification
of degree divisible by four at such a pole.

This rules out the naive idea that the entire gamma function defines the
single-valued elliptic map used in the local coordinate construction. A
special-value identity or an explicitly branched/corrected construction is
still possible. The local inverse in the previous note is not invalidated.

A second elementary restriction: any GL3(Q) change of the original three
periods gives ratios in K. It cannot produce the CM modulus omega, since
K is cubic and contains no quadratic subfield. Thus merely rebasing the
rank-three periods cannot prove (5.2).

## 8. Numerical tests and their scope

The classical target is evaluated from theta functions at omega via (4.4)
and the ordinary Euler Gamma period. It is NOT evaluated by taking a cube
root of J and substituting it into the purported theta answer.

The finite Gauss sum is evaluated separately. The BCG elliptic gamma is
evaluated independently using its convergent smoothed logarithmic series
with the negative-period convention retained. The numerical tests run at
70 and 110 decimal digits. They check all six nonzero points in the CM
kernel, doubling, the Gauss/CM identity, reconstruction of U_alg, and the
open gamma equality as a numerical regression only. Wrong torsion branches
and literal argument doubling are negative controls.

At 110 digits the gamma-versus-CM reconstructed unit discrepancy is about
3.08e-107. This is not an additional independent proof or an interval
certificate. The small residual reflects the same original conjecture.

The simple-pole test is evaluated through the exact theta difference law.
It checks that (z-z_star)F(z) tends to the explicitly nonzero residue. The
pole-order theorem itself follows from the product and is not numerical.

## 9. Verification, failures, and trust boundary

exact_checks.py has 211 named exact checks in the accepted run. These INCLUDE
108 assertions on 36 finite-field seven-torsion points, as well as finite
character multiplication and symbolic arithmetic tests. The finite points
occur for primes 61,67,79,163,181,199 in the declared search of split primes
below 200. The universal order-seven result is proved by (2.1), not by these
finite checks. The shell tests cover shells 1--15; the proof of the infinite
lattice bound is the shell argument and integral bound in section 4.

numerical_checks.py has 33 assertions at each of two precisions, together
with the pole probes and wrong-branch controls. Both production scripts
passed their first executed versions. The numerical script was subsequently
extended to include the argument-doubling control and passed again. No
failed production run is omitted. A separate source-ZIP extraction replay
is recorded in the release receipt.

No Lean verification, new rigorous interval certificate, independent human
review, or general proof of the gamma conjecture is asserted. A successful
source replay authenticates these computations, not the unproved identity.

## Sources and inherited results

1. J. S. Milne, Elliptic Curves, second edition, Chapter III: complex
   uniformization, addition, torsion, and complex multiplication.
   https://www.jmilne.org/math/Books/EC2.pdf
2. NIST DLMF 23.5.8: equianharmonic period normalization.
   https://dlmf.nist.gov/23.5#E8
3. NIST DLMF 23.6.14: Weierstrass function from theta derivatives.
   https://dlmf.nist.gov/23.6#E14
4. NIST DLMF 23.2 and 23.9: lattice definition and Laurent series.
   https://dlmf.nist.gov/23.2
   https://dlmf.nist.gov/23.9
5. Bergeron--Charollois--Garcia, Elliptic units for complex cubic fields,
   arXiv:2311.04110v2: the original analytic example, gamma definition and
   sign continuation, inversion, and conjectural arithmetic interpretation.
   https://arxiv.org/html/2311.04110v2
6. The attached preceding Komorebi proofs: Jacobi--Kummer algebra, exact
   ray-field identification, and the non-torsion three-isogeny fiber. Their
   archive hashes are recorded in PREDECESSORS.json. These supply the
   arithmetic names used in section 3; the new torsion identities are checked
   directly on the fixed rational curve.

<!-- END ORIGINAL FILE: PROOF(20261002-154405).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-162814).md -->
# Archive Part 8: `PROOF(20261002-162814).md`

# Komorebi H12: norm-five descent, a degree-36 abelian radical, and new smoothing tests

## Status

We work only with the pure cubic example K=Q(beta), beta^3=7. The original elliptic-gamma equality remains UNPROVED. The Stark logarithmic formula also remains UNPROVED.

This note constructs an explicit algebraic unit W in the previously identified ray field E/K. It proves W^5/sigma(W)=U_alg^6, and proves that E(W^(1/6))/K is abelian of degree 36, with group C18 x C2. It derives additional algebraic smoothing values and tests them against independently computed norm-11 and norm-19 elliptic-gamma expressions. The numerical agreements do not prove those analytic identities.

The algebraic proofs use exact rational polynomial identities, irreducible reduction at one explicitly specified prime, and elementary Galois theory. They are not Lean proofs or independent human review. No priority or novelty claim is made for the classical Stark/Kummer mechanisms.

## 1. Fixed field, coordinate, and automorphism

Let omega^2+omega+1=0 and beta^3=7. Retain

    v^3-beta*v^2+1=0,
    E=Q(beta,v,omega).

The preceding arithmetic construction identified E with the degree-six ray class field of K of modulus f*infinity_R, f=(3,beta-1). It proved [E:Q]=18, and O_H=O_K[v] for H=K(v).

The generator sigma of Gal(E/K) is

    sigma(beta)=beta,
    sigma(v)=-beta^2*v^2+2*v+2*beta,
    sigma(omega)=omega^2.

Its cube fixes beta,v and conjugates omega. We denote this involution by iota.

The original algebraic candidate is

    Y=(4beta^2+beta-14)v^2+(11beta-23)v-beta^2+3beta-3,
    Z=[(-2beta^2+7beta-8)v^2+(-10beta^2+11beta+17)v]/3
       +7-beta-beta^2,
    U=(Y-(1+2omega)Z)/2.

The previous proof and the new script verify Y^2-4=-3Z^2, so iota(U)=U^(-1). The original reciprocal sextic and the fixed CM-theta branch are unchanged.

## 2. An explicit algebraic unit before norm-five smoothing

Define

    A=(21beta-42)v^2+(-15beta^2+30beta)v-beta^2-4beta+11,
    B=3beta^2*v^2+(18beta-42)v-11beta^2+13beta+7,
    W=(A+omega B)/3.                                      (2.1)

Exact reduction in

    Q[b,v,w]/(b^3-7, v^3-bv^2+1, w^2+w+1)

proves

    A^2-AB+B^2=9,
    W*iota(W)=1,
    W^5 = sigma(W)*U^6.                                   (2.2)

Thus W is a pre-smoothing algebraic unit, in the precise sense

    W^(5-sigma)=U^6.                                      (2.3)

Its polynomial over K is

    T^6+(5beta^2+14beta-43)T^5
    +(-beta^2-133beta+260)T^4
    +(-894beta^2+1470beta+461)T^3
    +(-beta^2-133beta+260)T^2
    +(5beta^2+14beta-43)T+1.                              (2.4)

The script evaluates (2.4) by exact Horner reduction. Monicity and the constant term 1 prove that W and its inverse are algebraic integers. Neither sigma^2 nor sigma^3 fixes W, so its orbit has six elements and (2.4) is irreducible over K. In particular K(W)=E.

For the retained complex branch,

    W ~= 58.71527576075526028673865
          +5.862763937852255698247237 i.

This decimal is not used to prove (2.2).

At a real embedding of K, v and its three conjugates are real. Conjugating omega therefore acts as ordinary complex conjugation. Since W*iota(W)=1, every embedding of W above the real place has absolute value one. W is a unit at all finite places.

### What (2.3) means, and what it does not mean

BCG's conjectural gamma/Stark relation has the shape

    u_Stark^(N(a)-sigma_a) = u_gamma^(e_f),

where e_f is the number of roots of unity in the ray field. In this example e_f=6, and the norm-five ideal has sigma_a=sigma. Equation (2.3) establishes the ALGEBRAIC shape for our explicit W and U.

It does not prove that W satisfies the exact partial-zeta logarithmic formula, or that the analytic gamma is U. We call W an algebraic Stark-type candidate, not a proved Stark special-value unit.

## 3. Roots of unity and the ambiguity of W

The preceding Gauss construction gives E=Q(omega,Xi,BetaXi), where it is more convenient here to set

    A0=Xi, B0=beta/Xi,
    A0^3=J=2+3omega, B0^3=Jbar=-1-3omega, A0 B0=beta.

The valuations at the distinct primes J,Jbar show these two cubic Kummer directions are independent over Q(omega). Their Galois group is C3 x C3. The involution fixing beta sends A0 to B0, B0 to A0, and omega to omega^2. On the exponent group it acts by (a,b)->(-b,-a).

Its commutator subgroup is the diagonal C3. The fixed field is

    Q(omega,theta), theta=zeta_7+zeta_7^(-1),

as can also be seen from the invariant A0^2 B0=beta Xi and Fourier inversion. Thus this is the largest subfield of E abelian over Q.

Every cyclotomic subfield of E lies there. This degree-six field lies in Q(zeta_21), whose roots of unity have order dividing 42. It does not contain zeta_7: its unique quadratic subfield is Q(omega), whereas Q(zeta_7) has quadratic subfield Q(sqrt(-7)). Therefore

    mu(E)=mu_6.                                          (3.1)

The standard cyclotomic facts in this paragraph can equivalently be checked by the conductors 3 and 7 and the Galois subgroups of Q(zeta_21).

If W' in E satisfies (W')^(5-sigma)=U^6, put d=W'/W. Then sigma(d)=d^5. Applying sigma six times gives d^(5^6-1)=1. By (3.1), d lies in mu_6. Conversely sigma(zeta)=zeta^5 for zeta in mu_6, so every zeta W has the same smoothing. Hence the algebraic solutions are exactly

    {zeta W : zeta in mu_6}.                              (3.2)

This argument depends on d belonging to E. It cannot be applied to a gamma value not yet known to be algebraic.

## 4. The sixth-root extension is genuinely abelian

Choose t with t^6=W and write M=E(t). We first establish that this binomial is irreducible over E, rather than assuming its degree.

There is a degree-one residue map at 181 specified by

    beta -> 32, v -> 99, omega -> 48.

All three defining equations hold modulo 181, and W maps to 23. The defining integral order has discriminant supported only at 3 and 7: the v-discriminant is 1 relative to K, and adjoining omega contributes only 3. It is therefore maximal locally at 181. This residue map corresponds to a prime of E with residue field F_181.

Now

    23^90 = -1 mod 181,
    23^60 = 132 != 1 mod 181.

Thus 23 is neither a square nor a cube in F_181. The binomial T^6-23 is irreducible there (the script also checks its irreducibility directly). Monic irreducible reduction proves T^6-W irreducible over E. Consequently

    [M:E]=6, [M:K]=36.                                   (4.1)

Put c=-omega^2, a primitive sixth root of unity. The Kummer kernel is generated by

    tau(t)=c t, tau|E=id.

Equation (2.2) lets sigma lift explicitly:

    rho|E=sigma,
    rho(t)=t^5/U.                                        (4.2)

Indeed (t^5/U)^6=W^5/U^6=sigma(W). Irreducibility makes this a field embedding, and its image is M. These statements prove M/K is Galois.

The lifts commute with the Kummer kernel:

    rho(tau(t))=sigma(c)t^5/U=c^5 t^5/U,
    tau(rho(t))=c^5 t^5/U.

They agree on E as well. Since rho and tau generate the Galois group, the extension is ABELIAN.

To identify its group exactly, the script proves the additional identity

    W^21 = c U^25 sigma(U)^5 sigma^2(U).                  (4.3)

Hence

    rho^3(t)=c/t,
    rho^6(t)=c^4 t,
    rho^6=tau^4.

Together with tau^6=1 and commutation, this gives the presentation

    <tau,rho | [tau,rho]=1, tau^6=1, rho^6=tau^4>.

Its relation matrix has Smith invariants 2,18. The group has order 36 by (4.1), so

    Gal(M/K) = C2 x C18.                                 (4.4)

This proves the abelian-radical condition expected of a Stark candidate. It does not prove the logarithmic formula. The conductor of M/K is not computed in this note, and M is not identified with the original degree-six ray field E.

Also, rho is a specified lift of sigma. We do not claim it is the arithmetic Frobenius of a specified prime in M without an additional residue calculation.

## 5. Norm five is not multiplication by five on one CM kernel

Retain the two seven-torsion x-coordinate directions

    x_plus=1/Xi, x_minus=Xi/beta.

The norm-five Artin automorphism acts by

    sigma(omega)=omega^2,
    sigma(Xi)=omega beta/Xi,
    sigma(x_plus)=omega^2 x_minus.                       (5.1)

So it exchanges the two conjugate CM kernels.

On a point R of order seven in the J-kernel, ordinary multiplication by five is multiplication by -2. Thus

    x([5]R)=x([2]R)=omega^2 x_plus,                       (5.2)

which differs from (5.1). The cubes already distinguish them: x_plus^3=1/J and x_minus^3=1/Jbar.

There is also no degree-five CM ENDOMORPHISM of this fixed curve. Its endomorphism degree is the Eisenstein norm

    a^2-ab+b^2 = 0 or 1 modulo 3,

whereas 5 is 2 modulo 3. The scalar map [5] has degree 25. This does not rule out five-isogenies to different curves; it rules out the particular proposed same-curve identification.

The correct norm-five operation on our two-coordinate packet is the explicit semilinear Artin action (5.1).

## 6. Algebraic smoothing at two new primes

The degree-one primes of norm 11 have Frobenius sigma^5, and the degree-one primes of norm 19 have Frobenius sigma^4. These assertions are checked on the actual reductions of v and omega:

    norm 5:  beta=3, sigma,
    norm 11: beta=6, sigma^5,
    norm 19: beta=4,6,9, sigma^4.

The relative cubics at these degree-one primes are irreducible, and their p-th power maps equal the stated formulas.

Define WITHOUT TAKING NEW ROOTS

    U11 = W^6/[U^5 sigma(U)],
    U19 = W^4/U.                                        (6.1)

Using iota(W)=W^(-1) and (2.3), one obtains

    U11^6 = W^(11-sigma^5),
    U19^6 = W^(19-sigma^4).                             (6.2)

For example sigma^4(W)=sigma(W)^(-1), so

    W^(19-sigma^4)=W^19 sigma(W)=W^24/U^6=(W^4/U)^6.

Both are algebraic units. They also satisfy

    U U19 = W^4.                                       (6.3)

Changing W by zeta in mu_6 does not change U11, but multiplies U19 by zeta^4. Thus the residual cube-root phase for the norm-19 SIXTH ROOT is explicit. Equations (6.2), not a silent normalization of every sixth root, are the invariant assertions.

For our chosen branch the values are approximately

    U11=-305.6421213100186165 -1130.369118304654039 i,
    U19=-136686.6685612096862 +253854.2682303568543 i.

## 7. Explicit gamma expressions for the new smoothing tests

For a prime N not dividing 21 and r satisfying

    r^3=7 mod N, r=1 mod 3,

define

    tau_(N,r)=[beta^2+2beta-r(r+2)]/(3N),
    sigma_(N,r)=(r-beta)/(3N),
    G_(N,r)=Gamma_ell(1/3;tau_(N,r),sigma_(N,r))^N
              /Gamma_ell(N/3;N tau_(N,r),N sigma_(N,r)).   (7.1)

In particular (N,r)=(5,-2) is the exact original BCG value.

These parameters have an explicit BCG admissible-lattice interpretation. Put

    a_N=(N,beta-r), (N)=a_N c_N,
    L_N=f c_N^(-1)=a_N f/N.

A basis of a_N f is

    beta(beta-r), r-beta, 3N.

Membership follows from the residues at f and a_N, and the determinant is 3N, the ideal norm. Dividing by N gives a basis of L_N. Its rational intersection is exactly 3Z. The choice lambda=3, h=lambda/3=1 is admissible: lambda/N=3/N belongs to a_N^(-1)L_N=f/N and is nonzero in its quotient by L_N, which has prime order N.

In this basis the unit epsilon=2-beta has the integral determinant-one matrix

    [r+2,                    1, 0;
     -r^2,                   2, 3N;
     (r^3-7)/(3N),           0, 2-r].                    (7.2)

The primitive dual forms

    a=(-(r+2),-1,0), b=(-1,0,0)

satisfy b=epsilon*a. With the orientation induced by the chosen complex embedding, their primitive kernel direction is +3. Their positive duals have period ratios -sigma_(N,r), -tau_(N,r). The finite face quotient is a singleton.

BCG's geometric gamma is consequently 1/Gamma_ell(-z;tau_(N,r),sigma_(N,r)), with z=w/3, using the standard sign continuation and reflection identity. Its smoothed special value at h=1 is G_(N,r) evaluated at -1/3 instead of +1/3. BCG's exact inversion relation for N coprime to 6 identifies this with G_(N,r)^(-1).

Keeping this inversion matters for the ray class label. If sigma indexes the class of the norm-two prime, then the rational ideal (N) has class 1 for N=1 mod 3 and sigma^3 for N=-1 mod 3. Thus c_N has class (N)/a_N. The raw expressions (7.1) carry the inversion-shifted labels

    (5,-2): index 5,
    (11,-5): index 1,
    (19,4),(19,25),(19,-29): index 5.

The norm-11 raw value therefore compares to sigma^2(U11), whereas the norm-19 raw values compare to U19, up to the explicit possible sixth-root phases. These are assignments of the source's geometric data, not a proof of its conjectural Artin action on gamma values.

### Numerical results, with the phases exposed

Independent gamma series and classical CM theta evaluation give at both 90 and 130 decimal digits

    G_(5,-2)       ~= U,
    G_(11,-5)      ~= (-omega) sigma^2(U11),
    G_(19,4)       ~= U19,
    G_(19,25)      ~= (-omega) U19,
    G_(19,-29)     ~= -U19.                              (7.3)

The three last lines test three different prime ideals of norm 19. Their SIXTH POWERS agree numerically, but their raw phases differ. We do not erase those differences.

At 130 digits the relative errors in (7.3) are, respectively,

    2.08e-129, 1.48e-129, 9.83e-129, 1.80e-127, 2.78e-127.

A control at N=19,r=1, which does not solve r^3=7 mod 19, is nowhere close to any predicted conjugate and sixth-root phase. These are numerical regressions, not proofs of (7.3).

The exact algebraic W was found from the original U before these additional gamma tests. No norm-11 or norm-19 gamma value was used to fit its coefficients. The phase alignments in (7.3) are observations, not independently proved normalizations.

## 8. A conditional two-smoothing rigidity theorem

There is a useful finite theorem for future comparisons. On a six-packet with shift T, suppose the multiplicative discrepancy d has inversion

    T^3 d=d^(-1).

If its norm-five smoothing is trivial, then T d=d^5 and hence d^126=1. This does NOT force d^6=1: a primitive seventh root with successive components d^(5^j) is a counterexample.

If the norm-nineteen smoothing is also trivial, then

    T^4 d=d^19,
    T^4 d=(T d)^(-1)=d^(-5).

Thus d^24=1, and gcd(126,24)=6 gives

    d^6=1.                                             (8.1)

The integral operator identity behind this is

    (20+5T+T^2)(5-T)-5(19-T^4)=6 mod (T^3+1).            (8.2)

Conversely every mu_6-valued packet d_j=d_0^(5^j) passes both tests. Thus mu_6 is the exact residual kernel, not merely an upper bound.

This is conditional on TWO ACTUAL smoothed comparisons. We have not proved them for the analytic gamma packet. A numerical comparison alone cannot activate this theorem.

## 9. What remains

We now have three additional exact arithmetic facts:

1. The original candidate is the norm-five smoothing of an explicit algebraic W, in the sixth-power sense W^(5-sigma)=U^6.
2. Adjoining a sixth root of W yields a genuinely abelian degree-36 extension of K.
3. The same W gives exact norm-11 and norm-19 algebraic smoothing values, with correctly labeled numerical gamma tests.

The missing claims remain:

    original G_(5,-2)=U,
    exact Stark partial-zeta logarithmic formula for W,
    exact identities and root phases for the additional G_(N,r).

The new computations do not prove the first claim by proving the algebraic radical is abelian. They also do not turn a high-precision residual into zero. They expose a coherent multi-smoothing arithmetic target and a finite residual criterion that a future analytic comparison could use.

## 10. Verification and failures

The production exact script uses no LLL or numerical recognition. It rechecks the proposed coefficients entirely over Q and the indicated finite polynomial quotients. The accepted run has 114 exact assertions.

The numerical script uses ordinary classical theta functions to construct Xi_CM independently, then algebraically reconstructs W and its conjugates. It separately computes all five gamma expressions by the convergent smoothed logarithmic series. It has 36 numerical equality assertions at each of 90 and 130 digits, plus two negative controls. These runs are not rigorous interval certificates.

The exploratory discovery search initially encountered two SymPy LLL assertion failures with large rational data. An assertions-disabled trial found no usable candidate and is not verification. Replacing the exploratory rational floor conversion by exact integer quotient allowed the search to find the displayed coefficients. A longer 126-branch exploratory search was interrupted after branch 31; it found candidates at branches 1 and 22 before interruption. This is not a completed exhaustive search. A subsequent symbolic draft had an unmatched parenthesis and was corrected before its mathematical checks ran. An unsupported streaming invocation and a follow-up missing-file invocation also produced no result.

These exploratory failures are recorded; none is counted as a successful scientific test. Both production scripts passed, then passed again from a separate ZIP extraction. There is no Lean certificate, new interval certificate, or independent human review.

## Sources

- Bergeron, Charollois, Garcia, Elliptic units for complex cubic fields, arXiv:2311.04110v2, definitions 2.2-2.3, smoothing (2.13), inversion (4.32), relation to Stark (3.5), and the pure cubic example in 5.2. https://arxiv.org/html/2311.04110v2
- The retained Komorebi H12 proof of the integral cubic and the ray field, for the arithmetic definition of E. Its archive hash is recorded in PREDECESSORS.json.
- The retained seven-torsion/CM-theta proof, for Xi_CM and the original candidate U. Its archive hash is also recorded. No new gamma theorem is imported from it.
- Classical finite Kummer theory and the standard facts that monic irreducible reduction proves field irreducibility, and cyclotomic fields are abelian over Q. The field and automorphisms used here are explicit, so the degree-36 abelian conclusion is proved rather than supplied by a Stark conjecture.

<!-- END ORIGINAL FILE: PROOF(20261002-162814).md -->

---

<!-- BEGIN ORIGINAL FILE: PROOF(20261002-POLYPHASE_TRANSPORT).md -->
# Archive Part 9: `PROOF(20261002-POLYPHASE_TRANSPORT).md`

# Komorebi H12 continuation — exact Hecke/polyphase transport

**Date:** 2026-10-02

## Status

This note sharpens the current analytic strategy for the pure cubic example
\(K=\mathbf Q(\beta)\), \(\beta^3=7\).

It proves exact lattice-transport identities behind the three BCG elliptic-gamma
parameter pairs, proves that the transported lattices remain stable under the
same cubic unit, derives a finite-grid distribution identity for the smoothed
elliptic gamma, and computes the resulting finite unit-orbit structures.

It does **not** yet prove the elliptic-gamma value algebraic. The final
fixed-point/orbit cancellation theorem is still missing.

---

## 1. Base data

Use
\[
\tau=\frac{\beta^2+2\beta}{15},\qquad
\sigma=-\frac{\beta+2}{15}.
\]

The arithmetic lattice basis is
\[
B_0=(\beta^2+2\beta,\;-(\beta+2),\;15).
\]

Multiplication by
\[
\epsilon=2-\beta
\]
has matrix
\[
M=
\begin{pmatrix}
0&1&0\\
-4&2&15\\
-1&0&4
\end{pmatrix},
\qquad
\det M=1.
\]

Its characteristic/determinant polynomial is
\[
h(X)=\det(I-XM)=1-6X+12X^2-X^3.
\]

---

## 2. The two additional BCG period pairs are exact Hecke refinements

The two additional period pairs can be rewritten exactly as
\[
(\tau_{10},\sigma_{10})
=
\left(
\frac{\tau+1}{10},
\frac{\sigma+3}{10}
\right)
\]
and
\[
(\tau_{23},\sigma_{23})
=
\left(
\frac{\tau+5}{23},
\frac{\sigma-2}{23}
\right).
\]

Equivalently, with
\[
A_{10}=
\begin{pmatrix}
1&0&0\\
0&1&0\\
1&3&10
\end{pmatrix},
\qquad
A_{23}=
\begin{pmatrix}
1&0&0\\
0&1&0\\
5&-2&23
\end{pmatrix},
\]
we have
\[
(\tau,\sigma,1)A_{10}
=
10(\tau_{10},\sigma_{10},1),
\]
\[
(\tau,\sigma,1)A_{23}
=
23(\tau_{23},\sigma_{23},1).
\]

Their determinants are
\[
\det A_{10}=10,\qquad
\det A_{23}=23.
\]

Thus the other two BCG evaluations are attached to explicit index-10 and
index-23 sublattices of the original rank-three arithmetic lattice.

---

## 3. The cubic unit preserves both transported lattices

Conjugating the original unit matrix gives
\[
M_{10}=A_{10}^{-1}MA_{10}
=
\begin{pmatrix}
0&1&0\\
11&47&150\\
-3&-13&-41
\end{pmatrix},
\]
and
\[
M_{23}=A_{23}^{-1}MA_{23}
=
\begin{pmatrix}
0&1&0\\
71&-28&345\\
7&-3&34
\end{pmatrix}.
\]

Both are integral determinant-one matrices and both have the same
characteristic polynomial
\[
\lambda^3-6\lambda^2+12\lambda-1.
\]

Therefore the index-10 and index-23 lattices are genuinely stable under the
same arithmetic unit. They are not arbitrary analytic reparameterizations.

The conductor-three point remains unit-fixed. With
\[
v_0=(0,0,1/3)^T,
\]
one has
\[
(M_{10}-I)v_0=(0,50,-14)^T\in\mathbf Z^3,
\]
\[
(M_{23}-I)v_0=(0,115,11)^T\in\mathbf Z^3.
\]

So all three BCG values are built from the same type of unit-fixed
conductor-three arithmetic datum.

---

## 4. Exact finite-grid distribution identity

Write \(t=-\tau\), so \(t,\sigma\) are in the upper half-plane, and define
\[
F_{t,\sigma}(z)
=
\frac{\Gamma_{\rm ell}(z;-t,\sigma)^5}
     {\Gamma_{\rm ell}(5z;-5t,5\sigma)}.
\]

Its convergent logarithm in a fundamental strip is
\[
L_{t,\sigma}(z)
=
-5\sum_{\substack{m\ge1\\5\nmid m}}
\frac{
e^{2\pi i m(z+t)}
-
e^{2\pi i m(\sigma-z)}
}
{m(1-e^{2\pi i mt})(1-e^{2\pi i m\sigma})}.
\]

Suppose
\[
t'=\frac{t-a}{n},
\qquad
\sigma'=\frac{\sigma+b}{n},
\]
with \(a,b\in\mathbf Z\). Then
\[
e^{2\pi i n t'}=e^{2\pi i t},
\qquad
e^{2\pi i n\sigma'}=e^{2\pi i\sigma}.
\]

Using
\[
\frac1{1-P}
=
\frac{1+P+\cdots+P^{n-1}}{1-P^n}
\]
twice in every summand gives the exact logarithmic identity
\[
L_{t',\sigma'}(z)
=
\sum_{u=1-n}^{0}\sum_{v=0}^{n-1}
L_{t,\sigma}(z+ut'+v\sigma').
\]

Exponentiating in the common convergence domain, and then continuing
meromorphically, yields the branch-free product identity
\[
\boxed{
F_{t',\sigma'}(z)
=
\prod_{u=1-n}^{0}\prod_{v=0}^{n-1}
F_{t,\sigma}(z+ut'+v\sigma').
}
\]

This is the exact polyphase/distribution formula needed to place all three
BCG values inside one base analytic realization.

For the two transported values:
\[
t_{10}=\frac{t-1}{10},
\qquad
\sigma_{10}=\frac{\sigma+3}{10},
\]
and
\[
t_{23}=\frac{t-5}{23},
\qquad
\sigma_{23}=\frac{\sigma-2}{23}.
\]

Hence the other BCG values are finite products over respectively \(100\)
and \(529\) translated copies of the original smoothed function.

A direct numerical test of the logarithmic identity in an independent
artificial convergence domain agrees to approximately \(2.2\times10^{-16}\)
at ordinary finite truncation. The identity itself is the algebraic
geometric-series derivation above, not the numerical test.

---

## 5. The polyphase grids are unit invariant

For the convergent \(t=-\tau\) convention, switch the first basis sign:
\[
\widetilde M
=
\operatorname{diag}(-1,1,1)\,
M\,
\operatorname{diag}(-1,1,1)
=
\begin{pmatrix}
0&-1&0\\
4&2&15\\
1&0&4
\end{pmatrix}.
\]

The two transport matrices become
\[
\widetilde A_{10}
=
\begin{pmatrix}
1&0&0\\
0&1&0\\
-1&3&10
\end{pmatrix},
\qquad
\widetilde A_{23}
=
\begin{pmatrix}
1&0&0\\
0&1&0\\
-5&-2&23
\end{pmatrix}.
\]

At \(z=1/3\), the distribution grids can be represented in base coordinates as
\[
\mathcal G_n=
\left\{
v_0+
\widetilde A_n
\begin{pmatrix}u/n\\v/n\\0\end{pmatrix}
:
u,v\in\mathbf Z/n\mathbf Z
\right\}
\subset(\mathbf Q/\mathbf Z)^3.
\]

Direct exact arithmetic shows
\[
\widetilde M(\mathcal G_{10})=\mathcal G_{10},
\qquad
\widetilde M(\mathcal G_{23})=\mathcal G_{23}.
\]

So the finite product in the distribution formula is not merely a grid:
it is a finite unit-dynamical system.

---

## 6. Exact orbit decomposition

### Index 23

The \(23^2=529\) points decompose under \(\widetilde M\) as

\[
\boxed{529=1+528.}
\]

There is exactly one fixed point:
\[
v_0=(0,0,1/3),
\]
and every other point lies in one orbit of length
\[
528=23^2-1.
\]

Thus the nontrivial part of the entire 23-polyphase grid is a single unit orbit.

The induced linear action on the two polyphase coordinates is
\[
T_{23}
\equiv
\begin{pmatrix}
0&-1\\
-71&-28
\end{pmatrix}
\pmod{23}
=
\begin{pmatrix}
0&22\\
21&18
\end{pmatrix}.
\]

Its action on the nonzero vectors of \(\mathbf F_{23}^2\) is transitive.
Equivalently, this is a Singer-type cycle of order \(23^2-1\).

This is a strong localization pattern: one arithmetic fixed point plus one
complete nontrivial orbit.

### Index 10

The \(10^2=100\) points decompose as
\[
\boxed{
100=1+3+8\cdot12.
}
\]

Thus there are:
- one fixed point \(v_0\),
- one orbit of length \(3\),
- eight orbits of length \(12\).

The unique three-cycle is represented by
\[
(1/2,0,5/6)
\to
(0,1/2,5/6)
\to
(1/2,1/2,1/3)
\to
(1/2,0,5/6).
\]

All remaining \(96\) points lie in twelve-cycles.

---

## 7. Why this matters for the missing theorem

The other two BCG special values have now been expressed as finite products of
the **same base smoothed function** \(F_{t,\sigma}\) over finite sets that are
exactly invariant under the arithmetic unit action.

This changes the analytic problem.

Instead of comparing three unrelated infinite products, one can try to apply
the unit functional equations orbit by orbit.

For the index-23 value there are only two orbit types:
1. the fixed arithmetic target \(1/3\),
2. one complete orbit of length \(528\).

If the multiplier accumulated around the 528-cycle can be evaluated exactly,
the entire index-23 distribution product reduces to a fixed-point contribution
times one explicitly computable orbit multiplier.

For the index-10 value there are only ten orbits in total.

This is precisely the setting in which a finite determinant/localization
formula could arise. It also explains why the determinant
\[
\frac{\det(\omega M-I)}{\det(I-M)}=2+3\omega
\]
keeps appearing: the primitive character sector is a fixed-point contribution
of the same unit dynamics.

---

## 8. New concrete target

The next analytic block should prove an orbit-product formula of the form

\[
\prod_{x\in\mathcal O}
\frac{F(\widetilde Mx)}{F(x)}
=
\text{explicit theta/eta multiplier}
\]

for every finite unit orbit \(\mathcal O\), with the representative and
trivialization data retained.

On a complete orbit the left side telescopes to \(1\), so the total multiplier
must satisfy an exact finite identity. The nontrivial information is carried by
the cocycle/trivialization accumulated while replacing \(\widetilde Mx\) by its
chosen representative in the finite grid.

The index-23 case is especially attractive because there is a single
nontrivial orbit. It is the cleanest place to derive the missing primitive
sector before handling the more complicated index-10 decomposition.

The desired endpoint remains the three-sector closure identities
\[
S_0=-6\beta^2+14\beta-2,
\]
\[
S_1S_2=208\beta^2+214\beta-1169,
\]
\[
S_1^3=(\beta c(\beta,\omega))^3(2+3\omega).
\]

---

## 9. Boundary

What has been proved here:
- exact index-10 and index-23 lattice inclusions;
- exact integral conjugate unit matrices;
- exact preservation of the conductor-three fixed point;
- exact finite-grid distribution identity for the smoothed gamma;
- exact unit invariance of the finite grids;
- exact orbit decompositions \(1+528\) and \(1+3+8\cdot12\).

What is not yet proved:
- the accumulated cocycle multiplier around those orbits;
- the three Fourier-sector identities;
- \(U_\Gamma=U_{\rm alg}\);
- the general BCG algebraicity/reciprocity conjecture.

This is therefore a genuine reduction of the remaining analytic problem, not
its completion.

<!-- END ORIGINAL FILE: PROOF(20261002-POLYPHASE_TRANSPORT).md -->

---
