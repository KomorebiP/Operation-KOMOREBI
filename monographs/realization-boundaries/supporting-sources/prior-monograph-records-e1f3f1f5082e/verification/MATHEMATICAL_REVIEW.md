# Mathematical review record

This is an internal review of the ordinary arguments prepared with the monograph. It is not independent external review and is not a Lean certificate.

## Claims and contracts checked

The main statement inventory is `theorem_inventory.csv` (also JSON). It records 44 theorem, proposition, lemma, and corollary environments with their source locations and printed page references. These are not 44 claims of historical novelty.

The ambient arguments distinguish the finite direct products, their zero-extension direct limit, and their projection inverse limit. The proof that P/D is a rational vector space checks both surjectivity and injectivity of multiplication by every positive integer. The absence of divisible subgroups in P is proved separately from divisibility of its quotient.

The pure-preimage correspondence is proved in both directions. Its converse subtracts the coordinates at the prime divisors of the multiplier before invoking purity. The common-completion result proves cofinality among all finite quotients, not merely agreement with a chosen inverse system. Maps to possibly nonabelian finite targets are handled without subtracting homomorphisms.

The section is not assumed additive. Its finite-support defect is established before the cocycle is used as a direct-sum element. Normal-form uniqueness is obtained in the rational quotient. Positive root certificates include finite torsion correction. The root kernel and its exact squarefree cardinality are derived from the ambient coordinate product.

The unmarked classification is eventual selector equality, not literal equality. The marked classification uses exact root tests. Every abstract homomorphism is shown to be diagonal using the canonical quotients G_A/pG_A; diagonal form is not imposed as an extra hypothesis. The endomorphism quotient scalar is shown to be unique, and the inverse-diagonal condition establishes the automorphism claim.

The effective criterion separates uniform marked decoding from nonuniform unmarked decoding with finite constants. The canonical-copy operation computes the selector through a concrete cocycle entry. A copy computable in X is not silently identified with a copy of exact degree X. The least presentation degree conclusion follows from the two directions actually proved.

The no-decoder theorem concerns the unmarked finite-quotient pro-object, not all mathematical observations. Residual finiteness separates elements after the domain is fixed. The admissible dense image is additional information. Completion faithfulness on maps is explicitly distinguished from fullness and reflection of isomorphisms.

The grammar escape construction uses infinitely repeated disagreements because a finite selector change leaves the unmarked group unchanged. The semantic enumeration is not claimed computable. An arbitrary selector is not treated as a free finite parameter.

## Computational evidence

The inherited core suite and the supplemental suite passed 168,022 exact finite assertions in the current preparation. Seven negative controls reject intentionally false simplifications. The code example printed in Chapter 11 was extracted from the LaTeX source and executed successfully from the package root. The earlier direct-sum checks were replayed separately.

The tests do not prove the infinite classification, arbitrary-oracle statements, or diagonal nonrealizability. They check the implemented exact arithmetic and finite examples described in the book. No noncomputable oracle was evaluated.

## Production failures and corrections

The initial figure build encountered a MathText parsing error caused by unbraced blackboard-bold commands. The labels were corrected and all eight figures regenerated.

The initial TeX build failed because loading newpxmath before amsthm redefined `openbox`. Loading the theorem and AMS packages before the math-font package resolved the conflict. Further layout adjustments removed a single-entry contents spillover, prevented hyphenation in chapter titles, moved the root-certificate diagram into the chapter opening, and removed the glossary label-width warning. The printed example's import was made valid from the package root and replayed.

The final PDF has 64 pages. All pages were rendered, screened in contact sheets, and checked for text boxes extending outside the page. Representative theorem, figure, table, contents, cover, and glossary pages were inspected at larger scale. The final TeX log has no unresolved-reference warnings, missing-character messages, or overfull boxes. These production checks are distinct from mathematical proof review.

## Open evidence tasks

No Lean environment was available and no Lean compilation was performed. A formalization plan is supplied, not verified Lean sources. No independent external referee report or exhaustive literature-priority audit is claimed. The book explicitly attributes the classical prime-spectrum coding and supplies complete ordinary proofs for the common-completion development.
