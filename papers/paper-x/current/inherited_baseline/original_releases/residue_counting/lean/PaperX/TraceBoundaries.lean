import PaperX.TraceExamples
import Mathlib.LinearAlgebra.Matrix.ToLinearEquiv

/-! Boundaries of finite trace information: distinctness is weaker than linear
independence; a multiplicity vector does not choose an embedded subspace. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.TraceBoundaries

open scoped BigOperators Matrix
open PaperX.FiniteSeparation

/-- Three distinct functions, but the third is the sum of the first two. -/
def dependentFunctions : Fin 3 → ℚ → ℚ := ![fun _ => 1, fun x => x, fun x => 1+x]

theorem functions_distinct : Function.Injective dependentFunctions := by
  intro i j h
  fin_cases i <;> fin_cases j <;> try rfl
  all_goals solve
    | (have h0 := congrFun h 0; norm_num [dependentFunctions] at h0)
    | (have h1 := congrFun h 1; norm_num [dependentFunctions] at h1)

theorem no_three_sample_separator (s : Fin 3 → ℚ) :
    (sampleMatrix dependentFunctions s).det = 0 := by
  apply Matrix.exists_mulVec_eq_zero_iff.mp
  refine ⟨![1,1,-1], ?_, ?_⟩
  · intro h
    have h0 := congrFun h 0
    norm_num at h0
  · ext j
    simp [sampleMatrix, dependentFunctions, Matrix.mulVec, dotProduct, Fin.sum_univ_succ]

/-- Two different embedded one-dimensional summands of the same trivial carrier. -/
def leftProjector : Matrix (Fin 2) (Fin 2) ℚ := !![1,0; 0,0]
def rightProjector : Matrix (Fin 2) (Fin 2) ℚ := !![0,0; 0,1]

theorem left_idempotent : leftProjector * leftProjector = leftProjector := by decide +kernel

theorem right_idempotent : rightProjector * rightProjector = rightProjector := by decide +kernel

theorem projectors_distinct : leftProjector ≠ rightProjector := by decide +kernel

theorem equal_projector_traces : leftProjector.trace = 1 ∧ rightProjector.trace = 1 := by
  decide +kernel

/-- Both projectors commute with every scalar action, hence in particular with a
trivial group representation. Their equal traces do not identify them. -/
theorem projectors_commute_scalar (a : ℚ) :
    leftProjector * (a • 1) = (a • 1) * leftProjector ∧
    rightProjector * (a • 1) = (a • 1) * rightProjector := by
  simp

end PaperX.TraceBoundaries
