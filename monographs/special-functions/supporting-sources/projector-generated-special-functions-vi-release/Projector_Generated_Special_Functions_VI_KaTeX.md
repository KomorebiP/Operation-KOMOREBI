# Projector-Generated Special Functions VI

## Meixner Shape Semigroups, Beta-Binomial Packet Refinement, Polynomial Martingales, and Gamma-Sech Berezin Kernels

**Author:** Komorebi P.

## 1. Log-Gamma packet

For \(\alpha>0\), define

$$
g_\alpha(y)
=
\Gamma(\alpha)^{-1/2}
\exp\left(\frac{\alpha y}{2}-\frac{e^y}{2}\right).
$$

The substitution \(u=e^y\) gives

$$
\int_{\mathbb R}|g_\alpha(y)|^2\,dy=1.
$$

## 2. Cross-shape ambiguity

For \(\alpha,\beta>0\),

$$
\mathcal A_{\alpha,\beta}(h,\eta)
=
\int_{\mathbb R}
g_\alpha\left(y+\frac h2\right)
g_\beta\left(y-\frac h2\right)e^{i\eta y}\,dy.
$$

Its exact closed form is

$$
\boxed{
\mathcal A_{\alpha,\beta}(h,\eta)
=
e^{(\alpha-\beta)h/4}
\frac{\Gamma((\alpha+\beta)/2+i\eta)}
{\sqrt{\Gamma(\alpha)\Gamma(\beta)}}
\operatorname{sech}^{(\alpha+\beta)/2+i\eta}\left(\frac h2\right).
}
$$

At the origin,

$$
F(\alpha,\beta)
=
\frac{\Gamma((\alpha+\beta)/2)}
{\sqrt{\Gamma(\alpha)\Gamma(\beta)}}.
$$

It obeys

$$
0<F(\alpha,\beta)\le1,
$$

with equality only when \(\alpha=\beta\). The local shape metric is

$$
\boxed{g_{\alpha\alpha}=\frac14\psi_1(\alpha).}
$$

## 3. Exact factorization

Define

$$
p_{\alpha,\beta}(h)
=
\frac{\Gamma(\alpha+\beta)}
{2^{\alpha+\beta}\Gamma(\alpha)\Gamma(\beta)}
e^{(\alpha-\beta)h/2}
\operatorname{sech}^{\alpha+\beta}\left(\frac h2\right)
$$

and

$$
\rho_s(\eta)
=
\frac{2^{s-1}}{\pi\Gamma(s)}
\left|\Gamma\left(\frac s2+i\eta\right)\right|^2.
$$

Then

$$
\boxed{
\frac1{2\pi}
|\mathcal A_{\alpha,\beta}(h,\eta)|^2
=
p_{\alpha,\beta}(h)\rho_{\alpha+\beta}(\eta).
}
$$

The variable

$$
u=\frac{e^h}{1+e^h}
$$

has the Beta\((\alpha,\beta)\) law under \(p_{\alpha,\beta}\).

## 4. Shape convolution semigroup

The characteristic function of \(\rho_s\) is

$$
\widehat\rho_s(h)=\operatorname{sech}^s(h/2).
$$

Therefore

$$
\boxed{\rho_{s+t}=\rho_s*\rho_t.}
$$

The two-step density recurrence is

$$
\boxed{
\rho_{s+2}(\eta)
=
\frac{s^2+4\eta^2}{s(s+1)}\rho_s(\eta).
}
$$

## 5. Levy generator and Bernoulli cumulants

The Levy-Khintchine exponent is

$$
\boxed{
-\log\cosh(\xi/2)
=
\int_0^\infty
\frac{\cos(\xi x)-1}{x\sinh(\pi x)}\,dx.
}
$$

The shape-\(s\) Levy density is

$$
\boxed{
\nu_s(dx)=\frac{s}{2|x|\sinh(\pi|x|)}\,dx.
}
$$

The generator is

$$
(\mathcal Lf)(\eta)
=
\int_0^\infty
\frac{f(\eta+x)+f(\eta-x)-2f(\eta)}
{2x\sinh(\pi x)}\,dx.
$$

The odd cumulants vanish. The even cumulants are

$$
\boxed{
\kappa_{2m}
=
s\frac{(2^{2m}-1)|B_{2m}|}{2m}.
}
$$

## 6. Meixner-Pollaczek packets

Let

$$
p_{n,s}(x)
=
\sqrt{\frac{n!}{(s)_n}}
P_n^{(s/2)}(x,\pi/2).
$$

The packets are orthonormal for the density \(\rho_s\).

### Two-child refinement

$$
\boxed{
p_{n,\alpha+\beta}(x+y)
=
\sum_{r=0}^n
C_{n,r}^{\alpha,\beta}
 p_{r,\alpha}(x)
 p_{n-r,\beta}(y),
}
$$

with

$$
\boxed{
C_{n,r}^{\alpha,\beta}
=
\sqrt{
\frac{n!(\alpha)_r(\beta)_{n-r}}
{(\alpha+\beta)_n r!(n-r)!}
}.
}
$$

The squared coefficients form the beta-binomial law

$$
|C_{n,r}^{\alpha,\beta}|^2
=
\binom nr
\frac{(\alpha)_r(\beta)_{n-r}}
{(\alpha+\beta)_n},
$$

so

$$
\sum_{r=0}^n|C_{n,r}^{\alpha,\beta}|^2=1.
$$

### Many-child refinement

For \(A=\sum_j\alpha_j\),

$$
\boxed{
p_{n,A}\left(\sum_jx_j\right)
=
\sum_{\sum r_j=n}
\sqrt{
\frac{n!\prod_j(\alpha_j)_{r_j}}
{(A)_n\prod_jr_j!}
}
\prod_jp_{r_j,\alpha_j}(x_j).
}
$$

The squared coefficients form the Dirichlet-multinomial law. The formula is independent of the order in which binary refinements are performed.

## 7. Polynomial martingales and transfer singular values

Let \(X_s\sim\rho_s\) have independent Meixner increments. Then

$$
\boxed{
\mathbb E\left[
P_n^{((s+t)/2)}(X_{s+t},\pi/2)
\mid X_s
\right]
=
P_n^{(s/2)}(X_s,\pi/2).
}
$$

In orthonormal coordinates,

$$
\boxed{
T_{s,t}p_{n,s+t}
=
\sigma_n(s,t)p_{n,s},
\qquad
\sigma_n(s,t)=\sqrt{\frac{(s)_n}{(s+t)_n}}.
}
$$

The cocycle is

$$
\sigma_n(s,t)\sigma_n(s+t,u)=\sigma_n(s,t+u).
$$

For large degree,

$$
\sigma_n(s,t)
\sim
\sqrt{\frac{\Gamma(s+t)}{\Gamma(s)}}n^{-t/2}.
$$

Hence \(T_{s,t}\) is compact for every \(t>0\), and

$$
T_{s,t}\in S_p
\quad\Longleftrightarrow\quad
pt>2.
$$

## 8. Coherent-state frame

Define

$$
\psi_{\alpha,u,\eta}(y)
=
e^{i\eta(y-u/2)}g_\alpha(y-u).
$$

The overlap is

$$
\boxed{
\langle\psi_{\alpha,u,\eta},\psi_{\beta,v,\nu}\rangle
=
e^{i(\nu u-\eta v)/2}
\mathcal A_{\alpha,\beta}(v-u,\nu-\eta).
}
$$

The frame resolves the identity

$$
\boxed{
\frac1{2\pi}
\int_{\mathbb R^2}
|\psi_{\alpha,u,\eta}\rangle
\langle\psi_{\alpha,u,\eta}|\,du\,d\eta
=I.
}
$$

## 9. Berezin transform

The anti-Wick operator is

$$
\operatorname{Op}_\alpha(F)
=
\frac1{2\pi}
\int F(z)|\psi_z\rangle\langle\psi_z|\,dz.
$$

Its lower symbol is convolution with

$$
\mathcal B_\alpha(h,\eta)
=
\frac1{2\pi}|\mathcal A_{\alpha,\alpha}(h,\eta)|^2
=
p_\alpha(h)q_\alpha(\eta),
$$

where

$$
p_\alpha(h)
=
\frac{\Gamma(\alpha+1/2)}
{2\sqrt\pi\Gamma(\alpha)}
\operatorname{sech}^{2\alpha}(h/2)
$$

and

$$
q_\alpha(\eta)=\rho_{2\alpha}(\eta).
$$

The Fourier multiplier is

$$
\boxed{
\widehat{\mathcal B}_\alpha(\xi,x)
=
\frac{|\Gamma(\alpha+i\xi)|^2}{\Gamma(\alpha)^2}
\operatorname{sech}^{2\alpha}(x/2).
}
$$

It is strictly positive on the real dual plane. The transform is injective, while its inverse is unbounded.

The exact variances are

$$
\operatorname{Var}(H)=2\psi_1(\alpha),
\qquad
\operatorname{Var}(\Omega)=\frac\alpha2.
$$

## 10. Gaussian heat fixed point

If

$$
Z_\alpha=\sqrt{\frac\alpha2}H_\alpha,
\qquad
W_\alpha=\sqrt{\frac2\alpha}\Omega_\alpha,
$$

then

$$
\boxed{
Z_\alpha\Rightarrow N(0,1),
\qquad
W_\alpha\Rightarrow N(0,1).
}
$$

After the same rescaling, the Berezin transform converges to

$$
\boxed{e^{\Delta/2}.}
$$

## 11. Local metric coefficients

$$
\boxed{
g_{\alpha\alpha}=\frac14\psi_1(\alpha),
\qquad
g_{uu}=\frac\alpha4,
\qquad
g_{\eta\eta}=\psi_1(\alpha).
}
$$

## 12. Boundary

The positive semigroup and coherent-state results do not prove the signed Mobius coherence bound. They do not prove the Riemann hypothesis.
