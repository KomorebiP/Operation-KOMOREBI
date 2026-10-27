# Continue from checked Block 32

Authoritative predecessor: this focused Block32 release. Its own predecessor is
`predecessor/Block31_Checked.zip`, retained byte-for-byte. Read REPORT.md,
PROOF_BOUNDARY.md, MATHEMATICS.md, RESULTS.json, DEVELOPMENT_FAILURES.md,
COMPUTATION_CONTRACT.md, and REPRODUCE.md before editing. Run the read-only verifier
and reproduce a scoped predecessor build with the exact pin first.

Goal I / phase D is closed: actual finite reachable modules have chosen cyclic
coordinates and intrinsic exponent signatures. The signature classifies only the
underlying module. Do not assert canonical bases/matrices, further state-cardinality
reduction, a minimum-generator theorem, or observable minimization from this block.

## Block 33 target: unobservable submodule and reachable-observable quotient
First expose the inherited output as an actual linear map on the reachable module.
For the fixed digit system and output lambda, define

    N = {x | for every finite digit word w, lambda(T_w x)=0}.

Prove N is the greatest transition-invariant submodule in ker(lambda). Construct
it finitely by a descending kernel/preimage chain. Starting from top and an ambient
cardinality p^b, prove a valid stabilization bound by strict p-power cardinality
loss; state precisely which word lengths each iterate checks.

Construct Reach/N, prove the digit maps and output descend, preserve the initial
state and all canonical coefficients, and prove that quotient equality is exactly
future-output indistinguishability. Reuse Block32 for a cyclic presentation of the
quotient, without assuming field structure or freeness over ZMod(p^r).

A later minimality claim must specify the category: the behavior of every finite
digit word, linear reachability, and a comparison/universal property for other
realizations. Do not replace this by a rank argument over a field or conflate it
with minimal DFA state count. The smallest closed kernel/quotient block is already
a meaningful checkpoint if the full universal minimality proof is not finished.

Preserve all prior proof boundaries, counterexamples, definitions and explicit
execution-cost contracts. Continue to distinguish Lean mathematical constructions,
exact finite reference computations, and unperformed executable refinement.
