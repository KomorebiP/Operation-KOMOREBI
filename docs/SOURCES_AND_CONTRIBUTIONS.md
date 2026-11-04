# Sources and contributions for the worked examples

The worked examples connect established mathematics through the project's
packet, transfer, and residual language. This page identifies the classical
inputs to three starting points and describes what each walkthrough contributes.

## Euler numbers and quartic reciprocals

[Follow the Euler calculation](demonstrations/EULER_PACKETS.md).

| Ingredient | Source and exact locator | Use in the example |
|---|---|---|
| Signed Euler numbers, Euler polynomials, and the secant series | NIST *Digital Library of Mathematical Functions*, [24.2.6 and 24.2.8](https://dlmf.nist.gov/24.2#ii), [4.19.5](https://dlmf.nist.gov/4.19.E5) | Fixes the sign, degree, and factorial conventions. The page's positive secant sequence uses a compressed even-degree index. |
| Positive secant sequence | [OEIS A000364](https://oeis.org/A000364), entry credited to N. J. A. Sloane, and its [table](https://oeis.org/A000364/b000364.txt), indices 0–15 | Supplies the attributed comparison prefix. The checker also reconstructs those values by exact recurrence. |
| Quartic reciprocal sequence | [OEIS A211212](https://oeis.org/A211212), entry by Peter Luschny; recurrence credited to Ilya Gutkovskiy, 27 January 2020; generating function credited to Michael Wallner, 17 November 2020 | Identifies the displayed quartic recurrence and equivalent cosine/cosh generating function. |
| Generalized alternating permutations | Peter Luschny's [OEIS A181985](https://oeis.org/A181985), definition in COMMENTS | Supplies the comparison pattern: ascents occur exactly at positions divisible by the chosen block length. |

The walkthrough contributes a connected derivation: it carries the same Euler
data through reciprocal packets, polynomial coordinates, local arithmetic,
and explicit failure and repair calculations. Its written extensions use
identified statements from Papers IV and IX, with their own hypotheses and
[source notes](../verification/euler-packets/SOURCES.md).
The sequence values, named classical families, and credited OEIS formulas
remain their established inputs. Broader priority questions require a
statement-specific literature comparison.

## Haar wavelets, lifting, and polyphase filters

[Follow the sixteen-sample calculation](demonstrations/WAVELET_POLYPHASE.md).

| Ingredient | Source and exact locator | Translation used here |
|---|---|---|
| Discrete Haar analysis | Martin Vetterli and Jelena Kovačević, *Wavelets and Subband Coding* (1995), corrected online manuscript, [§3.1.2, equations 3.1.10–3.1.14, printed p. 104](https://waveletsandsubbandcoding.org/Repository/VetterliKovacevic95_Manuscript.pdf#page=121) | The walkthrough uses half-sums and half-differences, with corresponding synthesis weights, instead of the book's orthonormal normalization. |
| Polyphase matrix representation | Vetterli and Kovačević, [§3.2.1, equations 3.2.22–3.2.26, printed pp. 120–122](https://waveletsandsubbandcoding.org/Repository/VetterliKovacevic95_Manuscript.pdf#page=137) | The walkthrough explicitly derives its finite circular shift matrix and boundary correction. |
| Split, predict, update, and reverse the steps | Wim Sweldens, *The Lifting Scheme: A New Philosophy in Biorthogonal Wavelet Constructions* (1995), [Figure 1 and the inverse algorithm, PDF p. 5](https://cm-bell-labs.github.io/who/wim/papers/spie95.pdf#page=5) | The displayed pair factorization is a specialization of lifting with its declared sign and scale. |

The walkthrough contributes one fully specified rational calculation through
all four Haar levels, the chosen three-tap filter, the complete transfer
matrix, and exact omitted-interaction, commutator, and boundary residuals.
The derivations and reproducible tables make that example inspectable.
Haar analysis, lifting, polyphase representation, and operator conjugation
are established ingredients. The example's finite circular model gives the
scope of its formulas.

## Seed generation and the central framework

[Generate a space from one seed](examples/02_SEEDS.md), then follow
[Paper I's definitions and written results](works/paper-i.md).

A single linear operator makes a finite-dimensional vector space into a
polynomial module. Cyclic generation and primary decomposition are classical;
see Paul Garrett, *Abstract Algebra* (June 2007),
[Theorem 10.1.1 and Corollary 10.4.1, printed pp. 126 and 130](https://www-users.cse.umn.edu/~garrett/m/algebra/Whole#page=136).
Paper I's one-operator seed count is a consequence of that module structure.
The two-dimensional tutorial is an illustration of cyclic generation.

Realization Calculus develops its packet, transfer, refinement, and residual
constructions in the individual papers. [Komorebi Space](works/komorebi-space.md)
provides its own realization and compatibility framework, with a recorded
sixteen-group correspondence. Those works should be assessed through their
specific definitions, statements, assumptions, and comparisons with prior work.
The introductory calculations explain the language used to enter them.

For attribution, cite the particular work, result, and revision used, following
the [citation guide](../CITATION.md). The [project statement](PROJECT_STATEMENT.md#citations-and-acknowledgment-of-prior-work)
describes the continuing work on the wider citation record.

[Start here](START_HERE.md) · [Worked examples](DEMONSTRATIONS.md) · [Project map](PROJECT_MAP.md)
