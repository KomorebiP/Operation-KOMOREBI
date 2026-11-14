## Reading guide and engineering meaning

This reading connects a desired electrical response to a physical passive circuit. It asks which responses are compatible with passivity, how to build circuits that realize them, how many components are necessary, and how component variations affect the result. The worked examples concern ideal lumped networks and explicitly stated transmission-line or transformer models.

### Choose a reading route

| Your question | Start here | What the result provides |
|---|---|---|
| How do impedance and reflection describe the same load? | [One load through a transmission line](#one-load-through-a-transmission-line) | A complete calculation with physical units and exact Smith-chart coordinates. |
| Can missing observations be completed consistently? | [Passive completion](#passive-completion-from-incomplete-packets) and [singular data](#singular-completion) | Existence, ambiguity, forced predictions, and finite matrix certificates under the stated interpolation model. |
| Can I build a circuit with a certified component count? | [The minimum-six circuit](#exact-six), [first-order synthesis](#low-order-synthesis), and [family recognition](#deterministic-family) | Positive physical graphs, exact target binding, and the applicable minimum-count statements. |
| Can a smaller circuit approximate the target? | [Separated scales](#obstruction), [uniform physical transfer](#global-transfer), and [the one-inductor approximation](#one-inductor) | Lower bounds for specified targets and constructive approximations with explicitly defined errors. |
| What can component tolerances change? | [Component tolerances](#component-tolerances) | Reflection bounds for RC/RL networks and uncertainty disks for mixed networks with specified series losses. |

The [results table](#current-results) gives the detailed scope of each result. The contents list provides direct links to every chapter, and the [verification section](#source-ledger) explains the evidence supporting the statements.

### The quantities that must stay distinct

- **Impedance and reflection.** Physical impedance is measured in ohms. With a positive real reference impedance \(Z_0\), the normalized impedance is \(z=Z/Z_0\), and reflection is \(\Gamma=(z-1)/(z+1)\). The reflection coefficient is dimensionless. At a port with the stated real reference, \(|\Gamma|^2\) is the reflected fraction of incident power.
- **Complex frequency and sinusoidal frequency.** The Laplace variable is \(s=\sigma+i\omega\). A sinusoidal response is evaluated on \(s=i\omega\), whereas the separation theorems use specified real arguments \(s>0\). Bounds in one of these domains require their own justification in the other. The disk variables used for load interpolation are identified separately in the [conventions](#conventions-and-two-distinct-complex-variables).
- **Passivity and physical realization.** A positive-real impedance is analytic in the open right half-plane and has nonnegative real part there. A Schur reflection is analytic and bounded in magnitude by one in its stated disk. A physical realization additionally specifies permitted components, their interconnection, and positive values.
- **Transfer-function degree and physical storage.** Reduced rational degree counts the order visible at the port after common polynomial factors are canceled. Reactive count counts actual inductors and capacitors. An internal mode can disappear from the port response while its physical components remain in the circuit.
- **Exactness and approximation.** An exact realization gives the same rational impedance as the target. An approximation requires an error quantity, a comparison domain, and a bound. A plot or a finite collection of agreeing samples needs a separate argument before it establishes an identity or a uniform guarantee.

The principal circuit model is a finite one-port with positive resistors, inductors, and capacitors, uncoupled inductors, and no ideal transformer. A **one-port** has one pair of external terminals; a **topology** describes which component branches connect which nodes. The chapter about an ideal reciprocal combiner explicitly uses a broader model. **RC** means resistor–capacitor, **RL** means resistor–inductor, and **RLC** allows all three kinds. **KCL**, Kirchhoff's current law, requires the signed currents at each node to sum to its external current injection.

In code-style formulas, `*` means multiplication, `^` denotes a power, and an underscore introduces an index. **ESR** means equivalent series resistance. The mixed-loss theorem identifies precisely where a series resistance must be placed and how its value enters the guarantee.

### Read a minimum claim precisely

For the specified degree-six target, the positive circuit uses three inductors and three capacitors. Coprimality makes the reduced degree six, so the general degree lower bound and this construction give the same reactive count. Seven resistors and eight nodes describe that witness; the theorem minimizes its reactive count.

The open higher-degree families have their own construction and almost-everywhere total-component theorem. Here **almost everywhere** permits an exceptional set of coefficient vectors with zero Lebesgue measure. That statement does not decide whether a particular rational target belongs to the exceptional set. The generic count argument uses the standard parameter-dimension obstruction, as explained in the family chapter and in the established [generic-network minimality theory of Hughes, Morelli, and Smith](https://doi.org/10.1016/j.sysconle.2019.104562).

The separated-scale families address a different question: physical reactive complexity can exceed reduced rational degree. Their lower bounds permit competing topologies with arbitrary finite resistor counts. The scale thresholds and error margins are part of those theorems' hypotheses.

### Interpret a separation or tolerance bound

A **separation bound** is a lower bound on how closely a competing circuit class can approach a target in a specified error measure. A **tolerance bound** is an upper bound on the response change caused by allowed changes to a specified circuit. The direction of the inequality matters.

The topology-uniform four-reactive bound is an extremely small structural separation on seven positive real Laplace arguments. It establishes a positive gap in that metric. The larger physical-state and regional bounds require their stated graph, state, and perturbation conditions. Their numerical values should be interpreted with those conditions attached.

For fixed ideal RC or RL networks, the one-percent tolerance result bounds the **absolute change in reflection amplitude** by \(1/99\) at every positive sinusoidal frequency. This is not a percentage change in impedance. The mixed-RLC uncertainty disks require the dedicated positive series-loss model and an explicit reactance-to-loss budget over the frequency band. The bound below \(1/385\) concerns reflected power at a nominally matched frequency. Absorbed power can include internal dissipation; a matching guarantee alone does not determine useful delivered power.

### Convert normalized values to physical components

Choose a reference impedance \(Z_0>0\) and a time scale \(\tau>0\). For normalized resistance \(r\), inductance \(\ell\), and capacitance \(c\), the physical values are

\[
R=Z_0r,\qquad L=Z_0\tau\ell,\qquad C=\frac{\tau c}{Z_0}.
\]

For example, with a 50-ohm reference and a one-nanosecond time scale, normalized values \(r=2\), \(\ell=1\), and \(c=1\) become 100 ohms, 50 nanohenries, and 20 picofarads. The corresponding angular-frequency scale is one billion radians per second. Frequency in hertz is angular frequency divided by \(2\pi\).

This conversion preserves the normalized ideal response. Selecting real parts additionally requires justified loss and parasitic models, suitable ratings, and tolerances. The written ideal-component guarantees apply when the chosen physical model meets their hypotheses.

### Follow the evidence

An **exact certificate** is finite data that a checker uses to establish specified algebraic or inequality assertions. A **rational interval certificate** can prove that an exact positive algebraic component vector exists inside a rational box; the box's decimal center is an approximation to that vector. A **Lean receipt** records kernel checking of the named formal statements. Written universal proofs, exact finite checks, and selected formal statements have the scopes listed in the verification chapter.

The Smith geometry, Fourier projectors, interpolation criteria, classical synthesis procedures, dimension obstruction, and passive-contraction principles provide established foundations. The target constructions, physical reductions, and quantified specializations are stated with their own proofs and checks. Historical priority is a separate literature question, and the review provenance is project self-review.

The source download contains the authored proofs, component graphs, certificates, and a portable replay entry point. After extraction, run `python -B replay.py` from the extracted root. The package's `START_HERE.md` and source README specify the commands and scope. The pinned Lean toolchain and third-party full-text papers are separate resources.

### Use the reading controls

Every figure has a short alternative and an expandable **Text description** with its main relationships, interpretation, or component connections. These descriptions accompany the equations and tables that supply the detailed data. Figure source links retain the original artwork. The **Open diagram** control provides a larger view when JavaScript is available; use Escape to close it. The text descriptions remain available without JavaScript.

Use Tab and Shift+Tab to move among links and controls, and Enter or Space to operate a focused disclosure or button. A labeled table or code region can receive keyboard focus for horizontal scrolling. The contents links return directly to their chapters. Print view expands the figure descriptions and retains the complete article. Without JavaScript, the text, source links, tables, and TeX equations remain readable; rendered mathematical speech and interactive figure views use the supplied JavaScript tools.
