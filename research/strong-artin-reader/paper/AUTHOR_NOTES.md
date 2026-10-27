# Strong Artin reader edition: authoring notes

This edition retains the full earlier residual-realization proof spine and extends it with the later formal mechanisms and worked examples. It is written as a conjecture monograph with a matching visual guide. The global automorphic attachment remains open.

## What changed

The manuscript preserves all 78 theorem/proposition/lemma/corollary groups from the older mathematical spine. The new introduction distinguishes the unramified and all-local conjecture statements. The separate formal appendix develops the actual H1, H2, relation, syzygy, and ordered matrix Hensel mechanisms. The worked appendix supplies detailed finite controls, including failed stronger statements.

The mathematical source audit identified and corrected the following inherited weaknesses:

1. An l-adic theorem invoked a global semisimplicity result while stating only Frobenius semisimplicity. Global semisimplicity, continuity, and finite ramification are now explicit.
2. The local Fourier obstruction compared nonzero ratios but omitted zero-support mismatches. Both supports are now checked.
3. A large residual proof appeared to choose its separation field from the unknown lift after choosing the coefficient prime. The field, universal polynomial alphabet, and exceptional prime set are now fixed beforehand.
4. The complex finite-image proof used an invalid general continuous-image assertion. The current proof uses the no-small-subgroups property and an open normal kernel.
5. Algebraic pseudocharacter realization was treated as if it supplied topological continuity. A trace-coordinate proof supplies the missing step.
6. The quotient-prime collapse proof implicitly used splitting-field extensions over an arbitrary number field. The new proof uses commuting p-primary parts and modular characteristic-polynomial uniqueness.
7. Some almost-everywhere statements omitted exceptional unramified and archimedean checks. The current text includes them and retains the stronger all-local hypothesis where needed.
8. Finite Satake and Hecke alphabet claims were broader than a weak lower attachment justified. They are now made outside one fixed finite exceptional set.
9. Broad monomial and realization-range language concealed theorem hypotheses. Cyclic induction, cohomological occurrence, normalization, and nonregular lifting conditions are now explicit.

These are audit repairs and substantive authoring choices. They are not silently classified as typographical proofreading or a fresh formalization.

## Failed construction routes represented in the paper

The total induced sum loses the cyclic label because every quotient twist occurs as a summand. Central determinants lose the label when the quotient prime divides rank. Sufficiently ramified epsilon twists lose the same label once dimension and determinant agree. Product functional equations retain a norm identity without attaching one factor. Regular lifting hypotheses fail for repeated zero weights at rank greater than one. The paper states what each route preserves and what information it discards.

The worked local calculations also preserve negative controls. A square-zero scalar lift from Z/9 to Z/27 does not exist. The unipotent matrix Hensel control has a target rejected by its exact congruence. The derivative at diag(1,−1) is genuinely singular over Q_p, so the inverse certificate theorem cannot cover it.

## Transient production issues and limitations

A generated Scholze exponent contained a stray comma. The source reviewer identified it and the forced correction was made before typesetting. A French bibliography accent was initially generated as an undefined macro and was corrected during source inspection before compilation. The coefficient-place versus local-base-field wording in the repeated-weight-zero paragraph was also corrected during mathematical review.

The current Lean replay attempt was blocked while fetching the matching portable toolchain, with HTTP 403 before any compiler invocation. The preserved historical evidence is source-authenticated. A new compiler replay is not claimed.

The first complete paper build passed at 58 pages with no overflow, undefined references, missing glyphs, or out-of-page words. Additional passes stabilized the references. Full page-image QA then found that the fifth figure caption described the matrix inverse-derivative theorem while the actual figure was the scalar square-root prefix tree. The caption was rewritten to describe the exact finite tree, dead prefixes, and compatible all-depth branch, with a separate sentence connecting the certified matrix sector. No mathematical theorem was changed by this caption correction. Typesetting and page-image validation are recorded in the release layout report. Any further source line wrapping needed to remove overflow must be recorded as a layout edit and repinned in the final source checks. All imported mathematical theorems retain their original hypotheses and their own evidence limitations.
