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

Shared math-display self-review:

- Scope: the new plain-text-to-TeX projection and its use in search results,
  sequence definitions and the curated generator interface. Existing reader
  TeX is recovered from the pinned renderer rather than reconstructed from SVG.
- Checked fraction denominator scope, sum/product bodies and bounds, source
  versus local indices, powers and factorials, coefficient extraction,
  hypergeometric parameter rows, and source-index substitution notes.
- Mathematical-token changes to stored formulas, authored sources, programs
  and exact data: none. The new TeX is a presentation transcription only.
- The parser recognizes 6,441 of 6,501 recorded representations. The remaining
  60 retain their literal source notation. Ambiguous or unsupported syntax
  fails to the original source rather than guessing a display.
- The pinned MathJax runtime compiled 524 representative samples spanning all
  292 recognized structural layouts, with no reported rendering errors. Unit
  tests check binding and unsupported cases. Browser checks cover dynamic
  formula replacement and both display modes at 1440, 390 and 320px.
- All 6,069 existing exact CSV/JSON/text exports compare byte-for-byte with the
  prior generated site. These checks establish presentation and implementation
  behavior; they do not prove the displayed identities or constitute an
  independent review of the research sources.

Footer and coefficient-table self-review:

- Coverage: library formula displays, source-index explanations, row polynomials,
  complete coefficient tables and their defining representations. This does not
  constitute proofreading of every manuscript in the project.
- Display corrections: removed visible dashes used as empty parameter-row
  placeholders; separated defining equations; stacked multi-condition sum
  bounds; replaced the displayed hypergeometric argument separator with a
  vertical bar. Legitimate parameter distinctions remain intact.
- Mathematical display correction: n!^2 now displays as (n!)^2. Ambiguous
  factorial exponents retain the original source instead of a guessed display.
- Removed an irrelevant rising-factorial boilerplate note from displays of
  formulas that do not use that notation. Original export metadata is retained.
- Authored mathematical source/token changes: none. The 139 additions are
  source-linked coefficient extractions and supported columns of the published
  registry families. The block-kernel inverse follows from the reciprocal
  generating-series identity. Classical kernels are identified as such.
- Exact validation covers every one of the 7,099 added coefficients/terms and
  their source maps, and both products of each forward/inverse block kernel on
  the finite 13-row windows. These checks are finite implementation evidence,
  not a historical novelty review or a proof inferred from matching terms.

The added generators reject nonintegral coefficients instead of truncating
rational values. The original authored sources and the 6,069 prior exact data
exports remain byte-identical. The row table and footer controls were checked
at 1440/390/320px, with no-JavaScript, enlarged-text and forced-color reading.
