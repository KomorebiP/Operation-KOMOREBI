import KomorebiLSM.Block5Examples

open Komorebi.LSM.Behavior Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block5Examples

example :
    (wordAction (fun s => (reconstructed process undersized undersized s).mulVecLin)
      [((),true),((),true)] (tableState process undersized [])) 0 =
      process [((),true),((),true)] := by
  have hmass := tableState_mass process selected 0 first_test_empty [((),true),((),true)]
  rw [double_true_history_state] at hmass
  rw [← hmass]
  norm_num [wordAction,undersized_true_matrix,undersized_initial,Matrix.mulVec,dotProduct,
    Fin.sum_univ_succ]
