# Rational Hankel reader publication checks

Author: Komorebi P. Date: 20 November 2026.

This edition extends the existing binomial-sum and differential-Hankel readers
with the general rationality proof, sharp separated rank, common rational
moment kernel, and explicit linear-weight recurrence and numerator. The
linear calculator uses exact BigInt arithmetic through determinant size 256.
The general transfer bound is an existence result, not an efficiency claim.

The proof review is a project self-review. Historical novelty, independent
review, and Lean formalization are not established by these checks.

## Exact and source checks

- `verify_sequence_rational_hankel.py`: 3,830 exact assertions, including full
  transfer-vector certificates, boundary cases, and malformed-certificate rejection.
- `verify_sequence_linear_hankel.py`: all 19 degree-18 vector evaluations,
  152 early-index identities, 342 direct determinants, 115 additional checks,
  and an exact polynomial Bezout identity at a=b=1.
- The Python/JavaScript bridge agrees on 13,621 values at 53 integer parameter
  pairs through index 256, alongside independent Schur/direct comparisons
  and five common-kernel cases.
- Existing closed-form Python tests (30), core JavaScript tests (20), and
  source-renderer tests (8) pass. Differential, polynomial-Hankel, catalogue,
  OEIS-receipt, and all 41 existing calculator handoff checks pass.
- The broader sequence JavaScript suite passes all 132 tests.
- The two verifiers and new bridge replay successfully from a fresh extraction
  of the generated `sequence-formula-source.zip`.

Existing formulas in `FINITE_DIFFERENTIAL_HANKEL.md` are unchanged. Its obsolete
scope sentence is replaced with a link to the separate rationality proof.
The new mathematical statements are additions in their own source notes.
The catalogue remains at 2,333 records, 7,126 formulas, and 46 generalized
families, with the existing complete OEIS comparison receipts preserved.

## Reader checks

`browser-rational.json` records the new reader/calculator matrix;
`browser-existing.json` records the existing closed-form reader regression.
Both pass at 1440px, 390px, and 320px without page overflow or page errors.
Checks include keyboard disclosure, exact copying, URL restoration, CSV,
invalid parameters, zero minors, and static no-JavaScript reading. The new
reader also passes enlarged-text, reduced-motion, and forced-colors checks.
Desktop and phone screenshots were inspected locally. These are automated
project checks, not accessibility certification or independent user testing.

The latest upstream branding change (base revision
`33732c2017c28e98e8bff61a88e2680a7611b0df`) was integrated without conflicts.
The full-site CI and matching live revision are publication gates; their
outcome is recorded by the pull request and deployment, separately from
this local verification receipt.
