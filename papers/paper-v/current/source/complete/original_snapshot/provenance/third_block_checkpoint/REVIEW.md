# Paper V compiler and proof review, v0.3.0

Author: Komorebi P.

## Result

The actual pinned Lean build and axiom audit pass for **133 theorem targets in 14 modules**, including every inherited candidate. This is the first reproduced compiler pass for these Paper V sources in this workflow. The full verifier returns 0. The manual 20-result ledger retains incomplete manuscript obligations.

## Repairs to inherited candidates

The first build found a genuine unclosed goal in packet annihilation: simplification rewrote the phase equality but did not use the required distinct-residue hypothesis. The proof now supplies that hypothesis directly. The FIR inverse-address proof needed explicit reduction of composed equivalences, and integer analysis/synthesis needed the positive-modulus argument specialized in its quotient rewrite. The real absolute-value triangle theorem name was updated to the pinned API.

Other repairs satisfy the retained warnings-as-errors gate: unused simplification arguments and an unused section typeclass were removed, a class-valued definition received the appropriate instance-reducibility annotation, deprecated imports and an if-expression lemma were replaced, and one unnecessary simplification was corrected. No inherited theorem was removed or weakened. The unused Fintype premise removed from packet_refinement broadens that theorem.

## Added checked mathematics

HilbertPackets provides actual complex l2 spaces and bounded linear operators, rather than assuming l2 membership for pointwise masks. It proves norm contraction, idempotence, annihilation, exact synthesis, symmetry, orthogonality, and integer residue refinement. Integer address coordinates lift to a linear isometry equivalence. The impulse family has a convergent expansion, finite-support expansion, dense shift-generated span, and an explicitly defined isometric shift.

CompletePrunings uses typed node identities, so repeated labels do not collapse distinct nodes. It proves that every recursive cut hits every terminal path exactly once. Conversely, every node set with that property yields a unique recursive cut. The condition is equivalent to a covering antichain under literal rooted-tree ancestry. Finiteness and arbitrary-objective attainment are transported to the set-valued pruning space.

HaarHilbert proves both reconstruction identities and the energy equality for arbitrary complex l2 channels, using normalized real scalar coefficients and the Hilbert-space parallelogram law. These are infinite-channel results, not finite regression tests.

CRT proves literal residue-mask factorization, including arbitrary signed input addresses and the dyadic-odd case. SmithAction proves a normalized homogeneous action, composition, scaling, and nonzero-pair preservation. Its half-turn swaps zero and infinity in homogeneous coordinates. Finite-chart formulas carry explicit denominator assumptions.

FiniteAdaptive additionally transfers the deterministic gap certificate to a probability lower bound by inclusion of the joint local-error event.

## What this does not establish

The entire manuscript is not yet certified. In particular, there is no completed Lean proof of the formal-series cyclic product theorem, the full measurable-mask perturbation statement, or the literal transform-domain filter-bank representation. The packet-tree adjoint and energy construction and several named semantic specializations also remain. The ledger is a manual statement comparison and is not a machine-checked PDF-to-Lean equivalence.

No manuscript PDF was changed, no new compiler axioms were introduced, and finite Python testing is not counted as a universal proof. The runtime adapter only supplies the compiler's own executable path and is disclosed in verification/runtime/RUNTIME.md. Failed development builds are development evidence, not release certificates.
