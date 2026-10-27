# Projector-Generated Special Functions VIII

## q-Hahn Lowest-Weight Packets, q-Racah Recoupling, Askey-Wilson Transfer Functions, and Deformation Geometry

**Author:** Komorebi P.

## 1. Symmetric q-number

For $q>0$, $q\neq1$,

$$
[x]_q=\frac{q^x-q^{-x}}{q-q^{-1}}.
$$

At $q=1$, set $[x]_1=x$ by continuity. With $q=e^{-\theta}$,

$$
[x]_q=\frac{\sinh(x\theta)}{\sinh\theta}.
$$

## 2. Positive q-shape packet

On the basis $\{|n\rangle:n\ge0\}$,

$$
K_0|n\rangle=(n+\kappa)|n\rangle,
$$

$$
K_+|n\rangle=\sqrt{[n+1]_q[2\kappa+n]_q}|n+1\rangle,
$$

$$
K_-|n\rangle=\sqrt{[n]_q[2\kappa+n-1]_q}|n-1\rangle.
$$

The local algebra is

$$
[K_0,K_\pm]=\pm K_\pm,
\qquad
[K_-,K_+]=[2K_0]_q.
$$

## 3. Coproduct

The symmetric coproduct is

$$
\Delta K_0=K_0\otimes I+I\otimes K_0,
$$

$$
\Delta K_\pm=K_\pm\otimes q^{K_0}+q^{-K_0}\otimes K_\pm.
$$

For three factors,

$$
\Delta^{(3)}K_-
=
K_-\otimes q^{K_0}\otimes q^{K_0}
+
q^{-K_0}\otimes K_-\otimes q^{K_0}
+
q^{-K_0}\otimes q^{-K_0}\otimes K_-.
$$

## 4. q-Casimir

Define

$$
\mathcal C_q=[K_0]_q[K_0-1]_q-K_+K_-.
$$

On the positive packet $D^+_{\kappa,q}$,

$$
\mathcal C_q=[\kappa]_q[\kappa-1]_q I.
$$

## 5. Fixed excitation and multiplicity

For $m$ factors,

$$
\mathcal H_N^{(m)}
=\operatorname{span}\{|n_1,\ldots,n_m\rangle:n_1+\cdots+n_m=N\}.
$$

Then

$$
\dim\mathcal H_N^{(m)}=\binom{N+m-1}{m-1}.
$$

The lowest-weight packet is

$$
\mathcal M_N^{(m)}
=\ker\left(K_-^{[m]}\big|_{\mathcal H_N^{(m)}}\right),
$$

with

$$
\dim\mathcal M_N^{(m)}=\binom{N+m-2}{m-2}.
$$

## 6. Explicit q-Hahn lowest packet

For two shapes $\kappa_1,\kappa_2$ and total excitation $N$, set

$$
\lambda=q^{-(N-1+\kappa_1+\kappa_2)}.
$$

A lowest-weight vector is

$$
|\Omega_N\rangle
=\frac1{\sqrt{Z_N}}
\sum_{n=0}^{N}
(-\lambda)^n
\sqrt{
{N\brack n}_q
\frac{[2\kappa_2+N-n]_{q,n}}{[2\kappa_1]_{q,n}}
}
|n,N-n\rangle.
$$

The coefficient ratio is

$$
\frac{c_{n+1}}{c_n}
=-q^{-(N-1+\kappa_1+\kappa_2)}
\sqrt{
\frac{[N-n]_q[2\kappa_2+N-n-1]_q}
{[n+1]_q[2\kappa_1+n]_q}
}.
$$

## 7. Pair q-Casimir spectra

For a pair of shapes $a,b$,

$$
\lambda_j^{ab}(q)
=
[\kappa_a+\kappa_b+j]_q
[\kappa_a+\kappa_b+j-1]_q,
\qquad 0\le j\le N.
$$

## 8. q-Racah recoupling

Let $L_N$ diagonalize the restricted pair Casimir $\mathcal C_{12}$ and let $R_N$ diagonalize $\mathcal C_{23}$. The recoupling matrix is

$$
\mathcal R_N(q)=L_N^{\mathsf T}R_N.
$$

It satisfies

$$
\mathcal R_N(q)^{\mathsf T}\mathcal R_N(q)
=
\mathcal R_N(q)\mathcal R_N(q)^{\mathsf T}
=I.
$$

## 9. Exact equal-shape one-excitation transform

For

$$
\kappa_1=\kappa_2=\kappa_3=\frac12,
\qquad N=1,
$$

$$
\mathcal R_q=
\begin{pmatrix}
c_q&s_q\\
s_q&-c_q
\end{pmatrix},
$$

where

$$
c_q=\frac{q}{1+q^2},
\qquad
s_q=\frac{\sqrt{1+q^2+q^4}}{1+q^2}.
$$

At $q=1$,

$$
\mathcal R_1=
\begin{pmatrix}
1/2&\sqrt3/2\\
\sqrt3/2&-1/2
\end{pmatrix}.
$$

As $q\downarrow0$,

$$
\mathcal R_q\to
\begin{pmatrix}0&1\\1&0\end{pmatrix}.
$$

## 10. Bistochastic measurement kernel

Define

$$
P_{jm}(q)=|\mathcal R_N(q)_{jm}|^2.
$$

Then

$$
P_{jm}\ge0,
\qquad
\sum_mP_{jm}=1,
\qquad
\sum_jP_{jm}=1.
$$

For every probability vector $p$,

$$
H(pP)\ge H(p).
$$

For the one-excitation kernel,

$$
p(q)=c_q^2=\frac{q^2}{(1+q^2)^2}
$$

and the spectral mixing gap is

$$
\operatorname{gap}(q)
=
\frac{2q^2}{(1+q^2)^2}.
$$

## 11. Deformation generator

Write

$$
q=e^{-\theta}.
$$

In a continuous sign gauge,

$$
A_N(\theta)
=
\mathcal R_N(\theta)^{\mathsf T}
\partial_\theta\mathcal R_N(\theta).
$$

Then

$$
A_N(\theta)^{\mathsf T}=-A_N(\theta)
$$

and

$$
\partial_\theta\mathcal R_N
=
\mathcal R_NA_N.
$$

The finite deformation metric is

$$
g_N(\theta)=\frac12\|A_N(\theta)\|_F^2.
$$

## 12. Four-body q-pentagon

Let $B_0,\ldots,B_4$ be the complete joint-Casimir bases for the five binary four-body coupling trees. Define

$$
U_{r,r+1}=B_r^{\mathsf T}B_{r+1}.
$$

Then

$$
U_{01}U_{12}U_{23}U_{34}U_{40}=I.
$$

## 13. Givens compiler

Every real orthogonal $d\times d$ q-Racah matrix has a factorization

$$
R=G_1^{\mathsf T}\cdots G_L^{\mathsf T}D,
$$

where each $G_j$ is a two-coordinate Givens rotation and $D$ is a diagonal sign matrix. One may choose

$$
L\le\frac{d(d-1)}2.
$$

## 14. Scalar q-Racah function

Let

$$
(a;q)_n=\prod_{j=0}^{n-1}(1-aq^j).
$$

Define

$$
R_n(\mu(y);\alpha,\beta,\gamma,\delta\mid q)
={}_4\phi_3\left(
\begin{matrix}
q^{-n},\alpha\beta q^{n+1},q^{-y},\gamma\delta q^{y+1}\\
\alpha q,\beta\delta q,\gamma q
\end{matrix}
;q,q
\right),
$$

where

$$
\mu(y)=q^{-y}+\gamma\delta q^{y+1}.
$$

The duality law is

$$
R_n(\mu(y);\alpha,\beta,\gamma,\delta\mid q)
=
R_y(\mu(n);\gamma,\delta,\alpha,\beta\mid q).
$$

If

$$
\alpha=q^A,
\quad
\beta=q^B,
\quad
\gamma=q^G,
\quad
\delta=q^D,
$$

then, for fixed $n,y$,

$$
\lim_{q\to1^-}
R_n(\mu(y);q^A,q^B,q^G,q^D\mid q)
={}_4F_3\left(
\begin{matrix}
-n,n+A+B+1,-y,y+G+D+1\\
A+1,B+D+1,G+1
\end{matrix};1
\right).
$$

## 15. Askey-Wilson transfer function

Define

$$
\mathcal A_n(z)
={}_4\phi_3\left(
\begin{matrix}
q^{-n},abcdq^{n-1},az,az^{-1}\\
ab,ac,ad
\end{matrix};q,q
\right).
$$

Let

$$
A(z)=\frac{(1-az)(1-bz)(1-cz)(1-dz)}{(1-z^2)(1-qz^2)}.
$$

The q-difference operator is

$$
(\mathcal Lf)(z)
=A(z)(f(qz)-f(z))
+A(z^{-1})(f(q^{-1}z)-f(z))
+\left(1+\frac{abcd}{q}\right)f(z).
$$

Then

$$
\mathcal L\mathcal A_n
=
\left(q^{-n}+abcdq^{n-1}\right)\mathcal A_n.
$$

## 16. Exact boundary

q-Racah and Askey-Wilson functions are classical. The generated object is the complete packet tuple

$$
\left(
\mathcal M_N,
\mathcal C_{12},
\mathcal C_{23},
\mathcal R_N(q),
P_N(q),
A_N(\theta),
\{U_r(q)\}_{r=0}^{4}
\right).
$$

It retains the object space, two exact coordinate atlases, reversible synthesis, a measured stochastic channel, a local deformation generator, and a closed associator loop.
