import KomorebiLSM.NoisySubspaceResidual

set_option autoImplicit false
namespace Komorebi.LSM.Block12Examples
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [FiniteDimensional ℝ E]

theorem zero_residual_equal_rank (P Q : Submodule ℝ E)
    (hres : ∀ x : P, (x:E) = Q.starProjection x)
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) :
    P.starProjection = Q.starProjection := by
  have h := OneSidedSubspace.projection_gap P Q 0 (by norm_num) (by norm_num)
    (by intro x; rw [← hres x]; simp) hdim
  exact sub_eq_zero.mp (norm_eq_zero.mp (le_antisymm h (norm_nonneg _)))

theorem unequal_rank_zero_one_sided :
    ∀ x : (⊥ : Submodule ℝ ℝ), ‖(x:ℝ)-(⊤ : Submodule ℝ ℝ).starProjection x‖ = 0 := by
  intro x
  simp

theorem unequal_rank_full_gap_one :
    ‖(⊥ : Submodule ℝ ℝ).starProjection-(⊤ : Submodule ℝ ℝ).starProjection‖ = 1 := by
  simp

theorem quarter_noise_gap (P Q : Submodule ℝ E)
    (hres : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ (1/2:ℝ)*‖x‖)
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) :
    ‖P.starProjection-Q.starProjection‖ ≤ (1/2:ℝ) :=
  OneSidedSubspace.projection_gap P Q (1/2) (by norm_num) (by norm_num) hres hdim

end Komorebi.LSM.Block12Examples
