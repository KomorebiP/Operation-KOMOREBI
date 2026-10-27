# A visual atlas of finite resolution

Checkpoint **SF-DISCOVERY-110**. Base checkpoint **SF-DISCOVERY-100**, source SHA256 `ca4debff6f9653b784b849ccc7519fcf2493a7a24e814658a950a936e8513f21`. Attribution: Komorebi P.

A structural change need not produce a large change in the measurements we can make. A tiny feedback tap can change the order of an entire function. An excluded prime can change the exact arithmetic inverse. A negative atom can destroy positivity of a measure. Each change becomes visible at a different resolution.

This atlas makes those statements quantitative. Its three controls are observation radius, absolute precision and polynomial degree. Each example includes a bound that can be evaluated without trusting the appearance of a curve. The large radii below are sufficient guarantees from conservative estimates. The degree bounds bracket a detection problem. Neither is presented as an optimal threshold.

| Family | Structural difference | Finite observation | Certificate that resolves it |
|---|---|---|---|
| Positive feedback | A nonzero fast tap changes entire order | Values on a fixed complex disk | A sufficient radius for a factor of two separation |
| Arithmetic depth | The excluded prime set changes | Values or finitely many derivatives on a disk | A bracket for the negative depth needed to reach an absolute tolerance |
| Signed sieve | One prime shelf has negative mass | All squared polynomial norms up to a given degree | An explicit rational polynomial with negative norm |

## 1. A weak tap that changes global growth

Let the normalized positive feedback function satisfy

\[
F_\varepsilon'(z)=1+(1-\varepsilon)F_\varepsilon(z/4)^2
 +\varepsilon F_\varepsilon(3z/4)^2,
\qquad F_\varepsilon(0)=0,
\qquad 0\le\varepsilon\le1.
\]

The base theorem gives a unique entire function with nonnegative odd coefficients. At zero weight, the order is \(1/2\). At every positive weight it is

\[
\rho=\frac{\log2}{\log(4/3)}\approx2.40942084.
\]

Thus the order jumps at a parameter value where the entire functions themselves converge uniformly on every compact set.

### The disk has a numerical error budget

Write \(f=f_{3/4}\) for the normalized diagonal function, and
\(f(z)=\sum_{n\ge0}d_nz^{2n+1}\). The inherited tap continuity theorem gives

\[
\sup_{|z|\le R}|F_\varepsilon(z)-F_0(z)|
\le \varepsilon L(R),\qquad
L(R)=\sum_{n\ge1}n d_nR^{2n+1}
=\frac{Rf'(R)-f(R)}2.
\tag{RA-1}
\]

The following elementary certificate makes the unit disk example fully computable. Positive coefficient domination by tangent, followed by \(\sin x\le x\) and \(\cos x\ge1-x^2/2\), gives

\[
f(4/3)\le\tan(4/3)\le12.
\]

For \(N\ge1\) and \(0\le R\le1\), put \(t=3R/4\). If
\((N+2)t^2\le N+1\), then \(n t^{2n+1}\) is nonincreasing for \(n\ge N+1\), and hence

\[
0\le L(R)-\sum_{n=1}^{N}n d_nR^{2n+1}
\le12(N+1)t^{2N+3}.
\tag{RA-2}
\]

Indeed the left side is a sum of \(d_n(4/3)^{2n+1}\) multiplied by \(n t^{2n+1}\). Bound the multiplier by its first value, then use the positive total mass \(f(4/3)\le12\). The coefficients \(d_n\) are rational. With \(N=40\), the exact rational upper bound is less than

\[
L(1)<0.241890267.
\]

The decimal shown here is rounded upward from the rational certificate. Consequently

\[
\boxed{\sup_{|z|\le1}|F_{10^{-12}}(z)-F_0(z)|<2.41890267\times10^{-13},}
\]

although their entire orders are different. If observations have an absolute error allowance at least half this bound, midpoint data can be consistent with both functions throughout the disk. This is an ambiguity under a stated noise allowance, not equality of their exact values.

![A weak tap changes the global order while its normalized compact response stays small. The dashed curve is the analytic Lipschitz envelope.](figures_v11/resolution_01_weak_tap.pdf)

**How to read the figure.** The left curves divide the difference by the tap weight, so the relevant small quantity is the plotted height multiplied by \(\varepsilon\). The right panel records the proved order, which is determined by arbitrarily large radii. The curve computation uses powers through \(z^{201}\), with a normalized analytic omitted-tail bound below \(5.26\times10^{-23}\) on the unit interval. Ordinary floating rounding is separate from that analytic tail bound.

### A radius at which a difference is guaranteed

The base lower-type theorem supplies, for every \(\varepsilon>0\),

\[
\log F_\varepsilon(R)\ge c_\varepsilon(R+3/\varepsilon)^\rho
\ge c_\varepsilon R^\rho\qquad(R\ge2),
\]
\[
c_\varepsilon=\frac{\log2}{(4/\varepsilon+8/3)^\rho}.
\]

For the slow function, the base upper-type construction with \(q=r=1/4\), \(N=2\), yields

\[
\log F_0(R)\le C_0\sqrt R\qquad(R\ge e),
\qquad C_0=e^{-1/2}(1+22\log2)\approx9.85566103.
\]

The value of \(C_0\) comes directly from the earlier explicit constants:
\(V_2=15\log2\), \(\Delta=2\log2\), and \(B_+=5\log2\).
Thus \(V_2+1+\Delta+B_+=1+22\log2\).

Define

\[
R_2(\varepsilon)=\max\left\{
 e,\left(\frac{2C_0}{c_\varepsilon}\right)^{1/(\rho-1/2)},
 \left(\frac{2\log2}{c_\varepsilon}\right)^{1/\rho}\right\}.
\tag{RA-3}
\]

Then, for every \(R\ge R_2(\varepsilon)\),

\[
\boxed{F_\varepsilon(R)\ge2F_0(R).}
\]

To prove this, the last two constraints imply that \(c_\varepsilon R^\rho\) is at least both \(2C_0\sqrt R\) and \(2\log2\). It is therefore at least their half-sum \(C_0\sqrt R+\log2\). Exponentiating proves the claim.

| Tap weight | Difference on the unit disk is at most | Sufficient radius \(R_2\), rounded |
|---|---:|---:|
| \(10^{-3}\) | \(2.419\times10^{-4}\) | \(2.029\times10^5\) |
| \(10^{-6}\) | \(2.419\times10^{-7}\) | \(1.237\times10^9\) |
| \(10^{-9}\) | \(2.419\times10^{-10}\) | \(7.549\times10^{12}\) |
| \(10^{-12}\) | \(2.419\times10^{-13}\) | \(4.608\times10^{16}\) |

The radius column displays the analytic formula approximately. For a certificate use the formula itself or a rigorously rounded upper value. These large numbers reflect the conservatism of the global comparison. They do not mean that observations at all smaller radii fail. The formula grows proportionally to \(\varepsilon^{-\rho/(\rho-1/2)}\) as the tap vanishes.

![Conservative type estimates turn the qualitative change of order into a sufficient observation radius.](figures_v11/resolution_02_growth_resolution.pdf)

## 2. An excluded prime and the precision needed to see it

Fix \(a=\beta=2\), and use the arithmetic depth family

\[
A_Q(s)=\sum_{\substack{n\ge2\\\mu(n)^2=1\\(n,Q)=1}}
 n^{-4}(1-n^{-2})^{2s}.
\]

For a prime \(p\), let \(D_p=A_1-A_p\). This positive difference consists exactly of the squarefree atoms divisible by \(p\). Its largest frequency is

\[
\lambda_p=-2\log(1-p^{-2}),
\]

and its total mass is \(D(4)/(p^4+1)\), where \(D(4)=\zeta(4)/\zeta(8)=105/\pi^4\).

### Exact disk bounds include derivative measurements

For every integer \(k\ge0\) and \(R\ge0\),

\[
\sup_{|s|\le R}|D_p^{(k)}(s)|
\le \lambda_p^k e^{R\lambda_p}\frac{D(4)}{p^4+1}.
\tag{RA-4}
\]

This is the inherited arithmetic inverse theorem, now read as a precision requirement. For fixed \(R\), the envelope is of order \(p^{-4-2k}\). Each additional derivative suppresses the large-prime difference even further in absolute units. This does not rule out methods that rescale derivatives and account for their corresponding noise amplification.

At integer radius \(R=5\), an especially simple rational certificate follows from \(D(4)<\zeta(4)<4/3\):

\[
\boxed{\sup_{|s|\le5}|D_p(s)|
 <\frac{4}{3(p^4+1)}(1-p^{-2})^{-10}.}
\tag{RA-5}
\]

For derivatives, multiply this rational bound by \([2/(p^2-1)]^k\), using \(-\log(1-u)\le u/(1-u)\). Thus this part of the certificate needs no transcendental evaluation at all.

| Excluded prime | Rational upper bound on \(|s|\le5\), rounded upward |
|---|---:|
| 101 | \(1.283\times10^{-8}\) |
| 1009 | \(1.287\times10^{-12}\) |
| 10007 | \(1.330\times10^{-16}\) |

![Arithmetic distinctions shrink rapidly on a bounded window, including in every fixed derivative order.](figures_v11/resolution_03_prime_precision.pdf)

### Increasing negative depth gives a two-sided threshold bracket

There is also an elementary lower bound, because the removed prime atom is present:

\[
\boxed{p^{-4}e^{\lambda_pT}\le D_p(-T)
\le\frac{D(4)}{p^4+1}e^{\lambda_pT}\qquad(T\ge0).}
\tag{RA-6}
\]

Choose an absolute tolerance \(\eta>D(4)/(p^4+1)\). The strict inequality makes the initial difference smaller than the tolerance. Define

\[
T_-=\frac{\log\bigl(\eta(p^4+1)/D(4)\bigr)}{\lambda_p},
\qquad T_+=\frac{\log(\eta p^4)}{\lambda_p}.
\tag{RA-7}
\]

Then \(D_p(-T)\le\eta\) for \(0\le T\le T_-\), while \(D_p(-T)\ge\eta\) for \(T\ge T_+\). The true crossing exists and is unique because \(D_p(-T)\) is continuous and strictly increasing. Therefore it belongs to \([T_-,T_+]\). If the tolerance hypothesis fails, the interval starting at zero is not certified by this formula. The executable record represents an absent lower interval by `null`.

The bracket width and its large-prime scale are explicit:

\[
T_+-T_-=\frac{\log\bigl(D(4)p^4/(p^4+1)\bigr)}{\lambda_p},
\qquad
T_+=\frac{p^2}{2}\bigl(4\log p+\log\eta\bigr)(1+O(p^{-2})).
\]

For \(\eta=10^{-6}\), rounded values are:

| Prime | No larger than tolerance through \(T_-\) | At least tolerance by \(T_+\) |
|---|---:|---:|
| 101 | 23,307.789 | 23,690.516 |
| 1009 | 7,012,695.633 | 7,050,894.424 |
| 10007 | 1,149,287,766.447 | 1,153,045,061.461 |

These are approximate evaluations of exact analytic endpoints, not directed-rounding intervals.

### The direct difference and subtraction of full functions have different conditioning

The positive series for \(D_p\) can be evaluated directly if the excluded prime is already specified. Recovering it by subtracting independently evaluated full functions can be much harder. The atom \(n=2\) in \(A_1\) gives

\[
\boxed{\frac{A_1(-T)}{D_p(-T)}
\ge\frac{p^4+1}{16D(4)}e^{(\lambda_2-\lambda_p)T}.}
\tag{RA-8}
\]

At the sufficient endpoint \(T_+\), the base-ten logarithm of this lower bound is about 5,924 for \(p=101\), 1,761,864 for \(p=1009\), and 288,119,991 for \(p=10007\). These are conditioning scales for subtracting full signals. They are not running times, required precision for every possible algorithm, or claimed numerical evaluations of the full functions at those enormous depths. The logarithmic bound is computed directly without forming those functions.

![The absolute visibility threshold has a narrow analytic bracket, but subtraction of full arithmetic functions can be severely ill conditioned.](figures_v11/resolution_04_prime_depth.pdf)

## 3. A negative atom that every low-degree test misses

Consider the one-prime signed sieve at \(p=2\), with \(\lambda_2=-1-\delta\), \(\delta>0\). Its nodes are \(x_n=(1-n^{-2})^2\), and its quadratic form is

\[
Q_\delta(f)=\sum_{\substack{n\ge1\\\mu(n)^2=1\\n\text{ odd}}}n^{-4}f(x_n)^2
-\delta\sum_{\substack{n\ge1\\\mu(n)^2=1\\n\text{ even}}}n^{-4}f(x_n)^2.
\]

Every even squarefree atom has negative mass. We will certify that all polynomials through degree four nevertheless have positive norm for \(\delta=10^{-12}\), and then construct a degree-seven polynomial of negative norm. This is an assertion about every polynomial in a finite-dimensional space, not a plot of a few test vectors.

### A rational certificate for every polynomial through a chosen degree

Choose \(d+1\) distinct odd squarefree labels \(n_0,\ldots,n_d\), including 1, and set \(y_i=x_{n_i}\). Their Lagrange polynomials are

\[
\ell_i(x)=\prod_{j\ne i}\frac{x-y_j}{y_i-y_j},
\quad
b_i=\prod_{j\ne i}\frac{\max(y_j,1-y_j)}{|y_i-y_j|},
\quad K_d=\sum_{i=0}^{d}n_i^4b_i^2.
\]

For \(x\in[0,1]\), we have \(|\ell_i(x)|\le b_i\). Interpolation and weighted Cauchy--Schwarz give, for every real polynomial of degree at most \(d\),

\[
|f(x)|^2\le
\left(\sum_{i=0}^{d}n_i^{-4}f(y_i)^2\right)
\left(\sum_{i=0}^{d}n_i^4\ell_i(x)^2\right)
\le K_d\sum_{i=0}^{d}n_i^{-4}f(y_i)^2.
\]

The total even mass satisfies
\(\sum_{n\text{ even}}\mu(n)^2n^{-4}<\frac1{16}(1+\frac13)=1/12\).
Keeping the selected nodes in the positive part yields the explicit bound

\[
\boxed{Q_\delta(f)\ge
\left(1-\frac{\delta K_d}{12}\right)
\sum_{i=0}^{d}n_i^{-4}f(y_i)^2.}
\tag{RA-9}
\]

A nonzero polynomial of degree at most \(d\) cannot vanish at all \(d+1\) nodes. Thus \(\delta<12/K_d\) proves strict positive definiteness of the Hankel matrix of order \(d+1\).

For \(d=4\), use labels \(1,3,5,7,11\). Exact rational arithmetic gives

\[
K_4\approx1.50393441996\times10^{11},\qquad
12/K_4\approx7.9790713217\times10^{-11}>10^{-12}.
\]

The inequality is checked as an exact rational comparison. Therefore every nonzero polynomial of degree at most four has positive norm in the chosen signed measure.

### A shorter detector by killing the first positive shelves

Let \(S\) be exactly the set of all odd squarefree labels \(n\le K\), where \(K\) is an odd squarefree integer, and let \(n_+\) be the next such label. Assume \(n_+>2\), and define

\[
P_{S,m}(x)=\prod_{n\in S}\frac{x-x_n}{x_2-x_n}
\left(\frac{1-x}{1-x_2}\right)^m,
\]
\[
C_S=\prod_{n\in S}\frac{1-x_n}{|x_2-x_n|},
\qquad r_S=\frac{1-x_{n_+}}{1-x_2}<1.
\]

This polynomial has degree \(|S|+m\), equals one at \(x_2\), and kills every positive atom through the cutoff. At each remaining positive node, the product of the absolute root factors is at most \(C_S\), and the last factor is at most \(r_S^m\). Dropping all other negative atoms and bounding the positive tail by the integral \(\sum_{n>K}n^{-4}\le1/(3K^3)\) gives

\[
\boxed{Q_\delta(P_{S,m})\le-\frac\delta{16}
 +\frac{C_S^2}{3K^3}r_S^{2m}.}
\tag{RA-10}
\]

For any chosen \(S\), a computable sufficient exponent is the first nonnegative integer \(m\) for which

\[
 r_S^{2m}<\frac{3K^3\delta}{16C_S^2}.
\]

It can be found by multiplying rational numbers, without logarithms or eigenvalues. Searching finitely many choices of \(S\) improves the sufficient degree but does not prove its optimality.

For the worked defect \(\delta=10^{-12}\), take

\[
S=\{1,3,5,7\},\quad K=7,\quad n_+=11,\quad m=3.
\]

Then

\[
C_S=\frac{756482048}{20777538825},\qquad
r_S=\frac{3856}{102487},
\]

and \(P_{S,3}\) has degree seven. The exact rational right side of (RA-10) is strictly negative and is approximately

\[
\boxed{Q_{10^{-12}}(P_{S,3})\le-5.8845708899\times10^{-14}.}
\]

The negative atom contributes \(-6.25\times10^{-14}\). The full positive tail contributes at most \(3.6542911008\times10^{-15}\), a bound that covers every omitted atom. The exact certificate is stored as numerator and denominator. The original generic isolating detector needed degree 21 for this defect. Using the known sign pattern and killing later positive shelves reduces the exhibited degree to seven.

![A degree-seven polynomial kills the first positive shelves and leaves a strictly negative certified quadratic form.](figures_v11/resolution_05_signed_detector.pdf)

The fifth-order Hankel matrix is therefore positive definite, while the eighth-order matrix is not positive semidefinite. The two intervening polynomial degrees, five and six, are not decided by these certificates. A numerical eigenvalue could suggest a sharper boundary, but it would be a different calculation requiring its own conditioning and error analysis.

![As the negative defect shrinks, exact interpolation bounds and explicit negative detectors bracket the degree needed to expose it.](figures_v11/resolution_06_degree_gap.pdf)

## 4. What the three examples establish together

The three resolution controls act on different mathematical objects. Radius controls what part of an entire function is sampled. Precision controls whether two different arithmetic parameters are distinguishable within an observation model. Degree controls the richness of a positivity test. The common lesson has a precise form: a property determined by an unbounded collection of tests need not have a uniform margin on each bounded subcollection.

Here the positive tap changes a proved global order. The excluded prime changes an exactly recoverable radical. The signed sieve lies outside the exact positivity domain even while a whole low-degree polynomial space passes. Each conclusion follows from explicit formulas and local proofs. There is no claim that the three mechanisms are identical, and no historical novelty claim for interpolation, spectral peeling, or the use of isolating polynomials.

## 5. Reproduction and evidence

Run from the release root:

```sh
python checks/resolution_v11.py
python build_resolution_figures.py
```

The first command uses only the Python standard library. It records **985 exact rational assertions** and **16 floating algebra checks**, with source hashes and exact certificate numerators and denominators. It tests interpolation identities in the monomial basis, all selected root values, sample envelope inequalities, exact negative norms for finite sums, coefficient continuity bounds and each displayed certificate. The universal analytic conclusions rely on the proofs above, rather than on the finite count.

The figure command uses NumPy, Matplotlib and mpmath. Six figures are saved in PDF and PNG form. The weak-tap curves use 100 decimal digits and an explicit positive-coefficient tail bound. Every other curve displays a closed analytic bound or rational certificate, so it has no omitted arithmetic series. Displayed floating values and polynomial curves are not interval arithmetic. The script never evaluates the huge full arithmetic functions in the cancellation example.

One preliminary presentation issue was corrected during development: a negative formula for \(T_-\) was initially clamped to zero. That would misleadingly label an already visible difference as invisible at zero. The finished formula requires its stated tolerance hypothesis, and the executable record marks an absent interval by `null`. The exact assertion run passed. This correction did not affect any of the three listed prime examples.
