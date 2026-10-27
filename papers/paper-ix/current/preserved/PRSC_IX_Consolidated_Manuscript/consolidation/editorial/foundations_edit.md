# Foundations and open-questions editorial pass

Scope: complete reading and prose editing of `manuscript/sections/10_foundations.tex` and `manuscript/sections/50_open_questions.tex` only. The mathematical proofreading skill was read. The user explicitly requested more human, polished prose, so paragraph-level style edits accompany conservative mathematical proofreading.

## Editorial changes

- Replaced repeated administrative expressions such as “actual,” “does not claim,” and “not newly certified” with direct descriptions of what the constructions do and where their hypotheses apply.
- Improved transitions among residue selection, triangular coordinates, filtration, finite differences, and recurrence packets.
- Preserved all statements distinguishing formal series from analytic convergence, finite identities from infinite expansions, finite CRT from global descent, and source preservation from Lean verification.
- Recast the open section as a research discussion. Retained singular persistence, Native 13.2, Native 13.3, all four arithmetic refinements, historical recovery gaps, and the historical-chart interface task.
- Retained both counterexamples and every historical coverage limitation, including missing original TeX, figure sources, and the complete historical experiment package.
- Added cross-references from finite CRT to Native 13.3 and from the chart-interface discussion to singular persistence. All existing references and labels remain.

## Mathematical-token changes

1. Added `E_h f(n)=f(n+h)` at the start of the proof of the finite Newton–Mahler theorem (`thm:mahler-foundation`). Previously the proof used `(E_h-I)^s` without defining `E_h`. The coordinating agent requested this notation repair after it was reported. It is forced by the preceding definition of the step-h forward difference and by the signed-stencil formula in the same theorem. Source correspondence: `baseline/PRSC_IX_v0.11.0_Nishibuchi_Completion.zip`, member `PRSC_IX_v0.11.0_Nishibuchi_Completion/formalization/FiniteMahler.lean`, declarations `difference_one` and `difference_explicit`.
2. Declared `M≥1` and `s,r,k∈N` explicitly before the affine Mahler kernel. The recovered source states exactly these nonnegative integer domains in the subsection “The affine Mahler kernel,” lines 2245–2271 of `strengthening/recovery/PSC_Paper_IX_Local_Polyphase_Annals_Edition.retrieved.tex`. This clarifies the domain of the unchanged polynomial coefficient formula and its finite support statement.
3. Declared `L≥1` and that `x̄` is a root modulo `p^L` before defining the finite lift set in the singular-persistence discussion. These are the precise domains needed by the invoked finite obstruction theorem. Source: `native/Native_Conjectures_Progress.md`, section 2, “A complete polynomial obstruction theorem.” The condition `L≥1` supplies `2L≥L+1`; no stronger persistence claim is introduced.
4. Added the name `Ext¹` in the source-based summary of restricted intrinsic obstruction progress. This names the existing result in `native/Native_Conjectures_Progress.md`, section 3; it does not introduce or alter a formula or theorem.

No pre-existing operator, sign, coefficient, bound, quantifier, hypothesis, conclusion, formula, or proof step was changed. All pre-existing inline and displayed mathematics is preserved in order, as checked after whitespace normalization. The explicit domain clarifications above close exposition omissions without broadening the cited theorems.

## Completeness follow-up

The coordinating agent requested a concise account of additional results already preserved in `native/Native_Conjectures_Progress.md`. The entire source was read before editing. A paragraph now names its restricted intrinsic finite Ext¹ obstruction for finitely presented commutative integer algebras (section 3), finite polynomial CRT reconstruction (section 4, “A precise reconstruction that does hold”), and rectangular finite relation/equality-label characterization (section 4, “A finite compatibility criterion with a precise universal property”). The paragraph distinguishes the external theorem specialization from the note's prose proofs and explicitly keeps the general Native 13.2/13.3 statements open. The exact external source hypotheses are retained in the named progress note and are not broadened or newly claimed as Lean formalizations.

The phrase “the remaining link” in Native 13.2 was corrected to “one of the links still needed,” because the listed definition and comparison requirements remain open. This was requested by the coordinating agent following semantic review.

## Validation

PASS: ordered displayed formulas, all pre-existing inline mathematics, labels, Lean names, citation keys, and LaTeX environment sequence match the originals. The only math-token additions are the four items recorded above. Every changed paragraph was reread in context. The overall manuscript build and rendered-page inspection are delegated to the coordinating agent to avoid concurrent builds of shared output.

No unresolved proofreading issue remains in these two files. This pass does not independently certify all historical research claims; the manuscript's stated historical and open-problem boundaries remain explicit.

Development note: one multi-file patch failed its context check before applying because a wrapped line did not match. The context was corrected and the patch reapplied successfully. An initial search used a nonexistent extracted `formalization` directory; the relevant preserved Lean source was then read from the baseline ZIP.

## File evidence

Final hashes after the completeness follow-up:

```json
[
  {
    "file": "10_foundations.tex",
    "before_sha256": "0096aef722073b6da8076ab7cb418683fd90d46dcfb99378ae859778146921cd",
    "after_sha256": "2bb63ee8c53cc7c6646c0f6ae0eb39b7846debb42fc12065c73c07cd797cdc6b",
    "displayed_formulas_preserved": 34,
    "theorem_environments_preserved": 11,
    "labels_preserved": 13,
    "lean_names_preserved": 51
  },
  {
    "file": "50_open_questions.tex",
    "before_sha256": "6f8f69265a26c1dd26bbfd57ee0749234c14ae07dcc5120973a167de6b5f14c5",
    "after_sha256": "3d8e7c89dd4fe318c099fa04d52c8de1f26143b82e33144d7a11745d3598be9f",
    "displayed_formulas_preserved": 9,
    "theorem_environments_preserved": 0,
    "labels_preserved": 6,
    "lean_names_preserved": 3
  }
]
```
