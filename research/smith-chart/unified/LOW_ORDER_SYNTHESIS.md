# Complete first-order synthesis and positive Cauer constructions

These constructions close executable synthesis on two precisely specified
classes. They are classical circuit mathematics with new project integration,
exact certificate emission and independent physical-graph replay. They do not
solve the practical minimum problem for arbitrary mixed RLC targets.
All optimality comparisons here use finite positive ordinary uncoupled,
transformer-free one-ports. The zero impedance is an explicitly separate boundary.

## Every real first-order positive-real impedance

Write the reduced impedance as

$$Z(s)=\frac{as+b}{cs+d},\qquad (c,d)\ne(0,0).$$

Normalize the nonzero denominator leading coefficient to one. Then positive
realness is equivalent to $a,b,c,d\ge0$, with zero coefficients allowed.
Indeed a denominator with a positive real pole is inadmissible; nonnegativity
on the positive real axis forces the two numerator endpoint coefficients to
be nonnegative. Conversely, for $s=x+iy$, $x>0$,

$$\Re Z(s)=\frac{ac(x^2+y^2)+(ad+bc)x+bd}{|cs+d|^2}\ge0.$$

The denominator is nonzero there. Cancellation must be performed first:
an unreduced positive pole can be removable, and $ad=bc$ gives a constant.

For $c,d>0$, put $\Delta=ad-bc$, $r_0=b/d$ and $r_\infty=a/c$.
If $\Delta>0$, the exact realization is

$$Z=R_0+(R_1\parallel sL),\qquad
R_0=r_0,\quad R_1=r_\infty-r_0,\quad L=\Delta/d^2.$$

If $\Delta<0$, it is

$$Z=R_0+(R_1\parallel 1/(sC)),\qquad
R_0=r_\infty,\quad R_1=r_0-r_\infty,\quad C=c^2/(-\Delta).$$

Every displayed nonzero component is strictly positive. A zero series
resistance means that the branch is omitted, rather than emitted as a
zero-valued element. If $c=0$, use $Z=b/d+s(a/d)$. If $d=0$, use
$Z=a/c+b/(cs)$, with $C=c/b$. Constant positive impedances need one resistor.
The zero function is reported separately as an ideal-short boundary.

These formulas cover the whole reduced class. One reactive element is minimal
for every degree-one target by the degree bound. For rational input all
constructed values are rational; the unchanged composition consumer rebuilds
the physical graph and verifies its complete rational impedance.

## Resistor minima, including competitors with extra storage

An impedance dissipating positive power at some regular imaginary frequency
requires at least one resistor. A circuit with no resistors is lossless and
has zero real driving-point impedance there. This separates the pure inductor
and capacitor cases from the remaining first-order targets.

There is a stronger endpoint obstruction. In a network with only one resistor
$R$, each of its DC and infinite-frequency impedance limits belongs to
$\{0,R,\infty\}$. To see this, take the positive-real Laplace limit. At zero,
delete capacitors and contract inductors; at infinity interchange those roles.
Every surviving graph has just wires, opens and at most that single resistor.
Its port impedance is consequently a short, that resistor, or an open.

This limiting argument includes singular and floating components. For any
sequence of positive real Laplace arguments approaching the endpoint, the
unit-source/unit-series-resistor voltages and currents have a convergent
subsequence. Its branch equations impose exactly the stated deletions and
contractions. Summing KCL cancels all internal wire currents. The resistor-only
port response is unique, so all subsequences give the same limit. The earlier
compact-model proof supplies the boundedness; the finite contraction identity
now also has a Lean companion. Full formalization of this analytic limiting
argument remains separate.

Thus two distinct finite positive endpoint resistances require at least two
resistors, even if the competitor contains arbitrarily many reactive elements.
The two-resistor first-order circuits above attain the bound. When exactly one
endpoint is zero or infinite, the displayed one-resistor circuit attains the
one-resistor lower bound. Pure $sL$ and $1/(sC)$ need no resistor. Therefore the
algorithm attains both the reactive and resistor minimum throughout the
nonzero first-order class. The resistor lower bound is a written theorem; it
is not an extra conclusion supplied by the existing composition checker.

The rising formulas coincide with Morelli's 2019 dissertation, Table 5.4,
network 15, under $(B,C,E,F)=(a,b,c,d)$ and $A=D=0$. The falling formulas follow
by frequency inversion. This is established overlap, not a novelty claim.
[Primary source, printed pages 57–58](https://api.repository.cam.ac.uk/server/api/core/bitstreams/0008b1b9-9d58-4813-8e97-1db41532cc8c/content).

The same endpoint lower bound closes the resistor count for the normalized
Hughes base: $H(0)=4/9$ and $H(\infty)=1$ force at least two resistors. The
retained exact five-reactive witness contains exactly two, so the global
resistor minimum is two. The current replay checks that witness with the
unchanged algebraic consumer and applies the separate endpoint-bound checker.
This resistor conclusion permits arbitrary reactive counts in competitors.
It does not settle the resistor count of the original degree-six target or
the higher-degree lifted families.

## Complete rational RC and RL classes

An RC driving-point impedance is a rational Stieltjes function,

$$Z(s)=R_\infty+\sum_{j=1}^{n}\frac{a_j}{s+p_j},\qquad
R_\infty\ge0,\quad a_j>0,\quad p_j\ge0,$$

after equal poles have been combined. All poles are simple and negative or
zero. The RL class is its frequency inverse $Z(1/s)$. These are classical
Foster–Cauer classes; Morelli's Theorems 2.2–2.3 give their complete passive
network characterization, including bridge networks.

The implementation extracts $R_\infty$, then writes the strictly proper
remainder as $H=P/Q$. Set $A=\sum a_j$ and extract $C=1/A$ from
$1/H$. The new series core is

$$Z_{\rm next}=\frac{1}{1/H-s/A}
 =\frac{AH}{A-sH},\qquad A-sH=\sum_j\frac{a_jp_j}{s+p_j}.$$

This is again Stieltjes and has degree one less. For completeness, if some
$p_j>0$, the denominator sum has strictly negative derivative between its
negative real poles. Its zeros are simple and interlace those poles. At a
zero $r<0$, $H(r)=A/r<0$, so the residue of $AH/(A-sH)$ is positive. Its
constant at infinity is $A^2/(\sum a_jp_j)>0$. If a zero pole is present in
$H$, it survives with positive residue and the remaining pole count still
falls by one. If the only pole is zero, $H=A/s$ is already a pure capacitor.
These observations prove the inductive preservation and termination.

Coefficient extraction uses exact polynomial leading coefficients, not
numerically recovered poles or residues. Therefore rational input yields
rational positive components even when its negative poles are irrational.
The final graph has exactly the reduced degree in capacitors; frequency
inversion gives the corresponding number of inductors. That count is globally
minimal among ordinary RLC competitors by the degree lower bound. No general
resistor-minimum claim is made for these higher-degree graphs.

The current Cauer implementation supports degrees through fifteen within the
unchanged consumer's depth and arithmetic limits. Failure of a defining
positive extraction means outside this RC or RL class, not mixed-RLC
nonrealizability; a resource or acceptance limit remains `UNKNOWN`.

Use `solver/first_order.py` or `solver/cauer.py --kind RC` / `--kind RL` from the
current source. Both return a result wrapper containing its portable physical
composition certificate. The exact finite regressions are implementation
checks; the preceding proofs provide the stated class coverage.
