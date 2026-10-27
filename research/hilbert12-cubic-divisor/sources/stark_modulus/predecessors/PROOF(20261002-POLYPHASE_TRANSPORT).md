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
