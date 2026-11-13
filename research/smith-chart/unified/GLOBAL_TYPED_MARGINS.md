# Whole one-inductor and one-capacitor margins

The physical lemmas in this chapter now close every mixed three-reactive circuit
and every four-reactive circuit with only one inductor or only one capacitor.
All resistor counts, placements and positive finite values are allowed.
The maximum absolute reflection error on the same seven positive-real
Laplace samples is strictly greater than these constants:

| Reactive budget | At most one L | At most one C |
|---|---|---|
| three | $10^{-11}$ | $10^{-13}$ |
| four | $10^{-30}$ | $10^{-37}$ |

Pure RC/RL and smaller budgets use their stronger inherited margins. These
constants establish structural separation; they are too small for useful
hardware tolerances. Whole-skeleton coverage rises from 138 to 1,334 of
2,130 representatives. Only the 796 balanced two-L/two-C placements remain.
This is written project self-review with exact arithmetic and finite graph
controls, not an independent review or an extension of the selected Lean count.

Use $P_H=4+3s+6s^2$, $Q_H=9+2s+6s^2$, $Z_H=P_H/Q_H$ and
$S=\{1/2,3/4,1,5/4,3/2,7/4,2\}$. The reference resistance and resonant
frequency are one. All graph pairs below are natural determinant pairs
normalized by $P(1)+Q(1)=1$. The required energy and rounding lemmas are
proved after this main argument; earlier checkpoints are retained below them.

## A one-kind physical quartic retains real roots

For exactly one L and at most three C branches, either natural determinant
has the form

$$A(s)=G+sC+(h/s)bb^T,\quad
D=\det(G+sC),\quad N=b^T\operatorname{adj}(G+sC)b,\quad p=sD+hN.$$

Here $G,C$ are real positive semidefinite, $h>0$ and
$\operatorname{rank}C\le3$. Both $D$ and $N$ have degree at most three:
at most three independent columns can come from $C$ in the determinant or
the cofactor with the rank-one term. If $p$ is quartic, $D$ is cubic and
nonzero. Thus $G+C$ is positive definite; a common null vector would make
$D$ identically zero.

Whiten by $G+C$ and diagonalize
$(G+C)^{-1/2}C(G+C)^{-1/2}$. Its eigenvalues lie in $[0,1]$. It follows that
$D$ has three real nonpositive roots counted with multiplicity and

$$N/D=a+\sum_{j=1}^k r_j/(s+t_j),
\qquad a\ge0,\quad r_j>0,\quad t_j\ge0,$$

where equal active poles are combined. Between successive active poles,
$s+hN/D$ tends to $+\infty$ on the right of the left pole and to
$-\infty$ on the left of the right pole. The intermediate value theorem
gives at least $k-1$ real zeros away from $D$. At roots of $D$, $p$ retains
total multiplicity at least $3-k$: an active simple pole removes only one
copy even if $D$ has a repeated root. Thus $p$ has at least two real roots
counted with multiplicity. If $k=0$, $p=D(s)(s+ha)$ has four. The proof
includes $b=0$, as for an L between fixed terminals.

Physical inversion $s=1/t$ exchanges L and C with reciprocal values. At
retained budget four each natural polynomial becomes $t^4p(1/t)$, with
the same normalization. For a one-C quartic with $p(0)\ne0$, inversion
preserves real root count. If $p(0)=0$, its zero and the remaining real
cubic's real root already give two counted with multiplicity. Thus the same
condition holds for one-C quartics. A physical two-L/two-C example with a
quartic numerator having no real roots refutes extension to that class.

## The resonant denominator is automatically bounded

Use the affine coefficient projection with $\epsilon=C_4\delta$, rather
than the larger nonnegative repair distance. Write its pair as
$(P_Hm,Q_Hm)$, $m=a+bs+cs^2$, $a+b+c=1/30$. If a one-L graph had
$|P(i)|<1/100$, then $|P_H(i)|=\sqrt{13}>3$ and coefficient error at most
$\epsilon$ imply

$$|b|,|a-c|\le B=(1/100+5\epsilon)/3,
\qquad a,c\ge1/60-B.$$

For real $x$, $m(x)\ge r(1+x^2)$, where $r=1/60-3B/2$, using
$|x|\le(1+x^2)/2$. The identities

$$P_H(x)-\tfrac52(1+x^2)=\tfrac72(x+3/7)^2+6/7,$$
$$\tfrac54(1+x^2)^2-\sum_{j=0}^4|x|^j=(|x|-1)^4/4$$

give
$P(x)\ge[\tfrac52r-\tfrac54\epsilon](1+x^2)^2>0$ and
$P_4\ge6(1/60-B)-\epsilon>0$. Both are strict at $\delta=10^{-11}$,
and hence below it, by exact rational arithmetic. This positive quartic has
no real roots, a contradiction. Thus $|P(i)|\ge1/100$ automatically.
For one C use $Q$ and $Q_H(x)-5(1+x^2)=(x+1)^2+3$; this gives
$|Q(i)|\ge1/100$. At budget three both moduli are already at least $1/13$
for $\delta\le10^{-9}$ by the preceding fiber bound.

The natural determinant bounds imply finite phasors: nonzero $P(i)$ makes
the port-Dirichlet problem invertible; nonzero $Q(i)$ makes the grounded
unit-current problem invertible. Detached components are discarded. An
artificially multiplied representation is not used.

## Every one-L class at budgets three and four

Let $\tau$ be the nonnegative-fiber coefficient distance. At every vertex
of its segment or quadrilateral the first $q-1$ numerator coefficients sum
to at least $2/15$. For the constants below,
$2/15-(q-1)\tau\ge13/100$. Nonnegativity of the actual coefficients gives

$$P(\sigma)\ge(13/100)\sigma^{q-2},\qquad0<\sigma\le1.$$

This prefix bound avoids subtracting an absolute coefficient error from a
tiny denominator. Set $R=P Q_H-Q P_H$. At the sample nodes,
$|R(s_j)|\le W_j\delta$, where
$W_j=(P_H+Q_H)(s_j)\max(1,s_j^q)/2$. At the same $q+3$ nodes used by
the energy certificate, exact Lagrange interpolation gives

$$|R(t)|\le K_q(t)\delta,\qquad
K_q(t)=\sum_j|\ell_j(t)|W_j.$$

If a reactive value lies outside $[\eta,1/\eta]$, positive-real rounding
removes it with error at most $4\eta$. Choose $\delta+4\eta$ below the
already established smaller-budget margin; all reactive values are then
bounded first. Removing the sole L instead gives a pure RC graph, whose
stronger margin suffices. A DC short requires the sole L directly across
the port and is excluded by its stronger shunt margin. Otherwise $Y_0$ is
finite, including zero for a DC-open port. The preceding energy trade-off,
now with automatic denominator, gives $Y_0<K_q^{\rm DC}\delta$; if
$Y_0=0$ this bound is immediate.

Bounded rational unit-voltage potentials have DC limits in $[0,1]$. The L
drop is zero and the capacitor currents vanish. This limit is a Dirichlet
trial at $\sigma$, with at most $q-1$ C values at most $1/\eta$. Hence

$$Y(\sigma)\le Y_0+(q-1)\sigma/\eta.$$

Interpolation, however, implies

$$Y(\sigma)\ge Y_H(\sigma)
-\frac{K_q(\sigma)\delta}{P_H(\sigma)(13/100)\sigma^{q-2}}.$$

| Budget | $\delta$ | $\eta$ | $\sigma$ | Lower $Y(\sigma)$ | DC upper bound |
|---|---|---|---|---|---|
| three | $10^{-11}$ | $2\cdot10^{-7}$ | $10^{-7}$ | $>1.2532$ | $<1.0021$ |
| four | $10^{-30}$ | $2\cdot10^{-12}$ | $10^{-12}$ | $>2.1555$ | $<1.5001$ |

The exact certificate checks the rational inequalities underlying these
decimal summaries. Rounding at three uses the accepted two-reactive margin
$10^{-6}$; at four it uses the new three-reactive one-L margin $10^{-11}$.
These strict contradictions leave no resistor cap, DC or resonance guard.

## A one-C endpoint inequality

Use unit current, exactly one C, arbitrary L/R, and finite positive endpoint
resistances $r_0=Z(0)$, $r_\infty=Z(\infty)$. Suppose a finite phasor at
$i$ has $Z_i=Z(i)$, $e=\operatorname{Re}Z_i\ge0$, and

$$e<r_0,\qquad \operatorname{Im}Z_i>\sqrt{r_\infty e}.$$

Let $G_R$ be resistor-only unit-voltage conductance and $R_a$ the effective
resistance after all reactives are shorted. Dirichlet applied to the phasor
potentials divided by $Z_i$ gives $G_R\le e/|Z_i|^2$. The real parts of
its resistor currents after reactive contraction form a feasible unit-current
flow, so Thomson gives $R_a\le e$. Contracted ports give $R_a=0$.

Let $V_0,V_i$ be oriented C voltages at DC and $i$, and $J_\infty$ its
oriented short current at infinity. Shorting the sole C in the DC network
and using reciprocity gives $r_0-R_a=V_0J_a$, with $|J_a|\le1$ by the
unit-current cut bound. Thus $|V_0|\ge r_0-e$. If C is a loop after L
contraction, $r_0=R_a\le e$, outside the strict hypothesis. Comparing
resistor-only potentials $V_R\in[0,1]$ to the infinity state gives

$$1-G_Rr_\infty=J_\infty\Delta V_R,
\qquad |J_\infty|\ge1-e r_\infty/|Z_i|^2>0.$$

Let $R_{0i},R_{i\infty},R_{0\infty}$ be sums of paired resistor currents
weighted by resistance. At DC all L drops and the C current vanish; at
infinity all L currents and the C drop vanish. Green and Cauchy give

$$R_{0i}=r_0-iC V_0V_i,\qquad Z_i=R_{i\infty}+V_iJ_\infty,$$
$$|R_{0i}|\le\sqrt{r_0e},\qquad
|R_{i\infty}|\le\sqrt{r_\infty e},$$
$$R_{0\infty}=r_0-V_0J_\infty,\qquad
R_{0\infty}^2\le r_0r_\infty.$$

Taking the real part of the first forces $V_0\operatorname{Im}V_i<0$;
taking the imaginary part of the second forces
$J_\infty\operatorname{Im}V_i>0$. Thus $V_0J_\infty<0$ and

$$\boxed{r_\infty\ge r_0
\left[1+(1-e/r_0)(1-e r_\infty/|Z_i|^2)\right]^2.}$$

Disconnected resistor cores are included: floating Dirichlet minimizers
may be chosen in $[0,1]$, and carry zero current and energy. Endpoint states
may be obtained as bounded rational positive-real limits, with no uniqueness
requirement on irrelevant potentials. At zero loss this says
$r_\infty\ge4r_0$; the target violates it, since $1<4(4/9)$, and has
two capacitors. This is not asserted for an arbitrary mixed graph.

## Every one-C class at budgets three and four

First settle exceptional endpoints. DC-open with only one C makes that C
a port-cut bridge: deleting it disconnects the terminal R+L components.
Thus the impedance is a series C plus an RL impedance, excluded by margin
$1/500000$. Infinity-short requires the sole C directly across the port,
excluded by the terminal-C/RL margin $1/100000$. A closer fit therefore has
finite $Z_0$ and finite $Y_\infty$, with zero still allowed initially.

Unit-current branch currents at positive real frequency have modulus at
most one. For finite $Z_0$, bounded rational current limits give a DC flow
with zero C current and zero L drops. It is a Thomson trial at $\sigma$.
For finite $Y_\infty$, the bounded unit-voltage limit at infinity has zero
L currents and zero C drop and is a Dirichlet trial at $T$. If L values
lie in $[\eta,1/\eta]$, then

$$Z(\sigma)\le Z_0+(q-1)\sigma/\eta,\qquad
Y(T)\le Y_\infty+(q-1)/(T\eta).$$

DC-short currents are still bounded by the unit-current cut argument;
infinity-open potentials are still in $[0,1]$. These boundary cases are
included before positivity is deduced.
The fiber vertices give prefix/suffix sums at least $3/10$ for the first
$q-1$ Q coefficients and $1/5$ for P coefficients at indices two through
$q$. After the coefficient perturbation the choices below give

$$Q(\sigma)\ge(29/100)\sigma^{q-2},\quad
P(T)\ge(19/100)T^2,\qquad T\ge1.$$

Thus exact Lagrange interpolation gives $Z_0\ge r_*>0$ and
$Y_\infty\ge y_*>0$, where

$$r_*=Z_H(\sigma)
-\frac{K_q(\sigma)\delta}{Q_H(\sigma)(29/100)\sigma^{q-2}}
-(q-1)\sigma/\eta,$$
$$y_*=Y_H(T)
-\frac{K_q(T)\delta}{P_H(T)(19/100)T^2}
-(q-1)/(T\eta).$$

Set $r^*=1/y_*$. The automatic natural Q bound gives
$|Z_i-i|\le e_*=K_i\delta/(3\beta)$, with $\beta=1/13$ at budget
three and $1/100$ at four. Thus $e\le e_*$,
$|Z_i|^2\ge(1-e_*)^2$ and $\operatorname{Im}Z_i\ge1-e_*$.

| Budget | $\delta$ | $\eta$ | $\sigma=1/T$ | $r_*$ | $r^*$ | Lower endpoint RHS |
|---|---|---|---|---|---|---|
| three | $10^{-13}$ | $2\cdot10^{-7}$ | $4\cdot10^{-9}$ | $>0.3548$ | $<1.1521$ | $>1.4192$ |
| four | $10^{-37}$ | $2\cdot10^{-14}$ | $8\cdot10^{-16}$ | $>0.3215$ | $<1.1417$ | $>1.2860$ |

Exact arithmetic gives $r_*>e_*$ and $(1-e_*)^2>r^*e_*$, verifying the
endpoint sign hypotheses. All bracket factors are positive, so its RHS is
at least

$$r_*[1+(1-e_*/r_*)(1-e_*r^*/(1-e_*)^2)]^2>r^*,$$

contradicting $r_\infty\le r^*$. Rounding at three uses the old
two-reactive margin; at four it uses this new one-C three-reactive margin.
Removing the only C gives a pure RL graph. Thus all reactive values are
bounded first; no endpoint or resonance guard, resistor cap or imaginary-axis
rounding is assumed.

## Evidence and the remaining balanced class

`solver/check_global_typed.py` tests 128 physical one-kind graphs, 112
quartic root counts and 128 reciprocal-polynomial comparisons. Endpoint
controls include floating cores, reversed C orientations, nonzero losses and
zero-loss equality. Six Sturm controls include repeated roots. Four corrupt
certificates and the physical balanced no-real-root numerator are negative
controls. `verification/current-exact-008` binds observed inputs before/after;
`solver/check_current_global.py` preserves every predecessor replay.

The enumeration independently counts 26 covered mixed classes at budget two,
246 at three, and 1,062 at four: 1,334 total, an increase of 1,196. The
remaining 796 are exactly the balanced two-L/two-C class. The real-root
lemma fails there; its stable triangle and resistor open/wire faces still
need a uniform separator with a useful bound. Full formal/independent proof
assurance, arbitrary mixed minimum synthesis, higher resistor minima,
broader physical models/data and priority remain the other open contracts.
