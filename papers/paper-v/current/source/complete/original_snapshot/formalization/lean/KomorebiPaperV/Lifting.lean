import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.LinearAlgebra.Matrix.Notation
import Mathlib.Tactic

/-!
Author: Komorebi P.
Checked source. Exact pair and coordinatewise lifting.
The normalized Haar transform and its l2 energy theorem are separate obligations.
-/

namespace KomorebiPaperV
section Lifting
variable {K : Type*} [Field K] [CharZero K]

def liftingAnalysis (x : K × K) : K × K :=
  (x.1 + (x.2 - x.1) / 2, x.2 - x.1)

def liftingSynthesis (y : K × K) : K × K :=
  (y.1 - y.2 / 2, y.2 + (y.1 - y.2 / 2))

theorem lifting_synthesis_analysis (x : K × K) :
    liftingSynthesis (liftingAnalysis x) = x := by
  apply Prod.ext <;> dsimp [liftingAnalysis, liftingSynthesis] <;> ring

theorem lifting_analysis_synthesis (y : K × K) :
    liftingAnalysis (liftingSynthesis y) = y := by
  apply Prod.ext <;> dsimp [liftingAnalysis, liftingSynthesis] <;> ring

theorem lifting_determinant :
    Matrix.det (!![(1 / 2 : K), 1 / 2; -1, 1]) = 1 := by
  norm_num [Matrix.det_fin_two]

def liftingEquiv : (K × K) ≃ (K × K) where
  toFun := liftingAnalysis
  invFun := liftingSynthesis
  left_inv := lifting_synthesis_analysis
  right_inv := lifting_analysis_synthesis

theorem lifting_coordinates_roundtrip {I : Type*} (x : I → K × K) :
    (fun i => liftingSynthesis (liftingAnalysis (x i))) = x := by
  funext i
  exact lifting_synthesis_analysis (x i)
end Lifting
end KomorebiPaperV
