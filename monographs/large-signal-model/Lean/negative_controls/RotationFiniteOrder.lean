import KomorebiLSM.RotationDensity

open Komorebi.LSM.RotationDensity

/- The exact rational rotation must not be given a positive finite period. -/
example : ∃ n : ℕ, 0<n ∧ rotation^n=1 := by
  have h : ¬ ∃ n : ℕ, 0<n ∧ rotation^n=1 := by
    rintro ⟨n,hn,hpow⟩
    exact rotation_pow_ne_one n hn hpow
  simp only [h]
