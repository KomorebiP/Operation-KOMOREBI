import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.LinearAlgebra.Dimension.Finite
import Mathlib.LinearAlgebra.Matrix.Rank

/-! Finite separation of an arbitrary finite linearly independent family of functions.
The evaluation matrix is selected from the actual functions, not postulated invertible.
The index and sample spaces may be empty. No arithmetic density is assumed here. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.FiniteSeparation

open scoped BigOperators
universe u v w
variable {K : Type u} [Field K] {I : Type v} [Fintype I] {X : Type w}

/-- The linear measurement at a single point. -/
def row (f : I → X → K) (x : X) : (I → K) →ₗ[K] K :=
  ∑ i, (f i x) • LinearMap.proj i

theorem row_apply (f : I → X → K) (x : X) (c : I → K) :
    row f x c = ∑ i, c i * f i x := by
  simp [row, mul_comm]

/-- Independent columns mean that their evaluations span the entire coefficient dual. -/
theorem evaluation_span (f : I → X → K) (hi : LinearIndependent K f) :
    Submodule.span K (Set.range (row f)) = ⊤ := by
  apply Submodule.span_eq_top_of_ne_zero
  intro c hc
  by_contra! h
  have hz : ∑ i, c i • f i = 0 := by
    funext x
    have hx := h (row f x) (Set.mem_range_self x)
    simpa [row_apply] using hx
  exact hc (funext ((Fintype.linearIndependent_iff.mp hi) c hz))

/-- Exactly as many distinct samples as columns suffice. This is a genuine existence
result extracted from the spanning evaluation forms, not an invertibility hypothesis. -/
theorem exists_square_separator (f : I → X → K) (hi : LinearIndependent K f) :
    ∃ s : I → X, Function.Injective s ∧
      Function.Injective (fun c : I → K => fun j => ∑ i, c i * f i (s j)) := by
  classical
  obtain ⟨J, a, ha, hs, hl⟩ := exists_linearIndependent' K (row f)
  have htop : ⊤ ≤ Submodule.span K (Set.range (row f ∘ a)) := by
    rw [hs, evaluation_span f hi]
  let b := Module.Basis.mk hl htop
  let e : J ≃ I := b.indexEquiv (Pi.basisFun K I).dualBasis
  let b' := b.reindex e
  refine ⟨a ∘ e.symm, ha.comp e.symm.injective, ?_⟩
  intro c d hcd
  apply (Module.evalEquiv K (I → K)).injective
  apply b'.ext
  intro j
  have hj := congrFun hcd j
  simpa [b', b, Module.Basis.reindex_apply, Module.Basis.mk_apply, row_apply,
    Function.comp_def] using hj

/-- Matrix form, with row orientation made explicit. -/
def sampleMatrix (f : I → X → K) (s : I → X) : Matrix I I K :=
  fun j i => f i (s j)

theorem exists_nonsingular_samples [DecidableEq I]
    (f : I → X → K) (hi : LinearIndependent K f) :
    ∃ s : I → X, Function.Injective s ∧ (sampleMatrix f s).det ≠ 0 := by
  obtain ⟨s, hs, hinj⟩ := exists_square_separator f hi
  refine ⟨s, hs, ?_⟩
  have hmul : Function.Injective (sampleMatrix f s).mulVec := by
    intro c d hcd
    apply hinj
    funext j
    simpa [sampleMatrix, Matrix.mulVec, dotProduct, mul_comm] using congrFun hcd j
  exact ((Matrix.isUnit_iff_isUnit_det _).mp
    (Matrix.mulVec_injective_iff_isUnit.mp hmul)).ne_zero

/-- A valid square separator has full column rank. -/
theorem separator_rank [DecidableEq I] (f : I → X → K) (s : I → X)
    (h : (sampleMatrix f s).det ≠ 0) :
    (sampleMatrix f s).rank = Fintype.card I := by
  exact (Matrix.linearIndependent_rows_of_det_ne_zero h).rank_matrix


/-- The converse: one invertible evaluation matrix certifies actual functional
independence. Distinctness alone is not substituted for this condition. -/
theorem independent_of_separator [DecidableEq I] (f : I → X → K) (s : I → X)
    (h : (sampleMatrix f s).det ≠ 0) : LinearIndependent K f := by
  rw [Fintype.linearIndependent_iff]
  intro c hc
  have hz : (sampleMatrix f s).mulVec c = 0 := by
    funext j
    simpa [sampleMatrix, Matrix.mulVec, dotProduct, mul_comm] using congrFun hc (s j)
  have hu : IsUnit (sampleMatrix f s) :=
    (Matrix.isUnit_iff_isUnit_det _).2 (isUnit_iff_ne_zero.mpr h)
  have hh : c = 0 := Matrix.mulVec_injective_iff_isUnit.mpr hu (by simpa using hz)
  intro i
  exact congrFun hh i

end PaperX.FiniteSeparation
