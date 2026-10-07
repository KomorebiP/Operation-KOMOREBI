# Attribution and related work

This is a scoped source and context note, not a complete literature review or a historical-priority determination. The release makes no first-ever claim.

## Formal dependencies

The formalization is built on Lean and mathlib. It uses their existing polynomial, power-series, modular arithmetic, valuation, finite-module, quotient, and cardinality theories. Dependency revisions are recorded in `padic/lake-manifest.json`. The local theorem register gives the new source declarations without reclassifying imported results as original discoveries.

One direct classical input is the finite abelian group structure theorem. `padic/lean/KomorebiPadic/FiniteModulePresentation.lean` invokes `AddCommGroup.equiv_directSum_zmod_of_finite'` from `Mathlib.GroupTheory.FiniteAbelian.Basic`, then proves the restrictions and transport statements needed for the prime-power module presentation. The cyclic decomposition theorem is not presented as an invention of this project.

## Relevant mathematical context

**Prime-power automatic congruences.** Eric Rowland and Reem Yassawi, “Automatic congruences for diagonals of rational functions,” *Journal de Théorie des Nombres de Bordeaux* 27 (2015), 245–288, DOI [10.5802/jtnb.901](https://doi.org/10.5802/jtnb.901). The paper develops finite-automaton methods for coefficient congruences modulo prime powers in rational-diagonal and algebraic settings. It is relevant context for Cartier-based finite representations. Its hypotheses should not be identified with this release's rational-mask Mahler hypotheses without a separate argument.

**Abstract minimization.** Thomas Colcombet and Daniela Petrişan, “Automata Minimization: a Functorial Approach,” *Logical Methods in Computer Science* 16(1), article 32 (2020), DOI [10.23638/LMCS-16(1:32)2020](https://doi.org/10.23638/LMCS-16(1:32)2020). The paper gives a categorical framework for minimization across classes of acceptors, including deterministic and weighted automata. It supplies relevant context for intrinsic behavior and universal comparison. This note does not assert that its statements and the finite-module cardinality theorem here have identical scope.

The publisher pages were checked for bibliographic metadata and stated scope on 21 September 2026. This is not a full theorem-by-theorem comparison with either paper. Neither reference is silently substituted for the project's Lean proof.

## How to read the contribution claim

The object offered for examination is the connected formal development: an explicit prime-power correction construction, its exact obstruction and closure contracts, reductions preserving canonical coefficient output, and the residual-module realization theorem as instantiated for the specified masks. Established ideas, imported library results, newly written proofs, numerical checks, and implementation work should be evaluated separately.

The generic residual and realization arguments belong in the context of established linear and weighted-automaton theory. Their formal inclusion here does not, by itself, establish mathematical novelty. The theorem inventory measures source coverage rather than historical originality.

## Reproduction sources

The [official Lean installation guide](https://lean-lang.org/install/manual/) explains Elan and opening existing mathlib projects. The [official Elan reference](https://lean-lang.org/doc/reference/latest/Build-Tools-and-Distribution/Managing-Toolchains-with-Elan/) explains project toolchain selection. The [Lean 4.34.0-rc2 release](https://github.com/leanprover/lean4/releases/tag/v4.34.0-rc2) and the [pinned mathlib toolchain file](https://raw.githubusercontent.com/leanprover-community/mathlib4/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/lean-toolchain) identify the historical environment. Public source availability is not a successful clean build of this candidate.

## Attribution corrections

A correction should identify a claimed result, the relevant source and its exact hypotheses, and the relationship that needs clarification. The absence of a source from this short context note is not evidence of priority. Corrections will be recorded without rewriting the historical evidence as though it had never needed amendment.
