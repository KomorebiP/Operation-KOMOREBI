# Finite perturbation bounds for dissipative mixed networks

This written theorem uses the same ordinary uncoupled transformer-free model,
fixed topology and fixed positive real reference as the existing tolerance
chapter. Normalize that reference to one.

## Exact branch-to-port mismatch contraction

Consider a finite port-connected graph whose branch impedances z_e and z'_e
have strictly positive real parts at the frequency under consideration. Floating
components can be discarded. Drive each graph through a unit resistor from a
unit voltage source. Both grounded nodal systems are nonsingular: the real
part of the homogeneous energy is a sum of positive branch conductances times
squared voltage drops, including the unit drive resistor. It vanishes only for
zero potential on the grounded port component.
If the port has no path to the other terminal, its reflection is the fixed
value $1$ and the same disk conclusion is trivial. Disconnected floating
components do not contribute to the port response.

The earlier finite Green and bilinear identities give

$$\Gamma'-\Gamma=2\sum_e(z'_e-z_e)i_ei'_e,\qquad
 P=\sum_e\Re z_e|i_e|^2=\frac{1-|\Gamma|^2}{4},$$

with the analogous identity for $P'$. Suppose $B\ge0$ and every branch satisfies

$$|z'_e-z_e|^2\le4B\Re z_e\Re z'_e.$$

The triangle inequality and Cauchy-Schwarz now give

$$|\Gamma'-\Gamma|
 \le4\sqrt B\sum_e\sqrt{\Re z_e}|i_e|
                         \sqrt{\Re z'_e}|i'_e|
 \le4\sqrt{BPP'}.$$

Squaring proves the finite-change inequality

$$|\Gamma'-\Gamma|^2\le
 B(1-|\Gamma|^2)(1-|\Gamma'|^2).$$

There is no small-perturbation expansion or multiplication by branch count.
The conclusion permits simultaneous changes in every branch. It is a
contraction in the classical half-plane/disk mismatch geometry; no novelty
claim for the general contraction principle is made.

## A rational Smith-chart uncertainty disk

Let $g=\Gamma$, $r=|g|^2$, $c=B(1-r)$ and $A=1+c$. The preceding inequality is exactly

$$\left|\Gamma'-\frac gA\right|^2
 \le\frac{B(1+B)(1-r)^2}{A^2}.$$

Thus nominal $g$ and a verified local mismatch budget give the center and squared
radius of a guaranteed disk. For rational complex $g$ and rational $B$ both are
exact rational data. If $g=0$, the reflected-power bound becomes

$$|\Gamma'|^2\le\frac B{1+B}.$$

Since both responses are passive, the simpler global majorant
$|\Gamma'-\Gamma|^2\le B$ also follows. A sharper global distance bound is

$$|\Gamma'-\Gamma|\le
 \frac{2\sqrt B}{\sqrt{1+B}+1}.$$

To see the last statement, put $d=|\Gamma'-\Gamma|$ and $m=(\Gamma+\Gamma')/2$.
The parallelogram identity implies $|m|^2+d^2/4\le1$ and
$(1-|\Gamma|^2)(1-|\Gamma'|^2)\le(1-d^2/4)^2$. Hence
$d\le\sqrt B(1-d^2/4)$, whose nonnegative root is the displayed bound.
The rational squared disk is sufficient for exact acceptance tests, without
requiring numerical square roots.

## Component tolerances with explicit series losses

Pair each reactive component with its own positive series resistor, with no
other branch at the internal series node. Treat the pair as a compound branch
$z=R+iX$, where $X=\omega L$ or $-1/(\omega C)$. Additional ordinary resistors and an
arbitrary interconnection of these branches are allowed. Both L and C kinds
may occur. All compound branches have positive real parts, so the preceding
existence and contraction argument applies.

Fix $0<\delta<1$. Independently scale every physical $R,L,C$ by a factor in
$[1-\delta,1+\delta]$. If nominal $|X|/R\le\kappa$ throughout a chosen positive
frequency band, write $a=R'/R$. For an inductive pair the reactance ratio $b=X'/X$
lies in that same factor interval. For a capacitive pair it is the reciprocal
of the capacitance factor. Therefore
in both cases $a\ge1-\delta$, $|a-1|\le\delta$ and
$|b-1|\le\delta/(1-\delta)$. Substitution gives

$$\frac{|z'-z|^2}{4\Re z\Re z'}
 =\frac{(a-1)^2+(X/R)^2(b-1)^2}{4a}
 \le\frac{\delta^2((1-\delta)^2+\kappa^2)}{4(1-\delta)^3}=B.$$

For the capacitor, the bound is attained locally by decreasing both its series
$R$ and $C$ by $\delta$ when $|X|/R=\kappa$. Standalone resistor branches satisfy the
same common bound. A nominal band budget can be computed directly as the
maximum of $\omega_{\max}L/R$ over inductive pairs and $1/(\omega_{\min}CR)$ over
capacitive pairs. The reference impedance is fixed and its normalization does
not change these ratios or multiplicative errors.

At one-percent tolerances with nominal $|X|/R\le1$, $B=19801/388119600<1/19600$.
Consequently the absolute reflection change is at most $1/140$. This is a
strongly damped example, not a promise for high-Q components. General $\kappa$
remains explicit in the formula.

The old shared-resistor/undamped parallel-LC counterexample does not meet the
local condition: a changed ideal reactive branch has zero real part and a
nonzero impedance change, so it admits no finite $B$. A positive resistor placed
elsewhere in a network cannot silently be counted as a dedicated series loss.

This theorem concerns an explicit lumped series-loss model. It does not supply
measured ESR, additional stray couplings, nonlinear behavior, frequency-varying
material models, or laboratory validation. Those remain separate engineering
inputs.

## A matching guarantee and an exact consumer

For a moderate band budget $\kappa\le10$ and independent one-percent errors,
a nominally matched port satisfies the exact reflected-power bound

$$|\Gamma'|^2\le\frac{1009801}{389129401}<\frac1{385}.$$

Thus less than $0.26\%$ of incident power is reflected at that nominally
matched frequency under the specified component-box model. This does not bound
internal dissipation or guarantee that the model describes a particular part.
One normalized example consists of a series $L=1/4$ pair and a series $C=4$
pair, each with its own resistor $1/20$, plus a series resistor $9/10$.
On $\omega\in[1/2,2]$ it has $\kappa=10$ and it is matched at $\omega=1$.

![The normalized mixed-loss example: exact guaranteed reflection disks at three frequencies, with a magnified view of the nominal match and the reflected-power bound below one divided by 385. These regions are guarantees within the stated component model, not measured hardware data.](figures/mixed-loss-disks.svg)

The exact consumer accepts a compound-branch graph, a positive frequency band,
a fixed reference and independent component tolerance. It reconstructs the
loss budget and the nominal center and squared radius at requested frequencies.
The whole-band component guarantee follows from the theorem; the displayed
samples merely evaluate the nominal disk and do not stand in for band coverage.
Dedicated internal series nodes are created explicitly for physical replay.

The standard-library controls solve nine fixed graph families, including a
mixed bridge, an open port, a loop, a nonunit reference and the matching example.
They check 1,110 physical component corners, 4,686 local mismatch inequalities,
1,110 bilinear identities and ten malformed-model or corrupt-certificate
rejections. Selected Lean statements now connect actual KCL and branch laws
to the finite contraction and disk identity. This is project self-review and
kernel replay of those statements, not independent human review.

For attribution, [Nadarloo, Hajiahmadi and Soleimani, arXiv:2611.06279v1](https://arxiv.org/html/2611.06279v1)
gives the established mismatch contraction and disk geometry in a broader
passive reconfiguration setting; see Theorem 1, equation (13), the independent
block rule and Supplement S2.3. The overlap is known after translating
$B=\sinh^2(d/2)$. The elementary graph proof and explicit component-box
certificate here are a project specialization. No new general contraction
principle or global historical priority is claimed. The result does not depend
on accepting the preprint's proof, because the finite graph argument is given
above and its selected KCL-to-disk implication is kernel-checked separately.
