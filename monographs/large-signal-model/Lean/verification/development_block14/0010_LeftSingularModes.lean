import KomorebiLSM.SpectralTail

set_option autoImplicit false
namespace Komorebi.LSM.Spectral
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [NormedAddCommGroup F] [InnerProductSpace ℝ F]
variable [FiniteDimensional ℝ E] [FiniteDimensional ℝ F]

/-- Normalized image of a right singular mode; used only at positive singular values. -/
noncomputable def leftMode (A : E →ₗ[ℝ] F) (i : Fin (Module.finrank ℝ E)) : F :=
  (A.singularValues i)⁻¹ • A (rightBasis A i)

theorem singular_smul_leftMode (A : E →ₗ[ℝ] F) (i : Fin (Module.finrank ℝ E))
    (hi : 0 < A.singularValues i) :
    A.singularValues i • leftMode A i = A (rightBasis A i) := by
  simp [leftMode, smul_smul, ne_of_gt hi]

theorem leftMode_leftGram (A : E →ₗ[ℝ] F) (i : Fin (Module.finrank ℝ E)) :
    (A.comp A.adjoint) (leftMode A i) = A.singularValues i^2 • leftMode A i := by
  have hg := A.isSymmetric_adjoint_comp_self.apply_eigenvectorBasis rfl i
  change A.adjoint (A (rightBasis A i)) = _ at hg
  rw [← A.sq_singularValues_fin rfl i] at hg
  simp only [leftMode, LinearMap.comp_apply, map_smul, hg]
  rw [smul_comm]

theorem leftModes_orthonormal (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (hr : k ≤ Module.finrank ℝ A.range) :
    Orthonormal ℝ (fun i : Fin k => leftMode A (Fin.castLE hk i)) := by
  rw [orthonormal_iff_ite]
  intro i j
  have hi : A.singularValues (Fin.castLE hk i) ≠ 0 := ne_of_gt
    (A.singularValues_pos_iff_lt_finrank_range.mpr (lt_of_lt_of_le i.isLt hr))
  simp only [leftMode, inner_smul_left, inner_smul_right, conj_trivial,
    image_inner, (rightBasis A).inner_eq_ite]
  by_cases hij : i = j
  · subst j
    simp [hi]
    field_simp
  · have hne : Fin.castLE hk i ≠ Fin.castLE hk j :=
      fun h => hij (Fin.castLE_injective hk h)
    simp [hij, hne]

/-- The constructed subspace is precisely the span of an orthonormal family of
left Gram eigenvectors with the first `k` ordered singular values. -/
theorem leadingLeft_eq_span_leftModes (A : E →ₗ[ℝ] F) (k : ℕ)
    (hk : k ≤ Module.finrank ℝ E) (hr : k ≤ Module.finrank ℝ A.range) :
    leadingLeft A k hk = Submodule.span ℝ
      (Set.range (fun i : Fin k => leftMode A (Fin.castLE hk i))) := by
  apply le_antisymm
  · rintro y ⟨x,hx,rfl⟩
    induction hx using Submodule.span_induction with
    | mem x hx =>
      obtain ⟨i,rfl⟩ := hx
      rw [← singular_smul_leftMode A _
        (A.singularValues_pos_iff_lt_finrank_range.mpr (lt_of_lt_of_le i.isLt hr))]
      exact Submodule.smul_mem _ _ (Submodule.subset_span ⟨i,rfl⟩)
    | zero => simp
    | add x y hx hy ihx ihy => simpa using Submodule.add_mem _ ihx ihy
    | smul a x hx ih => simpa using Submodule.smul_mem _ a ih
  · apply Submodule.span_le.mpr
    rintro _ ⟨i,rfl⟩
    exact (leadingLeft A k hk).smul_mem _
      ⟨_,basis_mem_rightHead A k hk _ i.isLt,rfl⟩

end Komorebi.LSM.Spectral
