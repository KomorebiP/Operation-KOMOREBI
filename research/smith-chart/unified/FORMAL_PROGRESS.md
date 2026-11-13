# Resistor elimination and finite mixed-loss contraction

The next companion adds sixteen selected theorem axiom audits to the earlier
twenty-five, for forty-one across four receipts. It closes two concrete finite
algebraic steps rather than replacing the remaining analytic proof obligations.

For a resistor-only internal vertex with nonnegative incident conductances
$g_j$, put

$$G=\sum_jg_j,\qquad S=\sum_jg_ju_j,\qquad v=S/G.$$

When $G>0$, its zero-injection KCL determines $v$ uniquely. Eliminating the
vertex adds a nonnegative symmetric mesh conductance

$$\widehat g_{ij}=g_ig_j/G.$$

`StarMesh.lean` checks that the eliminated KCL is satisfied, proves its
converse, and proves every retained-current equation

$$\sum_j\widehat g_{ij}(u_i-u_j)=g_i(u_i-v).$$

It also checks the retained equations with arbitrary preexisting conductances.
This resistor-elimination file uses real potentials, as at positive-real
Laplace samples; the mixed-loss file uses complex potentials and currents.
If $G=0$, nonnegativity forces every incident conductance to vanish, which is
the separately checked isolated-vertex case. The index type is any finite
type; these are actual weighted network equations rather than a scalar example.

`LossContraction.lean` derives the complex dissipated-power identity from
finite incidence KCL and the branch laws. It combines the existing bilinear
impedance-change identity with finite weighted Cauchy-Schwarz to prove

$$|\Gamma'-\Gamma|^2\le
 B(1-|\Gamma|^2)(1-|\Gamma'|^2)$$

from the stated local mismatch inequalities and two actual unit-drive branch
solutions. The exact polynomial identity behind the uncertainty disk is also
checked. The formal theorem takes those solutions as hypotheses; the
positive-loss existence argument and the physical component-box specialization
are supplied by the written proof, not silently included in the formal count.

The replay authenticates and repeats the original graph-core receipt, compiles
both extensions, prints all sixteen axiom dependencies, rejects a missing-factor
mesh control and an understated-disk control, and accepts two positive fixture
statements. Only the established standard axioms are allowed. Commands, input
hashes and output hashes are retained in the new receipt.

The remaining universal assurance gap includes iteration over arbitrary
resistor eliminations with the complete boundary semantics, bounded-current
existence in the broader compact model, analytic limits, the rational sample
identity and the packet-transfer chain. The two-reactive coefficient separator
also retains classical source leaves and a written physical bridge. Independent
human review remains separate from these author-produced kernel checks.
