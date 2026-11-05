import Controls.Positive
open Komorebi.PaperIII.JetNormControls

theorem false_nullary : (nullaryJet (fun k : Fin 0 => k.elim0) : ℝ) = 0 := by
  rw [nullary_value]
  norm_num
