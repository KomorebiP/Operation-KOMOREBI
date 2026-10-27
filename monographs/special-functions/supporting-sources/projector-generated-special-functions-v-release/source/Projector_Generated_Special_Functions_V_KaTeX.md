# Projector-Generated Special Functions V

## Core generated function

Let

$$
\alpha=\frac{2a-1}{\beta}>0.
$$

The normalized squarefree depth-time kernel converges after carrier removal to

$$
\mathfrak A_\alpha(h,\eta)
=
\frac{\Gamma(\alpha+i\eta)}{\Gamma(\alpha)}
\operatorname{sech}^{\alpha+i\eta}\left(\frac h2\right).
$$

## Log-Gamma packet

$$
g_\alpha(y)
=
\frac{1}{\sqrt{\Gamma(\alpha)}}
\exp\left(\frac{\alpha y}{2}-\frac{e^y}{2}\right).
$$

Its centered ambiguity function is exactly

$$
\int_{\mathbb R}
 g_\alpha\left(y+\frac h2\right)
 g_\alpha\left(y-\frac h2\right)
 e^{i\eta y}\,dy
=
\mathfrak A_\alpha(h,\eta).
$$

## Fourier and spectral laws

$$
\widehat g_\alpha(\omega)
=
\frac{2^{\alpha/2-i\omega}\Gamma(\alpha/2-i\omega)}
{\sqrt{2\pi\Gamma(\alpha)}}.
$$

$$
\rho_\alpha(\omega)
=
\frac{2^{\alpha-1}}{\pi\Gamma(\alpha)}
\left|\Gamma\left(\frac\alpha2+i\omega\right)\right|^2.
$$

$$
\int_{\mathbb R}\rho_\alpha(\omega)e^{i\omega h}\,d\omega
=
\operatorname{sech}^{\alpha}(h/2).
$$

## Wigner function

$$
W_\alpha(y,\omega)
=
\frac{2e^{\alpha y}}{\pi\Gamma(\alpha)}
K_{2i\omega}(e^y).
$$

## Uncertainty

$$
\operatorname{Var}Y=\psi_1(\alpha),
\qquad
\operatorname{Var}P=\frac\alpha4.
$$

$$
\Delta Y\Delta P
=
\frac12\sqrt{\alpha\psi_1(\alpha)}
>\frac12.
$$

## Laguerre-Meixner duality

$$
\Lambda_{n,\alpha}(y)
=
\sqrt{\frac{n!}{\Gamma(n+\alpha)}}
 e^{\alpha y/2-e^y/2}
 L_n^{(\alpha-1)}(e^y).
$$

$$
\widehat\Lambda_{n,\alpha}(\omega)
=
 i^n\widehat g_\alpha(\omega)p_{n,\alpha}(\omega).
$$

## Fractional depth

For $r>0$ and $a>1$,

$$
C_{a,\beta,\chi}(r,t)
=
\sum_{j=0}^{\infty}
(-1)^j\binom rj
\frac{1}{L(a+\beta j+it,\chi)}.
$$

$$
\frac{\partial}{\partial r}C_{a,\beta,\chi}(r,t)
=
-\sum_{m=1}^{\infty}\frac1m
C_{a+m\beta,\beta,\chi}(r,t).
$$

## RH boundary

The positive theory above is unconditional. The remaining principal signed problem is

$$
|c_k|^2
\le
C_\varepsilon k^\varepsilon E_k.
$$

This inequality is equivalent to RH through the classical sequential criterion and the proved asymptotic $E_k\asymp k^{-3/2}$. It is not proved in this paper.
