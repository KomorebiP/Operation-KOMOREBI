# From examples to papers, proofs, Lean and code

Choose a topic to move from a hand calculation to definitions and related source material. Each linked work has return links to these examples. These are subject routes, not new theorem-to-Lean correspondences.

[All hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Browse works](BROWSE.md)

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

<a id="packets"></a>

## 1. Split and reconstruct a vector

[Work through the example](examples/01_PACKETS.md)

**Terms:** [Projector](GLOSSARY.md#projector) · [Packet](GLOSSARY.md#packet) · [Complete packet family](GLOSSARY.md#complete-packet-family) · [Orthogonal projector](GLOSSARY.md#orthogonal-projector) · [Direct sum](GLOSSARY.md#direct-sum)

Exact packet coordinates provide the source setting for the elementary decomposition.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md#first-program-packet-analysis-and-reconstruction). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: packets()](../tools/check_hand_examples.py#L56). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="seeds"></a>

## 2. Generate a space from one seed

[Work through the example](examples/02_SEEDS.md)

**Terms:** [Seed](GLOSSARY.md#seed) · [Seed rank](GLOSSARY.md#seed-rank) · [Cyclic vector](GLOSSARY.md#cyclic) · [Span](GLOSSARY.md#span) · [Operator algebra](GLOSSARY.md#operator-algebra)

Paper I develops seed generation with its stated algebra and module hypotheses.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#1-seed). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: seeds()](../tools/check_hand_examples.py#L72). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="coordinates"></a>

## 3. Change coordinates

[Work through the example](examples/03_COORDINATES.md)

**Terms:** [Coordinates](GLOSSARY.md#coordinates) · [Coordinate change](GLOSSARY.md#coordinate-change) · [Inverse](GLOSSARY.md#inverse) · [Operator conjugation](GLOSSARY.md#conjugation) · [Linear isomorphism](GLOSSARY.md#isomorphism)

Use Paper I for exact packet coordinates and the library atlas for general coordinate changes.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#tensor-and-operator-transport). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: coordinates()](../tools/check_hand_examples.py#L84). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="transfer"></a>

## 4. Assemble transfer blocks

[Work through the example](examples/04_TRANSFER.md)

**Terms:** [Transfer block](GLOSSARY.md#transfer-block) · [Composition](GLOSSARY.md#composition) · [Block matrix](GLOSSARY.md#block-matrix)

Paper II supplies transfer background. Paper VIII develops operator algorithms and compilation.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets | [Read](works/paper-ii.md#read) | [Proofs](works/paper-ii.md#written-proofs) | [Coverage and sources](works/paper-ii.md#lean) | [Code and setup](works/paper-ii.md#code) | [Status](works/paper-ii.md#evidence) |
| Paper VIII: Packet Operator Algorithms, Exact Compilation, and GPU Realization | [Read](works/paper-viii.md#read) | [Proofs](works/paper-viii.md#written-proofs) | [Coverage and sources](works/paper-viii.md#lean) | [Code and setup](works/paper-viii.md#code) | [Status](works/paper-viii.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#transfer-blocks). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: transfer()](../tools/check_hand_examples.py#L98). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="refinement"></a>

## 5. Refine a signal

[Work through the example](examples/05_REFINEMENT.md)

**Terms:** [Refinement](GLOSSARY.md#refinement) · [Coarsening](GLOSSARY.md#coarsening) · [Polyphase decomposition](GLOSSARY.md#polyphase) · [Residue class](GLOSSARY.md#residue-class) · [Compatibility](GLOSSARY.md#compatibility)

Read Paper II for refinement and Paper V for signal and polyphase constructions.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets | [Read](works/paper-ii.md#read) | [Proofs](works/paper-ii.md#written-proofs) | [Coverage and sources](works/paper-ii.md#lean) | [Code and setup](works/paper-ii.md#code) | [Status](works/paper-ii.md#evidence) |
| Paper V: Polyphase Signal Calculus | [Read](works/paper-v.md#read) | [Proofs](works/paper-v.md#written-proofs) | [Coverage and sources](works/paper-v.md#lean) | [Code and setup](works/paper-v.md#code) | [Status](works/paper-v.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#6-refine). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: refinement()](../tools/check_hand_examples.py#L118). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="redundancy"></a>

## 6. Use redundant coordinates

[Work through the example](examples/06_REDUNDANT_COORDINATES.md)

**Terms:** [Analysis and synthesis](GLOSSARY.md#analysis-synthesis) · [Left inverse](GLOSSARY.md#left-inverse) · [Redundant coordinates](GLOSSARY.md#redundancy) · [Reconstruction](GLOSSARY.md#reconstruction)

Compare the exact packet setting of Paper I with the broader analysis and synthesis construction in the library guide.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/ANALYSIS_SYNTHESIS_SYSTEMS.md#components-versus-projectors). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: redundant_coordinates()](../tools/check_hand_examples.py#L135). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="obstructions"></a>

## 7. Detect lost information

[Work through the example](examples/07_OBSTRUCTIONS.md)

**Terms:** [Obstruction](GLOSSARY.md#obstruction) · [Fiber](GLOSSARY.md#fiber) · [Factorization through a map](GLOSSARY.md#factorization) · [Kernel](GLOSSARY.md#kernel) · [Quotient space](GLOSSARY.md#quotient-space)

The finite recovery obstruction is an entry point to the works on compatibility and realization boundaries.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory | [Read](works/paper-iii.md#read) | [Proofs](works/paper-iii.md#written-proofs) | [Coverage and sources](works/paper-iii.md#lean) | [Code and setup](works/paper-iii.md#code) | [Status](works/paper-iii.md#evidence) |
| Realization Boundaries | [Read](works/realization-boundaries.md#read) | [Proofs](works/realization-boundaries.md#written-proofs) | [Coverage and sources](works/realization-boundaries.md#lean) | [Code and setup](works/realization-boundaries.md#code) | [Status](works/realization-boundaries.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: obstructions()](../tools/check_hand_examples.py#L155). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="averages"></a>

## 8. Average with unequal weights

[Work through the example](examples/08_WEIGHTED_AVERAGES.md)

**Terms:** [Finite conditional expectation](GLOSSARY.md#conditional-expectation) · [Inner product](GLOSSARY.md#inner-product) · [Orthogonal projector](GLOSSARY.md#orthogonal-projector) · [Residual](GLOSSARY.md#residual)

Paper VI includes stochastic and Bayesian realizations. Its assumptions extend beyond this finite partition.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations | [Read](works/paper-vi.md#read) | [Proofs](works/paper-vi.md#written-proofs) | [Coverage and sources](works/paper-vi.md#lean) | [Code and setup](works/paper-vi.md#code) | [Status](works/paper-vi.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#dynamics-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: weighted_averages()](../tools/check_hand_examples.py#L165). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="rounding"></a>

## 9. Round a binary number

[Work through the example](examples/09_BINARY_ROUNDING.md)

**Terms:** [Precision](GLOSSARY.md#precision) · [Dyadic rational](GLOSSARY.md#dyadic-rational) · [Rounding](GLOSSARY.md#rounding) · [ULP](GLOSSARY.md#ulp) · [Numerical ternary](GLOSSARY.md#ternary) · [Exact](GLOSSARY.md#exact) · [Numerical](GLOSSARY.md#numerical)

Paper IX supplies dyadic arithmetic background. The rounding implementation and its contracts belong to Polyphase Float.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation | [Read](works/paper-ix.md#read) | [Proofs](works/paper-ix.md#written-proofs) | [Coverage and sources](works/paper-ix.md#lean) | [Code and setup](works/paper-ix.md#code) | [Status](works/paper-ix.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/polyphase-float/blob/main/docs/manual/chapters/06_arithmetic_ranges.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: binary_rounding()](../tools/check_hand_examples.py#L182). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="kernels"></a>

## 10. Find a kernel and its fibers

[Work through the example](examples/10_KERNELS.md)

**Terms:** [Kernel](GLOSSARY.md#kernel) · [Image](GLOSSARY.md#image) · [Rank](GLOSSARY.md#rank) · [Nullity](GLOSSARY.md#nullity) · [Rank–nullity identity](GLOSSARY.md#rank-nullity) · [Injective map](GLOSSARY.md#injective) · [Surjective map](GLOSSARY.md#surjective) · [Quotient space](GLOSSARY.md#quotient-space) · [Subspace](GLOSSARY.md#subspace)

These finite linear calculations give background for typed realizations and information loss. Read each work for its own claims.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |
| Information Realization | [Read](works/information-realization.md#read) | [Proofs](works/information-realization.md#written-proofs) | [Coverage and sources](works/information-realization.md#lean) | [Code and setup](works/information-realization.md#code) | [Status](works/information-realization.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/CARRIER_CHANGE_OBSTRUCTIONS.md). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: kernels()](../tools/check_hand_examples.py#L201). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="spectral"></a>

## 11. Build spectral projectors

[Work through the example](examples/11_SPECTRAL_PROJECTORS.md)

**Terms:** [Eigenvector](GLOSSARY.md#eigenvector) · [Eigenvalue](GLOSSARY.md#eigenvalue) · [Eigenspace](GLOSSARY.md#eigenspace) · [Diagonalizable operator](GLOSSARY.md#diagonalizable) · [Polynomial in an operator](GLOSSARY.md#polynomial-in-operator) · [Minimal polynomial](GLOSSARY.md#minimal-polynomial) · [Spectral projector](GLOSSARY.md#spectral-projector)

The example uses a diagonalizable two-dimensional matrix. The works develop wider packet and spectral constructions with additional hypotheses.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |
| Paper II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets | [Read](works/paper-ii.md#read) | [Proofs](works/paper-ii.md#written-proofs) | [Coverage and sources](works/paper-ii.md#lean) | [Code and setup](works/paper-ii.md#code) | [Status](works/paper-ii.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#spectral-and-packet-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: spectral_projectors()](../tools/check_hand_examples.py#L212). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="elimination"></a>

## 12. Eliminate a block of unknowns

[Work through the example](examples/12_BLOCK_ELIMINATION.md)

**Terms:** [Block matrix](GLOSSARY.md#block-matrix) · [Schur complement](GLOSSARY.md#schur-complement) · [Elimination](GLOSSARY.md#elimination) · [Determinant](GLOSSARY.md#determinant) · [Inverse](GLOSSARY.md#inverse)

Paper VI gives elimination background. The collected Gaussian elimination guide retains its pending source qualification and unassessed confidence.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper VI: Transfer Semigroups: Stochastic, Bayesian, Fractional, and PDE Realizations | [Read](works/paper-vi.md#read) | [Proofs](works/paper-vi.md#written-proofs) | [Coverage and sources](works/paper-vi.md#lean) | [Code and setup](works/paper-vi.md#code) | [Status](works/paper-vi.md#evidence) |
| Gaussian Elimination: collected guide | [Read](works/gaussian-elimination-guide.md#read) | [Proofs](works/gaussian-elimination-guide.md#written-proofs) | [Coverage and sources](works/gaussian-elimination-guide.md#lean) | [Code and setup](works/gaussian-elimination-guide.md#code) | [Status](works/gaussian-elimination-guide.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#dynamics-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: block_elimination()](../tools/check_hand_examples.py#L225). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="modular"></a>

## 13. Reconstruct from residues

[Work through the example](examples/13_MODULAR_RECONSTRUCTION.md)

**Terms:** [Integer congruence](GLOSSARY.md#congruence) · [Coprime integers](GLOSSARY.md#coprime) · [Modular inverse](GLOSSARY.md#modular-inverse) · [Chinese remainder theorem](GLOSSARY.md#chinese-remainder) · [Residue class](GLOSSARY.md#residue-class)

The example is ordinary integer CRT. Paper IX develops arithmetic packets and local deformation beyond this calculation.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper IX: Arithmetic Packets, Dyadic Towers, and Local Polynomial Deformation | [Read](works/paper-ix.md#read) | [Proofs](works/paper-ix.md#written-proofs) | [Coverage and sources](works/paper-ix.md#lean) | [Code and setup](works/paper-ix.md#code) | [Status](works/paper-ix.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/GENERAL_COORDINATE_ATLAS.md#spectral-and-packet-coordinates). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: modular_reconstruction()](../tools/check_hand_examples.py#L237). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="haar"></a>

## 14. Separate averages and details

[Work through the example](examples/14_HAAR_PAIRS.md)

**Terms:** [Haar pair](GLOSSARY.md#haar-pair) · [Detail coefficient](GLOSSARY.md#detail-coefficient) · [Normalization](GLOSSARY.md#normalization) · [Orthogonal matrix](GLOSSARY.md#orthogonal-matrix) · [Refinement](GLOSSARY.md#refinement)

Paper V supplies signal background. Information Realization includes a finite Haar contract within its recorded formal core.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper V: Polyphase Signal Calculus | [Read](works/paper-v.md#read) | [Proofs](works/paper-v.md#written-proofs) | [Coverage and sources](works/paper-v.md#lean) | [Code and setup](works/paper-v.md#code) | [Status](works/paper-v.md#evidence) |
| Information Realization | [Read](works/information-realization.md#read) | [Proofs](works/information-realization.md#written-proofs) | [Coverage and sources](works/information-realization.md#lean) | [Code and setup](works/information-realization.md#code) | [Status](works/information-realization.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#signal-realization). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: haar_pairs()](../tools/check_hand_examples.py#L247). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

<a id="typed-paths"></a>

## 15. Compose typed operations

[Work through the example](examples/15_TYPED_PATHS.md)

**Terms:** [Typed system](GLOSSARY.md#typed-system) · [Typed path](GLOSSARY.md#typed-path) · [Operator relation](GLOSSARY.md#relation) · [Domain and codomain](GLOSSARY.md#domain-codomain) · [Intertwiner](GLOSSARY.md#intertwiner) · [Commutator](GLOSSARY.md#commutator)

Paper I develops typed systems and their realizations. Paper III continues with typed transfer and obstructions.

| Related work | Paper or book | Written proofs | Lean | Code | Evidence |
|---|---|---|---|---|---|
| Paper I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates | [Read](works/paper-i.md#read) | [Proofs](works/paper-i.md#written-proofs) | [Coverage and sources](works/paper-i.md#lean) | [Code and setup](works/paper-i.md#code) | [Status](works/paper-i.md#evidence) |
| Paper III: Typed Transfer, Nonlinear Packets, and Obstruction Theory | [Read](works/paper-iii.md#read) | [Proofs](works/paper-iii.md#written-proofs) | [Coverage and sources](works/paper-iii.md#lean) | [Code and setup](works/paper-iii.md#code) | [Status](works/paper-iii.md#evidence) |

[Related library guide and code examples](https://github.com/KomorebiP/komorebi-math/blob/main/docs/UNIFIED_LANGUAGE.md#3-operate). The guide covers related constructions and their software interfaces.

[Python arithmetic check for this example: typed_paths()](../tools/check_hand_examples.py#L263). This checks the displayed finite calculations with exact fractions.

The Lean links open each work’s recorded coverage and sources. They do not certify this tutorial. A work may have limited coverage or no linked Lean or code. Its page states what is available.

[Back to topics](#topics)

[All hand-worked examples](HAND_WORKED_EXAMPLES.md) · [Glossary](GLOSSARY.md) · [Reading routes](READING_ROUTES.md)
