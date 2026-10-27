# Primary external sources checked

The mathematical input used for the finite-round bound is the quotient-cardinality
identity in the exact pinned local mathlib source:
  Mathlib/LinearAlgebra/Quotient/Card.lean
  Submodule.card_eq_card_quotient_mul_card
The full required local source and its theorem type were inspected before use.
Official documentation was also checked during this block:
https://leanprover-community.github.io/mathlib4_docs/Mathlib/LinearAlgebra/Quotient/Card.html

The integer computational reference uses SymPy's column Hermite-normal-form API.
Its official documentation was checked, and the installed version is recorded
in the finite-audit result:
https://docs.sympy.org/latest/modules/matrices/normalforms.html
https://docs.sympy.org/latest/modules/polys/domainmatrix.html

No theorem novelty or priority conclusion follows from these API checks. The
source proofs are checked against local pinned mathlib, not against a changing
online documentation revision. The numerical HNF library is cross-checked in
small finite domains, not formally verified in this release.
