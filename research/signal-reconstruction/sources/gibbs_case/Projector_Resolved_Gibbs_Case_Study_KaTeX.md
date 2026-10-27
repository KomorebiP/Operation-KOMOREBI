# Projector-Resolved Gibbs Reconstruction

## One step-by-step derivation

**Author:** Komorebi P.

This derivation follows one signal through Fourier analysis, the Gibbs limit, packet projectors, finite interval recovery, synthesis, and the final residual. It accompanies the full PDF.

---

## 1. The single signal

Work on the circle

$$
\mathbb T=\mathbb R/(2\pi\mathbb Z),
$$

using representatives in $[-\pi,\pi)$.

Define the smooth seed

$$
\boxed{
s(x)=\frac14+\frac25\cos(2x)-\frac13\sin(3x)+\frac15\cos(5x).
}
$$

Define the geometric edge packet

$$
\boxed{
j(x)=\mathbf 1_{[-\pi/3,\,\pi/3)}(x).
}
$$

The full signal is

$$
\boxed{f(x)=s(x)+j(x).}
$$

The smooth packet is a degree-five trigonometric polynomial. The edge packet has two discontinuities and unit jump amplitude.

---

## 2. Fourier conventions

For a periodic function $g$,

$$
\widehat g(n)=\frac1{2\pi}\int_{-\pi}^{\pi}g(x)e^{-inx}\,dx.
$$

The order-$N$ partial sum is

$$
S_Ng(x)=\sum_{|n|\le N}\widehat g(n)e^{inx}.
$$

The nonzero smooth coefficients are

$$
\widehat s(0)=\frac14,
$$

$$
\widehat s(\pm2)=\frac15,
$$

$$
\widehat s(3)=\frac{i}{6},
\qquad
\widehat s(-3)=-\frac{i}{6},
$$

and

$$
\widehat s(\pm5)=\frac1{10}.
$$

Therefore

$$
\boxed{S_Ns=s\quad\text{for every }N\ge5.}
$$

---

## 3. Exact Fourier coefficients of the edge packet

Let $a=\pi/3$. For $n\ne0$,

$$
\begin{aligned}
\widehat j(n)
&=\frac1{2\pi}\int_{-a}^{a}e^{-inx}\,dx\\
&=\frac{e^{ina}-e^{-ina}}{2\pi i n}\\
&=\frac{\sin(na)}{\pi n}.
\end{aligned}
$$

For $n=0$,

$$
\widehat j(0)=\frac a\pi=\frac13.
$$

Thus

$$
\boxed{
\widehat j(n)=
\begin{cases}
1/3,&n=0,\\[2mm]
\sin(n\pi/3)/(\pi n),&n\ne0.
\end{cases}
}
$$

The factor $\sin(n\pi/3)$ has the six-phase pattern

$$
\sin\left(\frac{n\pi}{3}\right)=
\begin{cases}
0,&n\equiv0,3\pmod6,\\[1mm]
\sqrt3/2,&n\equiv1,2\pmod6,\\[1mm]
-\sqrt3/2,&n\equiv4,5\pmod6.
\end{cases}
$$

The edge coefficients therefore have exact residue structure, but their nonzero subsequences decay only as $1/|n|$.

---

## 4. Raw Fourier reconstruction

Direct substitution gives

$$
\boxed{
S_Nj(x)=\frac13+\frac2\pi\sum_{n=1}^{N}
\frac{\sin(n\pi/3)}{n}\cos(nx).
}
$$

For $N\ge5$,

$$
S_Nf=s+S_Nj.
$$

All remaining error is the error produced by approximating the edge packet globally.

---

## 5. Dirichlet-kernel form

The Dirichlet kernel is

$$
D_N(u)=\sum_{n=-N}^{N}e^{inu}
=\frac{\sin((N+1/2)u)}{\sin(u/2)}.
$$

The partial sum is a convolution:

$$
S_Ng(x)=\frac1{2\pi}\int_{-\pi}^{\pi}D_N(x-t)g(t)\,dt.
$$

For the edge packet,

$$
\boxed{
S_Nj(x)=\frac1{2\pi}\int_{-a}^{a}D_N(x-t)\,dt.
}
$$

The kernel sharpens as $N$ increases, but it has alternating positive and negative sidelobes. At the discontinuity it samples both one-sided values.

---

## 6. Scaled edge coordinate

At the right edge $x=a$, use

$$
x_N(z)=a-\frac{z}{N+1/2}.
$$

Positive $z$ approaches the edge from the interior.

The scaled limit is

$$
\boxed{
\lim_{N\to\infty}S_Nj\left(a-\frac{z}{N+1/2}\right)
=\frac12+\frac1\pi\operatorname{Si}(z),
}
$$

where

$$
\operatorname{Si}(z)=\int_0^z\frac{\sin u}{u}\,du.
$$

Differentiate:

$$
\frac{d}{dz}
\left(
\frac12+\frac1\pi\operatorname{Si}(z)
\right)
=
\frac1\pi\frac{\sin z}{z}.
$$

The first positive maximum occurs at $z=\pi$. Hence

$$
\frac12+\frac{\operatorname{Si}(\pi)}{\pi}
=1+G,
$$

with

$$
\boxed{
G=\frac{\operatorname{Si}(\pi)}{\pi}-\frac12
=0.08948987223608351\ldots.
}
$$

The ringing region has width $O(1/N)$, but the normalized first overshoot does not go to zero.

---

## 7. The exact model space

Let

$$
\mathcal T_5
=
\operatorname{span}_{\mathbb R}
\{1,\cos x,\sin x,\ldots,\cos5x,\sin5x\}.
$$

Let

$$
\mathcal J=\operatorname{span}_{\mathbb R}\{j\}.
$$

Every element of $\mathcal T_5$ is continuous. Every nonzero element of $\mathcal J$ is discontinuous. Therefore

$$
\mathcal T_5\cap\mathcal J=\{0\}.
$$

Define the direct-sum model

$$
\boxed{
\mathcal M_5=\mathcal T_5\oplus\mathcal J.
}
$$

Every $g\in\mathcal M_5$ has a unique representation

$$
g=t+cj,
\qquad
t\in\mathcal T_5,
\quad c\in\mathbb R.
$$

---

## 8. Smooth and edge projectors

Define

$$
P_s(t+cj)=t,
$$

and

$$
P_j(t+cj)=cj.
$$

Then

$$
P_s^2=P_s,
$$

$$
P_j^2=P_j,
$$

$$
P_sP_j=P_jP_s=0,
$$

and

$$
\boxed{P_s+P_j=I_{\mathcal M_5}.}
$$

The analysis map is

$$
\mathcal A(g)=(P_sg,P_jg).
$$

The synthesis map is

$$
\mathcal S(t,cj)=t+cj.
$$

Hence

$$
\boxed{\mathcal S\mathcal A=I_{\mathcal M_5}.}
$$

For the worked signal,

$$
P_sf=s,
\qquad
P_jf=j.
$$

---

## 9. The resolved reconstruction operator

Raw truncation applies $S_N$ to both packets:

$$
S_Nf=S_NP_sf+S_NP_jf.
$$

The first block is appropriate. The second block creates the Gibbs oscillation.

Define instead

$$
\boxed{
\mathcal R_N=S_NP_s+P_j.
}
$$

Then, for $g=t+cj$,

$$
\mathcal R_Ng=S_Nt+cj.
$$

If $N\ge5$,

$$
S_Nt=t.
$$

Therefore

$$
\boxed{
\mathcal R_Ng=g
\qquad
(g\in\mathcal M_5,\ N\ge5).
}
$$

In particular,

$$
\boxed{
\mathcal R_Nf=f
\qquad(N\ge5).
}
$$

Relative to the direct sum $\mathcal T_5\oplus\mathcal J$,

$$
\mathcal R_N=
\begin{pmatrix}
S_N|_{\mathcal T_5}&0\\
0&I_{\mathcal J}
\end{pmatrix}.
$$

For $N\ge5$,

$$
\boxed{
\mathcal R_N=
\begin{pmatrix}
I&0\\
0&I
\end{pmatrix}.
}
$$

The discontinuity is not represented by a finite Fourier series. It bypasses the Fourier block.

---

## 10. Exact one-sided values

At the right edge,

$$
f(a^-)=s(a)+1,
$$

and

$$
f(a^+)=s(a).
$$

For $N\ge5$,

$$
(\mathcal R_Nf)(a^-)=s(a)+1,
$$

$$
(\mathcal R_Nf)(a^+)=s(a).
$$

There is no jump-induced overshoot, undershoot, or transition layer.

---

## 11. General smooth packets

Suppose instead that

$$
f=s+cj
$$

with a non-bandlimited smooth packet $s$. Keep the same resolved operator:

$$
\mathcal R_Nf=S_Ns+cj.
$$

Then

$$
\boxed{
f-\mathcal R_Nf=s-S_Ns.
}
$$

The discontinuity contributes no approximation error.

If

$$
|\widehat s(n)|\le Ce^{-\rho|n|},
$$

then

$$
\begin{aligned}
\|f-\mathcal R_Nf\|_\infty
&\le2\sum_{n>N}|\widehat s(n)|\\
&\le2C\sum_{n>N}e^{-\rho n}\\
&=\boxed{
\frac{2Ce^{-\rho(N+1)}}{1-e^{-\rho}}.
}
\end{aligned}
$$

This bound is uniform across the jump because the jump is not part of the truncated packet.

---

## 12. Fejer, Lanczos, and spectral filtering

The Fejer mean is

$$
\sigma_Ng=\frac1{N+1}\sum_{m=0}^{N}S_mg.
$$

Its kernel is nonnegative and normalized. Hence

$$
0\le j\le1
\quad\Longrightarrow\quad
0\le\sigma_Nj\le1.
$$

Fejer averaging removes overshoot of the jump packet but replaces the exact edge by a transition layer.

Lanczos and exponential filters damp high-frequency coefficients. They reduce sidelobes by suppressing the coefficients needed to sharpen the discontinuity.

The packet operator changes the question:

$$
\text{filtering: approximate the whole signal in one atlas,}
$$

versus

$$
\text{packet calculus: select the atlas and operator block by component.}
$$

---

## 13. Finite sample model

Take

$$
M=96,
$$

with sample points

$$
x_m=-\pi+\frac{2\pi m}{M},
\qquad0\le m<M.
$$

The true interval begins at

$$
r_*=32
$$

and has length

$$
\ell_*=32.
$$

Let $q_{r,\ell}\in\{0,1\}^M$ denote the cyclic interval mask starting at $r$ with length $\ell$.

The true sample vector is

$$
y=B\theta_*+q_{32,32},
$$

where $B$ is the sampled degree-five trigonometric design.

---

## 14. Smooth-background projector

Let $B\in\mathbb R^{M\times11}$ have columns

$$
1,\cos x,\sin x,\ldots,\cos5x,\sin5x.
$$

Let $Q$ be an orthonormal basis for $\operatorname{Ran}(B)$.

Define

$$
P_B=QQ^T
$$

and

$$
P_B^\perp=I-P_B.
$$

Because $B\theta_*$ is in the smooth subspace,

$$
P_B^\perp y=P_B^\perp q_*.
$$

The unknown smooth coefficients have been eliminated exactly before the packet search begins.

---

## 15. Profile amplitude for one candidate packet

For a candidate mask $q$, write

$$
y^\perp=P_B^\perp y,
$$

and

$$
q^\perp=P_B^\perp q.
$$

The best amplitude is

$$
\boxed{
\widehat A(q)=
\frac{\langle q^\perp,y^\perp\rangle}
{\|q^\perp\|_2^2}.
}
$$

The profiled residual is

$$
\boxed{
J(q)=
\|y^\perp-\widehat A(q)q^\perp\|_2^2.
}
$$

---

## 16. Finite exact recovery theorem

Assume

$$
y=B\theta_*+A_*q_*,
\qquad A_*>0.
$$

Then

$$
y^\perp=A_*q_*^\perp.
$$

Substituting $q_*$ gives

$$
\widehat A(q_*)=A_*
$$

and

$$
J(q_*)=0.
$$

If no other admissible $q$ has $q^\perp$ equal to a positive scalar multiple of $q_*^\perp$, then $q_*$ is the unique positive-amplitude minimizer.

The program enumerates every cyclic interval with length from $8$ to $48$. The unique result is

$$
\boxed{
(\widehat r,\widehat\ell,\widehat A)=(32,32,1).
}
$$

The best objective is

$$
J(q_*)=0,
$$

and the second-best objective is

$$
0.7531607493634364.
$$

Thus the finite identifiability gap is

$$
\boxed{
\Gamma=0.7531607493634364.
}
$$

---

## 17. Reconstruction after packet recovery

With the selected packet $\widehat q$ and amplitude $\widehat A$, define

$$
\widehat s=P_B(y-\widehat A\widehat q).
$$

Then

$$
\widehat y=\widehat s+\widehat A\widehat q.
$$

For the worked signal,

$$
\widehat q=q_*,
\qquad
\widehat A=1,
\qquad
\widehat s=s|_{\{x_m\}}.
$$

The maximum reconstruction residual is

$$
\boxed{
\max_m|\widehat y_m-y_m|
=5.551115123125783\times10^{-16}.
}
$$

---

## 18. Packet perturbation identity

Let $q,\widetilde q\in\{0,1\}^M$ and amplitudes $A,\widetilde A\in\mathbb R$.

Partition the addresses into the common support and the two one-sided support differences. Then

$$
\begin{aligned}
\|Aq-\widetilde A\widetilde q\|_2^2
&=(A-\widetilde A)^2
|\operatorname{supp}q\cap\operatorname{supp}\widetilde q|\\
&\quad+A^2
|\operatorname{supp}q\setminus\operatorname{supp}\widetilde q|\\
&\quad+\widetilde A^2
|\operatorname{supp}\widetilde q\setminus\operatorname{supp}q|.
\end{aligned}
$$

If $A=\widetilde A=1$,

$$
\boxed{
\|q-\widetilde q\|_2^2
=|\operatorname{supp}q\triangle\operatorname{supp}\widetilde q|.
}
$$

A wrong edge is therefore diagnosed geometrically. The residual is localized at the incorrectly assigned boundary samples.

---

## 19. Noise and off-grid status

The supplied program performs deterministic finite experiments with Gaussian noise and with edges shifted between sample locations.

These experiments are not promoted to universal recovery theorems.

The exact theorem remains:

$$
\text{declared finite model}
+
\text{distinct residualized packet rays}
\Longrightarrow
\text{unique exact finite recovery}.
$$

The numerical studies show how the reconstruction changes when the exact hypotheses are perturbed.

---

## 20. Exact-versus-approximate ledger

| Statement | Status |
|---|---|
| Edge Fourier coefficient formula | exact identity |
| Dirichlet-kernel representation | exact identity |
| Scaled sine-integral Gibbs profile | asymptotic theorem |
| Smooth-edge projectors | exact algebra |
| $\mathcal R_N=I$ on $\mathcal M_5$ for $N\ge5$ | exact theorem |
| Exhaustive finite interval search | exact finite optimization |
| Noise recovery curves | deterministic computation |
| Off-grid convergence curve | deterministic computation |
| Universal unknown-edge recovery | not claimed |

---

## 21. Closed algorithm

1. Build the sampled trigonometric design $B$.
2. Compute an orthonormal basis $Q$ of $\operatorname{Ran}(B)$.
3. Residualize the data: $y^\perp=y-QQ^Ty$.
4. Enumerate every admissible cyclic interval mask $q$.
5. Residualize each mask: $q^\perp=q-QQ^Tq$.
6. Compute $\widehat A(q)$ in closed form.
7. Reject nonpositive amplitudes.
8. Minimize $J(q)$ exactly over the finite library.
9. Reconstruct $\widehat s=QQ^T(y-\widehat A\widehat q)$.
10. Synthesize $\widehat y=\widehat s+\widehat A\widehat q$.
11. Return the residual, the second-best objective, and the finite gap.

---

## 22. Final theorem

For

$$
f(x)=
\frac14+
\frac25\cos(2x)-
\frac13\sin(3x)+
\frac15\cos(5x)+
\mathbf1_{[-\pi/3,\pi/3)}(x),
$$

the following statements are established in the worked example:

1. Raw Fourier partial sums have normalized Gibbs overshoot

$$
G=0.08948987223608351\ldots.
$$

2. The model decomposes exactly as

$$
\mathcal M_5=\mathcal T_5\oplus\operatorname{span}\{j\}.
$$

3. The resolved operator

$$
\mathcal R_N=S_NP_s+P_j
$$

satisfies

$$
\mathcal R_N=I_{\mathcal M_5}
\qquad(N\ge5).
$$

4. The finite sampled solver uniquely recovers

$$
(r,\ell,A)=(32,32,1).
$$

5. The final sample reconstruction has maximum residual

$$
5.551115123125783\times10^{-16}.
$$

The Gibbs theorem remains true. The calculus changes the packet-specific operator so that the discontinuity is not sent through the truncation block that creates the phenomenon.
