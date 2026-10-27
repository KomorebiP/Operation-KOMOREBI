import KomorebiLSM.OneSidedSubspace

set_option autoImplicit false
namespace Komorebi.LSM.OneSidedSubspace
variable {E F : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [FiniteDimensional ℝ E] [NormedAddCommGroup F] [NormedSpace ℝ F]

/-- Transfer an observed tail bound to the true operator using its actual error. -/
theorem true_residual (Q : Submodule ℝ E) (X N : F →L[ℝ] E)
    (η ε : ℝ) (htail : ‖Qᗮ.starProjection.comp (X+N)‖ ≤ η)
    (hnoise : ‖N‖ ≤ ε) (u : F) :
    ‖Qᗮ.starProjection (X u)‖ ≤ (η+ε)*‖u‖ := by
  have ht := (Qᗮ.starProjection.comp (X+N)).le_opNorm u
  have hn := N.le_opNorm u
  have hp := Qᗮ.norm_starProjection_apply_le (N u)
  have he : Qᗮ.starProjection (X u) =
      Qᗮ.starProjection ((X+N) u)-Qᗮ.starProjection (N u) := by simp
  rw [he]
  calc
    _ ≤ ‖Qᗮ.starProjection ((X+N) u)‖+‖Qᗮ.starProjection (N u)‖ := norm_sub_le _ _
    _ ≤ η*‖u‖+ε*‖u‖ := add_le_add
      (ht.trans (mul_le_mul_of_nonneg_right htail (norm_nonneg u)))
      (hp.trans (hn.trans (mul_le_mul_of_nonneg_right hnoise (norm_nonneg u))))
    _ = _ := by ring

/-- A bounded right inverse on the true subspace transfers the data residual.
Its norm estimate remains an explicit premise, separate from singular values. -/
theorem residual_on_range (P Q : Submodule ℝ E) (X N : F →L[ℝ] E)
    (R : P →L[ℝ] F) (η ε κ : ℝ) (hη : 0 ≤ η) (hε : 0 ≤ ε)
    (htail : ‖Qᗮ.starProjection.comp (X+N)‖ ≤ η) (hnoise : ‖N‖ ≤ ε)
    (hR : ‖R‖ ≤ κ) (hright : ∀ x : P, X (R x) = (x:E)) (x : P) :
    ‖(x:E)-Q.starProjection x‖ ≤ ((η+ε)*κ)*‖x‖ := by
  have he : Qᗮ.starProjection (x:E) = (x:E)-Q.starProjection x :=
    eq_sub_of_add_eq' (Q.starProjection_add_starProjection_orthogonal (x:E))
  rw [← he, ← hright x]
  have h := true_residual Q X N η ε htail hnoise (R x)
  have hr := (R.le_opNorm x).trans (mul_le_mul_of_nonneg_right hR (norm_nonneg x))
  exact h.trans (by simpa [mul_assoc] using
    mul_le_mul_of_nonneg_left hr (add_nonneg hη hε))

/-- Conditional noisy-table gap: the tail and inverse estimates are inputs. -/
theorem noisy_projection_gap (P Q : Submodule ℝ E) (X N : F →L[ℝ] E)
    (R : P →L[ℝ] F) (η ε κ : ℝ) (hη : 0 ≤ η) (hε : 0 ≤ ε) (hκ : 0 ≤ κ)
    (htail : ‖Qᗮ.starProjection.comp (X+N)‖ ≤ η) (hnoise : ‖N‖ ≤ ε)
    (hR : ‖R‖ ≤ κ) (hright : ∀ x : P, X (R x) = (x:E))
    (hsmall : (η+ε)*κ < 1) (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) :
    ‖P.starProjection-Q.starProjection‖ ≤ (η+ε)*κ :=
  projection_gap P Q _ (mul_nonneg (add_nonneg hη hε) hκ) hsmall
    (residual_on_range P Q X N R η ε κ hη hε htail hnoise hR hright) hdim

/-- The manuscript's constant follows once the spectral tail and inverse bounds
are supplied; this theorem does not infer either spectral premise. -/
theorem two_epsilon_gap (P Q : Submodule ℝ E) (X N : F →L[ℝ] E)
    (R : P →L[ℝ] F) (ε s : ℝ) (hε : 0 ≤ ε) (hs : 0 < s) (hsmall : ε < s/2)
    (htail : ‖Qᗮ.starProjection.comp (X+N)‖ ≤ ε) (hnoise : ‖N‖ ≤ ε)
    (hR : ‖R‖ ≤ s⁻¹) (hright : ∀ x : P, X (R x) = (x:E))
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) :
    ‖P.starProjection-Q.starProjection‖ ≤ 2*ε/s ∧ 2*ε/s < 1 := by
  have he : (ε+ε)*s⁻¹ = 2*ε/s := by ring
  have hm : 2*ε/s < 1 := (div_lt_one hs).mpr (by linarith)
  refine ⟨?_,hm⟩
  rw [← he]
  exact noisy_projection_gap P Q X N R ε ε s⁻¹ hε hε (inv_nonneg.mpr hs.le)
    htail hnoise hR hright (by rwa [he]) hdim

end Komorebi.LSM.OneSidedSubspace
