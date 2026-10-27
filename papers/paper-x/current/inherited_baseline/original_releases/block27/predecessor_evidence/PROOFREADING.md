# Block 19 conservative mathematical proofreading

Status: PASS within the scope below. No substantive unresolved issue was found in the Block 19 documentation. This record is a prose and notation review, not an additional proof certificate.

## Scope and mode

Applied the mathbox proofread-math skill in self-review mode. Read README.md, FIVE_PARTIALS_STATUS.md, Paper_X_Nineteenth_Block_Ledger.md and NEXT_TARGET.md. For the amended manuscript, reviewed the new Block 19 paragraph, its new front status paragraph, the neighboring Block 18 hypotheses, the preamble, and the generated Block 19 patch. Whole-source structural checks supplemented that local manuscript review. Historical theorem statements and proofs were not substantively re-audited.

Compared the new statements with the declarations and structures in OrthogonalProjectors, CornerProjectors, OrthogonalPartial, OrthogonalLifting, FamilySummands, FamilyRigidity, FamilyClassification, FamilyExamples and FamilyBoundary. Checked the finite example counts against exact_families.json. The separate source proof audit and release verification provide their own evidence.

## Minimal corrections

- Updated the manuscript's front formal-verification status from Block 18 to Block 19. It now states complete orthogonal-family lifting, the uniform precision loss, actual images and reductions, and labeled conjugacy under the appropriate local/nonunit hypotheses. The fifteen-checked/five-partial arithmetic status is unchanged.
- Qualified the historical Block 18 ledger sentence: simultaneous families “were not asserted in Block 18.” It no longer reads as a current Block 19 limitation.
- Regenerated source/Block19_Amendments.patch against the unchanged Block 18 amended manuscript.

Mathematical-token changes: none to formulas, hypotheses, quantified theorem statements or proof steps. The status paragraph was updated to summarize the already checked Block 19 scope. No production Lean source was changed during this proofreading pass.

## Scope correspondence

- Existence starts with an actual supplied integral carrier and a complete equivariant family at depth e+k. The retained depth k is positive. The nonzero group order divides pi^e. No local-ring hypothesis is asserted for this theorem.
- All labels are lifted with one averaging cost. Exact orthogonality and the sum-to-identity equation are obtained, including the empty-label case when the supplied equations can hold.
- The finite direct sum in the manuscript is represented by a finite product of actual invariant image submodules in Lean. The image reduction statements are surjectivity onto the reduced projector images; they are not claimed as unproved intrinsic quotient-module identifications.
- Rigidity uses the order U = sum_i F_i E_i and the relation U E_i U^-1 = F_i. Local coefficients with nonunit pi and positive retained depth give invertibility. Finite-group, domain and completeness hypotheses are not claimed for rigidity alone.
- The two-adic three-label example retains the prescribed data modulo 2. The impossibility statement concerns preserving that same whole family modulo 4, rather than existence of arbitrary integral decompositions.
- The finite computation counts match their report: 98 constructed lifts, 370 projectors, 49 conjugacy comparisons, 8 exhaustive small lifts, and 128 vector decompositions. The computational and Lean final-complement procedures are correctly distinguished.
- No arithmetic packet attachment, coefficient or Hodge–Tate/period comparison, arithmetic Frobenius coverage, or universal occupancy has been promoted to a proved claim.

## Validation actually performed

- Python structural scan of the amended source, after excluding LaTeX comments and literal listing bodies: matched all begin/end environments; balanced braces; no duplicate labels; no unresolved internal ref/eqref/cref/Cref targets.
- The new Block 19 paragraph has three matched display-math pairs and paired unescaped inline-dollar delimiters. It introduces no label or citation keys.
- Applied the generated patch to a temporary copy of the Block 18 amended source with the system patch command. The result was byte-identical to the Block 19 amended source.
- Re-read both corrected passages and the new theorem displays in context. No further correction was required.

No PDF was typeset or visually inspected in this pass. Structural source checks do not certify pagination, line breaks, overfull boxes, font rendering or graphic placement. The release states this limitation explicitly.

## Reviewed file hashes

These SHA-256 values identify the exact reviewed revisions. Later changes require corresponding review of the changed portions.

| File | SHA-256 |
|---|---|
| README.md | `9b12c90c35b0d304e5284c47002d9b18180b58873145eaaa4c706790c65463f1` |
| FIVE_PARTIALS_STATUS.md | `4f2de332044003e1c52b804aefcae2d539aa6a888b8f3c39d8e30a3fcbf054bb` |
| Paper_X_Nineteenth_Block_Ledger.md | `260edea5c17885cc15dfee1a70418084baf542ce5aa5d7ff7ac3149cfc735875` |
| NEXT_TARGET.md | `2754a22b696fed84ae084cbd753e56ebe3080a35a0d8f184b2f284cc08a822b1` |
| source/Projector_Resolved_Seed_Calculus_X_Block19_Amended.tex | `a70af5afbee1574fabc7fdca9b5248ad2d63d3e7fc025e2e4caa3b7a9082b5bd` |
| source/Block19_Amendments.patch | `a911249fe898f233f901dc2ed88b1e843f308b373f0621322068ea92cb92eec7` |
