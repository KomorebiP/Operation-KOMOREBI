# Information beyond total spin

**Komorebi P. · Reviewed reading edition · 13 November 2026**

This exact example asks whether the integral-symmetry assumption supplies
response information beyond a three-query cache, spin conservation and a
common spectral interval. It does. The comparison concerns admissible
operators; it is not a runtime benchmark.

## The structured model and its uncertainty

Use the [normal form](normal-form.md) with
$t=0$, $K=T_1/8$ and $C=I_5/64$. Let $H_0$ be the resulting matrix in
determinant coordinates, and take $b=e_0=(1,0,\ldots,0)^{\mathsf T}$.
The source is a pure doublet: $S^2b=3b/4$.

The positive definite $C$ supplies an explicit positive-integral
representative. The commutator norm equals the eigenvalue diameter of its
symmetric coefficient. The five $T_a$ have squared diameters
$4,9,4,4,4$, so

$$
\|H_0\|_2\le\frac14+\frac{25}{64}=\frac{41}{64}.
$$

At $E=0$ and $\eta=1$, in the example's fixed energy units,

$$
g_0=b^{\mathsf T}(iI-H_0)^{-1}b
=-\frac{107}{1157}-\frac{1146}{1157}i.
$$

Let the observed raw cache be $Y_0=H_0V$, with $V$ from the
[recovery theorem](three-queries.md). Allow aggregate action error
$\epsilon=1/4096$ and real source error $\delta=1/8192$. Since the
least-squares residual is zero and $\|b\|=1$, the response radius is

$$
R_g=\frac{\sqrt{20}}{4096}
+\frac{16385}{67108864}<0.001336.
$$

Every compatible family member is positive in the integral-Gram sense,
because $\|C-C_0\|_2\le r_H/4<1/64$. It also has spectrum in
$[-1,1]$, because $41/64+r_H<1$. Thus adding these two restrictions
does not remove the compatible set used by the structured enclosure.

## An indistinguishable spin-preserving operator

Keep the exact same source, cache, energy, broadening, spin operator and
spectral interval. Define

$$
u=(5/8,0,-1/8,-3/8,1/8,0,1/4,0,0)^{\mathsf T},
\qquad H_1=H_0+\frac{uu^{\mathsf T}}{4u^{\mathsf T}u}.
$$

Direct calculation gives $V^{\mathsf T}u=0$, $u^{\mathsf T}u=5/8$,
and $q^{\mathsf T}u=0$ for
$q=(0,0,1,0,-1,0,1,0,0)^{\mathsf T}$. Since
$S^2=3I_9/4+qq^{\mathsf T}$, it follows that

$$
H_1V=H_0V,\qquad [H_1,S^2]=0,
\qquad \|H_1\|_2\le\frac{57}{64}<1.
$$

The same cache is therefore compatible with a larger class of real
symmetric, spin-preserving operators. Within that class, $H_1$ has response

$$
g_1=-\frac{9186358980826208}{40332559606654033}
-\frac{37472614526567424}{40332559606654033}i.
$$

The pi-scaled source-resolved density is $\ell=-\operatorname{Im}(g)$.
Its difference between the two operators is exactly

$$
|\ell_1-\ell_0|
=\frac{2865298301987012250}{46664771464898716181}
\approx0.06140174>R_g.
$$

The inequality is checked using an outward rational square-root bound;
the printed decimals are explanatory approximations. Hence the structured
response disk excludes $g_1$, even though its cache and spin/spectral
information agree with those of $H_0$.

## Interpretation and limits

The perturbation is nonzero. If $H_1$ belonged to the integral-symmetry
family, its identical cache would contradict injectivity of the three-probe
map. Thus $H_1$ lies outside that family, while remaining inside the
explicit larger comparison class.

This is a strict information separation. It does not compare complete
algorithm costs with an observable-specific Krylov method. The tensor for
$H_0$ is an algebraic positive-integral representative; realization by
actual Coulomb orbitals is not established. The two nonzero error caps in
this example are assumptions, rather than measured errors of the original
H10 neutral state.

The example also explains why a zero residual alone cannot verify a model:
an outside-family operator can produce the same cache. The structural
assumption and justified error caps are essential to interpreting the
enclosure.
