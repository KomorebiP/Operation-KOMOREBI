# From examples to papers, proofs, Lean and code

Choose a topic to move from a hand calculation to definitions and related source material. Each linked work has return links to these examples. These are subject routes, not new theorem-to-Lean correspondences.

[All hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Browse works](BROWSE.md)

## Start from a core paper

Choose the paper you are reading. The examples introduce selected ideas. They do not cover every result or establish new Lean correspondences.

- [Paper I](works/paper-i.md#worked-examples-for-this-work): [1. Split and reconstruct a vector](examples/01_PACKETS.md) · [2. Generate a space from one seed](examples/02_SEEDS.md) · [3. Change coordinates](examples/03_COORDINATES.md) · [6. Use redundant coordinates](examples/06_REDUNDANT_COORDINATES.md) · [10. Find a kernel and its fibers](examples/10_KERNELS.md) · [11. Build spectral projectors](examples/11_SPECTRAL_PROJECTORS.md) · [15. Compose typed operations](examples/15_TYPED_PATHS.md)
- [Paper II](works/paper-ii.md#worked-examples-for-this-work): [4. Assemble transfer blocks](examples/04_TRANSFER.md) · [5. Refine a signal](examples/05_REFINEMENT.md) · [11. Build spectral projectors](examples/11_SPECTRAL_PROJECTORS.md)
- [Paper III](works/paper-iii.md#worked-examples-for-this-work): [7. Detect lost information](examples/07_OBSTRUCTIONS.md) · [15. Compose typed operations](examples/15_TYPED_PATHS.md)
- [Paper IV](works/paper-iv.md#worked-examples-for-this-work): [16. Split reciprocal coefficients into cyclic packets](examples/16_CYCLIC_RECIPROCALS.md)
- [Paper V](works/paper-v.md#worked-examples-for-this-work): [5. Refine a signal](examples/05_REFINEMENT.md) · [14. Separate averages and details](examples/14_HAAR_PAIRS.md)
- [Paper VI](works/paper-vi.md#worked-examples-for-this-work): [8. Average with unequal weights](examples/08_WEIGHTED_AVERAGES.md) · [12. Eliminate a block of unknowns](examples/12_BLOCK_ELIMINATION.md)
- [Paper VII](works/paper-vii.md#worked-examples-for-this-work): [17. Calculate quantum measurement and dephasing](examples/17_QUANTUM_MEASUREMENT.md)
- [Paper VIII](works/paper-viii.md#worked-examples-for-this-work): [4. Assemble transfer blocks](examples/04_TRANSFER.md)
- [Paper IX](works/paper-ix.md#worked-examples-for-this-work): [9. Round a binary number](examples/09_BINARY_ROUNDING.md) · [13. Reconstruct from residues](examples/13_MODULAR_RECONSTRUCTION.md)
- [Paper X](works/paper-x.md#worked-examples-for-this-work): [18. Follow a modular lift branch](examples/18_LIFT_BRANCHES.md)
- [Paper XI](works/paper-xi.md#worked-examples-for-this-work): [19. Compute Frobenius in a quadratic finite field](examples/19_FINITE_FROBENIUS.md)
- [Paper XII](works/paper-xii.md#worked-examples-for-this-work): [20. Separate support from multiplicity](examples/20_SUPPORT_AND_MULTIPLICITY.md)

## Topics

- [1. Split and reconstruct a vector](#packets)
- [2. Generate a space from one seed](#seeds)
- [3. Change coordinates](#coordinates)
- [4. Assemble transfer blocks](#transfer)
- [5. Refine a signal](#refinement)
- [6. Use redundant coordinates](#redundancy)
- [7. Detect lost information](#obstructions)
- [8. Average with unequal weights](#averages)
- [9. Round a binary number](#rounding)
- [10. Find a kernel and its fibers](#kernels)
- [11. Build spectral projectors](#spectral)
- [12. Eliminate a block of unknowns](#elimination)
- [13. Reconstruct from residues](#modular)
- [14. Separate averages and details](#haar)
- [15. Compose typed operations](#typed-paths)
- [16. Split reciprocal coefficients into cyclic packets](#cyclic-reciprocals)
- [17. Calculate quantum measurement and dephasing](#quantum-measurement)
- [18. Follow a modular lift branch](#lift-branches)
- [19. Compute Frobenius in a quadratic finite field](#finite-frobenius)
- [20. Separate support from multiplicity](#support-multiplicity)

<a id="packets"></a>

## 1. Split and reconstruct a vector

[Work through the example](examples/01_PACKETS.md)

**Terms:** [Projector](GLOSSARY.md#projector) · [Packet](GLOSSARY.md#packet) · [Complete packet family](GLOSSARY.md#complete-packet-family) · [Orthogonal projector](GLOSSARY.md#orthogonal-projector) · [Direct sum](GLOSSARY.md#direct-sum)

Exact packet coordinates provide the source setting for the elementary decomposition.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: packets()](../tools/check_hand_examples.py#L56). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="seeds"></a>

## 2. Generate a space from one seed

[Work through the example](examples/02_SEEDS.md)

**Terms:** [Seed](GLOSSARY.md#seed) · [Seed rank](GLOSSARY.md#seed-rank) · [Cyclic vector](GLOSSARY.md#cyclic) · [Span](GLOSSARY.md#span) · [Operator algebra](GLOSSARY.md#operator-algebra)

Paper I develops seed generation with its stated algebra and module hypotheses.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: seeds()](../tools/check_hand_examples.py#L72). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="coordinates"></a>

## 3. Change coordinates

[Work through the example](examples/03_COORDINATES.md)

**Terms:** [Coordinates](GLOSSARY.md#coordinates) · [Coordinate change](GLOSSARY.md#coordinate-change) · [Inverse](GLOSSARY.md#inverse) · [Operator conjugation](GLOSSARY.md#conjugation) · [Linear isomorphism](GLOSSARY.md#isomorphism)

Use Paper I for exact packet coordinates and the library atlas for general coordinate changes.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: coordinates()](../tools/check_hand_examples.py#L84). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="transfer"></a>

## 4. Assemble transfer blocks

[Work through the example](examples/04_TRANSFER.md)

**Terms:** [Transfer block](GLOSSARY.md#transfer-block) · [Composition](GLOSSARY.md#composition) · [Block matrix](GLOSSARY.md#block-matrix)

Paper II supplies transfer background. Paper VIII develops operator algorithms and compilation.

### Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

[Read](works/paper-ii.md#read) · [Written proofs](works/paper-ii.md#written-proofs) · [Lean coverage](works/paper-ii.md#lean) · [Code and setup](works/paper-ii.md#code) · [Evidence](works/paper-ii.md#evidence)

### Paper VIII: Packet Operator Algorithms, Exact Compilation, and GPU Realization

[Read](works/paper-viii.md#read) · [Written proofs](works/paper-viii.md#written-proofs) · [Lean coverage](works/paper-viii.md#lean) · [Code and setup](works/paper-viii.md#code) · [Evidence](works/paper-viii.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#transfer-blocks). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: transfer()](../tools/check_hand_examples.py#L98). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="refinement"></a>

## 5. Refine a signal

[Work through the example](examples/05_REFINEMENT.md)

**Terms:** [Refinement](GLOSSARY.md#refinement) · [Coarsening](GLOSSARY.md#coarsening) · [Polyphase decomposition](GLOSSARY.md#polyphase) · [Residue class](GLOSSARY.md#residue-class) · [Compatibility](GLOSSARY.md#compatibility)

Read Paper II for refinement and Paper V for signal and polyphase constructions.

### Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

[Read](works/paper-ii.md#read) · [Written proofs](works/paper-ii.md#written-proofs) · [Lean coverage](works/paper-ii.md#lean) · [Code and setup](works/paper-ii.md#code) · [Evidence](works/paper-ii.md#evidence)

### Paper V: Polyphase Signal Calculus

[Read](works/paper-v.md#read) · [Written proofs](works/paper-v.md#written-proofs) · [Lean coverage](works/paper-v.md#lean) · [Code and setup](works/paper-v.md#code) · [Evidence](works/paper-v.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: refinement()](../tools/check_hand_examples.py#L118). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="redundancy"></a>

## 6. Use redundant coordinates

[Work through the example](examples/06_REDUNDANT_COORDINATES.md)

**Terms:** [Analysis and synthesis](GLOSSARY.md#analysis-synthesis) · [Left inverse](GLOSSARY.md#left-inverse) · [Redundant coordinates](GLOSSARY.md#redundancy) · [Reconstruction](GLOSSARY.md#reconstruction)

Compare the exact packet setting of Paper I with the broader analysis and synthesis construction in the library guide.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: redundant_coordinates()](../tools/check_hand_examples.py#L135). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="obstructions"></a>

## 7. Detect lost information

[Work through the example](examples/07_OBSTRUCTIONS.md)

**Terms:** [Obstruction](GLOSSARY.md#obstruction) · [Fiber](GLOSSARY.md#fiber) · [Factorization through a map](GLOSSARY.md#factorization) · [Kernel](GLOSSARY.md#kernel) · [Quotient space](GLOSSARY.md#quotient-space)

The finite recovery obstruction is an entry point to the works on compatibility and realization boundaries.

### Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory

[Read](works/paper-iii.md#read) · [Written proofs](works/paper-iii.md#written-proofs) · [Lean coverage](works/paper-iii.md#lean) · [Code and setup](works/paper-iii.md#code) · [Evidence](works/paper-iii.md#evidence)

### Realization Boundaries

[Read](works/realization-boundaries.md#read) · [Written proofs](works/realization-boundaries.md#written-proofs) · [Lean coverage](works/realization-boundaries.md#lean) · [Code and setup](works/realization-boundaries.md#code) · [Evidence](works/realization-boundaries.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: obstructions()](../tools/check_hand_examples.py#L155). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="averages"></a>

## 8. Average with unequal weights

[Work through the example](examples/08_WEIGHTED_AVERAGES.md)

**Terms:** [Finite conditional expectation](GLOSSARY.md#conditional-expectation) · [Inner product](GLOSSARY.md#inner-product) · [Orthogonal projector](GLOSSARY.md#orthogonal-projector) · [Residual](GLOSSARY.md#residual)

Paper VI includes stochastic and Bayesian realizations. Its assumptions extend beyond this finite partition.

### Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations

[Read](works/paper-vi.md#read) · [Written proofs](works/paper-vi.md#written-proofs) · [Lean coverage](works/paper-vi.md#lean) · [Code and setup](works/paper-vi.md#code) · [Evidence](works/paper-vi.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#dynamics-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: weighted_averages()](../tools/check_hand_examples.py#L165). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="rounding"></a>

## 9. Round a binary number

[Work through the example](examples/09_BINARY_ROUNDING.md)

**Terms:** [Precision](GLOSSARY.md#precision) · [Dyadic rational](GLOSSARY.md#dyadic-rational) · [Rounding](GLOSSARY.md#rounding) · [ULP](GLOSSARY.md#ulp) · [Numerical ternary](GLOSSARY.md#ternary) · [Exact](GLOSSARY.md#exact) · [Numerical](GLOSSARY.md#numerical)

Paper IX supplies dyadic arithmetic background. The rounding implementation and its contracts belong to Polyphase Float.

### Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation

[Read](works/paper-ix.md#read) · [Written proofs](works/paper-ix.md#written-proofs) · [Lean coverage](works/paper-ix.md#lean) · [Code and setup](works/paper-ix.md#code) · [Evidence](works/paper-ix.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/chapters/06_arithmetic_ranges.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: binary_rounding()](../tools/check_hand_examples.py#L182). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="kernels"></a>

## 10. Find a kernel and its fibers

[Work through the example](examples/10_KERNELS.md)

**Terms:** [Kernel](GLOSSARY.md#kernel) · [Image](GLOSSARY.md#image) · [Rank](GLOSSARY.md#rank) · [Nullity](GLOSSARY.md#nullity) · [Rank–nullity identity](GLOSSARY.md#rank-nullity) · [Injective map](GLOSSARY.md#injective) · [Surjective map](GLOSSARY.md#surjective) · [Quotient space](GLOSSARY.md#quotient-space) · [Subspace](GLOSSARY.md#subspace)

These finite linear calculations give background for typed realizations and information loss. Read each work for its own claims.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)

### Information Realization

[Read](works/information-realization.md#read) · [Written proofs](works/information-realization.md#written-proofs) · [Lean coverage](works/information-realization.md#lean) · [Code and setup](works/information-realization.md#code) · [Evidence](works/information-realization.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: kernels()](../tools/check_hand_examples.py#L201). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="spectral"></a>

## 11. Build spectral projectors

[Work through the example](examples/11_SPECTRAL_PROJECTORS.md)

**Terms:** [Eigenvector](GLOSSARY.md#eigenvector) · [Eigenvalue](GLOSSARY.md#eigenvalue) · [Eigenspace](GLOSSARY.md#eigenspace) · [Diagonalizable operator](GLOSSARY.md#diagonalizable) · [Polynomial in an operator](GLOSSARY.md#polynomial-in-operator) · [Minimal polynomial](GLOSSARY.md#minimal-polynomial) · [Spectral projector](GLOSSARY.md#spectral-projector)

The example uses a diagonalizable two-dimensional matrix. The works develop wider packet and spectral constructions with additional hypotheses.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)

### Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

[Read](works/paper-ii.md#read) · [Written proofs](works/paper-ii.md#written-proofs) · [Lean coverage](works/paper-ii.md#lean) · [Code and setup](works/paper-ii.md#code) · [Evidence](works/paper-ii.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#spectral-and-packet-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: spectral_projectors()](../tools/check_hand_examples.py#L212). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="elimination"></a>

## 12. Eliminate a block of unknowns

[Work through the example](examples/12_BLOCK_ELIMINATION.md)

**Terms:** [Block matrix](GLOSSARY.md#block-matrix) · [Schur complement](GLOSSARY.md#schur-complement) · [Elimination](GLOSSARY.md#elimination) · [Determinant](GLOSSARY.md#determinant) · [Inverse](GLOSSARY.md#inverse)

Paper VI gives elimination background. The collected Gaussian elimination guide retains its pending source qualification and unassessed confidence.

### Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations

[Read](works/paper-vi.md#read) · [Written proofs](works/paper-vi.md#written-proofs) · [Lean coverage](works/paper-vi.md#lean) · [Code and setup](works/paper-vi.md#code) · [Evidence](works/paper-vi.md#evidence)

### Gaussian Elimination: collected guide

[Read](works/gaussian-elimination-guide.md#read) · [Written proofs](works/gaussian-elimination-guide.md#written-proofs) · [Lean coverage](works/gaussian-elimination-guide.md#lean) · [Code and setup](works/gaussian-elimination-guide.md#code) · [Evidence](works/gaussian-elimination-guide.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#dynamics-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: block_elimination()](../tools/check_hand_examples.py#L225). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="modular"></a>

## 13. Reconstruct from residues

[Work through the example](examples/13_MODULAR_RECONSTRUCTION.md)

**Terms:** [Integer congruence](GLOSSARY.md#congruence) · [Coprime integers](GLOSSARY.md#coprime) · [Modular inverse](GLOSSARY.md#modular-inverse) · [Chinese remainder theorem](GLOSSARY.md#chinese-remainder) · [Residue class](GLOSSARY.md#residue-class)

The example is ordinary integer CRT. Paper IX develops arithmetic packets and local deformation beyond this calculation.

### Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation

[Read](works/paper-ix.md#read) · [Written proofs](works/paper-ix.md#written-proofs) · [Lean coverage](works/paper-ix.md#lean) · [Code and setup](works/paper-ix.md#code) · [Evidence](works/paper-ix.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#spectral-and-packet-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: modular_reconstruction()](../tools/check_hand_examples.py#L237). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="haar"></a>

## 14. Separate averages and details

[Work through the example](examples/14_HAAR_PAIRS.md)

**Terms:** [Haar pair](GLOSSARY.md#haar-pair) · [Detail coefficient](GLOSSARY.md#detail-coefficient) · [Normalization](GLOSSARY.md#normalization) · [Orthogonal matrix](GLOSSARY.md#orthogonal-matrix) · [Refinement](GLOSSARY.md#refinement)

Paper V supplies signal background. Information Realization includes a finite Haar contract within its recorded formal core.

### Paper V: Polyphase Signal Calculus

[Read](works/paper-v.md#read) · [Written proofs](works/paper-v.md#written-proofs) · [Lean coverage](works/paper-v.md#lean) · [Code and setup](works/paper-v.md#code) · [Evidence](works/paper-v.md#evidence)

### Information Realization

[Read](works/information-realization.md#read) · [Written proofs](works/information-realization.md#written-proofs) · [Lean coverage](works/information-realization.md#lean) · [Code and setup](works/information-realization.md#code) · [Evidence](works/information-realization.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: haar_pairs()](../tools/check_hand_examples.py#L247). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="typed-paths"></a>

## 15. Compose typed operations

[Work through the example](examples/15_TYPED_PATHS.md)

**Terms:** [Typed system](GLOSSARY.md#typed-system) · [Typed path](GLOSSARY.md#typed-path) · [Operator relation](GLOSSARY.md#relation) · [Domain and codomain](GLOSSARY.md#domain-codomain) · [Intertwiner](GLOSSARY.md#intertwiner) · [Commutator](GLOSSARY.md#commutator)

Paper I develops typed systems and their realizations. Paper III continues with typed transfer and obstructions.

### Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

[Read](works/paper-i.md#read) · [Written proofs](works/paper-i.md#written-proofs) · [Lean coverage](works/paper-i.md#lean) · [Code and setup](works/paper-i.md#code) · [Evidence](works/paper-i.md#evidence)

### Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory

[Read](works/paper-iii.md#read) · [Written proofs](works/paper-iii.md#written-proofs) · [Lean coverage](works/paper-iii.md#lean) · [Code and setup](works/paper-iii.md#code) · [Evidence](works/paper-iii.md#evidence)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: typed_paths()](../tools/check_hand_examples.py#L263). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="cyclic-reciprocals"></a>

## 16. Split reciprocal coefficients into cyclic packets

[Work through the example](examples/16_CYCLIC_RECIPROCALS.md)

**Terms:** [Coefficient](GLOSSARY.md#coefficient) · [Power series](GLOSSARY.md#power-series) · [Truncation](GLOSSARY.md#truncation) · [Formal reciprocal](GLOSSARY.md#formal-reciprocal) · [Coefficient convolution](GLOSSARY.md#convolution) · [Root of unity](GLOSSARY.md#root-of-unity)

This coefficient model introduces cyclic projection and reciprocal recursion in Paper IV. Its finite product check does not address the paper’s analytic growth or spectral-zero results.

### Paper IV: Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data

[Read](works/paper-iv.md#read) · [Written proofs](works/paper-iv.md#written-proofs) · [Lean coverage](works/paper-iv.md#lean) · [Code and setup](works/paper-iv.md#code) · [Evidence](works/paper-iv.md#evidence)

**Source passages:**

- [Paper IV: cyclic projection](../papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex#L325)
- [Paper IV: reciprocal powers](../papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex#L918)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#cyclic-coefficient-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: cyclic_reciprocals()](../tools/check_hand_examples.py#L276). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="quantum-measurement"></a>

## 17. Calculate quantum measurement and dephasing

[Work through the example](examples/17_QUANTUM_MEASUREMENT.md)

**Terms:** [Complex conjugate](GLOSSARY.md#complex-conjugate) · [Adjoint matrix](GLOSSARY.md#adjoint) · [Unitary matrix](GLOSSARY.md#unitary) · [Quantum amplitude](GLOSSARY.md#amplitude) · [Density matrix](GLOSSARY.md#density-matrix) · [Matrix trace](GLOSSARY.md#trace) · [Born probability](GLOSSARY.md#born-probability) · [Purity of a density matrix](GLOSSARY.md#purity) · [Dephasing](GLOSSARY.md#dephasing) · [Kraus operators](GLOSSARY.md#kraus-operator) · [Hermitian matrix](GLOSSARY.md#hermitian) · [Positive semidefinite matrix](GLOSSARY.md#positive-semidefinite) · [Coherence in a chosen basis](GLOSSARY.md#coherence)

Paper VII develops finite quantum constructions and separate continuum research targets. This example covers one two-dimensional state, a unitary phase change and a measurement channel.

### Paper VII: Quantum Seed Calculus

[Read](works/paper-vii.md#read) · [Written proofs](works/paper-vii.md#written-proofs) · [Lean coverage](works/paper-vii.md#lean) · [Code and setup](works/paper-vii.md#code) · [Evidence](works/paper-vii.md#evidence)

**Source passages:**

- [Paper VII: measurements and channels](../papers/paper-vii/current/editable/traditional/parts/01_finite_core.tex#L670)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#quantum-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: quantum_measurement()](../tools/check_hand_examples.py#L305). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="lift-branches"></a>

## 18. Follow a modular lift branch

[Work through the example](examples/18_LIFT_BRANCHES.md)

**Terms:** [Prime power](GLOSSARY.md#prime-power) · [Modular reduction](GLOSSARY.md#modular-reduction) · [Lift branch](GLOSSARY.md#lift-branch) · [Compatible tower](GLOSSARY.md#compatible-tower) · [p-adic integer](GLOSSARY.md#padic-integer) · [Survival to a finite level](GLOSSARY.md#surviving-branch)

Finite lift branches give elementary background for Paper X’s residual constructions. Its completion result requires supplied all-depth data, closure and the other stated inputs.

### Paper X: Universal Residual Seeds and Conditional Occupied-System Completion

[Read](works/paper-x.md#read) · [Written proofs](works/paper-x.md#written-proofs) · [Lean coverage](works/paper-x.md#lean) · [Code and setup](works/paper-x.md#code) · [Evidence](works/paper-x.md#evidence)

**Source passages:**

- [Paper X: conditional completion inputs](../papers/paper-x/current/manuscript/conditional_completion.tex#L8)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#komorebi_mathdeformation). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: lift_branches()](../tools/check_hand_examples.py#L340). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="finite-frobenius"></a>

## 19. Compute Frobenius in a quadratic finite field

[Work through the example](examples/19_FINITE_FROBENIUS.md)

**Terms:** [Prime field](GLOSSARY.md#prime-field) · [Extension field](GLOSSARY.md#extension-field) · [Finite-field Frobenius](GLOSSARY.md#frobenius) · [Field trace](GLOSSARY.md#field-trace) · [Field norm](GLOSSARY.md#field-norm) · [Irreducible polynomial](GLOSSARY.md#irreducible-polynomial)

This is finite-field background for Paper XI’s finite packet theory. Conjecture 66 separately asks for an actual arithmetic realizer with its declared comparison data.

### Paper XI: Packets, Arithmetic Realization, and Conditional Comparison

[Read](works/paper-xi.md#read) · [Written proofs](works/paper-xi.md#written-proofs) · [Lean coverage](works/paper-xi.md#lean) · [Code and setup](works/paper-xi.md#code) · [Evidence](works/paper-xi.md#evidence)

**Source passages:**

- [Paper XI: finite theory and the comparison boundary](../papers/paper-xi/current/publication/source/traditional/reader_route.tex#L17)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/PUBLIC_API.md#komorebi_mathlanglandslocal). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: finite_frobenius()](../tools/check_hand_examples.py#L353). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="support-multiplicity"></a>

## 20. Separate support from multiplicity

[Work through the example](examples/20_SUPPORT_AND_MULTIPLICITY.md)

**Terms:** [Commutative ring with identity](GLOSSARY.md#ring) · [Module](GLOSSARY.md#module) · [Module presentation](GLOSSARY.md#module-presentation) · [Cokernel](GLOSSARY.md#cokernel) · [Nilpotent operator](GLOSSARY.md#nilpotent) · [Module annihilator](GLOSSARY.md#annihilator) · [Module support](GLOSSARY.md#module-support) · [Zeroth Fitting ideal](GLOSSARY.md#fitting-ideal) · [Multiplicity in the module example](GLOSSARY.md#multiplicity) · [Ideal](GLOSSARY.md#ideal) · [Prime ideal](GLOSSARY.md#prime-ideal) · [Localization at a prime](GLOSSARY.md#localization)

Paper XII distinguishes module support from packet and arithmetic constructions. This example compares two explicitly supplied modules. Patching, classicality and the other arithmetic inputs remain separate.

### Paper XII: Patching Support, Hecke Packets, and Conditional Automorphic Completion

[Read](works/paper-xii.md#read) · [Written proofs](works/paper-xii.md#written-proofs) · [Lean coverage](works/paper-xii.md#lean) · [Code and setup](works/paper-xii.md#code) · [Evidence](works/paper-xii.md#evidence)

**Source passages:**

- [Paper XII: support and evidence boundaries](../papers/paper-xii/current/core/publication/source/traditional/reading_route.tex#L2)


[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#deformation-and-langlands-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: support_multiplicity()](../tools/check_hand_examples.py#L378). This checks the displayed finite calculations with exact rational or modular arithmetic.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

[All hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Reading routes](READING_ROUTES.md)
