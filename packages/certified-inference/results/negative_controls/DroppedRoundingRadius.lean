import Komorebi.RationalBall
example : Komorebi.RoundedPosterior.Encloses ⟨0,0⟩ (1/1024) := by
  unfold Komorebi.RoundedPosterior.Encloses
  decide +kernel
