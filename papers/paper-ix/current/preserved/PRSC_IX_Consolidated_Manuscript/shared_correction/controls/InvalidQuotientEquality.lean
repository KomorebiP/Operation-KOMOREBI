import SharedCorrectionControls

open Komorebi.SharedCorrection Komorebi.SharedCorrectionControls

-- EXPECTED FAILURE: the missing compatibility cannot be proved by reflexivity.
example : (Submodule.Quotient.mk (0 : Two) : Common identity identity) =
    Submodule.Quotient.mk (1 : Two) := by
  apply (quotient_mk_eq_iff_common identity identity 0 1).mpr
  exact ⟨0, rfl, rfl⟩
