# Audit of the compact-model and effective-margin argument

**Verdict: proved as written at the level of the checked written argument.**
This is a separate adversarial project self-review of the base-margin proof,
followed by the finite packet-transfer implications. It is not outside peer
review or a Lean proof. Every listed mathematical obligation passed this fresh
internal review. Independent or formal verification remains a separate task.

## Claim and dependencies

For every finite positive ordinary uncoupled transformer-free RLC one-port with
at most four reactive branches and arbitrary finite resistor count, the seven
specified positive real samples separate its reflection response from the Hughes
target by at least $2^{-2^{803}}$. The samples are real Laplace arguments.

The dependency graph is: resistor elimination; bounded sample witnesses;
physical open/short semantics; seven-sample identity; Hughes's exclusion;
the integer polynomial model; the effective-minimum theorem. The packet-family
conclusions additionally use the compact-admittance estimate, physical scale
allocation, target-error bounds and disjoint-pole degree argument.

## Arbitrarily many resistors really reduce to ten vertices

Retain both port terminals and all reactive endpoints. There are at most
$2q+2$ retained vertices. Every other vertex is incident only to resistors.
Discard resistor components touching no retained vertex. For each remaining
eliminated component, its grounded Dirichlet block $D$ is positive definite:
its quadratic energy can vanish only when all internal potentials agree and
vanish at the attached boundary. Hence $D$ is invertible and $D^{-1}\ge0$.

In the resistor Laplacian's Schur complement $A-BD^{-1}B^T$, the off-diagonal
entries are nonpositive and row sums vanish. It is therefore another nonnegative
conductance Laplacian on retained vertices. This operation is independent of $s$,
and leaves every reactive branch in place. Parallel resistors combine by adding
conductances. This proves the bounded representation for arbitrary finite
resistor count, including components attached to just one retained vertex.

For $q=4$, pad to ten vertices, 45 resistor slots and four labeled reactive
slots. Repeated reactive positions are allowed. The $90^4$ placements are a
finite covering family of labeled skeletons, not a completed enumeration.

## The bounds include disconnected and boundary states

Drive the network through a unit resistor from a unit voltage source. Then
$V+I=1$. On its port component the maximum principle gives potentials between
zero and $V$. A voltage-level cut between an edge's endpoint potentials carries
total current $I$ in one direction, so every physical edge current has magnitude
at most $I$. Floating components may be assigned zero potential. Thus voltages
lie in $[0,1]$ and oriented currents in $[-1,1]$ uniformly in all positive values.

Each component has one shared parameter $t=\kappa/(1+\kappa)$ across all samples.
The equation $b(1-t)i-at(v_u-v_v)=0$ imposes an open at $t=0$ and a wire at $t=1$.
Delete every open and contract every wire. Summed KCL cancels internal wire
currents. Every remaining branch has a positive finite value fixed across
samples, so the recovered equations belong to one physical ordinary RLC graph.
The reactive budget can only decrease. Floating remnants do not alter its port.

The port is short, open or a finite positive one-port. Arbitrary wire-current
circulations do not create another device: they disappear under contraction.
This proves the reverse implication needed to rule out spurious zero-error
boundary solutions.

## Exact current elimination and counts

The potential resistor star is a spanning tree even when its compact slots
are open. KCL uniquely expresses each star current using the retained voltage
and chord currents. Substituting into branch equations and retaining both
recovered-current bounds is a bijective elimination of variables, including
at opens and shorts; it is not a physical network reduction.

There are 49 component parameters, $7\cdot49$ sample variables and the error
variable: $\nu=393$. The 343 branch equalities, 786 direct box inequalities,
126 recovered-current bounds and fourteen error inequalities give $m=1269$.
All polynomials are integer and quadratic or linear. Distinct parallel slots
retain distinct current variables. Sample factors have numerator and denominator
at most seven; the error inequalities have height at most twice the largest
reduced target denominator, giving $H=304$.

## Why the objective cannot vanish

The feasible set is closed inside the displayed bounded box. A zero-error
point would recover one physical circuit matching all seven samples. Opens and
shorts have extreme reflection values and cannot match these interior data.
For $q$ reactive branches, the spanning-tree and terminal-separating forest
formulas, multiplied by $s$ to the number of inductors, have degrees at most $q$.
Cancellation decreases degree. A degree-at-most-four competitor and the
degree-two target therefore have a cross-product polynomial of degree at most
six. Seven distinct positive agreements imply identity.

The classical exclusion needed here was checked in Hughes, arXiv:1611.06258v2,
Lemma 3 and Theorems 4–6, printed pages 4–5. The normalized target has
$K=\omega_0=F=1$, $W=2/3$. Its exceptional three-reactive parameters fail; the
four-reactive alternatives require an incompatible $W$ range or $F^2=4/3$ or
$4/27$, whereas $F^2=1$. The result permits arbitrary resistor counts.
[Primary source](https://arxiv.org/pdf/1611.06258v2).

Thus every nonempty compact component has a strictly positive objective minimum.
No genericity, isolated root or full-rank Jacobian hypothesis has been used.

## The effective theorem fits this exact model

Jeronimo–Perrucci–Tsigaridas, arXiv:1112.0544v1, Theorem 1 on printed page 2,
applies to an integer basic closed set, a compact connected component, even
degree bound $d$, coefficient bound $H$, and a nonzero polynomial minimum.
Its factor $\widetilde H$ multiplies $d^\nu$; it is not raised to $d$.
[Primary source](https://arxiv.org/pdf/1112.0544v1).

The objective is the integer linear coordinate $z$, and $d=2$. With
$\widetilde H=3324<2^{12}$, its denominator bound has base less than $2^{213}$
and exponent $393\,2^{786}$. Therefore

$$
z\ge2^{-83709\,2^{786}}>2^{-2^{803}},\qquad 83709<2^{17}.
$$

Choose $z$ equal to the actual maximum sample error. It is feasible and lies
in $[0,2]$. Every skeleton has the same bounds, so no enumeration or penalty
for the number of skeletons is required. The theorem's hypotheses and exponent
were checked against rendered primary-source pages, not parsed exponents alone.

## The finite transfer also keeps physical storage

For $u_e=y_e/(1+y_e)$, the driven nodal derivative is
$\partial\gamma/\partial y_e=-2(v_a-v_b)^2$. The voltage and cut-current
bounds give $|v_a-v_b|+|i_e|\le1$, hence
$|\partial\gamma/\partial u_e|\le2$. Integrating coordinates proves

$$|\gamma(u)-\gamma(u')|\le2\sum_e|u_e-u'_e|.$$

Interior networks can be regularized on a fixed skeleton. This uniform estimate
gives a unique continuous boundary response, which the compact equations identify
with physical deletion/contraction. The estimate therefore includes the boundary.

Threshold rounding changes a sample response by at most $2QM\eta$. A capacitor's
local coefficient is $C\epsilon^j$ and an inductor's is $h\epsilon^{-j}$.
If $\epsilon<(\eta/(1-\eta))^2$, the same physical component can be active in
at most one packet. Summing required packet budgets proves the allocation
contradiction without a bound on resistor count or an assumed competitor topology.

For the three Hughes profiles, use budgets $1,5,1$, outer margins $8/105$ and
$3/20$, and the checked base margin. The displayed $\eta_0,\delta$ bounds leave
the asserted $\Delta/2$ separation. The second allocation uses
$Q=7k-1$, $M_B=2/\delta$ and the displayed $\eta_1,\epsilon_k$; its rounding and
leakage errors are each below $\Delta/8$. This yields the $7k$ lower budget and
the $\Delta/4$ separation. The retained positive construction gives the upper
budget. The explicit pole annulus has ratio at least $(32/225)\delta^2$, larger
than $\epsilon_k$, so scaled poles are disjoint and degree is exactly $4k$.
Adding $\rho=\Delta/16$ changes positive-real sample responses by at most
$\Delta/8$ and adds no storage. The strictly dissipative conclusion follows.

## Obligation record and remaining work

| Obligation | This review |
|---|---|
| Arbitrary-resistor reduction and retained-vertex bound | Passed in written self-review |
| Bounded voltages/currents and floating components | Passed in written self-review |
| Uniform physical open/short semantics | Passed in written self-review |
| Star elimination, counts and coefficient height | Passed in written self-review |
| Seven-sample rational identity | Passed in written self-review |
| Exact Hughes and JPT source implications | Verified against exact primary versions |
| Finite packet allocation, constants and degree | Passed in written self-review |
| Independent peer review or formal kernel proof | Not performed |
| Useful-size optimized margin or compact global refutation | Still open |
| Arbitrary-target minimum synthesis and hardware tolerance | Still open |

The new boundary experiment checks all 243 open/finite/short assignments on one
specified five-edge graph, at three positive real samples and two regularization
values: 1,458 exact comparisons. It includes parallel branches and floating
components. Those controls test the implementation and interpretation; the
written uniform proof, rather than that finite inventory, supplies global scope.
No historical novelty claim is made.
