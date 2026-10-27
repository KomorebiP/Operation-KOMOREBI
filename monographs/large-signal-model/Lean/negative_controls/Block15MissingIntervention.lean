import KomorebiLSM.MissingIntervention

open Komorebi.LSM.MissingIntervention

-- Passive agreement must not be accepted as unrestricted agreement.
example : process false [(true, false)] = process true [(true, false)] := by
  rw [intervention_disagreement.1, intervention_disagreement.2]
  norm_num
