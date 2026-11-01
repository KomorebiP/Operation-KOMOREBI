# Hand-worked examples

Work through these calculations with pencil and paper. Every example gives its
inputs, intermediate steps, result and a short exercise with an answer. You do
not need to install software.

For a guided path from calculation to runnable code and source evidence, start
with the [three complete demonstrations](DEMONSTRATIONS.md).

Start with the first example if matrices are new to you. A matrix acts on a
column vector by taking the dot product of each row with that vector. The
[glossary](GLOSSARY.md) explains the notation and the distinctions used here.

Use the [topic map](LEARNING_MAP.md) to find the related papers, written proofs,
Lean coverage and code. Each example has these routes at the end, and the
related work pages link back to the examples.

Already reading a paper? [Find its examples in the paper index](LEARNING_MAP.md#start-from-a-core-paper).
For a book or another work, use the [monograph and work index](LEARNING_MAP.md#start-from-a-monograph-or-another-work).
The [coverage list](EXAMPLE_COVERAGE.md) shows which works still need an introductory tutorial in this guide.

| Example | What you will work out | Background |
|---|---|---|
| 1. [Split and reconstruct a vector](examples/01_PACKETS.md) | Projectors, complete packet families and an oblique decomposition | Addition and multiplication |
| 2. [Generate a space from one seed](examples/02_SEEDS.md) | Operator orbits, span and dependence on the allowed action | Vectors and span |
| 3. [Change coordinates and transport an operator](examples/03_COORDINATES.md) | An inverse coordinate change and the same calculation in two systems | Small matrix products |
| 4. [Assemble an operator from transfer blocks](examples/04_TRANSFER.md) | Source packets, target packets and reconstruction of an operation | Example 1 |
| 5. [Refine a signal into smaller packets](examples/05_REFINEMENT.md) | Even and odd samples, residue classes and a discarded component | Indexing a list |
| 6. [Reconstruct from redundant coordinates](examples/06_REDUNDANT_COORDINATES.md) | A left inverse and components that are not projectors | Examples 1 and 3 |
| 7. [Find an obstruction to recovering information](examples/07_OBSTRUCTIONS.md) | Two inputs with the same coarse value and different requested answers | Two-variable arithmetic |
| 8. [Average with unequal weights](examples/08_WEIGHTED_AVERAGES.md) | Conditional expectation and orthogonality in a weighted inner product | Weighted means |
| 9. [Round a binary number by hand](examples/09_BINARY_ROUNDING.md) | Precision, ties to even, error direction and local spacing | Fractions and powers of two |
| 10. [Find a kernel and its fibers](examples/10_KERNELS.md) | Rank, nullity and the information a map erases | Linear equations |
| 11. [Build spectral projectors](examples/11_SPECTRAL_PROJECTORS.md) | Eigenvectors, polynomial identities and oblique packets | Examples 1 and 2 |
| 12. [Eliminate one block](examples/12_BLOCK_ELIMINATION.md) | Schur complements, back substitution and singular cases | Two linear equations |
| 13. [Reconstruct from residues](examples/13_MODULAR_RECONSTRUCTION.md) | Modular inverses, CRT and residue selectors | Integer remainders |
| 14. [Separate averages and differences](examples/14_HAAR_PAIRS.md) | Two Haar levels, reconstruction and energy accounting | Averages and squares |
| 15. [Compose typed operations](examples/15_TYPED_PATHS.md) | Legal paths, one-sided inverses and a commutator | Matrix dimensions and products |
| 16. [Split reciprocal coefficients](examples/16_CYCLIC_RECIPROCALS.md) | Paper IV: coefficient recursion, cyclic projection and truncation | Polynomial multiplication |
| 17. [Calculate quantum measurement](examples/17_QUANTUM_MEASUREMENT.md) | Paper VII: phases, density matrices, probabilities and dephasing | Complex numbers and small matrices |
| 18. [Follow modular lift branches](examples/18_LIFT_BRANCHES.md) | Paper X: reduction compatibility and branches that stop | Integer remainders |
| 19. [Compute finite-field Frobenius](examples/19_FINITE_FROBENIUS.md) | Paper XI: a quadratic field, trace, norm and an intertwiner | Modular arithmetic and matrices |
| 20. [Separate support from multiplicity](examples/20_SUPPORT_AND_MULTIPLICITY.md) | Paper XII: module presentations, fibers and nilpotent structure | Quotients and linear maps |
| 21. [Choose a proof certificate](examples/21_PROOF_CERTIFICATES.md) | Proof Path Theory: shared premises, minimum cost and incomparable certificates | Sets and small tables |
| 22. [Recover hidden memory](examples/22_HIDDEN_MEMORY.md) | Sufficient Resolution and Machine Societies: visible summaries and delayed feedback | Two-coordinate updates |
| 23. [Find a reusable calibration](examples/23_CALIBRATED_CONTINUATION.md) | Grounded Abstraction: known inputs, compatible models and an invariant core | Basis vectors and matrix products |
| 24. [Calculate feedback coefficients](examples/24_CONTRACTED_FEEDBACK.md) | Special Functions: contracted arguments and a nonlinear coefficient recurrence | Polynomial products and differentiation |
| 25. [Choose repair directions](examples/25_REPAIR_MENUS.md) | Constructive Repair: free repair, weighted menus and an obstruction witness | Linear equations and span |
| 26. [Update a Gaussian model](examples/26_GAUSSIAN_UPDATE.md) | Certified Inference: one observation, posterior covariance and a candidate gain | Small matrices and Gaussian densities |

## Extended research examples

The [Euler-number derivation](demonstrations/EULER_PACKETS.md),
[factorial-lanes derivation](demonstrations/FACTORIAL_LANES.md), and
[wavelet and polyphase transfer](demonstrations/WAVELET_POLYPHASE.md) follow
longer chains of exact representations, transfer laws, and explicit failure
witnesses. The wavelet case includes a three-tap discrete filter, four levels of
Haar coefficients, exact predict–update lifting, a weighted best-detail
selection, sharp finite stability, a full wavelet transfer matrix, a
filtering-versus-coarsening counterexample, boundary repair and downloadable
results. Each extended example retains its own finite evidence scope.

The [Stirling, Bell and Fubini example](demonstrations/STIRLING_BELL_FUBINI.md)
adds a combinatorial flagship: one triangular counting kernel with two
distinct input weightings, a signed inverse, a general formal-series
substitution, Touchard polynomial and moment operations, complete residue
packet transfers, and an exact interpolation-versus-aggregation boundary. It includes a standalone exact
Python checker and downloadable source-bound records.

The [roots-of-unity and falling-factorial example](demonstrations/ROOTS_UNITY_FALLING_FACTORIAL.md)
connects the earlier arithmetic, Euler and Stirling examples. It carries
a character projector through a Stirling/Newton change of basis and
independently checks the resulting operation against actual function-image
enumeration, rational spectral projectors, filtered generating functions,
finite differences, general translation and cyclic carry blocks, and
transported multiplication. Wrong-basis and characteristic-three spectral
counterexamples keep the assumptions explicit. Eleven exact CSV tables
and three Python-generated SVG diagrams accompany the source.

## Conventions and scope

Vectors are columns unless a displayed signal is explicitly a list. Matrix
products act from right to left. All fractions in the calculations are exact.
Example 9 uses exact fractions to describe a specified rounding operation.

These are introductory finite examples, not new results about the research
programs. The pages state the identities they use and link to the relevant
source guides. A successful example does not replace the hypotheses of a
general theorem or establish a new Lean correspondence.

## Check the arithmetic or run a program

The [exact arithmetic checker](../tools/check_hand_examples.py) checks the 26
examples with Python's standard library and exact rational, modular and finite-set calculations. From the
collection checkout, run:

    python -B tools/check_hand_examples.py

Expected result:

    PASS: 26 hand-worked examples

The checker covers the displayed finite calculations. It does not validate every
sentence in the tutorials, review a research proof or run Lean.

For executable library examples, continue to [First runs](FIRST_RUN.md) or the
[Komorebi Math user guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md).
The hand calculations remain useful without either library.

[Reading routes](READING_ROUTES.md) · [Glossary](GLOSSARY.md) · [Browse works](BROWSE.md)
