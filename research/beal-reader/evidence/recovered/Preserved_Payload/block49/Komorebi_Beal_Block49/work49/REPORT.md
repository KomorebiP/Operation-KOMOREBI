# Komorebi Beal research — Block 49

The full Beal conjecture and the complete signature **A³+B⁵=C⁷ remain unresolved**. This continuation studies positive pairwise-coprime integers A, B, C. It adds structural restrictions to two surviving branches of the existing argument; it does not exhaust every branch or prove nonexistence.

This checkpoint extends the frozen Block48 archive with SHA256 `bbf78879d4b5714c818dd1521053dcd6b80c0694799b120b440fa850efec091a`. Earlier files are unchanged. The detailed proofs retain the external mathematical and database inputs of that checkpoint. No literature-wide novelty claim is made.

## Results and their scope

| Investigation | Result | Remaining obstruction |
|---|---|---|
| Reducible branch, 3990 divides C | C must have another prime divisor q with q modulo 35 in {1,8,13,22,27,29}. | Eligible primes can occur; this is not a contradiction. |
| Last form at level (45), norm 2025 | The explicit CM Jacobian of D: Y²=X⁶+324X identifies the surviving form l. Its residual congruence forces 8778 divides B and gcd(C,210)=1, retaining the previous residues modulo eleven. | The CM congruence has not been excluded for nonzero B. Higher levels remain separate. |
| Local geometry at three and five | The quadratic twist has split toric monodromy matrices (7v₃(C)−3)I₂ and (14v₅(C)−5)I₂. | Its natural seven-torsion is ramified; changing lattices changes residual extension data. |
| Alternative elliptic representation | A curve with rational three-torsion gives an absolutely irreducible mod-seven representation over Q whenever 5 divides C. | On the difficult branch, its residual conductor retains variable primes dividing B. |
| Global formulation of the CM branch | An abstract cover over Q(√5) has degree1176 and genus191; every solution attached to l lifts to a rational point over that field. | Its defining equation and required rational-point exclusion remain unknown. |

Review completion and final revision pins are recorded in `VERIFICATION.md`. The conclusions are written arithmetic arguments with exact-source checks and finite computational support, not new Lean-formalized arithmetic theorems.

## Why the additional prime is forced

After the previously established quadratic twist, the residual characters are 1 and the mod-seven cyclotomic character χ. An opposite nonsplit extension has coefficients χ⁻¹. Local characteristic-zero sublines force this extension to split at seven and at C-primes whose norms are not 1 modulo seven; a local cohomology calculation handles three and five.

If no eligible prime divides C, the extension would produce an everywhere-unramified seven-extension of Q(√5,ζ₇). The class number one of Q(ζ₃₅), followed by extension and norm, rules this out. The rational residue classes in the table are exactly the translation of the prime-ideal norm condition. See `notes/extension_route.md` and its independent audit. The class-number input is checked in [Masley’s primary paper](https://www.numdam.org/article/CM_1976__33_2_179_0.pdf).

The independently reviewed companion `notes/extension_selmer_sharpness.md` determines the surviving abstract extension space: its dimension is the number of eligible prime ideals allowed to ramify. Thus the class-number argument genuinely stops at nonempty eligible support. A surviving abstract Galois class need not arise from the Jacobian and is not a Diophantine solution.

## What changed for the last modular candidate

The order-five automorphism of D proves CM by Q(ζ₅). Explicit good-reduction models give its exact RM conductor (45). CM theory and quadratic automorphic induction place its compatible system in the known Hilbert modular space. Its trace polynomial at eleven uniquely singles out [2.2.5.1-2025.1-l](https://www.lmfdb.org/ModularForm/GL2/TotallyReal/2.2.5.1/holomorphic/2.2.5.1-2025.1-l) among the fourteen retained orbits. Bounded trace agreement alone is not used to infer modularity or identity.

Comparing inertia at three forces 3 divides B; comparing at five excludes 5 divides C. At seven, finite-flat uniqueness allows comparison of the actual four-dimensional torsion groups. The boundary Jacobian has p-rank zero and a-number one. The earlier exact Cartier calculation then forces 7 divides B and excludes 7 divides C. Combining with 418 divides B gives **8778=2·3·7·11·19 divides B**.

This is where the earlier coefficient-section/polyphase calculation contributes: its Cartier strata now distinguish actual finite-flat torsion. It does not imply congruences modulo every power of seven or force B=0.

The further cover construction uses the explicit family
\[
Y^2=X^6+10t^2X^3-12t^3X+5t^4.
\]
At t=−B⁵/A³ it is rationally isomorphic to the actual Frey curve. Exact finite-group computations establish the geometric projective image PSL₂(F₄₉) and its normalizer quotient. The resulting cover is defined abstractly over Q(√5), with degree1176 and genus191. A solution matching l must lift to a Q(√5)-rational point above its rational parameter t. This is a necessary condition, not a converse or a determination of the point set. See `notes/last_form_cover_frontier.md` and its separate audit.

There is already a known rational boundary point over Q(√5): the unique unramified point above t=0. It corresponds to the excluded boundary B=0. The required next result must exclude the relevant nonboundary points; the entire rational-point set is not empty.

## What is still missing

The smallest-level CM congruence now has a specified global point problem, but no exclusion for B≠0. The reducible branch needs control of which surviving extension classes can arise from this Jacobian. The alternative curve needs a way to handle its variable conductor. The other three possible Hilbert levels have not been computed in this environment; the retained Magma exporter remains unexecuted.

Proofs, source locators, exact computation contracts, independent reviews, and an executable continuation handoff are included in the archive. Checksums verify the files’ bytes; they do not certify their mathematics.
