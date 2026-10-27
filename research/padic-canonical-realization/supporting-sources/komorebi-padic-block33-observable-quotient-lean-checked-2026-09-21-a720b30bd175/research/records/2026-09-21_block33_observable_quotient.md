# Route: quotient by complete future-output kernel

Claim: for the fixed reachable linear mask system, form the greatest silent
invariant submodule and its observable quotient. Success criterion: kernel-checked
finite horizon, exact future-equivalence quotient, preserved canonical output,
reachability, and unchanged predecessor semantics. Failure criterion: missing
invariance, wrong word order/horizon, or a nonfield counterexample.

Route: intersect kernels of word-output maps, prove the finite descending chain
using prior p-cardinality lemmas, descend maps with mathlib quotient APIs, and
instantiate the inherited actual reachable source. Cross-check numerical row-HNF
closure by independent exhaustive behavior partition refinement on small modules.

Outcome: proved as written under the recorded hypotheses. 67 new declarations,
13 successful final phases, 21,442 exact assertions. Concrete nonfield and
immediate-kernel restriction examples passed. Sources, commands, hashes, full
scope and failures are recorded in the root documents and results/ receipts.

Next implication: identify the behavior-map image with a representation-independent
residual-generated module, then compare all realizations of the same word series.
