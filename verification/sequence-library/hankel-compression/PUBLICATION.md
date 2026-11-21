# Hankel compression publication verification

Author: Komorebi P. Mathematical checkpoint: SEQ-DH-2026-11-20-002.
Source base: f3da1097aa4faacd2c1201b48e015de07ee4b045.

The new continuation reader supplies general even/odd parity compression,
a uniform order-at-most-126 result for quadratic weights, and exact minimal
orders63 and112 for the two explicitly stated worked examples. Their
recurrences start at n1. The order112 example includes a zero second minor.
The general mixed-parameter problem and a sharp universal quadratic63 formula
remain open. Review provenance is self-review, with separate implementations;
no independent review, historical novelty, or Lean certificate is asserted.

## Exact verification

- All351 points of the degree25 triangular grid pass, covering702 complete
  70-state identities and5616 early scalar identities. The stencil is fixed
  explicitly at degree drops and at the zero weight.
- The universal ideal identity is reconstructed over Z[A,p,q,x,y], with all
  coefficients checked and both quotient polynomials retained.
- The quadratic audit uses256 ordinary tensor coordinates,52 monomial block
  determinants, an exact rational-function comparison, and a modular Bezout
  identity with preserved degrees.
- The mixed audit rebuilds all12870 coordinates using bitmask states and
  explicit monomial moments. It verifies the integer residual, denominator,
  numerator, recurrence start and minimality witness without NumPy or SymPy.
- The parity checks reach M3 with924 and462 states,154 independent Schur
  values and78 direct original determinants.
- All five commands replay from a fresh extraction of the source bundle.

The browser matrix passes at1440px,390px and320px, with no page errors,
duplicate IDs, broken in-page anchors or page overflow. Keyboard disclosure,
enlarged text, forced colors and static no-JavaScript reading pass. Both worked
examples restore their intended parameters in the existing calculator and
match the exact determinant prefixes. Screenshots were inspected locally.
These are automated project checks, not accessibility certification.

Source-renderer tests (9), library/OEIS-receipt tests (15), differential tests
(14), all41 preset handoffs (one cross-language test), and metadata tests (7)
pass. The catalogue remains at2333 records,7126 formulas and46 generalized
families.

## Preservation and delivery

The preceding published source ZIP is retained byte for byte under
research/sequence-closed-forms/retained-sources/sequence-formula-source-f3da1097.zip.
Its SHA-256 is cac5a05178b8be7ccab1fadbbc76e0bf222a476c03db198f75013a813359d0a0.
It is linked through GitHub, without duplicating its bytes in the Pages output.

The new ZIP retains every preceding member. The existing mathematical source
notes, arithmetic engines, catalogue data and comparison receipts remain
byte-identical. Changes to predecessor members are confined to the builder,
source renderer, its regression test, and the synthetic README. Twelve new
members supply the continuation proofs, replayers and certificate data.
source-bundle.json binds the74 source members and archive bytes.

The required CI, deployment, and matching live revision are publication gates;
their final outcome is recorded by the pull request and deployment, separately
from this local verification report.
