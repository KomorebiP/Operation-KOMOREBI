# Block 32 proof boundary

PROVED: finite prime-power module cyclic presentations; exact exponent range;
componentwise scalar-reduction law; exact cardinality; complete generator relations;
p^k-torsion cardinalities and intrinsic factor multiplicities; uniqueness of the
multiset and sorted exponent list; signature classification of additive and ZMod
module isomorphism types; transport of initial states, digit maps, outputs and
ordered words; equivalence between coordinate choices by conjugacy; mixed-modulus
entry formula and source-annihilator/divisibility constraints; actual Block31
reachable mask integration; canonical all-coefficient output, output precision
compatibility and retained predecessor certificate; two noncanonicality witnesses.

Finite presentation existence assumes p prime and a finite ZMod(p^r)-module.
Precision r=0 is included and yields no nontrivial factors. Signature uniqueness
for already supplied p-power presentations only needs p>1. Natural representative
expansions and cyclic cardinality formulas explicitly require p>0; no claim is
made that natural representatives encode negative elements of ZMod(0)=Z.

Actual mask correctness assumes prime p, r>0, p not dividing B(0), and A(0)=B(0)
in ZMod(p^r). F is the inherited constructed canonical series, not an oracle.
The presentation is of the actual reachable submodule, not a supplied matrix
surrogate. A chosen additive coordinate equivalence respects the scalar reduction
in every factor. Digit endomorphisms are transported additive maps with that
ZMod-module compatibility, not unrestricted matrices over a single field.

The signature classifies only the UNDERLYING MODULE. Equal signatures need not
imply equal digit systems, equal outputs or equal coefficient sequences. The
chosen generators and literal transported matrices are not canonical. State
cardinality is exactly unchanged; the number of cyclic factors is not claimed
here as a separately proved minimal-generator theorem.

Observational quotients, minimal automata, precision-state morphisms, an optimized
executable Lean presentation algorithm, and formal Python/Lean refinement remain
open. The exact Python Smith engine is certificate-checked numerically. Its chosen
coordinates are not asserted equal to Lean's classical choice. No runtime/memory
saving follows solely from replacing a subtype by cyclic coordinates.

Lean4.34.0-rc2 and pinned cached mathlib are the checked lane. leanchecker reuses
Lean's own kernel. Cached dependencies were not independently rebuilt. Stable4.34.0,
independent human and independently implemented kernel review remain unperformed.
All prior mathematical modules are byte-identical except for a root import addition.
