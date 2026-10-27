import KomorebiLSM.BernsteinCoefficientError
import KomorebiLSM.BaseNormModels

/-! Two positive mass-preserving constant coefficient families differ even
though the original constant density has zero approximation bias. -/
open Komorebi.LSM BernsteinCoefficientError
open scoped Matrix BigOperators
noncomputable def swap : (Fin 2 → ℝ) →L[ℝ] (Fin 2 → ℝ) :=
  (show Matrix (Fin 2) (Fin 2) ℝ from !![0,1;1,0]).mulVecLin.toContinuousLinearMap

example (z : Fin 2 → ℝ) (hz : ∀ i,0≤z i) : ∀ i,0≤swap z i := by
  intro i
  fin_cases i
  · simpa [swap,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] using hz 1
  · simpa [swap,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] using hz 0

example (z : Fin 2 → ℝ) : ∑ i,swap z i=∑ i,z i := by
  simp [swap,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
  ring

example : (∫ x,(BaseNorm.orthant (Fin 2)).value
    (combination 1 (fun _ => ContinuousLinearMap.id ℝ (Fin 2 → ℝ)) x ![1,0] -
      combination 1 (fun _ => swap) x ![1,0])∂BernsteinKernel.measure)≤0 := by
  simp only [combination_constant]
  have h : (BaseNorm.orthant (Fin 2)).value
      ((ContinuousLinearMap.id ℝ (Fin 2 → ℝ)) ![1,0]-swap ![1,0])=2 := by
    have hv : (ContinuousLinearMap.id ℝ (Fin 2 → ℝ)) ![1,0]-swap ![1,0]=![1,-1] := by
      ext i
      fin_cases i <;> norm_num [swap,Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
    rw [hv,BaseNorm.orthant_value]
    norm_num [FiniteTV.l1,Fin.sum_univ_succ]
  rw [h]
  norm_num
