# Hand-worked examples

Work through these calculations with pencil and paper. Every example gives its
inputs, intermediate steps, result and a short exercise with an answer. You do
not need to install software.

Start with the first example if matrices are new to you. A matrix acts on a
column vector by taking the dot product of each row with that vector. The
[glossary](GLOSSARY.md) explains the notation and the distinctions used here.

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

## Conventions and scope

Vectors are columns unless a displayed signal is explicitly a list. Matrix
products act from right to left. All fractions in the calculations are exact.
Example 9 uses exact fractions to describe a specified rounding operation.

These are introductory finite examples, not new results about the research
programs. The pages state the identities they use and link to the relevant
source guides. A successful example does not replace the hypotheses of a
general theorem or establish a new Lean correspondence.

## Check the arithmetic or run a program

The [exact arithmetic checker](../tools/check_hand_examples.py) checks the nine
examples with Python's standard library and rational arithmetic. From the
collection checkout, run:

    python -B tools/check_hand_examples.py

Expected result:

    PASS: 9 hand-worked examples

The checker covers the displayed finite calculations. It does not validate every
sentence in the tutorials, review a research proof or run Lean.

For executable library examples, continue to [First runs](FIRST_RUN.md) or the
[Komorebi Math user guide](https://github.com/KomorebiP/komorebi-math/blob/main/docs/USER_GUIDE.md).
The hand calculations remain useful without either library.

[Reading routes](READING_ROUTES.md) · [Glossary](GLOSSARY.md) · [Browse works](BROWSE.md)
