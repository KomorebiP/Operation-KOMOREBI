# Complex Signal and Image Benchmark for Projector-Resolved Gibbs Reconstruction

**Author:** Komorebi P.

## 1. Purpose

The benchmark asks whether the projector-resolved Gibbs reconstruction program survives harder tests than a single interval edge. It includes:

- multi-jump periodic signals
- analytic and algebraic Fourier tails
- chirps, bursts, and rough backgrounds
- noise and near-collision sweeps
- unknown jump counts from 2 through 10
- two-dimensional rectangles, disks, ellipses, and bars
- out-of-dictionary stars, text, and nested rings
- four exploratory natural images

Exact-model results and exploratory results are reported separately.

## 2. One-dimensional model

Write

$$
f=s+j
$$

on the periodic domain $\mathbb T=\mathbb R/(2\pi\mathbb Z)$. The edge packet is piecewise constant with

$$
Dj=\sum_{\ell=1}^{L}a_\ell\delta_{\tau_\ell},
\qquad
\sum_{\ell=1}^{L}a_\ell=0.
$$

The derivative moments are

$$
m_n=2\pi i n\widehat f(n)
=\sum_{\ell=1}^{L}a_\ell z_\ell^n+e_n,
\qquad
z_\ell=e^{-i\tau_\ell}.
$$

For decimation factor $N$ and offset $r$,

$$
m_{(q_0+q)N+r}
=
\sum_{\ell=1}^{L}b_{\ell,r}u_\ell^q+e_{(q_0+q)N+r},
$$

where

$$
u_\ell=z_\ell^N,
\qquad
b_{\ell,r}=a_\ell z_\ell^{q_0N+r}.
$$

The adjacent offset relation is

$$
\boxed{b_{\ell,r+1}=z_\ell b_{\ell,r}}.
$$

This relation identifies the physical phase that is lost by decimation.

## 3. Resolved synthesis

After recovering an edge packet $\widehat j$, the final reconstruction is

$$
\boxed{
\widehat f_M=A_M(f-\widehat j)+\widehat j
}.
$$

If $\widehat j=j$, then

$$
f-\widehat f_M=s-A_Ms.
$$

The discontinuity is synthesized directly rather than approximated by a finite global Fourier series.

## 4. Complex one-dimensional cases

The controlled cases are:

1. eight jumps with a bandlimited background
2. six jumps with an analytic background
3. six jumps with an algebraic Fourier tail

All three recover the correct jump count.

The stress cases are:

1. six jumps on a chirp
2. six jumps on localized bursts
3. four jumps on a rough background

The burst case returns nine jumps rather than six. This failure is retained as a negative control.

Across all six named cases, the median ratio

$$
\frac{\operatorname{RMSE}(\widehat f_{\mathrm{resolved}},f)}
{\operatorname{RMSE}(S_Nf,f)}
$$

is

$$
\boxed{2.5619\times10^{-4}}.
$$

## 5. Noise and collision boundary

For the six-jump analytic case, the recovery criterion is

$$
\max_\ell d_{\mathbb T}(\widehat\tau_\ell,\tau_\ell)<10^{-3},
\qquad
\max_\ell|\widehat a_\ell-a_\ell|<5\times10^{-3}.
$$

The success rate stays at one through moment noise $\sigma=5\times10^{-2}$, drops sharply at $\sigma=10^{-1}$, and is zero at $\sigma=2\times10^{-1}$.

For near-colliding jumps, a fixed moment perturbation $\sigma=10^{-3}$ is applied while the separation decreases to $10^{-3}$. The smallest sampled Vandermonde singular value falls and the amplitude error rises. This is the expected stability boundary.

## 6. Two-dimensional finite dictionary

The image model is

$$
y=Bc+D\alpha+\eta.
$$

Here $B$ is a low-frequency DCT background and $D$ is a finite dictionary of geometric masks. Let

$$
P_B=B(B^\mathsf TB)^{-1}B^\mathsf T,
\qquad
R_B=I-P_B.
$$

Then

$$
R_By=(R_BD)\alpha+R_B\eta.
$$

Set

$$
A=R_BD.
$$

Every $s$-sparse edge vector is uniquely determined exactly when

$$
\boxed{
\ker A\cap\{h:\|h\|_0\le2s\}=\{0\}
}
$$

or equivalently

$$
\boxed{\operatorname{spark}(A)>2s}.
$$

The implemented dictionary contains 318 residualized atoms:

- rectangles
- disks
- ellipses
- horizontal bars
- vertical bars

## 7. Exact geometric image results

Three named images are built from the same dictionary used for recovery:

- mixed geometry with four atoms
- curved shapes with three atoms
- thin structures with four atoms

The exact support is selected in all three cases.

The median ratio of dictionary-resolved RMSE to raw Fourier RMSE is

$$
\boxed{0.4169}.
$$

In forty additional random finite-dictionary images, the selected support matches the true support in every case under the deterministic benchmark settings.

## 8. Out-of-dictionary results

The following images are not represented by the finite dictionary:

- a seven-point star
- the word KOMOREBI over a gradient
- nested rings

The dictionary-resolved method is no longer uniformly competitive. This is a model failure, not an exact theorem failure. The next mathematical target is a geometry-adaptive packet family with a controlled complexity penalty.

## 9. Natural images

Four scikit-image examples are used as exploratory tests:

- camera
- coins
- moon
- page

Methods compared are raw Fourier, Fejer, Lanczos, Haar thresholding, and total variation. The best method depends on the image. No exact recovery theorem is claimed for these images.

## 10. Natural-background hybrid

A smoothed camera image is used as a realistic background. Three exact geometric packets are added. The finite dictionary selector chooses five atoms rather than the three true atoms. The background still contains structure outside the low-order DCT model, and the selector uses additional geometry to explain it.

This shows that a stronger background model is as important as a stronger edge model.

## 11. Main conclusion

The benchmark supports four conclusions.

1. The self-calibrating polyphase method remains strong on several complex one-dimensional finite-rate signals.
2. Unknown-order recovery fails when high-frequency background bursts imitate edge moments.
3. A finite geometric packet dictionary can substantially reduce boundary error when the true geometry belongs to the dictionary.
4. The same fixed dictionary does not provide universal image recovery.

The next theorem should bound model mismatch:

$$
\|f-\widehat f\|
\le
\|s-A_Ms\|
+
C_1\inf_{\|\alpha\|_0\le q}\|j-D\alpha\|
+
C_2\,\text{noise}
+
C_3\,\text{selection error}.
$$

The full PDF, figures, tables, JSON ledger, and single Python implementation are included in the release.
