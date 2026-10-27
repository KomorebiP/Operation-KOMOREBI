import PaperICompletion8.SemisimpleExistence
set_option autoImplicit false
example (R M : Type) [Ring R] [AddCommGroup M] [Module R M] [Module.Finite R M] : True := by
  have h := Komorebi.PaperICompletion8.SemisimpleExistence.exists_semisimple_seed_formula R M
  trivial
