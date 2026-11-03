import CoupledRescaling
open Komorebi.SpecialFunctions.Coupled
open Scales
example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {A B : ℂ} (he : ∀ z, s.V z = A * s.U (B * z)) (n : ℕ) :
    ((s.coefficients n).2 : ℂ) = A * ((s.coefficients n).1 : ℂ) * B ^ (2 * n) := by
  exact s.rescaling_coefficient_identity hs hstrict he n
