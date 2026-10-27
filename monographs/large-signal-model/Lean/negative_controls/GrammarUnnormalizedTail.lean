import KomorebiLSM.GrammarAccounting

open Komorebi.LSM.GrammarAccounting

-- An omitted evidence of 1/100 is half the posterior when total evidence is 2/100.
example : totalVariation (posterior (fun _ : Bool => (1 / 100 : ℝ)))
    (activePosterior {false} (fun _ : Bool => (1 / 100 : ℝ))) ≤ 1 / 100 := by
  norm_num [totalVariation, posterior, activePosterior, evidence, activeEvidence, tsum_fintype]
