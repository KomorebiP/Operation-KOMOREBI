# Conservative review: transport and worked models

Reviewed in full, review-only, using `c19/proofread-math` and its checklist:

- `04_transport.tex`, lines 1–539.
- `05_worked_models.tex`, lines 1–647.

Source base: `/workspace/scratch/9f53d520971c/paper1_work/monograph/Komorebi_Paper_I_Monograph_2026-10-08/editable/traditional/`.

No manuscript files were edited. Nearby coefficient conventions, hull and free-presentation definitions, finite-packet definitions, and entry-point macros were inspected.

## Mathematical notation requiring an explicit editorial choice

1. **05_worked_models.tex:445 — undefined notation and incorrect object label.**
   Current: `&\text{relations: }F^m/N_S,\\`

   `F` and `m` are not defined in the traditional manuscript. The free-presentation theorem in `02_foundations.tex:232–236` instead defines `N_S\leq A^{\oplus r}` and `A^{\oplus r}/N_S\cong\Hull_A(S)`. The quotient is the presented hull, while `N_S` is its relation module.

   Conservative correction options, according to the intended label:

   - `&\text{free presentation: }A^{\oplus r}/N_S,\\`
   - `&\text{relations: }N_S,\\`

   This is not a uniquely forced isolated token replacement because either the label or the displayed object can be corrected. Do not silently choose the old undefined `F,m` convention. The first option preserves the displayed quotient/presentation purpose and reuses the established theorem verbatim.

## Local mathematical wording corrections

2. **04_transport.tex:286 — packets versus projectors.**
   Exact phrase: `and the quotient packets are bounded.`
   Minimal correction: `and the quotient projectors are bounded.`

   A packet is the range subspace, which is generally unbounded as a subset of its normed ambient space. The proof immediately establishes a norm bound for the quotient projector `\overline P_\alpha`. This is a locally forced terminology correction, with no symbolic formula change.

3. **05_worked_models.tex:399 — eigenspaces do not occur in pairs.**
   Exact phrase: `the eigenspaces occur in pairs.`
   Minimal correction: `the remaining Fourier characters occur in pairs.`

   The indices `k,n-k` give two Fourier characters spanning the same eigenspace. The preceding eigenvalue formula and the following multiplicity sentence uniquely identify the intended distinction. No formula changes.

4. **05_worked_models.tex:277 — allow a zero projection.**
   Exact phrase: `A seed therefore supplies only one vector direction in that eigenspace.`
   Minimal correction: `A seed therefore supplies at most one vector direction in that eigenspace.`

   The eigenspace projection may be zero. The subsequent argument uses the upper bound, not existence of a nonzero projected vector. No formula changes.

5. **05_worked_models.tex:33 — coordinate versus its kernel subspace.**
   Exact phrase: `The third coordinate, which is $\ker B$, is unreachable`
   Minimal correction: `The third coordinate direction, which spans $\ker B$, is unreachable`

   The kernel is the third coordinate line in `V=\bbk^3`, not the scalar coordinate function. The later proof already uses the correct statement that `e_3` spans the kernel. No symbolic formula changes.

## Routine language and LaTeX

No other objective spelling, grammar, environment, citation-key, or reference-key issue was found in these two files. Stylistic compound hyphenation was left unchanged.

## Mathematical-token changes

No edits were applied. Item 1 requires recording the chosen exact formula/notation change in the delivery change log. Items 2–5 are minimal prose changes clarifying the mathematical meaning of immediately adjacent formulas and proofs; no new argument or theorem hypothesis is proposed.

## Validation

A local Python structural scan found balanced `begin/end` environments in both files, all referenced labels present in the traditional source, and all cited keys present in the local bibliography. No external source lookup or proof reconstruction was performed. PDF compilation and visual layout validation were not run by this reviewer; those remain part of the coordinating agent's build review.

Coverage is complete for the assigned two source files. No substantive proof gap was identified by this local proofreading pass. This is not a claim of an independent full proof audit.
