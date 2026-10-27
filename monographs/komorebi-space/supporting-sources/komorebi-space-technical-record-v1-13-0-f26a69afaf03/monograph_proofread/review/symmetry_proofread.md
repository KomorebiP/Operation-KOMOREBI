# Symmetry and geometry proofreading record

Mode: edit, following `mathbox:proofread-math` and its full checklist.

## Coverage

Read every line of the following files, including the definitions, proofs, worked examples, captions, and formal-scope statements. Also read the common preamble and the complete monograph root to establish conventions and context.

- `source/chapters/04_symmetry.tex`: 456 lines, complete.
- `source/chapters/04a_boundary_lab.tex`: 70 lines, complete.
- `source/chapters/04b_phase.tex`: 106 lines, complete.
- `source/chapters/05_geometry.tex`: 641 lines, complete.

Total coverage: 1,273 source lines.

## Corrections

Six localized wording corrections were made. The phase chapter required no edits.

- `source/chapters/04_symmetry.tex`, line 4: Terminology: abelian is the precise property of a group, whereas commutation applies to its elements.
  Before: `The groups need not commute and the homomorphisms need not be bijective.`
  After: `The groups need not be abelian and the homomorphisms need not be bijective.`
- `source/chapters/04_symmetry.tex`, line 166: Terminology: the existing proof explicitly requires p² = 1 and includes the identity; involution often means order exactly two.
  Before: `A cocycle is determined by an involution \(p\in H\).`
  After: `A cocycle is determined by an element \(p\in H\) whose square is the identity.`
- `source/chapters/04_symmetry.tex`, line 168: Consistency with the preceding square-identity condition; retain all four elements and the existing argument.
  Before: `For \(H=S_3\), the involutions are the identity and the three transpositions.`
  After: `For \(H=S_3\), these elements are the identity and the three transpositions.`
- `source/chapters/04a_boundary_lab.tex`, line 48: Scope: H is arbitrary here and may be infinite; the later S3 check is finite.
  Before: `This is a worked finite model of the marked transport mechanism.`
  After: `This is a worked two-view model of the marked transport mechanism.`
- `source/chapters/05_geometry.tex`, line 342: Resolve ambiguous pronoun: the projected input is x, not M or the error.
  Before: `A vector in \(M\) with that error is its unique orthogonal projection, so \(P=P_M\).`
  After: `A vector in \(M\) with that error is the unique orthogonal projection of \(x\), so \(P=P_M\).`
- `source/chapters/05_geometry.tex`, line 617: Replace compressed old exact wording with the existing precise meaning.
  Before: `More generally, suppose a unit vector \(x\) is old exact but orthogonal to the new kernel.`
  After: `More generally, suppose a unit vector \(x\) is exact for the original operator but orthogonal to the new kernel.`

## Mathematical-token changes

One explicit symbol was inserted while resolving a pronoun: in the proof of the two-stage projection theorem, `its unique orthogonal projection` became `the unique orthogonal projection of \(x\)`. The input `x` is already fixed at the start of the paragraph, and the argument has already established `Px ∈ M` and `x − Px ⟂ M`. No hypothesis, conclusion, or proof step changed.

The C2/S3 example now describes an element whose square is the identity instead of calling the identity an involution. Its proof already states `p² = 1` and lists the identity with three transpositions. The underlying set and argument are unchanged.

## Additions and remaining issues

No explanatory expansion was needed in this scope. The existing passages already explain product order, based versus marked boundaries, composition coverage, protected feasibility, the two-stage restriction, and the separate assumptions for projector motion. No new result or proof was added.

No unresolved local mathematical, notation, or cross-reference issue was found. This is a conservative proofreading result, not a claim of a fresh theorem-level audit, external-source verification, or Lean replay.

## Validation

- Re-read all changed passages with their surrounding definitions and proof steps.
- Every `ref`, `eqref`, `cref`, `Cref`, and `pageref` key in the assigned files resolves to a label in the source tree.
- All begin/end environments in the assigned files are balanced and correctly nested.
- No section, numbered environment, label, or display was added or removed.
- No full build was run during parallel source editing, as instructed. Final PDF layout review is pending the assembled build.

Source is frozen for integration. Exact before/after file hashes and all change text are recorded in `symmetry_proofread.json`.
