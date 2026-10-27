# Self-Calibrating Polyphase Fourier Reconstruction

## Unknown jump count, oracle-equivalent internal de-aliasing, rate-preserving edge recovery, and Gibbs-free synthesis

**Komorebi P.**

## 1. Problem

Let a real periodic signal be

$$
f(x)=s(x)+j(x),
$$

where $s$ is smooth and $j$ is piecewise constant with finitely many unknown jumps. Write

$$
Dj=
\sum_{\ell=1}^{L} a_\ell\,\delta_{\tau_\ell},
\qquad
\sum_{\ell=1}^{L}a_\ell=0.
$$

Set

$$
z_\ell=e^{-i\tau_\ell}.
$$

For $n\neq0$, define the differentiated Fourier moments

$$
m_n=2\pi i n\,\widehat f(n).
$$

Then

$$
\boxed{
m_n=
\sum_{\ell=1}^{L}a_\ell z_\ell^n+e_n,
}
$$

where

$$
e_n=2\pi i n\,\widehat s(n).
$$

The edge is a finite exponential signal. The smooth packet is the perturbation.

## 2. Smooth-tail class

Assume

$$
|\widehat s(n)|\le C_s(1+|n|)^{-p-2}.
$$

Then

$$
|e_n|\le C(1+|n|)^{-p-1}.
$$

The algorithm does not need the value of $p$. The exponent only controls the rate theorem.

## 3. Polyphase reorganization

Choose a decimation $N\ge2$ and offsets $r=0,1,\ldots,R-1$. On the channel

$$
n=(q_0+q)N+r,
$$

we have

$$
\begin{aligned}
m_{(q_0+q)N+r}
&=
\sum_{\ell=1}^{L}
a_\ell z_\ell^{(q_0+q)N+r}
+e_{(q_0+q)N+r}\\
&=
\sum_{\ell=1}^{L}
b_{\ell,r}u_\ell^q
+e_{(q_0+q)N+r},
\end{aligned}
$$

with

$$
u_\ell=z_\ell^N,
\qquad
b_{\ell,r}=a_\ell z_\ell^{q_0N+r}.
$$

Each offset channel has the same aliased nodes $u_\ell$. Its coefficients change by

$$
\boxed{
b_{\ell,r+1}=z_\ell b_{\ell,r}.
}
$$

This identity carries the physical phase that was lost under decimation.

## 4. Unknown order from a Hankel gap

For one offset channel, form a Hankel matrix

$$
H=(m_{(q_0+i+j)N})_{i,j}.
$$

In the exact edge-only model,

$$
\operatorname{rank}(H)=L.
$$

If

$$
H=H_0+E
$$

and the exact rank-$L$ matrix has smallest nonzero singular value $\sigma_L(H_0)$, Weyl's inequality gives

$$
\sigma_L(H)\ge\sigma_L(H_0)-\|E\|_2,
$$

and

$$
\sigma_{L+1}(H)\le\|E\|_2.
$$

A gap remains whenever

$$
\sigma_L(H_0)>2\|E\|_2.
$$

The jump count is therefore recoverable from the same Fourier data under a quantitative rank-gap condition.

## 5. Aliased-node recovery

A Prony, matrix-pencil, or ESPRIT solve on one channel recovers

$$
\widehat u_\ell\approx u_\ell=z_\ell^N.
$$

Decimation may improve conditioning, but each $\widehat u_\ell$ has $N$ possible roots. Taking the principal root is not valid in general.

## 6. Offset phase estimator

After matching each offset channel to the recovered aliased nodes, let $\widehat b_{\ell,r}$ be the fitted coefficient. Define

$$
S_\ell=
\sum_{r=0}^{R-2}
\overline{\widehat b_{\ell,r}}
\widehat b_{\ell,r+1},
$$

and

$$
\boxed{
\widetilde z_\ell=
\frac{S_\ell}{|S_\ell|}.
}
$$

In exact arithmetic,

$$
S_\ell=(R-1)|b_{\ell,0}|^2z_\ell,
$$

so

$$
\widetilde z_\ell=z_\ell.
$$

If

$$
\widehat b_r=bz^r+e_r,
\qquad
|e_r|\le\varepsilon,
$$

then

$$
\left|
\frac{
\sum_r\overline{\widehat b_r}\widehat b_{r+1}
}{
\left|\sum_r\overline{\widehat b_r}\widehat b_{r+1}\right|
}
-z
\right|
\le
4\frac{\varepsilon}{|b|}
+2\left(\frac{\varepsilon}{|b|}\right)^2
$$

whenever the denominator remains nonzero.

The unused offsets also give the validation residual

$$
\boxed{
\nu_\ell=
\frac{
\left(\sum_r|\widehat b_{\ell,r+1}-\widetilde z_\ell\widehat b_{\ell,r}|^2\right)^{1/2}
}{
\left(\sum_r|\widehat b_{\ell,r}|^2\right)^{1/2}
}.
}
$$

## 7. Branch lifting

Normalize the aliased estimate by

$$
\bar u_\ell=
\frac{\widehat u_\ell}{|\widehat u_\ell|}.
$$

Its candidate roots are

$$
\rho_{\ell,k}
=
\exp\left(
\frac{i(\arg\bar u_\ell+2\pi k)}{N}
\right),
\qquad
0\le k<N.
$$

Choose the candidate nearest $\widetilde z_\ell$.

If $\rho_\ell$ is the candidate continuously associated with the true $z_\ell$ and

$$
|\widetilde z_\ell-z_\ell|
+|\rho_\ell-z_\ell|
<
\sin\left(\frac{\pi}{N}\right),
$$

then the nearest candidate is uniquely $\rho_\ell$.

This gives an oracle-equivalence statement. Under the branch margin, the self-calibrated method selects exactly the same branch as an oracle that knows the true jump neighborhood.

## 8. One-order root gain

If

$$
|\bar u-u|\le\eta<2,
$$

then the associated roots satisfy

$$
\boxed{
|\rho-z|
\le
2\sin\left(
\frac1N\arcsin\frac\eta2
\right)
\le
\frac2N\arcsin\frac\eta2.
}
$$

Therefore, if

$$
|\widehat u-u|=O(N^{-p-1})
$$

and the correct branch is selected, then

$$
\boxed{
|\widehat z-z|=O(N^{-p-2}).
}
$$

The edge-location error has the same order.

## 9. Exact self-calibration theorem

Assume the smooth packet is bandlimited below the first moment used by the recovery algorithm. Suppose the edge count is bounded, jump amplitudes are nonzero, locations are separated, enough moments are available, and one tested decimation has distinct aliased nodes.

Then exact arithmetic recovers

$$
L,
\quad
u_\ell=z_\ell^N,
\quad
z_\ell,
\quad
\tau_\ell,
\quad
a_\ell,
\quad
j,
\quad
s,
$$

without externally supplied jump neighborhoods.


## 10. Explicit finite innovation budget

Assume the exact bandlimited control model and $L\le L_{\max}$. Choose $q_0N$ above the smooth bandwidth and take

$$
\mathcal I_0=\{(q_0+q)N:0\le q\le2L_{\max}\}
$$

and

$$
\mathcal I_1=\{(q_0+q)N+1:0\le q<L_{\max}\}.
$$

The base channel contains $2L_{\max}+1$ moments. Its Hankel matrix has exact rank $L$, so it determines the unknown order and the aliased nodes. The adjacent channel contains $L_{\max}$ moments and determines the coefficient products $b_{\ell,0}z_\ell$. Since the base channel gives $b_{\ell,0}$,

$$
z_\ell=\frac{b_{\ell,1}}{b_{\ell,0}}
$$

is recovered without a supplied branch neighborhood. The amplitudes follow from

$$
a_\ell=b_{\ell,0}u_\ell^{-q_0}.
$$

Therefore the exact high-frequency innovation budget is

$$
\boxed{
|\mathcal I_0|+|\mathcal I_1|=3L_{\max}+1.
}
$$

For $L_{\max}=6$, the implementation uses nineteen high-frequency coefficients, recovers the unknown order as four, and obtains maximum location and jump errors below $10^{-14}$. The count is an explicit upper bound for this construction, not a minimality theorem.

## 11. Perturbed theorem

For a non-bandlimited smooth packet with the stated Fourier-tail bound, assume a uniform Hankel gap, uniform local inverse bounds for the Prony and coefficient systems, nonzero offset coefficients, and the branch margin.

Then, for sufficiently large $N$,

$$
\widehat L=L,
$$

$$
\max_\ell
|\widehat\tau_\ell-\tau_\ell|_{\mathbb T}
\le
C_\tau N^{-p-2},
$$

and

$$
\max_\ell
|\widehat a_\ell-a_\ell|
\le
C_aN^{-p-1}.
$$

## 12. Gibbs-free synthesis

Let $A_M$ be a bounded reconstruction operator for the smooth class. Define

$$
\boxed{
\widehat f_M
=
A_M(f-\widehat j)+\widehat j.
}
$$

Then

$$
f-\widehat f_M
=
(s-A_Ms)
+
(I-A_M)(j-\widehat j),
$$

so

$$
\boxed{
\|f-\widehat f_M\|
\le
\|s-A_Ms\|
+
(1+\|A_M\|)\|j-\widehat j\|.
}
$$

The final reconstruction error is controlled by the smooth approximation error and the edge-parameter error. There is no persistent Gibbs term because the recovered edge is synthesized in its native coordinate rather than truncated in the global Fourier basis.

## 13. Oracle benchmark

Across four smooth-tail indices and seven decimation scales, the maximum node-set distance between the oracle branch and the self-calibrated branch was

$$
2.22\times10^{-16}.
$$

For the $p=2$ benchmark, the principal root produced angular errors between roughly $2.4$ and $3.1$ radians. The oracle and self-calibrated branches produced identical errors ranging from

$$
5.16\times10^{-4}
$$

down to

$$
1.08\times10^{-7}.
$$

## 14. Random stress family

One hundred deterministic random signals were generated under the theorem's separation and amplitude conditions. Their unknown jump counts ranged from two to five. Their smooth backgrounds used four different power-tail indices.

The algorithm recovered the correct jump count in all one hundred cases. Every maximum location error was below $10^{-3}$. The median error was

$$
1.19\times10^{-6},
$$

and the largest was

$$
2.84\times10^{-4}.
$$

This is a finite numerical certificate. It is not a universal probability theorem.

## 15. Main end-to-end example

True jump locations:

$$
(0.42,\ 1.37,\ 2.85,\ 4.62).
$$

True jumps:

$$
(1,\ -0.65,\ 0.40,\ -0.75).
$$

The non-bandlimited smooth packet is

$$
s(x)=0.35e^{0.7\cos x}+0.2\sin(2x)-0.15\cos(5x).
$$

With decimation $N=10$, six offset channels, and twenty-two samples per channel, the algorithm recovered the four locations to displayed machine precision. The order gap was

$$
3.8207\times10^{10},
$$

and the validation score was

$$
1.0408\times10^{-11}.
$$

For the power-tail reconstruction example:

$$
\begin{aligned}
\text{raw Fourier RMSE}&=4.7716\times10^{-2},\\
\text{Fejer RMSE}&=6.6610\times10^{-2},\\
\text{resolved RMSE}&=4.8374\times10^{-7},\\
\text{resolved maximum error}&=6.7934\times10^{-6}.
\end{aligned}
$$

## 16. Higher jump jets

For higher-order jump data, the moments have the confluent form

$$
m_n=
\sum_{\ell=1}^{L}z_\ell^nP_\ell(n)+e_n,
$$

where $P_\ell$ is a polynomial. On offset channels, the highest-degree confluent coefficient has the form

$$
\gamma_{\ell,r,d}=C_\ell z_\ell^r.
$$

Therefore

$$
\boxed{
\frac{\gamma_{\ell,1,d}}{\gamma_{\ell,0,d}}=z_\ell.
}
$$

The same internal phase lift extends to piecewise-polynomial and higher jump-jet models when the leading singular coefficient is nonzero.

## 17. What is new in the theorem package

The individual ingredients have substantial prior literatures. The field-facing contribution developed here is their rate-preserving composition for a piecewise-smooth Fourier model:

1. unknown jump count from the same Fourier data
2. decimated algebraic inversion
3. internal offset-channel branch selection
4. proof of equality with the oracle branch under a checkable margin
5. preservation of the decimated one-order location gain
6. an a posteriori validation residual
7. native edge synthesis with an explicit Gibbs-free error bound

## 18. Boundaries

The theorem does not claim:

- separation-free stability
- arbitrary two-dimensional edge curves
- unbounded jump count
- a general blind measurement theorem
- a minimax noisy recovery theorem
- model-free exponential convergence from Fourier data
- established historical priority for the full package

The full implementation passed

$$
\boxed{31/31\text{ named checks}.}
$$

It generated forty vector figures, forty matching PNGs, all tables, and the machine-readable result ledger from one Python file.
