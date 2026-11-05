import Controls.Positive
open Komorebi.PaperIII.JetNormControls

theorem false_contractivity :
    ‖obliqueSystem.continuousProjector oblique_continuous true‖ ≤ 1 := by
  have h := oblique_norm_ge_three
  linarith
