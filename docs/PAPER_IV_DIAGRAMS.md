# Paper IV: figure and atlas descriptions

These reading aids describe the 6 chapter figures, including their arrows, axes, scales and matrix entries. They retain the assumptions and example scope of the manuscript.

[Read the chapters](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/index.html) · [Accessibility and reading options](ACCESSIBILITY.md)

The [26 HTML atlas plates](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/atlas/index.html) already provide the original atlas drawings, all drawing labels, structured tables and selectable equations.

<a id="figure-1-exact-residue-lanes-for-order-three"></a>
<h2 id="figure-01" tabindex="-1">Figure 1: Exact residue lanes for order three</h2>

The horizontal axis is exponent $m$, from 0 through 17, and the vertical lanes are $j=0,1,2$. Lane 0 contains 0, 3, 6, 9, 12, 15; lane 1 contains 1, 4, 7, 10, 13, 16; lane 2 contains 2, 5, 8, 11, 14, 17. Each labeled dot is an exponent address. Equal spacing and lane height carry no information about Taylor coefficient size.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/cyclic-projection.html#L330)

<a id="figure-2-the-signed-shift-of-order-four"></a>
<h2 id="figure-02" tabindex="-1">Figure 2: The signed shift of order four</h2>

Read the cycle in order:

$$
e_0\to e_1\to e_2\to e_3\to e_0.
$$

The first three arrows have weight $+1$ and the closing $e_3\to e_0$ arrow has weight $-1$. The four-by-four matrix uses target rows and source columns numbered 0 through 3. The table gives every entry. Four applications traverse the negative edge once, giving $J_4^4=-I$.

<table>
<caption>Figure 2: The signed shift of order four</caption>
<thead><tr><th scope="col">Target / source</th><th scope="col">0</th><th scope="col">1</th><th scope="col">2</th><th scope="col">3</th></tr></thead>
<tbody>
<tr><th scope="row">0</th><td>0</td><td>0</td><td>0</td><td>-1</td></tr>
<tr><th scope="row">1</th><td>1</td><td>0</td><td>0</td><td>0</td></tr>
<tr><th scope="row">2</th><td>0</td><td>1</td><td>0</td><td>0</td></tr>
<tr><th scope="row">3</th><td>0</td><td>0</td><td>1</td><td>0</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/finite-algebra.html#L755)

<a id="figure-3-two-normalizations-of-secant-coefficients"></a>
<h2 id="figure-03" tabindex="-1">Figure 3: Two normalizations of secant coefficients</h2>

The columns use $n=0$ through 4. The upper row is the block exponential coefficient $P_{2,n}(1)$, and the lower row is the ordinary coefficient of $z^{2n}$ in $\sec z$. Dividing each upper value by $(2n)!$ gives the lower value. Both rows encode the same five terms of the secant function.

<table>
<caption>Figure 3: Two normalizations of secant coefficients</caption>
<thead><tr><th scope="col">Coefficient / index</th><th scope="col">0</th><th scope="col">1</th><th scope="col">2</th><th scope="col">3</th><th scope="col">4</th></tr></thead>
<tbody>
<tr><th scope="row">Block exponential coefficient</th><td>1</td><td>1</td><td>5</td><td>61</td><td>1385</td></tr>
<tr><th scope="row">Ordinary Taylor coefficient</th><td>1</td><td>1/2</td><td>5/24</td><td>61/720</td><td>1385/40320</td></tr>
</tbody>
</table>

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/reciprocal-powers.html#L923)

<a id="figure-4-reciprocal-order-parameter-polynomials"></a>
<h2 id="figure-04" tabindex="-1">Figure 4: Reciprocal-order parameter polynomials</h2>

The horizontal axis is reciprocal order $r$ on $[0,2]$, and the vertical axis is block coefficient. The straight curve evaluates $P_{2,1}(r)=r$; the curved one evaluates $P_{2,2}(r)=r(3r+2)$. Both begin at zero. At $r=1$ the marked points are 1 and 5; at $r=2$ the formulas give 2 and 16. The curves evaluate exact formulas; they are not fitted parameter estimates.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/logarithmic-derivatives.html#L1232)

<a id="figure-5-four-zeros-become-one-reduced-zero"></a>
<h2 id="figure-05" tabindex="-1">Figure 5: Four zeros become one reduced zero</h2>

The left panel has horizontal axis $\operatorname{Re}z$ and vertical axis $\operatorname{Im}z$. For $m=0,1,2$, put

$$
\tau_m=\sqrt{2}\,\pi\left(m+\frac12\right).
$$

The twelve dots are $\pm\tau_m$ and $\pm i\tau_m$. The right panel sends each group of four to

$$
\lambda_m=\tau_m^4=4\pi^4\left(m+\frac12\right)^4
$$

on a positive horizontal axis with logarithmic scale. Its three labeled positions correspond to $m=0,1,2$. This exact order-four model uses

$$
D_4(z)=\cos\left(\frac{z}{\sqrt{2}}\right)\cosh\left(\frac{z}{\sqrt{2}}\right).
$$

It does not classify finite exceptional zeros at other orders.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/zero-geometry.html#L1714)

<a id="figure-6-finite-partial-sums-of-zero-moments"></a>
<h2 id="figure-06" tabindex="-1">Figure 6: Finite partial sums of zero moments</h2>

Each horizontal axis counts $M$ retained reduced zeros, from 1 through 40, where

$$
\lambda_k=\pi^2\left(k+\frac12\right)^2.
$$

The left vertical axis is the sum of reciprocal zeros,

$$
\sum_{k=0}^{M-1}\lambda_k^{-1},
$$

and the right is the sum of their squared reciprocals,

$$
\sum_{k=0}^{M-1}\lambda_k^{-2}.
$$

Both vertical scales are linear. The solid curves are finite numerical sums, while the dashed levels are the exact infinite sums $1/2$ and $1/6$. The second sum approaches its limit much faster because the larger reciprocal powers give less weight to distant zeros. The exact levels come from the product and coefficient identities.

[Figure and surrounding text](https://komorebip.github.io/Operation-KOMOREBI/read/paper-iv/products-and-moments.html#L2266)
