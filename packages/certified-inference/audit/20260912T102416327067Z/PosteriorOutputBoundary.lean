import Komorebi.PosteriorOutputSemantics
import Mathlib.LinearAlgebra.Matrix.Notation

set_option autoImplicit false
namespace Komorebi.PosteriorOutput.Boundary
open Matrix Komorebi.ExactPosterior Komorebi.RoundedPosterior

def original : Matrix (Fin 2) (Fin 2) ℚ := !![1/4,3/4;3/4,9/4]
def centers : Matrix (Fin 2) (Fin 2) ℚ := fun i j => (rExact 1 (original i j)).center

theorem center_values : centers = !![0,1/2;1/2,2] := by decide +kernel

theorem original_valid : (realMatrix original).PosSemidef := by
  have he : realMatrix original =
      (!![(1/2 : ℝ);3/2] : Matrix (Fin 2) (Fin 1) ℝ) *
      (!![(1/2 : ℝ);3/2] : Matrix (Fin 2) (Fin 1) ℝ).transpose := by
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [original, realMatrix, Matrix.mul_apply]
  rw [he]
  exact gram_posSemidef _

/-- Even rounding an exact singular covariance once can produce invalid centers. -/
theorem centers_not_posSemidef : ¬ (realMatrix centers).PosSemidef := by
  intro h
  have hx := h.dotProduct_mulVec_nonneg ![(-3 : ℝ),1]
  norm_num [center_values, realMatrix, dotProduct, Matrix.mulVec, Fin.sum_univ_two] at hx

theorem original_entries_still_enclosed (i j : Fin 2) :
    Encloses (rExact 1 (original i j)) (original i j) := rExact_encloses _ _

end Komorebi.PosteriorOutput.Boundary
