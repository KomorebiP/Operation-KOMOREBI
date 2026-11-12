# A uniform component-tolerance theorem for RC and RL networks

Fix a finite ordinary uncoupled transformer-free RC network or RL network, a positive real
reference impedance, and its topology and component kinds. Normalize the
reference impedance to one. If every nonzero component is independently
perturbed by a multiplicative factor in $[1-\delta,1+\delta]$, $0<\delta<1$,
then at every positive real frequency

$$|\Gamma_{\rm pert}(i\omega)-\Gamma(i\omega)|
 \le -\log(1-\delta)\le\frac{\delta}{1-\delta}.$$

The bound is independent of network size and component magnitudes. At one
percent tolerance it is at most $1/99$. This is a theorem of the ideal fixed
model; it does not include added parasitic elements or measured hardware.

## Physical identity behind the bound

Drive the network through a unit resistor from a unit voltage source. Write
$V+I=1$ and $\Gamma=2V-1$. With consistently oriented branch currents $i_e$
and impedances $z_e$, finite summation of the node equations gives

$$S=V\overline I=\sum_e z_e|i_e|^2
 =\frac{1-|\Gamma|^2}{4}+\frac{i\,\Im\Gamma}{2}.$$

For two solutions on the same graph, the bilinear version gives

$$\Gamma'-\Gamma=2\sum_e(z'_e-z_e)i_ei'_e.$$

There is no conjugate on the two currents in this second identity. Both the
finite integration-by-parts identity and its two-solution consequence are
kernel-checked in `formal/GraphCore.lean`; the conversion to the analytic
network family and the estimates below remain a written proof.

Taking an infinitesimal change in a physical component $x_e$ yields
$\partial\Gamma/\partial\log x_e=2i_e^2\partial z_e/\partial\log x_e$.
For resistors, the sum of the absolute sensitivities is

$$\sum_R\left|\frac{\partial\Gamma}{\partial\log R_e}\right|
 =2\sum_RR_e|i_e|^2=\frac{1-|\Gamma|^2}{2}.$$

For RC, $z_C=-i/(\omega C)$, and all reactive powers have the same sign.
For RL, $z_L=i\omega L$, again with one sign. In either case,

$$\sum_{\rm storage}\left|\frac{\partial\Gamma}{\partial\log x_e}\right|
 =|\Im\Gamma|.$$

Writing $\Gamma=x+iy$, the combined budget satisfies the exact inequality

$$\frac{1-x^2-y^2}{2}+|y|
 =1-\frac{x^2+(|y|-1)^2}{2}\le1.$$

That scalar inequality is also checked in Lean. No multiplication by the
number of components is needed.

## Integrating actual component changes

Join the old and new component vectors by the positive logarithmic path
$x_e(t)=x_e(0)\exp(t\theta_e)$. Every $|\theta_e|$ is at most
$\tau=-\log(1-\delta)$. Along that path,

$$\left|\frac{d\Gamma}{dt}\right|
 \le\max_e|\theta_e|\sum_e
 \left|\frac{\partial\Gamma}{\partial\log x_e}\right|\le\tau.$$

Integrating over $[0,1]$ proves the assertion; the final rational majorant
follows by integrating $1/(1-t)\le1/(1-\delta)$ on $[0,\delta]$.

The nodal solution is differentiable for positive component values and
$\omega>0$. On a connected RC or RL port component, a homogeneous grounded
solution has zero dissipative energy and zero same-sign reactive energy, so
every branch drop vanishes. With the external unit drive resistor included,
the potential is therefore zero. This proves the needed nonsingularity.
Floating components can be discarded; disconnected or identified terminals
give a constant open or short response. Frequency-endpoint limits inherit the
bound whenever the reflected endpoint response is taken continuously.

## Why a mixed-RLC guarantee needs additional hypotheses

The same statement is false for arbitrary mixed RLC networks. Put

$$Z(s)=R+(sL\parallel 1/(sC)),\qquad
R=1/1000,\quad L=1/10^6,\quad C=10^6.$$

At $\omega=1$ the parallel LC arm is resonant and the reflected response is
$\Gamma=1$. Increasing only $L$ by one percent gives

$$Z'=1/1000-i\,101/10^6,\qquad
|\Gamma'-\Gamma|^2=\frac{4000000000000}{1002001010201}>(199/100)^2.$$

The independent exact nodal implementation reproduces this counterexample.
Opposite reactive powers can cancel while their individual magnitudes are
large, so the same-sign sensitivity argument cannot be extended. This does
not refute the earlier positive-real-Laplace compact-admittance estimate:
the frequency domain and proposed bound are different.

Mixed-RLC tolerance certification therefore still needs damping, component,
frequency-band or pole-separation information. Parasitics and experimental
validation remain open engineering work. The RC/RL theorem closes the stated
analytic component-tolerance subproblem without supplying those measurements.
