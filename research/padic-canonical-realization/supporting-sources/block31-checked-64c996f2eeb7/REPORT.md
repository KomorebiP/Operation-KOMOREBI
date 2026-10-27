# Block31 — Correlation-aware reachable modules

Status is controlled by RESULTS.json and fresh verification receipts.
Roadmap position: Goal I, phase C. The coordinate-ideal stages29–30 are the verified
predecessor. Canonical invariant-factor presentations and observational quotients
remain distinct later milestones.

## Main theorem
For an R-linear digit system M with seed v, define

  Reach(M)=span_R {T_w(v): w is any finite ordered digit word}.

The new generic theorem proves Reach is the least invariant R-submodule containing
v. It captures cross-coordinate relations, unlike coordinate support and products
of coordinate ideals. It works over a commutative coefficient ring, without an
assumed field or inversion of a nonunit.

Let U_0=0 and U_(n+1)=U_n+Rv+sum_d T_d(U_n). If the finite ambient module contains
p^b elements, p prime, then U_b=Reach and every subsequent iterate is equal to it.
Proper inclusion raises the p-power cardinality exponent by at least one. This
proves b rounds suffice; enumerating all p^b ambient vectors is not required by
the mathematical construction. It is a closure-round bound, not a runtime bound.

## Actual masks
The ambient module is the existing ideal mask state, whose cardinality is
p^(sum_i c_i). Thus b=sum_i c_i supplies the bound. Its transition and initial
state are unchanged. The reachable subtype injects into the prior cyclic state,
and that embedding commutes with the initial state, every digit, every ordered
word, and the output functional.

An additional image theorem proves that its image in the original profile space
is the globally least invariant R-submodule containing the initial full-profile
vector. It is not merely least within one independently chosen ideal product.
The generic image theorem commutes reachable spans with every linear simulation
that preserves the seed and intertwines the digit operators.

Under the unchanged mask assumptions p prime, r>0, p not dividing B(0), and
A(0)=B(0) modulo p^r, the new machine computes coeff_n(F) for every n of the
previously constructed canonical normalized Mahler series. No supplied-series
oracle is reintroduced. Precision reduction remains exact at the output level.
The certificate retains the complete predecessor cyclic-machine certificate.

## Exact witness
Over ZMod5, v=(1,1,0) and T(x)=(0,0,x0-x1) have

  Reach={(a,a,0):a in ZMod5}, cardinality5.

The previous least ideal product is the full three-coordinate box, cardinality125.
Both exact cardinalities and the submodule equality are production Lean theorems.
Every vector in the diagonal submodule maps to zero.

The span is not the orbit set. The identity system on ZMod5 with seed1 has orbit
{1}, but its reachable linear span has five elements and includes0. If its output
is zero, all these states remain observationally indistinguishable. These scope
witnesses prevent treating reachability as minimal automaton construction.

## Actual-mask finite examples
The exact Python reference uses integer column lattices containing p^r*Z^N. It
closes under seed and digit images using Hermite normal form. An independent
small-system oracle enumerates orbit and additive span. Actual-mask columns are
checked against direct polynomial operations; a second actual-mask route builds
the span of short words by direct polynomial transitions instead of HNF-basis images.
All numerical values below are finite audit results, not separate concrete kernel
reductions of the complete noncomputable actual-mask construction. A=1 in each row.

| p | r | B | Ideal-product exponent | Reachable-module exponent | Strict growth rounds |
|--:|--:|---|--:|--:|--:|
| 2 | 4 | 1+4z | 10 | 8 | 3 |
| 2 | 8 | 1-z | 101 | 52 | 5 |
| 2 | 8 | 1+16z | 20 | 16 | 3 |
| 3 | 6 | 1+81z | 11 | 9 | 2 |

Exponent e means p^e module states, not e independent generators. In the second
case the closure's cardinality exponents are 0,8,23,42,50,52 before stabilization.
The sufficient ambient bound is101 rounds; this numerical case stabilizes in5.
Strict reductions occur in25 of49 actual mask cases. Strict improvement is not a
universal theorem. No runtime or memory savings are inferred from cardinality.

## Verification and remaining scope
Three modules add56 source-declared theorems to878 inherited declarations, total934
in78 production modules. All inherited mathematical modules are byte-identical;
the root has only the new import. A clean project-local build and complete axiom
inventories are required by the final plan. Precise fresh test counts and exits
are recorded in RESULTS.json. Historical finite suites are not counted as fresh.

The entire module theory is checked as Lean mathematics. The Python HNF engine
is not formally refined to that code. Invariant factors, a canonical basis,
canonical transition matrices, observable quotients, minimum automata, state
isomorphisms across precision, analytic convergence, and bit/time/memory bounds
are not claimed. The underlying polynomial interfaces remain noncomputable.

The first full compiler/test sequence succeeded, but evidence aggregation omitted
62 wrapped axiom reports. The report parser was repaired and regression-tested;
all final phases were repeated after the repair with frozen execution inputs.
The failure and first receipts are retained. No theorem was changed or retracted.

The exact checked pin remains Lean4.34.0-rc2 with mathlib
 aeb72f1e9981b6d35b426b16dca7759be3e7ba06. Dependency artifacts are pinned, not
independently rebuilt. leanchecker is another replay through Lean's own kernel.
Stable4.34.0 compatibility and independent human/kernel review remain unperformed.
