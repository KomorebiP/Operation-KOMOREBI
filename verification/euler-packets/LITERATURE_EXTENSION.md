# External input for the expanded Euler example

**EULER-CASE-002 · checked 29 October 2026 · same-assistant source check**

## Source question

Does the cited Bernoulli denominator theorem imply
`v_2(B_(2r))=-1` for every integer `r>=1`, with the Bernoulli normalization
`z/(exp(z)-1)`? This is the only added external theorem needed for the sharp
dyadic kernel valuation. The generating-function identities, source-unit
factorization, finite reconstruction and sharpness implication are derived in
the worked page.

## Authentication and extraction

- Bibliographic record: NIST Digital Library of Mathematical Functions,
  Chapter 24, Bernoulli and Euler Polynomials, section 24.10(i),
  von Staudt-Clausen theorem.
- Stable locator: https://dlmf.nist.gov/24.10.E1 and the accompanying
  reduced-denominator sentence in https://dlmf.nist.gov/24.10.
- Observed version: 1.2.8, release 15 September 2026.
- Date accessed: 29 October 2026.
- Source status: states the standard theorem and cites its proof sources.
- Checks performed: opened the official NIST page, read the formula and
  denominator characterization, checked its prime condition and translated
  its positive even index `2n` to `2r`.
- Full-source retention: not requested. No full text or source cache is
  included in the repository. This record contains the checked implication.

The theorem identifies the reduced denominator of the positive even Bernoulli
number as the squarefree product of the primes `q` for which `q-1` divides
`2r`. The prime two always occurs exactly once. Coprimality of numerator and
denominator then gives the required valuation. The value `r=0` is excluded
and the kernel's constant coefficient is treated separately.

## Application and overlap

**Implication verdict: verified.** Multiplication by
`-2^(4r)*(2r-1)` adds `4r` to the valuation, since `2r-1` is odd.
It follows that `v_2(kappa_r)=4r-1` for positive r. The exact kernel formula
itself is proved from `Q(z)-zQ'(z)` in the page and checked by independent
rational series inversion through r=10.

Overlap: **known after translation of notation**. This is a bounded source
verification, not a novelty search. No Kummer, Euler periodicity, limiting
interpolation, universal root-classification or Lean claim is imported from
other portions of the cited chapter.

## Project source checked

At collection revision `9987ef468dcbfa49a256ea6da2b249d577da0a88`, read
`papers/paper-ix/current/sources/main/parts/20_arithmetic.tex`, from the
classical odd-length coordinate subsection through the row-dependent summand
weights, especially labels `thm:arith-odd-reconstruction`,
`cor:arith-odd-ladder`, `lem:arith-reconstruction`, `lem:arith-kappa`,
`thm:arith-sharp-tower` and `prop:arith-row-weight`.

The example reproduces those exact local identities in ordinary-degree
notation and supplies the complete E_8 rows. The normalized library sources
are pinned separately to `a3aa04ac18a523f30c50c7f5dba709f88e904eff`.
Written source review does not constitute a fresh execution of any Lean
declaration mentioned by Paper IX.
