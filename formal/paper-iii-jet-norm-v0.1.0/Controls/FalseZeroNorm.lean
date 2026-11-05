import Controls.Positive
open Komorebi.PaperIII.JetNormControls

theorem false_zero_norm :
    ‖(ContinuousMultilinearMap.constOfIsEmpty ℝ (fun (_ : Fin 0) => ℝ) (1 : ℝ))‖ ≤ 0 := by
  norm_num
