# Smith chart: exact packets and phase refinement

[Open the interactive Smith chart](https://KomorebiP.github.io/Operation-KOMOREBI/smith-chart.html) · [Extended demonstrations](../DEMONSTRATIONS.md)

**Author:** Komorebi P.  
**Status:** Interactive research demonstration with finite numerical checks. The classical Smith chart and roots-of-unity identities are not claimed as new discoveries.

## How to use this guide

This guide is a reading companion to the workbench. It starts with ordinary
impedance and reflection, then develops the cyclic packets and the sampling
construction used in the research tabs. The calculations are self-contained:
you can follow them without running Lean or using RF hardware.

1. For a first visit, read **Scope**, **Reading the reflection disk**, and the
   worked load and line examples. Try the same inputs in the workbench.
2. For the Komorebi construction, continue through **Exact impedance packets**,
   the worked packet examples, refinement, and energy.
3. For the sampling proposal, read **Angular sampling and limitations** and
   its worked example. Finish with the exercises and the verification scope.

The reader's **On this page** control links to the sections. Equations state
their domains; the displayed browser numbers are rounded approximations.

## Scope

The interactive chart starts with a passive physical load \(Z=R+iX\), reference resistance \(Z_0>0\), and normalized impedance \(z=Z/Z_0\). Its reflection coordinate is

\[
\Gamma=\frac{z-1}{z+1},\qquad z=\frac{1+\Gamma}{1-\Gamma}.
\]

For a passive load \(R\geq0\), the reflection coordinate lies in the closed unit disk. A lossless line rotates \(\Gamma\) without changing its magnitude. The workbench separately displays cyclic algebraic phase rotations; these are not conflated with propagation through a line.

## Reading the reflection disk

Write \(z=r+ix\) and \(\Gamma=u+iv\). The real number \(r=R/Z_0\) is
normalized resistance, while \(x=X/Z_0\) is normalized reactance. The
reference impedance \(Z_0\) is a positive real number in this guide. The
workbench uses \(i\) in the mathematics and may display \(j\) for the
imaginary unit in its RF readouts; the packet index \(j\) is a separate
integer.

From the Cayley transform, direct algebra gives

\[
\begin{aligned}
u&=\frac{r^2+x^2-1}{(r+1)^2+x^2},\\
v&=\frac{2x}{(r+1)^2+x^2}.
\end{aligned}
\]

These expressions also give

\[
1-|\Gamma|^2=
\frac{4r}{(1+r)^2+x^2}.
\]

For \(r>0\), the point lies strictly inside the unit disk. A finite
purely reactive load has \(r=0\) and lies on the boundary. The matched
load \(z=1\) is at the center; the short \(z=0\) is at \(\Gamma=-1\);
and the ideal open is the limiting point \(\Gamma=1\). The open is not
a finite complex impedance, because the inverse formula has a pole there.

The familiar grid curves follow from the same inverse. For a fixed
\(r\geq0\), the constant-resistance circle is

\[
\left(u-\frac{r}{1+r}\right)^2+v^2
=\left(\frac{1}{1+r}\right)^2.
\]

For a fixed nonzero \(x\), the constant-reactance circle is

\[
(u-1)^2+\left(v-\frac1x\right)^2=\frac1{x^2}.
\]

Only the arcs corresponding to \(r\geq0\) are used for passive finite
loads; the common point \(\Gamma=1\) represents the ideal-open limit.
Positive reactance appears above the horizontal axis and negative reactance
below it. Where \(z\ne0\), the admittance grid represents \(y=1/z\), using
\(\Gamma_y=-\Gamma_z\); the short has infinite admittance. Switching grids
does not change the physical load.

### Worked example: a 25 + j25 ohm load

Choose \(Z_0=50\,\Omega\) and \(Z=25+i25\,\Omega\). Then

\[
z=\frac{1+i}{2},
\qquad
\Gamma=\frac{-1+2i}{5}.
\]

Thus the point is at \((-0.2,0.4)\), and its distance from the center is
\(1/\sqrt5\). For \(0<|\Gamma|<1\), the standing-wave ratio and return loss are

\[
\begin{aligned}
\mathrm{VSWR}&=\frac{1+|\Gamma|}{1-|\Gamma|},\\
\mathrm{RL}&=-20\log_{10}|\Gamma|\ \mathrm{dB}.
\end{aligned}
\]

Here they are \((3+\sqrt5)/2\), approximately \(2.618\), and
\(10\log_{10}5\), approximately \(6.99\,\mathrm{dB}\). The matched case has
VSWR \(1\) and ideal infinite return loss; a boundary point has infinite
VSWR and \(0\,\mathrm{dB}\) return loss.

**Try it:** open the workbench and select the **25 + j25** load with
\(Z_0=50\,\Omega\). Check the load reflection, magnitude, and VSWR readouts.
Switch the grid between impedance and admittance and observe that the
selected physical load does not change.

### Worked example: a quarter-wave line

For the workbench's convention, a lossless line of length \(\ell\), measured
toward the source at the frequency under study, gives

\[
\Gamma_{\rm in}
=\Gamma_{\rm L}e^{-4\pi i\ell/\lambda}.
\]

Its magnitude stays fixed. At \(\ell=\lambda/4\), the factor is \(-1\), so
the reflection point makes a half-turn and \(z_{\rm in}=1/z_{\rm L}\)
whenever both impedances are finite. For the preceding load,
\(z_{\rm in}=1-i\), or \(Z_{\rm in}=50-i50\,\Omega\). At a half wavelength
the reflection coefficient returns to its load value.

**Try it:** retain the 25 + j25 load and set line distance to \(0.250\lambda\).
Compare **Load Z**, **Γ at the load**, and **Z in**. The separate cyclic
rotation index \(k\) acts on the phase orbit used for the algebraic
demonstration; it is not another physical length of transmission line.

## Exact impedance packets

For an integer \(N\geq1\) and \(|t|<1\), write \(z(t)=(1+t)/(1-t)\)
and project its Taylor coefficients into residue classes modulo \(N\).
Direct geometric-series summation gives

\[
\begin{aligned}
\mathcal P_{N,0}z(t)&=\frac{1+t^N}{1-t^N},\\
\mathcal P_{N,j}z(t)&=\frac{2t^j}{1-t^N}.
\end{aligned}
\]

The second formula is for \(1\leq j<N\). Summing all \(N\) packets
reconstructs \(z\). The normalized admittance is \(y=1/z\), and for even \(N\),

\[
\mathcal P_{N,j}y=(-1)^j\mathcal P_{N,j}z.
\]

For odd \(N\), parity alternates along a residue class, so the corresponding denominators are \(1+t^N\) rather than \(1-t^N\). In particular,

\[
\begin{aligned}
\mathcal P_{N,0}y&=\frac{1-t^N}{1+t^N},\\
\mathcal P_{N,j}y&=\frac{2(-1)^jt^j}{1+t^N}.
\end{aligned}
\]

Here \(N\) is odd, and the second formula is for \(1\leq j<N\).
Refinement to order \(2N\) separates these parities.

The individual nonconstant impedance packets need not be passive functions. Their denominators also create boundary poles that cancel in the full reconstruction. Truncating or interpreting isolated packets as physical loads can therefore be misleading.

### Why the phase average selects coefficients

Take an integer \(N\geq1\), let \(\omega=e^{2\pi i/N}\), and let \(j\)
be one of \(0,\ldots,N-1\). For a power series
\(f(t)=\sum_{m\geq0}a_mt^m\) at a point inside its disk of convergence,
define

\[
\mathcal P_{N,j}f(t)
=\frac1N\sum_{k=0}^{N-1}\omega^{-jk}f(\omega^k t).
\]

For each power \(t^m\), the inner average of
\(\omega^{k(m-j)}\) is \(1\) when \(m\equiv j\pmod N\), and \(0\)
otherwise. The projector therefore keeps exactly one residue class:

\[
\mathcal P_{N,j}f(t)
=\sum_{\substack{m\geq0\\m\equiv j\;(\mathrm{mod}\,N)}}a_mt^m.
\]

For impedance, \(z(t)=1+2t+2t^2+\cdots\) on \(|t|<1\).
The zero packet retains the constant \(1\) and the powers \(N,2N,\ldots\).
A nonzero packet retains \(j,j+N,\ldots\). Summing the resulting geometric
series gives the formulas above. Each coefficient occurs in exactly one
packet, so summing all packets reconstructs \(z(t)\).

### Worked example: two packets at \(t=1/2\)

Here \(z(1/2)=3\). With \(N=2\), the even and odd packets are

\[
\begin{aligned}
\mathcal P_{2,0}z(1/2)&=\frac53,\\
\mathcal P_{2,1}z(1/2)&=\frac43.
\end{aligned}
\]

They add to \(3\). The normalized admittance is \(y(1/2)=1/3\);
its corresponding packets are \(5/3\) and \(-4/3\), which add to
\(1/3\). This is the even-order sign rule in a concrete case.

**Try it:** set \(Z_0=50\,\Omega\), \(R=150\,\Omega\), \(X=0\), and
line length to zero. Then \(\Gamma_{\rm in}=1/2\). Choose cycle order
\(N=2\), leave \(k=0\), and switch packet \(j\) between \(0\) and \(1\)
in **Exact packets**. The readouts approximate the fractions above.

The individual odd packet is not itself a passive impedance function:
at \(t=-1/2\), \(\mathcal P_{2,1}z=-4/3\). This does not contradict
passivity of the recombined \(z(-1/2)=1/3\).

### Odd order and refinement

For \(N=3\) at \(t=1/2\), the impedance packets are
\(9/7\), \(8/7\), and \(4/7\), again summing to \(3\). The
admittance packets are \(7/9\), \(-8/9\), and \(4/9\), summing to
\(1/3\). The even-order sign rule does not apply to these coarse
odd-order packets: adding \(3\) changes the parity of a power.

Refinement separates the terms in a residue class into two alternating
subclasses:

\[
\mathcal P_{N,j}f
=\mathcal P_{2N,j}f+\mathcal P_{2N,j+N}f.
\]

For example, at \(t=1/2\), the \(N=2\) odd packet \(4/3\) is the sum
of the \(N=4\) packets \(16/15\) and \(4/15\). In **Finite polynomial**,
the workbench shows the coarse packet, both descendants, and their
reconstruction residual for a separate degree-31 polynomial. That fixture
is useful for testing the same coefficient rule; it is not the impedance
function itself.

### Products and coprime orders

If \(f_a\) contains only powers congruent to \(a\pmod N\), and \(g_b\)
only powers congruent to \(b\pmod N\), their product has powers only in
the class \(a+b\pmod N\). This is a statement about coefficient support.
It does not say that the product's value is zero at a nonzero input.

For a small counterexample to squaring only the zero packet, let
\(f(t)=1+t\) and \(N=2\). Then

\[
\mathcal P_{2,0}(f^2)=1+t^2,
\qquad
(\mathcal P_{2,0}f)^2=1.
\]

The missing \(t^2\) comes from multiplying the two odd parts. At
\(t=1/2\), the two expressions are \(5/4\) and \(1\). The workbench's
**Nonlinear & CRT** tab demonstrates the same issue with its own
degree-31 fixture.

For coprime orders, residue conditions can also be composed. For example,
a power is odd and congruent to \(2\pmod3\) exactly when it is congruent
to \(5\pmod6\). Consequently
\(\mathcal P_{2,1}\mathcal P_{3,2}f=\mathcal P_{6,5}f\).
This is the Chinese remainder theorem applied to coefficient indices.

### Two different energy comparisons

For the finite orbit \(t,\omega t,\ldots,\omega^{N-1}t\), the discrete
Parseval identity says

\[
\begin{aligned}
&\frac1N\sum_{k=0}^{N-1}|z(\omega^k t)|^2\\
&\qquad=\sum_{j=0}^{N-1}|\mathcal P_{N,j}z(t)|^2.
\end{aligned}
\]

At \(N=2\), \(t=1/2\), the left side averages \(3^2\) and
\((1/3)^2\), giving \(41/9\). The right side is
\((5/3)^2+(4/3)^2=41/9\). The workbench reports their numerical
difference as the **finite phase-orbit Parseval residual**.

The **angular mean-square** readout is a different quantity: it averages
one packet around the entire circle \(t=\rho e^{i\theta}\), with
\(0\leq\rho<1\). For \(1\leq j<N\), its value is

\[
\begin{aligned}
&\frac{1}{2\pi}\int_0^{2\pi}
|\mathcal P_{N,j}z(\rho e^{i\theta})|^2\,d\theta\\
&\qquad=\frac{4\rho^{2j}}{1-\rho^{2N}}.
\end{aligned}
\]

For the zero packet the value is
\(1+4\rho^{2N}/(1-\rho^{2N})\). At \(N=2\), \(\rho=1/2\), the
zero and nonzero means are \(19/15\) and \(16/15\), respectively.
Their sum is \(7/3\), not the finite-orbit value \(41/9\) above.
Both identities are exact, but they average over different sets of points.
These finite-radius means diverge as \(\rho\) approaches \(1\); they do
not establish a finite boundary \(H^2\) norm.

## Angular sampling and limitations

The symmetric open/short sensitivity weight is

\[
w(t)=\frac{1}{|1-t|^2}+\frac{1}{|1+t|^2}.
\]

At \(t=\rho e^{i\theta}\), it is a scalar multiple of the Poisson kernel at angle \(2\theta\), and its normalized angular density is

\[
p_\rho(\theta)=\frac{1-\rho^4}{2\pi(1-2\rho^2\cos(2\theta)+\rho^4)}.
\]

The weight has a concrete meaning. Since
\(z'(t)=2/(1-t)^2\) and \(y'(t)=-2/(1+t)^2\), motion around
\(t=\rho e^{i\theta}\) satisfies

\[
\left|\frac{dz}{d\theta}\right|
+\left|\frac{dy}{d\theta}\right|
=2\rho\,w(\rho e^{i\theta}).
\]

The weight therefore emphasizes angles where these two coordinate maps
change rapidly. It is an absolute coordinate-sensitivity weight, not a
relative condition number. The density is normalized to integrate to one.
At \(\rho=0\), it is uniform, although both coordinate speeds are zero.

For \(0\leq\rho<1\), let \(F_\rho(\theta)=\int_0^\theta p_\rho(s)\,ds\),
\(q=\rho^2\), and \(\beta=(1-q)/(1+q)\). Define
\(A(v)=\arctan\!\bigl(\beta\tan(2\pi v)\bigr)\) for \(-1/4<v<1/4\).
The branch-aware inverse \(Q_\rho(u)\) on \(0\leq u\leq1\) is

\[
\begin{cases}
A(u),&u<\tfrac14,\\
\pi/2,&u=\tfrac14,\\
\pi+A(u-\tfrac12),&\tfrac14<u<\tfrac34,\\
3\pi/2,&u=\tfrac34,\\
2\pi+A(u-1),&u>\tfrac34.
\end{cases}
\]

It satisfies \(F_\rho(Q_\rho(u))=u\). Thus the boundaries
\(Q_\rho(k/N)\) divide the circle into \(N\) equal-mass intervals, and the
workbench places its samples at the corresponding mass midpoints.

The browser uses a complex phase map to evaluate this inverse. In exact real
arithmetic, put \(\xi=2\pi u\) and \(\zeta=e^{2i\xi}\). When \(\cos\xi\ne0\),
the half-angle identity gives

\[
\begin{aligned}
\frac{\zeta+q}{1+q\zeta}
&=\frac{1+i\beta\tan\xi}{1-i\beta\tan\xi}\\
&=e^{2i\arctan(\beta\tan\xi)}.
\end{aligned}
\]

Each branch shifts \(\xi\) by a multiple of \(\pi\) inside the tangent
and adds a multiple of \(\pi\) to the inverse angle. These shifts leave
the doubled complex phase unchanged. At the two excluded quarter turns,
\(\zeta=-1\) and the map also gives \(-1\). The inverse is strictly increasing,
with \(Q_\rho(0)=0\), \(Q_\rho(1/2)=\pi\), and \(Q_\rho(1)=2\pi\); the
phase map's turn count therefore selects the same angle on each half of the
interval. This argument identifies the ideal formulas. It does not prove the
behavior of the floating-point browser implementation.

### Worked sampling example

Let \(\rho=4/5\). The sensitivity at the positive real point is
\(w(\rho)=2050/81\), while at the positive imaginary point it is
\(w(i\rho)=50/41\). Their ratio is

\[
\begin{aligned}
\frac{w(\rho)}{w(i\rho)}
&=\left(\frac{1+\rho^2}{1-\rho^2}\right)^2\\
&=\frac{1681}{81}\approx20.75.
\end{aligned}
\]

The density puts more mass near the open and short directions than near
the two imaginary-axis directions. It is symmetric across the four
quadrants: the cumulative masses at angles \(0,\pi/2,\pi,3\pi/2,2\pi\)
are \(0,1/4,1/2,3/4,1\). That does not mean the density is uniform
within each quadrant.

For this radius, \(\beta=9/41\). In a four-interval illustration, the
first interval's mass midpoint is at

\[
Q_\rho(1/8)=\arctan(9/41)\approx12.38^\circ,
\]

whereas the angular midpoint of the first quadrant is \(45^\circ\).
The workbench itself offers 32, 64, 96, or 128 sample points; it places
them at mass midpoints for the chosen count.

**Try it:** open **Sampling**, set the reflection radius to \(0.80\),
select 32 points, and turn on the weighted-sample overlay. The reported
weight ratio should be about \(20.75\). Compare the spacing near the
horizontal and vertical axes, then increase the radius to \(0.97\).

### What equal mass does and does not guarantee

For \(\rho>0\), density mass is proportional to the integral of
\(|dz/d\theta|+|dy/d\theta|\) over an angular interval. Suppose a
partition has \(N\geq1\) such nonnegative interval masses and fixed total
\(M\). At least one mass is at least \(M/N\); otherwise their sum would
be less than \(M\). The equal-mass partition attains \(M/N\) for every
interval, so it minimizes the largest of these integrated
coordinate-speed bounds. Consecutive displayed mass-midpoint nodes also
have equal mass between them, including across the wrap around the circle.
At \(\rho=0\), the coordinate speeds all vanish and every partition
attains the zero bound.

To see why an interval mass is an error bound, let \(L\) be the linear
interpolant of a continuously differentiable complex-valued curve \(h\) between
\(a<b\). Thus \(L(\theta)=(1-\alpha)h(a)+\alpha h(b)\), where
\(\alpha=(\theta-a)/(b-a)\). For \(a\leq\theta\leq b\), the triangle
inequality and the fundamental theorem of calculus give

\[
|h(\theta)-L(\theta)|
\leq\int_a^b |h'(s)|\,ds.
\]

Apply this separately to \(z(\rho e^{i\theta})\) and
\(y(\rho e^{i\theta})\), then add the bounds. This concerns linear
interpolation in the angle between endpoints; it does not describe every
possible reconstruction method.

An upper bound is not the actual interpolation error. The workbench's
fixed, noiseless interpolation comparison illustrates one case where these
nodes help the impedance coordinate and another where uniform nodes are
better for a different response. It is not a general theorem about noisy
measurements, arbitrary functions, or the best fitting method. In
particular, the page does not claim superiority over vector fitting,
rational reconstruction, measured RF data, or noisy S-parameter recovery.

## Physical load comparisons

The interactive comparison retains two physical loads, A and B. Changing the positive reference impedance \(Z_0\) changes their reflection coefficients even when their impedances stay fixed. It is therefore incorrect to compare a pinned \(\Gamma_A\) normalized with one \(Z_0\) to a current \(\Gamma_B\) normalized with another.

For finite loads, the chart computes both coefficients in the **current shared reference frame**:

\[
\begin{aligned}
\Gamma_A(Z_0)&=\frac{Z_A-Z_0}{Z_A+Z_0},\\
\Gamma_B(Z_0)&=\frac{Z_B-Z_0}{Z_B+Z_0}.
\end{aligned}
\]

The dashed A–B segment in the reflection disk represents the absolute complex difference \(|\Gamma_B-\Gamma_A|\). It is **not** a physical transmission-line path. The separate \(|Z_B-Z_A|\) readout stays in physical ohms, and the Swap control exchanges the physical loads without changing the shared \(Z_0\). The ideal open is represented by the limit \(\Gamma=1\). For display, the workbench treats two ideal opens as the same load and reports zero separation; an open paired with a finite load has unbounded impedance separation. This is a comparison convention, not arithmetic with \( \infty-\infty \).

**Try the reference change:** at \(Z_0=50\,\Omega\), pin
\(Z_A=25+i25\,\Omega\) and select the short as \(Z_B\). The physical
separation is \(25\sqrt2\), about \(35.3553\,\Omega\), while the
reflection separation is \(2/\sqrt5\), about \(0.894427\). Change
\(Z_0\) to \(75\,\Omega\). The physical separation stays the same;
the reflection separation becomes \(2\sqrt{34}/17\), about \(0.685994\).
The change is a re-expression in the new reference frame.

This is a corrected consistency rule and interaction aid, not a new RF theorem. Session import/export retains the physical reference load and re-normalizes it using the restored current \(Z_0\).

## Reversible load editing

**Undo load** and **Redo load** track physical load coordinates R, X, and Z₀, the ideal-open state, and the pinned A reference. One completed mouse or touch drag creates one history step; canceling a drag restores its starting point. Ctrl/Cmd+Z undoes an edit, Ctrl/Cmd+Shift+Z or Ctrl+Y redoes it. Standard text-field undo remains native to the browser.

History is intentionally separate from the lossless-line length, cyclic projector order, research view, and sampling options. Reset and JSON session import establish a new load-history starting point. These controls are reversible interface operations, not additional RF transformations.

## Direct load entry and packet selection

The workbench accepts physical impedance values and, under **Enter Γ directly**, an alternative pair of dimensionless load-reflection coordinates \(\Re\Gamma_L,\Im\Gamma_L\). The second input uses the same reference resistance \(Z_0\). Applying a new reflection point converts it through the inverse Cayley map and updates the physical load. A passive load must satisfy \(|\Gamma_L|\le 1\). Inputs outside the disk or too close to the open-circuit pole for stable double-precision conversion are rejected without changing the previous selected load. Unlike chart-pointer snapping near the endpoints, typed values inside the supported domain are not snapped to the ideal open or short.

The **Finite polynomial** view exposes each packet-magnitude bar as a keyboard-accessible selection control. Choosing a bar changes packet index \(j\) and updates the algebraic diagnostics without changing the physical load. The bars illustrate projected values of a fixed polynomial, not angular sectors of the reflection disk.

The numerical interface checks are finite fixtures. They do not assert arbitrary-precision inversion or new RF performance results.

## Chart magnification and edit recovery

The chart provides **Zoom in**, **Zoom out**, **Center**, and **Fit** controls. Zoom magnifies the displayed SVG coordinate view, centering initially on the selected load. **Center** recenters on the currently selected load and **Fit** restores the entire reflection disk. Magnification does not change the physical impedance, reflection coefficient, lossless-line phase, cyclic projector state, or pinned reference. Chart selection continues to use the inverse SVG screen transform under zoom, so an enlarged view is not a different RF coordinate system.

At higher magnifications, the chart retains readable axis and grid labels and uses non-scaling stroke widths so the boundary is not artificially thickened. Exported SVG charts retain those view settings.

The zoom view is not included in portable session files: importing settings or resetting the workbench restores a predictable full-disk chart. **Escape** cancels an unfinished chart drag, as does loss of browser focus; a canceled edit does not create a history entry. Reset and session restoration also cancel any ongoing drag before applying their new state. The zoom controls remain hidden without JavaScript, leaving the readable mathematics and chart unchanged.

Browser regression checks were exercised at 320, 390, 768, 1024, and 1440 pixel widths. They cover view-only magnification, precision of coordinate selection after zoom, export of the visible viewport, and interrupted-drag recovery. These are interface checks, not new impedance theorems.

## Exercises

Work these by hand first, then compare with the workbench where applicable.
The answers follow immediately below.

1. With \(Z_0=50\,\Omega\), find \(\Gamma\) and VSWR for a
   \(100\,\Omega\) resistive load.
2. With the same \(Z_0\), find \(z\) and \(Z\) when \(\Gamma=i/2\).
3. At \(t=1/2\), split the \(N=2\), \(j=1\) impedance packet into its
   two \(N=4\) descendants.
4. Let \(f(t)=1+2t\). For \(N=2\), compare
   \(\mathcal P_{2,0}(f^2)\) with \((\mathcal P_{2,0}f)^2\).
5. For \(N=3\) and \(\rho=1/2\), calculate the angular mean-square of
   the \(j=1\) impedance packet.
6. Does equal-density sampling prove that an arbitrary measured response
   has smaller interpolation error than with uniform samples? Why?

### Answers

1. \(z=2\), \(\Gamma=(2-1)/(2+1)=1/3\), and
   \(\mathrm{VSWR}=2\).
2. The inverse transform gives \(z=3/5+4i/5\), so
   \(Z=30+i40\,\Omega\).
3. The coarse value is \(4/3\), and the descendants are \(16/15\)
   and \(4/15\); their sum is \(20/15=4/3\).
4. \(f^2=1+4t+4t^2\), so the zero packet is \(1+4t^2\).
   The square of the zero packet of \(f\) is only \(1\).
5. The formula gives
   \(4(1/2)^2/[1-(1/2)^6]=64/63\).
6. No. Equal mass minimizes the stated integrated coordinate-speed
   bound, not the actual error for every response or a noisy-data fit.

## Verification and further reading

Run the numerical suite in the workbench's **Verification** tab to inspect
its deterministic fixtures, tolerances, and residuals. A passing
double-precision fixture is evidence about the tested inputs; it is not a
proof for all inputs or a hardware measurement. The repository also
contains exact-rational regression checks and separate bounded numerical
comparisons.

The [Lean companion](https://github.com/KomorebiP/Operation-KOMOREBI/tree/main/formal/smith-chart-v0.1.0)
formalizes the actual impedance packet series, canonical phase averages,
finite-orbit Parseval identity, finite passive-domain geometry, projector
and sensitivity identities, sampling-density normalization, the unique
abstract inverse and equal-mass partitions, and finite-radius angular
mean-square formulas. A piecewise real inverse-CDF formula is also proved,
including its branch points. The recorded replay uses cached Mathlib
dependencies and its mathematical review is self-review.

The exact-arithmetic phase-map derivation in this guide is a written
self-review. Correspondence to the browser's complex branch lift and
floating-point implementation is not formally verified. The finite-radius
angular mean-square is not a finite boundary \(H^2\) norm.

**What is established:** the stated exact formulas and tested implementation
behavior under the stated assumptions. **What remains open:** novelty
relative to all prior Smith-chart and polyphase literature, formal
certification of the browser implementation, and measurable benefit in
realistic RF measurement or model-fitting tasks.

The workbench is maintained as [HTML source](../../website/smith-chart-body.html),
[scoped CSS](../../website/assets/smith-chart.css), and
[JavaScript mathematics and interactions](../../website/assets/smith-chart.js).
For the classical engineering background, see Keysight Technologies'
[Understanding the Fundamental Principles of Vector Network Analysis](https://www.keysight.com/us/en/assets/7018-06841/application-notes/5965-7707.pdf),
which introduces reflection, transmission, the Smith chart, and network
measurements. The packet decomposition and its verification scope are
described by this guide and the linked companion; the engineering reference
is not cited as a source for those project-specific claims.
