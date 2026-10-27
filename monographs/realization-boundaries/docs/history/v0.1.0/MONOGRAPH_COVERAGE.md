# Monograph-to-Lean coverage

This table tracks every one of the book’s 45 numbered results. A formalized input is not counted as a proof of the theorem that eventually uses it. Counts of helper declarations do not measure book completion.

`COMPLETE` means the stated mathematical content is covered. `COMPLETE_ALGEBRAIC` records an equivalent algebraic formulation. `CORE_COMPLETE`, `PARTIAL`, and `INPUTS_READY` retain the explicit outstanding clauses.

| Book result | Status | Exact scope |
|---|---|---|
| 1.5 · Countable-code bound | PENDING | Not formalized in this tranche. |
| 1.8 · Reachability obstruction | PENDING | Not formalized in this tranche. |
| 2.1 · The torsion subgroup of the product | PARTIAL | Torsion equals finite support. Density and the topological clause are not formalized. |
| 2.2 · Diagonal endomorphisms of the direct sum | PENDING | Not formalized in this tranche. |
| 2.3 · An infinite seed obstruction | PENDING | Not formalized in this tranche. |
| 2.4 · Topological cyclicity | PENDING | Not formalized in this tranche. |
| 2.5 · Profinite completion of the direct sum | PENDING | Not formalized in this tranche. |
| 2.6 · Unique division in the ambient quotient | COMPLETE_ALGEBRAIC | Actual quotient and derived rational module; no nonzero divisible embedding in P. |
| 3.1 · Subgroup and isomorphism classification | PENDING | Not formalized in this tranche. |
| 3.2 · Finite observations leave continuum many possibilities | PENDING | Not formalized in this tranche. |
| 3.3 · The prime-spectrum criterion | PENDING | Not formalized in this tranche. |
| 3.4 · thm:noncompD | PENDING | Not formalized in this tranche. |
| 3.5 · Unary selector classification | PENDING | Not formalized in this tranche. |
| 4.2 · Pure-preimage correspondence | PARTIAL | Rational preimages are pure. Converse and order-preserving bijection remain. |
| 4.3 · Ambient root criterion | COMPLETE | Both directions for every positive multiplier and every actual preimage. |
| 4.4 · One finite-quotient system for every preimage | PARTIAL | Canonical algebraic quotients, transitions and finite-target kernel containment. Full inverse limit/profinite topology remains. |
| 4.5 · Finite-target equivalence | INPUTS_READY | Restriction/extension natural bijection itself is not yet formalized. |
| 4.6 · Structure of an ambient preimage | PARTIAL | Torsion, rational quotient, finite-coordinate separation and nonsplitting. Countability and the dimension classification remain. |
| 5.1 · Unique normal form | PARTIAL | Existence, uniqueness and actual additive realization. Countability of D and the resulting cardinality clause are not yet formalized. |
| 5.2 · A finite support bound | COMPLETE | The actual infinite-coordinate defect is supported on denominator primes. |
| 5.3 · Explicit group law | COMPLETE | Separate twisted group type, all additive group laws, and actual additive equivalence to the preimage. |
| 5.4 · One cocycle value reads one coordinate | PENDING | Not formalized in this tranche. |
| 5.5 · Finitely generated subgroups | PENDING | Not formalized in this tranche. |
| 6.1 · Root or obstruction | CORE_COMPLETE | Exact root equivalence and coordinate root/nonexistence certificates. The finite Python normal-form solver and its algorithmic cost are not verified extractions. |
| 6.2 · All roots and their number | PENDING | Coset enumeration and radical cardinality are not yet formalized. |
| 6.3 · All integer quotients | PARTIAL | Product of prime coordinates and transition maps proved. The explicit CRT equivalence with C_rad(m) remains. |
| 6.4 · Common profinite completion | INPUTS_READY | Full profinite completion has not been defined or proved in Lean in this tranche. |
| 7.1 · Tail signature | PENDING | Not formalized in this tranche. |
| 7.2 · Unmarked isomorphism classification | PENDING | Not formalized in this tranche. |
| 7.3 · Marked classification | INPUTS_READY | Exact marked root tests are proved, but the marked-isomorphism iff selector-equality theorem itself remains. |
| 7.5 · Complete homomorphism description | PENDING | Not formalized in this tranche. |
| 7.6 · Torsion-image obstruction | PENDING | Not formalized in this tranche. |
| 7.7 · Endomorphism ring | PENDING | Not formalized in this tranche. |
| 7.8 · Automorphisms | PENDING | Not formalized in this tranche. |
| 7.9 · Seed-rank separation | PENDING | Not formalized in this tranche. |
| 8.1 · Uniform construction relative to the selector | PENDING | Not formalized in this tranche. |
| 8.2 · Uniform marked decoding | PENDING | Not formalized in this tranche. |
| 8.3 · Exact oracle criterion | PENDING | Not formalized in this tranche. |
| 8.4 · Degree variation with fixed observations | PENDING | Not formalized in this tranche. |
| 9.1 · No decoder from the unmarked finite-quotient system | PENDING | Not formalized in this tranche. |
| 9.2 · A proper map invisible after completion | PENDING | Not formalized in this tranche. |
| 9.3 · Faithfulness and failure of fullness | PENDING | Not formalized in this tranche. |
| 9.4 · Reflection within the paired-prime family | PENDING | Not formalized in this tranche. |
| 10.1 · Escape within one profinite-completion class | PENDING | Not formalized in this tranche. |
| 10.2 · Admissible expansion | PENDING | Not formalized in this tranche. |

## Additional checked interfaces

`pairedSelector_infinite` proves the required infinite support for every binary selector. `quotientMap_rationalSection` proves that the concrete reduced-rational section lies over the intended rational multiple in the actual quotient. `cocycle_not_removable` proves that no D-valued correction can make the section additive. `NormalForm.realizationEquiv_coe` identifies the additive equivalence with the printed ambient realization formula.

The file `NAMED_THEOREMS.json` lists all explicit production theorem declarations with source lines, their actual elaborated types, and their audited axiom dependencies. The full declaration export, including generated helpers and instances, is in the accepted verification record.
