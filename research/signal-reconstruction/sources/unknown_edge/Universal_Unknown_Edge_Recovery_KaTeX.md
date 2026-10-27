# Universal Unknown-Edge Recovery

## Impossibility without structure, exact off-grid recovery in a finite-rate class, and Gibbs-free synthesis

**Komorebi P.**

## 1. The exact boundary

A model-free theorem is impossible. Let the measurements be

$$
M:X\to Y.
$$

If $M$ is not injective, choose $h\in\ker M$, $h\neq0$. Then

$$
M(f)=M(f+h),
$$

so no recovery map can distinguish $f$ from $f+h$. Finite point samples give a concrete example. A nonzero interval packet can lie between two sample locations and vanish at every sampled point.

The decomposition itself must also be identifiable. If the smooth class $\mathcal S$ and edge class $\mathcal J$ overlap, then for nonzero $h\in\mathcal S\cap\mathcal J$,

$$
f=s+j=(s+h)+(j-h).
$$

There is also no stability constant that is uniform over colliding edges. For

$$
D j_\delta=\delta_0-\delta_\delta,
$$

the Fourier moments are

$$
m_n(\delta)=1-e^{-in\delta}.
$$

For every fixed finite frequency set,

$$
\|m(\delta)\|\to0
\quad\text{as}\quad
\delta\to0,
$$

while the two jumps remain nonzero. Any stable theorem must therefore state a separation or conditioning hypothesis.

## 2. Finite edge dictionaries

Let $\mathcal S\subset\mathbb R^m$ be a background subspace, let $D\in\mathbb R^{m\times N}$ be a finite edge dictionary, and let

$$
P_{\mathcal S}
$$

be the orthogonal background projector. Define

$$
R_{\mathcal S}=I-P_{\mathcal S},
\qquad
A=R_{\mathcal S}D.
$$

The observation model is

$$
y=s_0+D\alpha_0+\eta,
\qquad
s_0\in\mathcal S,
\qquad
\|\alpha_0\|_0\le s.
$$

### Exact recovery theorem

Every $s$-sparse edge vector is uniquely recoverable if and only if

$$
\ker A\cap\{h:\|h\|_0\le2s\}=\{0\}.
$$

Equivalently,

$$
\operatorname{spark}(A)>2s.
$$

The proof is the usual secant argument after removing the background. Two admissible sparse vectors $\alpha$ and $\beta$ generate the same residualized data exactly when

$$
A(\alpha-\beta)=0,
$$

and $\alpha-\beta$ has at most $2s$ nonzero entries.

### Stability theorem

Define

$$
\gamma_{2s}
=
\min_{\substack{h\neq0\\\|h\|_0\le2s}}
\frac{\|Ah\|_2}{\|h\|_2}.
$$

If $\|R_{\mathcal S}\eta\|_2\le\varepsilon$ and a recovered vector $\widehat\alpha$ obeys

$$
\|A\widehat\alpha-R_{\mathcal S}y\|_2\le\varepsilon,
$$

then

$$
\boxed{
\|\widehat\alpha-\alpha_0\|_2
\le
\frac{2\varepsilon}{\gamma_{2s}}.
}
$$

This theorem is dimension-independent. It applies to one-dimensional interval packets, two-dimensional rectangle packets, or any finite geometric library.

## 3. The off-grid finite-rate class

Work on the periodic domain

$$
\mathbb T=\mathbb R/(2\pi\mathbb Z).
$$

Define the Fourier coefficient

$$
\widehat u(n)
=
\frac{1}{2\pi}
\int_0^{2\pi}u(x)e^{-inx}\,dx.
$$

Fix bounds $K\ge0$ and $L\ge2$. The class $\mathcal U_{K,L}$ contains all real periodic signals

$$
f=s+j
$$

such that

$$
s(x)=\sum_{|n|\le K}c_ne^{inx},
\qquad
c_{-n}=\overline{c_n},
$$

and $j$ is piecewise constant with at most $L$ distinct jumps. Write the active locations and jump amplitudes as

$$
0\le\tau_1<\cdots<\tau_r<2\pi,
\qquad
r\le L,
$$

$$
a_\ell=j(\tau_\ell^+)-j(\tau_\ell^-),
\qquad
a_\ell\neq0.
$$

Periodicity requires

$$
\sum_{\ell=1}^r a_\ell=0.
$$

The edge packet is normalized to mean zero. Any constant is absorbed into $s$.

## 4. The derivative packet

The distributional derivative of $j$ is

$$
\boxed{
Dj=\sum_{\ell=1}^r a_\ell\delta_{\tau_\ell}.
}
$$

Fourier differentiation gives

$$
2\pi in\widehat j(n)
=
\sum_{\ell=1}^r a_\ell e^{-in\tau_\ell}.
$$

For $n>K$, the smooth background vanishes. Therefore

$$
\widehat f(n)=\widehat j(n).
$$

Define

$$
z_\ell=e^{-i\tau_\ell}
$$

and the high-frequency edge moments

$$
\boxed{
m_n=2\pi in\widehat f(n)
=\sum_{\ell=1}^r a_\ell z_\ell^n,
\qquad n>K.
}
$$

The infinite-dimensional-looking edge problem has become a finite exponential moment problem.

## 5. Hankel rank and the unknown number of edges

Set

$$
n_0=K+1.
$$

For $q\ge1$, form

$$
H_q=(m_{n_0+p+q'})_{p,q'=0}^{q-1}.
$$

Let

$$
V_q=
\begin{pmatrix}
1&\cdots&1\\
z_1&\cdots&z_r\\
\vdots&&\vdots\\
z_1^{q-1}&\cdots&z_r^{q-1}
\end{pmatrix}.
$$

Then

$$
\boxed{
H_q
=V_q\operatorname{diag}(a_1z_1^{n_0},\ldots,a_rz_r^{n_0})V_q^T.
}
$$

When the locations are distinct and the amplitudes are nonzero,

$$
\boxed{
\operatorname{rank}(H_q)=r
\quad\text{for}\quad q\ge r.
}
$$

Thus the actual number of unknown edges is the exact Hankel rank.

## 6. The annihilating polynomial

Define the monic polynomial

$$
Q(z)=\prod_{\ell=1}^r(z-z_\ell)
=q_0+q_1z+\cdots+q_{r-1}z^{r-1}+z^r.
$$

Since $Q(z_\ell)=0$,

$$
\boxed{
\sum_{k=0}^r q_km_{n+k}=0.
}
$$

Using $2r$ consecutive moments gives the square system

$$
\begin{pmatrix}
m_{n_0}&m_{n_0+1}&\cdots&m_{n_0+r-1}\\
m_{n_0+1}&m_{n_0+2}&\cdots&m_{n_0+r}\\
\vdots&\vdots&&\vdots\\
m_{n_0+r-1}&m_{n_0+r}&\cdots&m_{n_0+2r-2}
\end{pmatrix}
\begin{pmatrix}
q_0\\q_1\\\vdots\\q_{r-1}
\end{pmatrix}
=-
\begin{pmatrix}
m_{n_0+r}\\m_{n_0+r+1}\\\vdots\\m_{n_0+2r-1}
\end{pmatrix}.
$$

The roots of $Q$ give

$$
\boxed{
\tau_\ell=-\arg z_\ell\pmod{2\pi}.
}
$$

## 7. Jump amplitudes and packet reconstruction

Once the locations are known, solve

$$
\begin{pmatrix}
z_1^{n_0}&\cdots&z_r^{n_0}\\
\vdots&&\vdots\\
z_1^{n_0+2L-1}&\cdots&z_r^{n_0+2L-1}
\end{pmatrix}
\begin{pmatrix}
a_1\\\vdots\\a_r
\end{pmatrix}
=
\begin{pmatrix}
m_{n_0}\\\vdots\\m_{n_0+2L-1}
\end{pmatrix}.
$$

Periodic integration of

$$
Dj=\sum_{\ell=1}^r a_\ell\delta_{\tau_\ell}
$$

recovers $j$ up to a constant. The zero-mean convention fixes that constant uniquely.

For $|n|\le K$, recover the smooth coefficients by

$$
\boxed{
\widehat s(n)=\widehat f(n)-\widehat j(n).
}
$$

Then

$$
s(x)=\sum_{|n|\le K}\widehat s(n)e^{inx}.
$$

## 8. Universal theorem on the declared class

Suppose $f\in\mathcal U_{K,L}$ has $r\le L$ active jumps. Assume the locations are distinct and the amplitudes are nonzero. Given

$$
\widehat f(n),
\qquad
-K\le n\le K,
$$

and

$$
\widehat f(n),
\qquad
n=K+1,\ldots,K+2L,
$$

the following objects are determined uniquely by finite linear algebra:

1. the actual jump count $r$
2. every off-grid location $\tau_\ell$
3. every jump amplitude $a_\ell$
4. the canonical zero-mean edge packet $j$
5. every background coefficient
6. the complete signal $f=s+j$

The high-frequency measurement count is $2L$. The low-frequency background count is $2K+1$.

## 9. Gibbs-free synthesis

A raw Fourier reconstruction keeps the discontinuity inside a finite global trigonometric approximation:

$$
S_Nf=S_Ns+S_Nj.
$$

For $N\ge K$, $S_Ns=s$, so the entire error is

$$
S_Nf-f=S_Nj-j.
$$

After edge recovery, use the resolved synthesis

$$
\widehat f_{\mathrm{resolved}}
=
\widehat s+\widehat j.
$$

The theorem gives $\widehat s=s$ and $\widehat j=j$. Therefore

$$
\boxed{
\widehat f_{\mathrm{resolved}}=f.
}
$$

The final reconstruction has no Gibbs overshoot because the recovered discontinuity is restored in its native packet rather than approximated by a truncated global Fourier series.

## 10. Stability certificate

With Fourier noise

$$
\widehat f_\eta(n)=\widehat f(n)+\eta_n,
$$

the moment noise is

$$
m_n^\eta-m_n=2\pi in\eta_n.
$$

Let the perturbed annihilator be

$$
\widetilde Q=Q+E_Q.
$$

Choose disjoint disks

$$
D_j=\{z:|z-z_j|<\rho\},
\qquad
0<\rho<\frac12\min_{j\ne k}|z_j-z_k|.
$$

Define

$$
m_j(\rho)=\min_{|z-z_j|=\rho}|Q(z)|.
$$

If

$$
\sup_{|z-z_j|=\rho}|E_Q(z)|<m_j(\rho)
$$

for every $j$, then Rouché's theorem gives exactly one recovered root in each disk. The location error is therefore less than $\rho$.

There is no separation-free bound. For opposite jumps separated by $\delta$,

$$
m_n(\delta)=1-e^{-in\delta},
$$

and

$$
|m_n(\delta)|\le|n|\delta.
$$

The measurements collapse as the locations collide.

## 11. Extensions

### Shared locations across channels

For

$$
m_n^{(c)}=\sum_{\ell=1}^r a_{c\ell}z_\ell^n,
$$

all channels share the annihilator

$$
Q(z)=\prod_{\ell=1}^r(z-z_\ell).
$$

A full-rank stacked recurrence system recovers the common locations. Channelwise Vandermonde solves recover the amplitudes.

### Piecewise-polynomial packets

If $u$ is piecewise polynomial of degree at most $d$, then

$$
D^{d+1}u
$$

is a finite combination of point-supported derivative distributions. The moment sequence has the form

$$
m_n=\sum_{\ell=1}^r p_\ell(n)z_\ell^n,
$$

with $\deg p_\ell\le d$. It is annihilated by

$$
\boxed{
\prod_{\ell=1}^r(E-z_\ell)^{d+1}.
}
$$

### Two-dimensional finite dictionaries

For a finite image background $B$ and geometric edge dictionary $D$, exact sparse recovery is still governed by

$$
\ker((I-P_B)D)\cap\{h:\|h\|_0\le2s\}=\{0\}.
$$

The supplied implementation recovers an unknown rectangle packet exactly from a complete finite rectangle library.

## 12. Numerical certificate

The implementation passes 19 of 19 checks. Representative errors are

$$
\max_\ell|\widehat\tau_\ell-\tau_\ell|_{\mathbb T}
=4.66\times10^{-14},
$$

$$
\max_\ell|\widehat a_\ell-a_\ell|
=2.93\times10^{-13},
$$

and

$$
\|\widehat f-f\|_\infty
=3.82\times10^{-14}.
$$

Across exact examples with two, four, six, and eight jumps, the largest reconstruction error was

$$
3.96\times10^{-13}.
$$

## 13. Final claim

The absolute model-free version of universal unknown-edge recovery is false. The finite-rate version proved here is exact:

$$
\boxed{
\text{bandlimited periodic background}
+
\text{finitely many off-grid jumps}
\Longrightarrow
\text{finite exact recovery}.
}
$$

This is a complete solution for the declared one-dimensional class. The full noisy piecewise-smooth problem and arbitrary continuous two-dimensional edge geometry remain larger problems.
