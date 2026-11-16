# Sequence-family coverage completion

Author: Komorebi P.

Date: November 16, 2026

## Scope

This change completes the family index for the preserved 90-record research
archive. The index now contains 36 definitions: the original ten exact
coefficient explorers and twelve analytic families, thirteen source-defined
discrete constructions, and one classical reference collection. All 90 archived
records have a family or reference home. These counts describe the index's
organization; they are not a count of distinct new infinite families.

The final membership sweep also assigns the three remaining curated scalar
seeds (natural numbers, odd numbers and partition numbers) to the existing
universal coefficient-section construction. It applies to their coefficient
series without requiring a new generator. These three records link to the
general definition rather than unsupported browser parent controls. Every one
of the 2,292 indexed integer records now has at least one family or reference
assignment. The definition and source-document counts stay at 36 and 12.

The original integer records, terms, b-files, offsets, review classifications
and OEIS annotations are preserved. Existing formulas and explorations remain
available. No new analytic-continuation or general numerical engine is implied
by the discrete family pages.

## Archived membership map

| Archive records | Family or reference definition |
| --- | --- |
| KOM001–KOM007, KOM017–KOM028 | GF-RECIPROCAL |
| KOM008–KOM012 | GF-CLASSICAL-REFERENCES |
| KOM013–KOM016 | GF-KBONACCI |
| KOM029–KOM035 | GF-BLOCK-LOGARITHMIC |
| KOM036–KOM042 | GF-BLOCK-TRANSFORMS |
| KOM043–KOM046 | GF-BLOCK-HANKEL |
| KOM047–KOM057 | GF-BLOCK-VALUATIONS |
| KOM058–KOM065 | GF-DIGIT-RESIDUES |
| KOM066–KOM068 | GF-CYCLIC-SUBSETS |
| KOM069–KOM074 | GF-PASCAL-VALUATIONS |
| KOM075–KOM076 | GF-TOTIENT-PREFIX |
| KOM077 | GF-PRIME-POWER-SUPPORT |
| KOM078–KOM079 | GF-COLLATZ-READOUTS |
| KOM080–KOM084 | GF-SMITH-POLYNOMIALS |
| KOM085–KOM087 | GF-CLIFFORD-WORDS |
| KOM088–KOM090 | GF-CYCLIC-MASKS |

Each family page gives its defining expression and domain, links the maintained
source passage, and displays representative stored examples with their exact
decimal integer strings and original offsets. Archive pages list every linked
KOM record. Source-defined discrete pages link the preserved generator and
source bundle. They do not expose an unsupported parameter calculator.

## Logarithmic normalization

Let

\[
D_N(z)=\sum_{m\ge0}\frac{(-1)^m z^{Nm}}{(Nm)!}.
\]

The transfer-tangent explorer uses

\[
T_N(m)=\bigl(N(m+1)-1\bigr)!
[z^{N(m+1)-1}]\left(-\frac{D_N'(z)}{D_N(z)}\right).
\]

The recovered logarithmic records use

\[
L_N(n)=(Nn)![z^{Nn}]
\left(-z\frac{D_N'(z)}{D_N(z)}\right).
\]

Multiplication by z shifts the coefficient degree by one. Therefore L_N(0)=0,
and for n>=1 the coefficient is unchanged before factorial normalization, giving

\[
L_N(n)=\frac{(Nn)!}{(Nn-1)!}T_N(n-1)=Nn\,T_N(n-1).
\]

The family page states this shift and factor explicitly. The archived records
link to that definition, not to an unadjusted tangent calculator. The focused
tests compare thirteen original values at each N=2 through 8 against this
independently computed relationship.

## Source binding

The additional source document is
`research/sequence-archive/generate_candidates.py`, pinned at repository commit
`96ef8755314fe6bfa3c5ca76b1d61e20f3c1e510`. Its UTF-8/LF SHA-256 is
`579d64c63fd3b142d645ee6f6204d7b7114f49bed65517ebe1d8fd583f629b18`.

The complete source manifest now lists 12 documents and 311 headings. Binding
the original generator and its passages supports reproducible definitions and
provenance. It does not constitute a new review of every source manuscript or
a historical-priority audit.

## Verification contract

The focused Python checks in `tools/test_sequence_families.py` verify:

- Source text hashes and source line bounds for all 12 bindings.
- The 36 definition types and ten unchanged exact engines.
- One meaningful family assignment for each archived KOM identifier.
- Complete membership for all 2,292 indexed records, with definition-only
  links and preserved values for the three unsupported classical parent seeds.
- Correct N and r in all nineteen reciprocal-explorer links, with eight
  coefficients per linked instance checked against the archived integers.
- The four original k-bonacci orders in generated links.
- The logarithmic shift and scale across the seven archived parameter choices.
- Exact string-valued example data, original offsets, static source/member
  links and reproduction access on all generated family pages.
- No mutation of the underlying integer record objects during family indexing.

The broader independent family audit retains its numerical, transfer,
modular-state and identification checks. Its report additionally records
family modes, complete record coverage and complete archive coverage. The family membership additions
do not alter the 1,231 existing typed record relations.

## Browser validation history

The first focused browser attempt,
[Actions run 43899106388](https://github.com/KomorebiP/Operation-KOMOREBI/actions/runs/43899106388),
completed the JavaScript-enabled checks at 1440, 390 and 320 pixels, then failed
in the JavaScript-disabled layout check. The test incorrectly awaited an
animation-frame promise in that context and reported
`page.evaluate: Resulting promise was garbage collected`.

That attempt was **not a clean browser pass**. The job appeared green because
the logged `node ... | tee ...` pipeline reported the successful log writer's
exit status instead of the failed test command's status. The workflow now
selects the explicit Bash runner shell, which enables `pipefail`, and requires
a final report containing `status: passed`, all three viewport results and the
completed JavaScript-disabled checks. The static layout check now waits for
page load and measures page width synchronously without requesting MathJax,
font-ready or animation-frame promises. The first run does not count as
completion evidence; subsequent runs must satisfy all of these assertions.

## Boundaries retained

Prime-adic tables do not claim a uniform valuation formula. Totient records are
prefix statistics, not full inverse fibers. Collatz records describe pointwise
inputs, not a proof of global orbit convergence. Smith polynomial records do
not assert circuit realizability. Clifford words use declared gate alphabets
and identity modulo global phase. The coefficient triangle keeps its flat
index distinct from row and column coordinates. Historical novelty remains
separate from exact definition and finite reproduction.
