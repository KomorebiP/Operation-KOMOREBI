import Controls.Positive
open Komorebi.PaperIII.JetNormControls

theorem false_norm_one : ‖(⊥ : Submodule ℝ ℝ).starProjection‖ = 1 := by
  norm_num
