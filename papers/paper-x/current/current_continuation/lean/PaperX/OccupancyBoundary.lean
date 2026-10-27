import PaperX.OccupancyExamples

/-! Exact counterexamples to dropping diagonalizability or commutation.
These refute proposed stronger finite statements, not universal occupancy. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.OccupancyBoundary

open scoped Matrix Polynomial
open Polynomial Module.End PaperX.SpectralProjectors

def jordan : Matrix (Fin 2) (Fin 2) ℚ := !![1,1;0,1]
def jordanOp : Module.End ℚ (Fin 2 → ℚ) := jordan.toLin'

def P : Matrix (Fin 2) (Fin 2) ℚ := !![1,0;0,0]
def Q : Matrix (Fin 2) (Fin 2) ℚ := !![1/2,1/2;1/2,1/2]

theorem individual_idempotents : P*P = P ∧ Q*Q = Q := by decide +kernel

theorem noncommuting : P*Q ≠ Q*P := by decide +kernel

theorem product_not_idempotent : (P*Q)*(P*Q) ≠ P*Q := by decide +kernel

theorem product_trace_half : (P*Q).trace = 1/2 := by decide +kernel

theorem jordan_eigenvectors (a : ℚ) (x : Fin 2 → ℚ)
    (hx : jordan *ᵥ x = a • x) : (a = 1 ∧ x 1 = 0) ∨ x = 0 := by
  have h0 := congrFun hx 0
  have h1 := congrFun hx 1
  simp [jordan, Matrix.mulVec, dotProduct, Fin.sum_univ_succ] at h0 h1
  by_cases h : a = 1
  · left; constructor
    · exact h
    · subst a; linarith
  · have hz1 : x 1 = 0 := by
      have hm : (a-1)*x 1 = 0 := by linarith
      exact (mul_eq_zero.mp hm).resolve_left (sub_ne_zero.mpr h)
    have hz0 : x 0 = 0 := by
      have hm : (a-1)*x 0 = 0 := by rw [hz1] at h0; linarith
      exact (mul_eq_zero.mp hm).resolve_left (sub_ne_zero.mpr h)
    right; ext i; fin_cases i <;> assumption

theorem jordan_eigenvalue_iff (a : ℚ) : jordanOp.HasEigenvalue a ↔ a = 1 := by
  constructor
  · intro ha
    obtain ⟨x,hx,hne⟩ := (Submodule.ne_bot_iff _).mp ha
    exact (jordan_eigenvectors a x (mem_eigenspace_iff.mp hx)).resolve_right hne |>.1
  · rintro rfl
    exact jordanOp.hasEigenvalue_of_hasEigenvector
      ⟨mem_eigenspace_iff.mpr (show jordan *ᵥ ![(1:ℚ),0] = 1 • ![1,0] by decide +kernel),
       by decide +kernel⟩

theorem jordan_spectrum : eigenvalues jordanOp = {1} := by
  ext a
  simp [mem_eigenvalues, jordan_eigenvalue_iff]

/-- On the Jordan block, the literal singleton Lagrange formula is the identity,
not the projector onto the one-dimensional eigenspace. -/
theorem jordan_spectral_identity : spectral jordanOp 1 = 1 := by
  simp [spectral, jordan_spectrum, selector]

theorem jordan_formula_wrong_image :
    ∃ x : Fin 2 → ℚ, spectral jordanOp 1 x ∉ jordanOp.eigenspace 1 := by
  refine ⟨![0,1], ?_⟩
  rw [jordan_spectral_identity]
  rw [mem_eigenspace_iff]
  change ¬ jordan *ᵥ ![(0:ℚ),1] = 1 • ![0,1]
  decide +kernel

theorem jordan_not_split : ¬ Split jordanOp := by
  intro h
  obtain ⟨x,hx⟩ := jordan_formula_wrong_image
  exact hx (spectral_maps_into jordanOp h 1 x)

end PaperX.OccupancyBoundary
