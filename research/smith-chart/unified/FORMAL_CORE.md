# Formal assurance of the finite graph core

The new Lean companion checks universal finite-graph identities used by the
physical boundary and sensitivity arguments. The graphs are actual finite
oriented incidence data, with independently indexed edges; parallel edges,
loops and disconnected graphs are allowed. There is no fixed vertex census,
connectedness assumption or nonsingular-network surrogate in these identities.

For source and destination maps and a branch-current vector, define

$$\operatorname{div}i(v)=\sum_e
 \bigl([\operatorname{src}e=v]-[\operatorname{dst}e=v]\bigr)i_e.$$

The checked discrete Green identity is

$$\sum_v u_v\operatorname{div}i(v)
 =\sum_e(u_{\operatorname{src}e}-u_{\operatorname{dst}e})i_e.$$

For any vertex quotient map $q$ and any quotient vertex $w$, Lean also checks

$$\sum_{q(v)=w}\operatorname{div}i(v)
 =\operatorname{div}_{q\circ\operatorname{src},q\circ\operatorname{dst}}i(w).$$

A wire whose endpoints are identified contributes zero after contraction.
The resulting KCL has exactly the summed original injections. Filtering out
contracted storage branches cannot increase their finite count. These results
close the finite algebraic cancellation step even when wire currents include
circulations and floating components are present.

The two-solution port version gives the bilinear impedance-change identity from actual
KCL and branch voltage-current laws. Its scalars form any commutative ring,
including complex phasors. The complex unit-drive power normalization and the
combined same-sign sensitivity-budget inequality also have checked statements.

`PureTypeMargins.lean` supplies the exact positive Stieltjes-kernel stencil,
its extension to arbitrary finite positive sums, and the two numerical sample
margin implications. Its physical shape characterization remains an explicit
classical source leaf.

The replay uses the existing pinned Lean 4.34.0-rc2 and Mathlib environment.
It recompiles the saved sources, prints axioms for the declared theorems and
rejects deliberately false conservation and margin controls. The published
receipt binds source bytes, compiler and dependency identities, commands and
raw outputs. This is kernel verification of the statements enumerated in that
receipt, not whole-book or whole-universal-margin formalization.

The follow-up `ShuntMargin.lean` adds four kernel and finite-sum theorems for
the direct-terminal-inductor/arbitrary-RC margin class. Its replay first
repeats and byte-matches the original seventeen-theorem receipt, then compiles
the extension and checks a false-shape control and a positive fixture.
There are twenty-one selected theorem axiom audits in total. The extension's
receipt is separate so the earlier proof and receipt bytes remain unchanged.

Still required for complete formal closure are the arbitrary-resistor Schur
reduction, bounded-current/max-principle existence, analytic boundary-limit
argument, rational-degree/sample-identity bridge, external effective-minimum
theorem application and full packet-transfer consequences. Independent human
review is also separate from these author-produced formal files.
