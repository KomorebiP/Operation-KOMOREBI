import KomorebiLSM.RegularPolygonAngles

open Komorebi.LSM.RegularPolygon

/- The opposite direction in a triangle has support one half, not three quarters. -/
example : ∃ j : Fin 3, (3/4:ℝ) ≤ inner ℝ (-1:ℂ) (vertex 3 j) := by
  have hu : ∀ j : Fin 3, inner ℝ (-1:ℂ) (vertex 3 j) ≤ (1/2:ℝ) := by
    intro j
    rw [vertex, inner_exp]
    simp only [norm_neg, norm_one, one_mul, Complex.arg_neg_one]
    fin_cases j
    · norm_num
    · norm_num only [Fin.isValue, Fin.val_one, Nat.cast_one, mul_one, Nat.cast_ofNat]
      rw [show 2*Real.pi/3-Real.pi = -(Real.pi/3) by ring,
        Real.cos_neg, Real.cos_pi_div_three]
    · norm_num only [Fin.isValue, Fin.val_two, Nat.cast_ofNat]
      rw [show 2*Real.pi*2/3-Real.pi = Real.pi/3 by ring, Real.cos_pi_div_three]
  have h : ¬ ∃ j : Fin 3, (3/4:ℝ) ≤ inner ℝ (-1:ℂ) (vertex 3 j) := by
    rintro ⟨j,hj⟩
    linarith [hu j]
  simp only [h]
