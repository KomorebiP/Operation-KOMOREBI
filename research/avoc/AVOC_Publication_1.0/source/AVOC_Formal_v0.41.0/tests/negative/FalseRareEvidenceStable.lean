import AVOC.BayesianInstability

open Komorebi.AVOC

example :
    let hε : 0 < (1 : ℚ) := by norm_num
    beliefL1Distance
      (conditionByWeight uniformBoolBelief (rareLikelihoodFalse 1)
        (rareLikelihoodFalse_nonneg 1 (le_of_lt hε))
        (rareLikelihoodFalse_mass_pos 1 hε))
      (conditionByWeight uniformBoolBelief (rareLikelihoodTrue 1)
        (rareLikelihoodTrue_nonneg 1 (le_of_lt hε))
        (rareLikelihoodTrue_mass_pos 1 hε)) = 0 := by
  dsimp
  have h := rare_evidence_maximal_posterior_flip (1 : ℚ) (by norm_num)
  rw [h]
