# Paper I proofreading: orientation, foundations, and preamble

Review-only. No manuscript files were edited. Reviewed all of `01_orientation.tex` (118 lines), `02_foundations.tex` (1017 lines), and `Paper_I_Monograph.tex` (218 lines). Read the mathematical proofreading skill. Checked the orientation's section paths and the target of its source-component cross-reference against neighboring source files. This was a conservative local review, not a new proof audit or external-source verification.

## Mathematical / meaning-related findings

1. **Orientation line 60, scope mismatch with foundations line 39.**
   - Old: `A finite quiver and a two-sided ideal of source and target compatible relations.`
   - Minimal new: `A quiver with finite vertex set and a two-sided ideal of source and target compatible relations.`
   - The definition requires only a finite vertex set; it does not require finitely many arrows. This is a mathematical hypothesis wording correction, explicitly distinguished from routine copyediting.

2. **Orientation line 99, missing field qualification for the Euclidean assertion.** The matrices are defined over an arbitrary field in line 93, whereas the Euclidean inner product requires a real setting.
   - Old: `The ranges form a direct sum, but the projectors are not orthogonal in the Euclidean inner product.`
   - Minimal new: `The ranges form a direct sum, but over \(\mathbb R\) the projectors are not orthogonal in the Euclidean inner product.`
   - This qualifies the inner-product assertion while retaining the matrix identities over the arbitrary coefficient field. It changes the explicitly printed domain of that assertion and should be logged as a mathematical-token/scope clarification. An equally sound authorial choice is to set the example over the real numbers at line 93, but that is less minimal.

3. **Foundations lines 778 and 794, undefined radical notation `J(A)`.** The manuscript uses `\Jac(A)` in the notation map and explicitly defines `J=\Jac(A)` at line 677; no function `J(A)` is introduced.
   - Line 778 old fragments: `M/J(A)M` and `A/J(A)`.
   - Line 778 new fragments: `M/\Jac(A)M` and `A/\Jac(A)`.
   - Line 794: make the same two replacements.
   - These are four isolated mathematical-notation corrections with no change of intended operator.

4. **Foundations lines 808–825, algebraically closed multiplicity corollary: unresolved scope/notation ambiguity.** The display prints `A\cong\prod_iM_{d_i}(\bbk)` while the next expression is `M/JM`; `J` is not rebound within this statement. Read literally, the displayed hypothesis makes `A` semisimple and hence `J=0`, so the result is a valid narrower specialization if the preceding finite generation conventions are carried forward. The preceding theorem also covers nonsemisimple finite-dimensional algebras via `A/\Jac(A)`, so an intended radical-quotient specialization is plausible. Replacing `A` with `A/J` would broaden the printed hypothesis and is **not a uniquely forced proofreading correction**. Leave the formula unchanged unless the author chooses its intended scope. For a self-contained narrower specialization, explicitly declare that `M` is finitely generated and that `J=\Jac(A)`; for the broader finite-dimensional specialization, state those hypotheses and use `A/J` in the first decomposition. No new proof is needed, but this is a scope decision beyond conservative token editing.

## Routine language finding

5. **Orientation line 111, grammatical number.**
   - Old: `For graph and applications involving residual transport, read Sections 8 to 10.`
   - Minimal new: `For graphs and applications involving residual transport, read Sections 8 to 10.`

## Validation and remaining scope

- No objective prose or LaTeX issue found in the preamble or abstract.
- No additional high-confidence local mathematical typo found in the foundations chapter.
- Orientation reading paths match the numbered sections. `thm:source-component-rank` exists.
- No build run by this reviewer because no edits were made; global compilation and rendered layout review remain with the parent task.
- No claims about Lean verification, certificate freshness, or external source support were made in this review.
