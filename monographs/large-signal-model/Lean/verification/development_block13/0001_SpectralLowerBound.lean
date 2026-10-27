import KomorebiLSM.SubspaceCoordinates

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

/-- Ordered orthonormal eigenbasis of the actual right Gram operator. -/
noncomputable def rightBasis (A : E →ₗ[ℝ] F) :
    OrthonormalBasis (Fin (Module.finrank ℝ E)) ℝ E :=
  A.isSymmetric_adjoint_comp_self.eigenvectorBasis rfl

theorem image_inner (A : E →ₗ[ℝ] F) (x : E) (i : Fin (Module.finrank ℝ E)) :
    inner ℝ (A (rightBasis A i)) (A x) =
      A.singularValues i ^ 2 * inner ℝ (rightBasis A i) x := by
  have hg := A.isSymmetric_adjoint_comp_self.apply_eigenvectorBasis rfl i
  change A.adjoint (A (rightBasis A i)) = _ at hg
  rw [← A.adjoint_inner_left, hg]
  rw [← A.sq_singularValues_fin rfl i]
  simp

theorem image_norm_sq (A : E →ₗ[ℝ] F) (x : E) :
    ‖A x‖^2 = ∑ i : Fin (Module.finrank ℝ E),
      A.singularValues i ^ 2 * (inner ℝ (rightBasis A i) x)^2 := by
  calc
    ‖A x‖^2 = inner ℝ x (A.adjoint (A x)) := by
      rw [A.adjoint_inner_right]
      simp
    _ = ∑ i, inner ℝ x (rightBasis A i) *
        inner ℝ (rightBasis A i) (A.adjoint (A x)) :=
      ((rightBasis A).sum_inner_mul_inner x (A.adjoint (A x))).symm
    _ = _ := by
      apply Finset.sum_congr rfl
      intro i _
      rw [A.adjoint_inner_right, image_inner, real_inner_comm x]
      ring

theorem zero_mode_mem_kernel (A : E →ₗ[ℝ] F) (i : Fin (Module.finrank ℝ E))
    (hz : A.singularValues i = 0) : rightBasis A i ∈ A.ker := by
  have h := image_inner A (rightBasis A i) i
  simp [hz] at h
  exact h

theorem tail_coordinate_zero (A : E →ₗ[ℝ] F) (x : E) (hx : x ∈ A.kerᗮ)
    (i : Fin (Module.finrank ℝ E)) (hi : Module.finrank ℝ A.range ≤ i) :
    inner ℝ (rightBasis A i) x = 0 :=
  A.ker.inner_right_of_mem_orthogonal
    (zero_mode_mem_kernel A i (A.singularValues_eq_zero_iff_le_finrank_range.mpr hi)) hx

/-- The actual smallest positive singular value, at zero-based index rank−1. -/
noncomputable def leastPositive (A : E →ₗ[ℝ] F) : ℝ :=
  A.singularValues (Module.finrank ℝ A.range - 1)

theorem leastPositive_pos (A : E →ₗ[ℝ] F) (hr : 0 < Module.finrank ℝ A.range) :
    0 < leastPositive A := by
  apply A.singularValues_pos_iff_lt_finrank_range.mpr
  omega

theorem lower_on_kernel_orthogonal (A : E →ₗ[ℝ] F)
    (x : E) (hx : x ∈ A.kerᗮ) : leastPositive A * ‖x‖ ≤ ‖A x‖ := by
  have hs : 0 ≤ leastPositive A := A.singularValues_nonneg _
  have hsum : (leastPositive A)^2 * ‖x‖^2 ≤ ‖A x‖^2 := by
    rw [image_norm_sq, ← (rightBasis A).sum_sq_inner_right x, Finset.mul_sum]
    apply Finset.sum_le_sum
    intro i _
    by_cases hi : (i:ℕ) < Module.finrank ℝ A.range
    · have hle : leastPositive A ≤ A.singularValues i :=
        A.singularValues_antitone (by omega)
      exact mul_le_mul_of_nonneg_right (pow_le_pow_left₀ hs hle 2) (sq_nonneg _)
    · rw [tail_coordinate_zero A x hx i (by omega)]
      simp
  have hp : (leastPositive A * ‖x‖)^2 = (leastPositive A)^2 * ‖x‖^2 := mul_pow _ _ 2
  nlinarith [mul_nonneg hs (norm_nonneg x), norm_nonneg (A x)]

end Komorebi.LSM.Spectral
