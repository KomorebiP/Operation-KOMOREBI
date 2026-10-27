import KomorebiLSM.GrammarAccounting

open Komorebi.LSM.GrammarAccounting

-- A value-two test violates the probability-kernel range and can amplify the tail error.
example : |predictiveEvent (posterior (fun _ : Bool => (1 : ℝ)))
      (fun g => if g then 2 else 0) -
    predictiveEvent (activePosterior {false} (fun _ : Bool => (1 : ℝ)))
      (fun g => if g then 2 else 0)| ≤ 1 / 2 := by
  norm_num [predictiveEvent, posterior, activePosterior, evidence, activeEvidence, tsum_fintype]
