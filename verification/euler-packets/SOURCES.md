# Sources, conventions, and overlap

Checked 29 October 2026. These are source-identification and bounded implication
checks for the worked example, not a literature-wide novelty review.

## Classical definitions and data

| Source | Exact locator and material used | Check and translation |
|---|---|---|
| NIST DLMF, Chapter 24 | [24.2(ii)](https://dlmf.nist.gov/24.2#ii), in particular 24.2.6 and 24.2.8 | Opened the definitions of signed Euler numbers and Euler polynomials. The worked example writes the polynomial as `mathcal E_m(x)` to distinguish its variable from a reciprocal power parameter. |
| NIST DLMF, Chapter 4 | [4.19.5](https://dlmf.nist.gov/4.19.E5) | Checked the secant expansion and sign conversion. Here `s_n=(-1)^n E_(2n)` is positive, and n is a compressed index. The analytic radius reported there is not used as a numerical error certificate. |
| OEIS A000364 | [entry](https://oeis.org/A000364), [b-file](https://oeis.org/A000364/b000364.txt), indices 0 through 15 | Opened the source table and checked the embedded integer prefix and zero offset. The program stores EGF numerators, not ordinary coefficients. |
| OEIS A211212 | [entry](https://oeis.org/A211212), prefix indices 0 through 11 and displayed generating function | Checked the quartic prefix, recurrence and generating function. Its `1/(cos(x/sqrt(2))*cosh(x/sqrt(2)))` is D_4(x)^(-1) in the example. The b-file request was unavailable, so the entry's displayed prefix is the source actually used. No asymptotic formula was used. |
| OEIS A181985 | [entry](https://oeis.org/A181985), definition of N-alternating permutations | Checked the comparison pattern: an ascent occurs exactly when N divides the position. The expanded example supplies its inclusion-exclusion derivation, with rank DP and small explicit permutations as finite controls. No novelty claim is made for this enumeration identity. |

No third-party paper PDF or licensed full text was copied into this publication.
The two short attributed numerical prefixes are embedded in the standalone
checker. Their exact values are independently reproduced from formal inversion
and finite permutation calculations in the stated ranges.

## Project sources

The collection source checkpoint is
`3a9b5f89883fbf24247410a56519045e809fbd1a`.
The source-file identities in the publication record pin these exact objects:

- `research/euler-signal-bridge/READ_ME.txt`: written shift/difference transfer,
  kernel support, signed Euler control, FIR interpretation and prime residual.
- `research/euler-signal-bridge/exact_results.json`: the earlier 395 finite
  checks, retained as its own historical evidence rather than added to the new counts.
- `papers/paper-iv/current/Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex`:
  the source route for cyclic denominators and reciprocal powers.

The mathematical library source pin is
`a3aa04ac18a523f30c50c7f5dba709f88e904eff`:

- `src/komorebi_math/sequences/families.py`: compressed integer recurrence,
  with count meaning the number of terms beginning at index zero.
- `src/komorebi_math/analytic/reciprocal.py` and `analytic/_series.py`:
  logarithmic reciprocal-power construction, with degree meaning the final
  compressed index. Integer and Fraction parameters have exact arithmetic.
- `src/komorebi_math/arithmetic/euler.py`: signed sech convention and separately
  named zigzag numbers, odd and dyadic source/kernel pairs, exact reconstruction,
  truncation and row-weight interfaces used by the expansion.

The expansion additionally reads
`papers/paper-ix/current/sources/main/parts/20_arithmetic.tex` at collection
revision `9987ef468dcbfa49a256ea6da2b249d577da0a88`. The odd-length reconstruction,
dyadic reconstruction, Bernoulli kernel, sharp tower and row weights are
**known after translation of notation** from that source. The new numerical
rows illustrate those results. `LITERATURE_EXTENSION.md` authenticates the
external NIST denominator theorem used by the sharp dyadic valuation proof.

The comparison checker records the actual checkout revision separately from the
source pin. The local checkout has documentation changes, but its tracked source
tree is checked against the pin before import. Every imported Komorebi source
must be tracked at that pin, and its actual file hash is observed before and
after the comparison. External NumPy is version-recorded, not rebuilt or
claimed kernel-certified. The compared outputs are exact integers and Fractions.

## Result used and implication status

The classical sources authenticate definitions, sequence identities and prefixes.
The universal algebraic identities in the new page are derived there and reviewed
in `PROOF_REVIEW.md` and `PROOF_REVIEW_EXPANSION.md`. No application premise is supplied solely by a matching
sequence name. The finite comparison range is in the computation contracts.

- Secant and quartic recurrences: **known verbatim**, with the displayed indexing.
- Quartic denominator generating function: **known after translation of notation**.
- The bridge `s_n=sum_k binomial(2n,4k)*4^k*b_k`: **formal corollary not stated**
  in the checked A211212 entry, obtained here by multiplying its generating
  function with cosh. This label concerns that source, not global priority.
- Matrix packet multiplication and Schur elimination: ordinary formal-series
  linear algebra presented in the project's coordinates.
- Residual-squaring inverse correction: an elementary classical identity,
  derived explicitly rather than presented as a new iteration.
- Integer shift/FIR and prime residual: **known after translation of notation**,
  with the existing project bridge read in full and its domains retained.

No global novelty, exclusive-method claim, or OEIS submission is made. Searching
these definitions and source entries establishes neither that the combined
exposition is unprecedented nor that another mathematical language cannot express
it. The example's contribution is the complete connected derivation, failure
witnesses, exact reconstruction, and inspectable computational checks.

## Matrix and congruence expansion

At checkpoint `0a1d2c6265885f22011e6717c5ddf3f3a627f462`, additionally read
the beginning of the pinned Paper IX arithmetic chapter, especially
`def:arith-euler`, `eq:arith-triangular`, `prop:arith-denominator` and
`ex:arith-bernoulli`. These identify the normalized congruential families,
their addresses and the boundary specialization, **known after translation
of notation**. The ordinary-degree and normalized coefficient conventions
are preserved.

The infinite coefficient matrices, factorial conjugation, Pascal sampling,
local chart-change cocycle, precision-loss estimate and coprime residue
combination are derived directly from finite coefficient algebra in the page.
The Euler index-shift statement modulo p^2 is a **formal corollary not stated**
in the checked odd-length reconstruction subsection: the page supplies the
unit-residue argument and its essential positive even starting-degree
hypothesis. This classification concerns that checked source, not priority.
No new external theorem or global novelty claim is introduced by these steps.
