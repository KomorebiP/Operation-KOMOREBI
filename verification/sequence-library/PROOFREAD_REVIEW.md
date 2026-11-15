# Formula-display self-review

Proofread: new representations and index descriptions in
`tools/sequence_formula_catalogue.py`, `tools/sequence_library.py`, and
`docs/SEQUENCE_LIBRARY.md`.

- Routine edits: defined coefficient extraction, rising factorials, generalized
  hypergeometric notation, and reduced rational components beside the formulas.
  Source index m and local index n are explicitly distinguished for sections.
- Mathematical-token changes during this proofreading pass: none. The added
  notation guide explains the existing representations.
- Unresolved proofreading issues: none in the changed displays and prose.
- Validation: independent finite arithmetic audit, source-bundle reproduction,
  generated-page checks, and browser reading/plot checks. Current computation
  evidence is identified in the adjacent README.
- Coverage: the newly added representations and explanatory text, not a new
  correctness or priority review of the source registry or earlier books.

Additional scope: the secancy parameter-column and Euler-transfer theta displays,
research guide, offset descriptions and source links added in this pass.

- Checked ordinary [r^k] and [x^k] extraction, rising versus falling factorials,
  unsigned first-kind Stirling coefficients, the 1/k Bell-column recurrence,
  signed sech coefficients, and source degrees Nn/2n at actual n offsets.
- The finite-composition/Stirling and Bell-column forms are algebraic
  derivations from the registry generator. The theta convolution follows by
  multiplying the two signed sech series. Coefficient formulas using inverse
  hypergeometric generators are labelled as such rather than single-term forms.
- Routine edits: explicit zero prefixes, first nonzero offsets, classical x=1
  specialization, and k=1 transfer-tangent reindexing links.
- Mathematical-token changes to prior authored sources or legacy records: none.
- Unresolved proofreading issues in the added displays: none.
- Validation: independent exact checks of all stored terms and source-index
  maps; standard-library source-ZIP reproduction; generated HTML/CSV tests.
- This is a source/display self-review, not an independent proof or historical
  novelty review. The registry's novelty status remains unassessed.
