import KomorebiLSM.SpectralTail

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

theorem exists_nonzero_intersection (P Q : Submodule ℝ E)
    (hdim : Module.finrank ℝ E < Module.finrank ℝ P + Module.finrank ℝ Q) :
    ∃ x : E, x ≠ 0 ∧ x ∈ P ∧ x ∈ Q := by
  by_contra h
  have hd : Disjoint P Q := Submodule.disjoint_def.mpr (by
    intro x hx hy
    by_contra hn
    exact h ⟨x,hn,hx,hy⟩)
  have hl := Submodule.finrank_add_finrank_le_of_disjoint hd
  omega

/-- Every ordered singular value changes by at most the operator perturbation.
This proof uses spectral subspaces and dimension intersection directly. -/
theorem singularValue_le_add_norm (A B : E →L[ℝ] F) (k : ℕ) :
    A.toLinearMap.singularValues k ≤ B.toLinearMap.singularValues k + ‖A-B‖ := by
  by_cases hk : k < Module.finrank ℝ E
  · let P := rightHead A.toLinearMap (k+1) (by omega)
    let Q := (rightHead B.toLinearMap k (by omega))ᗮ
    have hp : Module.finrank ℝ P = k+1 := rightHead_finrank _ _ _
    have hq : k + Module.finrank ℝ Q = Module.finrank ℝ E := by
      have h := (rightHead B.toLinearMap k (show k ≤ Module.finrank ℝ E by omega)).finrank_add_finrank_orthogonal
      rwa [rightHead_finrank] at h
    obtain ⟨x,hx,hpx,hqx⟩ := exists_nonzero_intersection P Q (by omega)
    have hl := lower_on_rightHead A.toLinearMap (k+1) (by omega) x hpx
    simp only [Nat.add_sub_cancel] at hl
    have hu := upper_on_rightTail B.toLinearMap k (by omega) x hqx
    have hn := (A-B).le_opNorm x
    have ht : ‖A x‖ ≤ ‖B x‖ + ‖(A-B) x‖ := by
      have he : A x = B x + (A-B) x := by rw [sub_apply]; abel
      rw [he]
      exact norm_add_le _ _
    have hxpos : 0 < ‖x‖ := norm_pos_iff.mpr hx
    change A.toLinearMap.singularValues k * ‖x‖ ≤ ‖A x‖ at hl
    change ‖B x‖ ≤ B.toLinearMap.singularValues k * ‖x‖ at hu
    have hm : A.toLinearMap.singularValues k * ‖x‖ ≤
        (B.toLinearMap.singularValues k + ‖A-B‖) * ‖x‖ := by nlinarith
    exact (mul_le_mul_iff_left₀ hxpos).mp hm
  · have hz : A.toLinearMap.singularValues k = 0 :=
      A.toLinearMap.singularValues_eq_zero_iff_le_finrank_range.mpr
        ((LinearMap.finrank_range_le A.toLinearMap).trans (by omega))
    rw [hz]
    exact add_nonneg (B.toLinearMap.singularValues_nonneg k) (norm_nonneg _)

theorem singularValue_abs_sub_le (A B : E →L[ℝ] F) (k : ℕ) :
    |A.toLinearMap.singularValues k - B.toLinearMap.singularValues k| ≤ ‖A-B‖ := by
  have h₁ := singularValue_le_add_norm A B k
  have h₂ := singularValue_le_add_norm B A k
  rw [norm_sub_rev B A] at h₂
  exact abs_le.mpr ⟨by linarith, by linarith⟩

theorem noisy_singular_lower (X N : E →L[ℝ] F) (ε : ℝ) (hnoise : ‖N‖ ≤ ε)
    (k : ℕ) : X.toLinearMap.singularValues k - ε ≤
      (X+N).toLinearMap.singularValues k := by
  have h := singularValue_le_add_norm X (X+N) k
  have hn : ‖X-(X+N)‖ = ‖N‖ := by simp
  rw [hn] at h
  linarith

theorem noisy_singular_upper (X N : E →L[ℝ] F) (ε : ℝ) (hnoise : ‖N‖ ≤ ε)
    (k : ℕ) : (X+N).toLinearMap.singularValues k ≤
      X.toLinearMap.singularValues k + ε := by
  have h := singularValue_le_add_norm (X+N) X k
  have hn : ‖X+N-X‖ = ‖N‖ := by simp
  rw [hn] at h
  linarith

theorem noisy_tail_at_rank (X N : E →L[ℝ] F) (ε : ℝ) (hnoise : ‖N‖ ≤ ε) :
    (X+N).toLinearMap.singularValues (Module.finrank ℝ X.toLinearMap.range) ≤ ε := by
  have h := noisy_singular_upper X N ε hnoise (Module.finrank ℝ X.toLinearMap.range)
  rw [X.toLinearMap.singularValues_finrank_range_self, zero_add] at h
  exact h

end Komorebi.LSM.Spectral
