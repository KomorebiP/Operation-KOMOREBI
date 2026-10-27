import KomorebiLSM.SpectralSharpness

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

/-- Span of the first `k` vectors of the ordered right Gram eigenbasis. -/
noncomputable def rightHead (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) : Submodule ℝ E :=
  Submodule.span ℝ (Set.range (fun i : Fin k => rightBasis A (Fin.castLE hk i)))

theorem rightHead_finrank (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) : Module.finrank ℝ (rightHead A k hk) = k := by
  have hi : LinearIndependent ℝ (fun i : Fin k => rightBasis A (Fin.castLE hk i)) :=
    (rightBasis A).orthonormal.linearIndependent.comp (Fin.castLE hk)
      (Fin.castLE_injective hk)
  exact (finrank_span_eq_card hi).trans (Fintype.card_fin k)

theorem basis_mem_rightHead (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (i : Fin (Module.finrank ℝ E)) (hi : (i:ℕ) < k) :
    rightBasis A i ∈ rightHead A k hk := by
  exact Submodule.subset_span ⟨⟨i,hi⟩, rfl⟩

theorem rightHead_coordinate_zero (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (x : E) (hx : x ∈ rightHead A k hk)
    (i : Fin (Module.finrank ℝ E)) (hi : k ≤ (i:ℕ)) :
    inner ℝ (rightBasis A i) x = 0 := by
  induction hx using Submodule.span_induction with
  | mem v hv =>
    obtain ⟨j,rfl⟩ := hv
    have hne : i ≠ Fin.castLE hk j := by
      intro he
      have := congrArg Fin.val he
      have := j.isLt
      simp only [Fin.val_castLE] at *
      omega
    exact (rightBasis A).orthonormal.2 hne
  | zero => simp
  | add x y hx hy ihx ihy => simp [inner_add_right, ihx, ihy]
  | smul a x hx ih => simp [inner_smul_right, ih]

theorem rightTail_coordinate_zero (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (x : E) (hx : x ∈ (rightHead A k hk)ᗮ)
    (i : Fin (Module.finrank ℝ E)) (hi : (i:ℕ) < k) :
    inner ℝ (rightBasis A i) x = 0 :=
  (rightHead A k hk).inner_right_of_mem_orthogonal (basis_mem_rightHead A k hk i hi) hx

theorem lower_on_rightHead (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (x : E) (hx : x ∈ rightHead A k hk) :
    A.singularValues (k-1) * ‖x‖ ≤ ‖A x‖ := by
  have hs := A.singularValues_nonneg (k-1)
  have hsum : A.singularValues (k-1)^2 * ‖x‖^2 ≤ ‖A x‖^2 := by
    rw [image_norm_sq, ← (rightBasis A).sum_sq_inner_right x, Finset.mul_sum]
    apply Finset.sum_le_sum
    intro i _
    by_cases hi : (i:ℕ) < k
    · have hle := A.singularValues_antitone (show (i:ℕ) ≤ k-1 by omega)
      exact mul_le_mul_of_nonneg_right (pow_le_pow_left₀ hs hle 2) (sq_nonneg _)
    · rw [rightHead_coordinate_zero A k hk x hx i (by omega)]
      simp
  nlinarith [mul_pow (A.singularValues (k-1)) ‖x‖ 2,
    mul_nonneg hs (norm_nonneg x), norm_nonneg (A x)]

theorem upper_on_rightTail (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (x : E) (hx : x ∈ (rightHead A k hk)ᗮ) :
    ‖A x‖ ≤ A.singularValues k * ‖x‖ := by
  have hs := A.singularValues_nonneg k
  have hsum : ‖A x‖^2 ≤ A.singularValues k^2 * ‖x‖^2 := by
    rw [image_norm_sq, ← (rightBasis A).sum_sq_inner_right x, Finset.mul_sum]
    apply Finset.sum_le_sum
    intro i _
    by_cases hi : (i:ℕ) < k
    · rw [rightTail_coordinate_zero A k hk x hx i hi]
      simp
    · have hle := A.singularValues_antitone (show k ≤ (i:ℕ) by omega)
      exact mul_le_mul_of_nonneg_right
        (pow_le_pow_left₀ (A.singularValues_nonneg _) hle 2) (sq_nonneg _)
  nlinarith [mul_pow (A.singularValues k) ‖x‖ 2,
    mul_nonneg hs (norm_nonneg x), norm_nonneg (A x)]

theorem basis_mem_rightTail (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (i : Fin (Module.finrank ℝ E)) (hi : k ≤ (i:ℕ)) :
    rightBasis A i ∈ (rightHead A k hk)ᗮ := by
  apply ((rightHead A k hk).mem_orthogonal' _).mpr
  intro x hx
  exact rightHead_coordinate_zero A k hk x hx i hi

end Komorebi.LSM.Spectral
