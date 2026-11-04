import KomorebiReader.StirlingRecovery

/- Deliberately false: the two displayed profiles have the same two summaries.
This file must fail compilation with an unsolved `False` goal. -/

open Komorebi.Reader.StirlingRecovery

example : summaries genuineProfile ≠ summaries candidateProfile := by
  norm_num [summaries, genuineProfile, candidateProfile, Fin.sum_univ_succ, Nat.factorial]
