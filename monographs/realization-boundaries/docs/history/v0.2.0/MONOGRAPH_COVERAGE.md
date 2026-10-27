# Monograph coverage — Lean v0.2.0

The original 45 numbered statements retain their printed numbers. COMPLETE means that all stated mathematical clauses are represented in the accepted Lean development, possibly by several declarations. It does not mean historical novelty or external review.

| Book statement | Title | Lean status | Exact scope |
|---|---|---|---|
| 1.5 | Countable-code bound | PENDING | Not formalized in this tranche. |
| 1.8 | Reachability obstruction | PENDING | Not formalized in this tranche. |
| 2.1 | The torsion subgroup of the product | COMPLETE | The original finite-support subgroup is torsion, dense and proper in the actual unrestricted product. |
| 2.2 | Diagonal endomorphisms of the direct sum | PENDING | Not formalized in this tranche. |
| 2.3 | An infinite seed obstruction | PENDING | Not formalized in this tranche. |
| 2.4 | Topological cyclicity | PENDING | Not formalized in this tranche. |
| 2.5 | Profinite completion of the direct sum | COMPLETE | Topological additive equivalence from Mathlib's actual all-finite-quotients completion of D to P, respecting the canonical map. |
| 2.6 | Unique division in the ambient quotient | COMPLETE_ALGEBRAIC | Actual quotient and derived rational module; no nonzero divisible embedding in P. |
| 3.1 | Subgroup and isomorphism classification | PENDING | Not formalized in this tranche. |
| 3.2 | Finite observations leave continuum many possibilities | PENDING | Not formalized in this tranche. |
| 3.3 | The prime-spectrum criterion | PENDING | Not formalized in this tranche. |
| 3.4 | (untitled corollary) | PENDING | Not formalized in this tranche. |
| 3.5 | Unary selector classification | PENDING | Not formalized in this tranche. |
| 4.2 | Pure-preimage correspondence | COMPLETE | Both directions, both inverse laws and order reflection are checked. Purity is root lifting in P; inclusion of D is explicit. |
| 4.3 | Ambient root criterion | COMPLETE | Both directions for every positive multiplier and every actual preimage. |
| 4.4 | One finite-quotient system for every preimage | COMPLETE | Canonical integer quotients, coordinate transitions, finite-target cofinal kernels and the actual profinite completion are checked. |
| 4.5 | Finite-target equivalence | COMPLETE | An equivalence between Hom(H_W,F) and Hom(D,F) for every finite additive-group target. Its forward map is the literal restriction, and naturality under target homomorphisms is proved. |
| 4.6 | Structure of an ambient preimage | PARTIAL | Torsion, quotient, reducedness via absence of divisible embeddings, residual finiteness, nonsplitting and Countable(H_W) iff Countable(W) are checked. The printed reformulation in terms of finite or countably infinite rational dimension is still pending. |
| 5.1 | Unique normal form | COMPLETE | Existence, uniqueness, the selector-independent Q x D domain and countable infinitude of every paired group are now checked. |
| 5.2 | A finite support bound | COMPLETE | The actual infinite-coordinate defect is supported on denominator primes. |
| 5.3 | Explicit group law | COMPLETE | Separate twisted group type, all additive group laws, and actual additive equivalence to the preimage. |
| 5.4 | One cocycle value reads one coordinate | PENDING | Not formalized in this tranche. |
| 5.5 | Finitely generated subgroups | PENDING | Not formalized in this tranche. |
| 6.1 | Root or obstruction | CORE_COMPLETE | Exact root equivalence and coordinate root/nonexistence certificates. The finite Python normal-form solver and its algorithmic cost are not verified extractions. |
| 6.2 | All roots and their number | PENDING | Coset enumeration and radical cardinality are not yet formalized. |
| 6.3 | All integer quotients | PARTIAL | Product of prime coordinates and transition maps proved. The explicit CRT equivalence with C_rad(m) remains. |
| 6.4 | Common profinite completion | COMPLETE | Every paired group has the actual canonical profinite completion P. Its induced product topology equals the full topology induced from the limit of all finite quotients. |
| 7.1 | Tail signature | PENDING | Not formalized in this tranche. |
| 7.2 | Unmarked isomorphism classification | PENDING | Not formalized in this tranche. |
| 7.3 | Marked classification | INPUTS_READY | Exact marked root tests are proved, but the marked-isomorphism iff selector-equality theorem itself remains. |
| 7.5 | Complete homomorphism description | PENDING | Not formalized in this tranche. |
| 7.6 | Torsion-image obstruction | PENDING | Not formalized in this tranche. |
| 7.7 | Endomorphism ring | PENDING | Not formalized in this tranche. |
| 7.8 | Automorphisms | PENDING | Not formalized in this tranche. |
| 7.9 | Seed-rank separation | PENDING | Not formalized in this tranche. |
| 8.1 | Uniform construction relative to the selector | PENDING | Not formalized in this tranche. |
| 8.2 | Uniform marked decoding | PENDING | Not formalized in this tranche. |
| 8.3 | Exact oracle criterion | PENDING | Not formalized in this tranche. |
| 8.4 | Degree variation with fixed observations | PENDING | Not formalized in this tranche. |
| 9.1 | No decoder from the unmarked finite-quotient system | PENDING | Not formalized in this tranche. |
| 9.2 | A proper map invisible after completion | COMPLETE | The literal inclusion D to G_a is not surjective. Its extension to their actual completions is a topological additive isomorphism, with equality on every canonical D point. |
| 9.3 | Faithfulness and failure of fullness | PENDING | Not formalized in this tranche. |
| 9.4 | Reflection within the paired-prime family | PENDING | Not formalized in this tranche. |
| 10.1 | Escape within one profinite-completion class | PENDING | Not formalized in this tranche. |
| 10.2 | Admissible expansion | PENDING | Not formalized in this tranche. |

The JSON companion contains the exact declaration names. Exported complete theorem types and axiom dependencies are in `verification/accepted_v0.2.0/declarations.json`. No global completion percentage is assigned.
