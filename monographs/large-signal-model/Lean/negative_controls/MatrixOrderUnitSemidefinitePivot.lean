import KomorebiLSM.MatrixOrderUnit

/-! Rejected control: the zero positive-semidefinite pivot cannot dominate
the identity. Positive definiteness in the order-unit theorem is essential. -/

example : ∃ a : ℝ,
    (a • (0 : Matrix (Fin 1) (Fin 1) ℝ)-(1 : Matrix (Fin 1) (Fin 1) ℝ)).PosSemidef := by
  have h : ¬ ∃ a : ℝ,
      (a • (0 : Matrix (Fin 1) (Fin 1) ℝ)-(1 : Matrix (Fin 1) (Fin 1) ℝ)).PosSemidef := by
    rintro ⟨a,ha⟩
    have hd := ha.diag_nonneg (i:=0)
    norm_num at hd
  rw [iff_false_intro h]
