# Proof and Dependency Audit

## Structural result

The final manuscript contains 43 theorems, propositions, lemmas, and corollaries. It contains 43 proof environments. Every proved result is followed by a proof.

## Reference integrity

* Declared labels: 76
* Duplicate labels: 0
* Internal references not found: 0
* Bibliography entries: 8
* Citation keys used: 8
* Missing bibliography entries: 0
* Uncited bibliography entries: 0

## Main proof chains checked

1. Refinement starts with the child sum identity, then proves coherent coordinate changes, refined operator blocks, and common refinements.
2. Filtered inversion starts from a complete multiplicative filtration, expands the Neumann inverse into ordered words, then restricts the words to directed packet paths.
3. Integral separation first gives Bézout and resultant bounds. It then identifies the exact denominator through the lattice gluing module and its Smith exponents.
4. The refinement exact sequence compares coarse and fine gluing modules and gives monotonicity of separation weight.
5. The precision theorem proves both sufficiency and necessity of the extra lattice digits.
6. The Smith theorem reduces the congruence to independent scalar equations and counts every kernel and free variable.
7. The defect section begins with a telescoping formula for powers and derives the polynomial, resolvent, holomorphic, exponential, and multilevel formulas.

## Computational checks

The original release suite passes all 21 tests. The revised verification script passes all 10 groups. These checks cover exact refinement, common refinement, residue and CRT identities, weighted inverse expansions, path series, gluing weights, precision delay, Smith solution counts, defect identities, and source integrity.

## Boundary

This audit checks internal proof structure, references, compilation, and finite examples. It is not independent specialist review and does not establish historical priority.
