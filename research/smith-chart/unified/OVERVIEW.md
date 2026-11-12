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
| [Selected formal graph core](#formal-graph-core) | Seventeen Lean theorem audits for conservation, contraction, port power, Stieltjes shape and exact margin implications; whole-chain formalization remains open. |
| [Usable typed margins and mixed reduction](#typed-margins) | Explicit bounds for all RC-only and RL-only networks; one mixed representative has an exact rational refutation at margin $1/1000$. The remaining mixed exclusion problem has 2,129 representatives. |
| [Component-tolerance theorem](#component-tolerances) | In ideal fixed RC/RL networks, one-percent component tolerances change reflection by at most $1/99$ at every positive real frequency. A mixed-LC counterexample explains the required restriction. |

Read the foundations first if cyclic packets and reflection coordinates are new
to you. The current synthesis arguments then lead from the exact-six circuit to
composition and deterministic family construction. The separation arguments
explain why rational degree alone does not always predict reactive complexity.
Historical searches and superseded status registers are retained in an expandable
history section, rather than presented as competing current results.

The model throughout the current RLC results is finite positive ordinary,
uncoupled and transformer-free. Resistor minima for the original degree-six and
higher-degree targets, mixed-RLC robustness and physical measurements,
historical priority and a practical arbitrary-target minimum solver remain open.
The older ideal-transformer construction has a different allowed component class.

The certificate replays and finite controls establish their declared exact
assertions. The new Lean replay checks selected universal finite-graph and shape
statements; it does not turn the whole book into a formally verified work.
The earlier formal companions and their original bindings remain available.
