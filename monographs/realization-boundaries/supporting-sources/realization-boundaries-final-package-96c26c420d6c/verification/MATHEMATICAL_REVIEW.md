# Ordinary proof review

This record concerns the final edition. It supersedes the predecessor's review preserved in `provenance/Prior_Monograph_Records.zip`. It is not an independent referee report or a Lean certificate.

## Reviewed proof chain

- The direct-sum and product arguments use distinct prime annihilators. The proof of a rational structure on P/D verifies both existence and uniqueness of integer division. Divisibility of the quotient is kept separate from the absence of nonzero divisible subgroups in P.
- The subgroup classification isolates a coordinate by the Chinese remainder theorem. The prime-spectrum computability criterion permits a nonuniform finite case. Complementary halting-set coding supplies an explicit finitely defined group without a computable copy.
- The pure-preimage correspondence is proved in both directions. Its converse removes finitely many divisor-prime coordinates before applying purity. Cofinality is proved among every finite quotient, not only a selected family. Restriction to D identifies homomorphisms to finite targets even when those targets are nonabelian.
- The rational section is not assumed additive. Its defect is proved finitely supported before becoming a cocycle in D. Normal-form uniqueness takes place in the rational quotient. Nonsplitting follows from reducedness of P, not from a claim that the quotient is not divisible.
- The integer-root construction retains its finite torsion correction. The kernel and root-fiber counts are squarefree, including m=1. Prime powers do not produce larger finite quotient factors.
- Unmarked isomorphism means equality modulo finite changes; marked isomorphism means literal selector equality. Every abstract homomorphism is proved diagonal using the prime quotients. The rational scalar in the endomorphism ring is unique; all nonzero diagonal coordinates give the automorphism inverse.
- Effective realization is an oracle existence theorem. Marked decoding is uniform. Unmarked decoding uses the name of an infinite-order element and finitely many exception data. A copy computable in X is not asserted to have exact degree X.
- Reconstruction failure uses the unmarked finite-quotient system, not every possible observation. Faithfulness, fullness, and reflection of isomorphisms are now separated with the exact source category. The erroneous predecessor scope was repaired, and Proposition 9.4 proves reflection on the paired-prime subcategory.
- Grammar escape repeats each disagreement infinitely often to survive eventual equality. The semantic enumeration is not claimed computable. An arbitrary selector is not a free finite parameter. Bit-length complexity uses a fixed binary encoding.

The 45 theorem-like statements and their source/page locations are in `theorem_inventory.csv` and `theorem_inventory.json`. The addition relative to the predecessor is Proposition 9.4, not a claim of 45 historically new results.

## Status

The central common-completion, classification, and oracle conclusions were retained. The categorical overstatement and several semantic/hypothesis ambiguities were corrected. Three fresh exact-arithmetic suites passed 189,069 finite assertions; their scope does not include universal infinite proofs. No Lean verification, external referee report, or exhaustive novelty audit is claimed. See `FINALIZATION_REPORT.md` for implementation defects, repairs, and recovered production failures.
