# Regularization and analytic appendix proofreading

Conservative final mathematical proofreading in edit mode.

Source review complete and frozen pending assembled PDF review.

## Coverage

Read all 958 assigned source lines:

- `source/chapters/05h_regularized_repair.tex`: 257 lines, edited.
- `source/chapters/05i_diagonal_regularization.tex`: 193 lines, no edit required.
- `source/chapters/05j_inexact_certificates.tex`: 176 lines, edited.
- `source/chapters/05k_stopping_rules.tex`: 149 lines, no edit required.
- `source/chapters/12_proof_tools.tex`: 183 lines, edited.

Read the bounded-realization Hilbert setup, adjoint convention, budget-frontier definitions and relevant closed-range statement as needed. Read the proofreading skill and detailed checklist.

## Edits

1. `source/chapters/05h_regularized_repair.tex` line 199: Clarify the stacked modifiers in the positive-floor, attained-projection row.
   Before: Strong convergence to the least norm least-squares correction, not an exact answer.
   After: Strong convergence to the least-squares correction of minimum norm, not an exact answer.
2. `source/chapters/05h_regularized_repair.tex` line 210: Clarify that the pair of residual data consists of vectors.
   Before: For two residual data $r,\widetilde r$
   After: For two residual data vectors $r,\widetilde r$
3. `source/chapters/05j_inexact_certificates.tex` line 68: Name the bound whose sharpness the first scalar example establishes.
   Before: For the first sharpness statement take $T=0$
   After: For sharpness of the correction-error bound, take $T=0$
4. `source/chapters/05j_inexact_certificates.tex` line 68: Name the bound whose sharpness the second scalar example establishes.
   Before: For the second, take $T=\sqrt\alpha\,I$
   After: For sharpness of the fitted-data bound, take $T=\sqrt\alpha\,I$
5. `source/chapters/12_proof_tools.tex` line 99: Remove drafting language suggesting an unresolved gap from the finished appendix.
   Before: The following derivation records the missing analytic step.
   After: The following derivation records this analytic step explicitly.

Mathematical-token changes: none. Explanatory additions: none. The assigned arguments already provide their needed explanatory bridges. No new results, shortened proofs, altered hypotheses, changed labels, or changed section/theorem counters.

## Local consistency and validation

Reviewed the positivity and invertibility argument, monotonicity comparisons, range-attainment alternatives, fixed-parameter noise factors, diagonal tail and ceiling estimates, primal/dual signs, full-kernel Gram convention, and stopping-rule hypotheses in their immediate context. No unresolved local mathematical issue was identified. This is a proofreading finding, not a fresh global proof audit.

- All existing inline and delimited display math spans are byte-identical before and after the editorial pass.
- All local reference targets resolve in the assembled source.
- LaTeX environments balance.
- Chapter/subsection/label declarations are unchanged.
- Every changed passage was reread with its surrounding statements and proofs.
- Full builds and rendered-page checks are reserved for the parent’s assembled source.

## Failure and recovery

The first automatic math-span comparison used an overbroad delimiter regex and mistook a table row-spacing command for an opening display. It stopped before writing any source changes. Requiring an unescaped opening delimiter corrected the check, which then passed.

## Remaining limitations

- This is local mathematical proofreading, not a fresh referee-level proof audit or independent formal replay.
- External citation support was not re-audited.
- No full LaTeX build was run during parallel source editing; parent owns the assembled build and PDF review.
