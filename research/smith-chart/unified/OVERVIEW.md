# Current results and reading route

The original degree-six target has a positive transformer-free circuit with
three inductors, three capacitors and seven resistors. Its reduced degree is six,
so its reactive minimum is exactly six. The full circuit and exact root certificate
are part of this reading, together with the constructive and lower-bound work.

| Result | What is now available |
|---|---|
| [Original target: minimum six](#exact-six) | The eight-node physical circuit, graph equations, positive root box and matching degree lower bound. |
| [Certified circuit composition](#composition) | Exact physical graph reconstruction from verified leaves and passive outer elements. |
| [Complete first-order and Cauer synthesis](#low-order-synthesis) | All first-order positive-real rational targets, plus rational RC/RL classes through degree fifteen within current caps; first-order resistor minima and the Hughes base's two-resistor minimum. |
| [Families in every degree](#families) | The written lift theorem and explicit inverse for a specified cubic family. |
| [Deterministic construction](#deterministic-family) | Exact recognition and replayable certificates for rational members; the implementation covers degrees three through sixteen within its stated resource limits. |
| [Hughes margin and transferred families](#effective-margin) | The written explicit margin $2^{-2^{803}}$ and the degree-$4k$, reactive-$7k$ deductions. |
| [Audit of the universal argument](#compact-model-audit) | The resistor reduction, physical boundaries, sample identity and external theorem hypotheses have received a fresh project self-review. Independent or formal verification remains separate. |
| [Selected formal graph core](#formal-graph-core) | Forty-one selected Lean theorem audits, including actual resistor-node elimination and mixed-loss contraction from KCL; whole-chain formalization remains open. |
| [Typed margins and balanced resonance](#typed-margins) | Whole one-L/one-C margins retain coverage of 1,334 of 2,130 classes. The exact balanced internal-mode face now has margin $10^{-13}$, and a certified detuning/opening-budget region has margin $3/40$. All 796 whole balanced placements remain open; current proofs state the missing near-mode transfer and regular-region separator explicitly. |
| [Component-tolerance theorem](#component-tolerances) | In ideal fixed RC/RL networks, one-percent component tolerances change reflection by at most $1/99$ at every positive real frequency. For mixed networks with dedicated positive series losses, an exact uncertainty disk now covers independent component errors over a specified band; a matched port with band ratio at most ten and one-percent errors reflects less than $1/385$ of incident power. |

Read the foundations first if cyclic packets and reflection coordinates are new
to you. The current synthesis arguments then lead from the exact-six circuit to
composition and deterministic family construction. The separation arguments
explain why rational degree alone does not always predict reactive complexity.
Historical searches and superseded status registers are retained in an expandable
history section, rather than presented as competing current results.

The model throughout the current RLC results is finite positive ordinary,
uncoupled and transformer-free. Resistor minima for the original degree-six and
higher-degree targets, broader parasitic models and physical measurements,
historical priority and a practical arbitrary-target minimum solver remain open.
The older ideal-transformer construction has a different allowed component class.

The certificate replays and finite controls establish their declared exact
assertions. The new Lean replay checks selected universal finite-graph and shape
statements; it does not turn the whole book into a formally verified work.
The earlier formal companions and their original bindings remain available.
