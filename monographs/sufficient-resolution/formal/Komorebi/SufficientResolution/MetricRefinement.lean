import Komorebi.SufficientResolution.MetricRepresentatives
import Komorebi.SufficientResolution.GlobalizationRefinement

/-!
# Refinement as a contraction of actual obstruction quotients

The compatibility space and metric stay fixed. Enlarging the realized range
induces a surjective quotient map. Its loss of norm has an exact recovered-energy
formula, evaluated on a canonical representative.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.MetricRefinement

open Globalization OrthogonalResolution HilbertGlobalization MetricObstruction
open MetricRepresentatives GlobalizationRefinement

variable {G₀ G₁ G₂ V W : Type*}
variable [AddCommGroup G₀] [Module ℝ G₀] [AddCommGroup G₁] [Module ℝ G₁]
variable [AddCommGroup G₂] [Module ℝ G₂]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A₀ : G₀ →ₗ[ℝ] V) (A₁ : G₁ →ₗ[ℝ] V) (delta : V →L[ℝ] W)

/-- The refinement map is on the old quotient types, not on invented normed proxies. -/
def refinementMap (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁) :
    ObstructionSpace A₀ delta.toLinearMap →ₗ[ℝ] ObstructionSpace A₁ delta.toLinearMap :=
  (realizationsInKernel A₀ delta.toLinearMap).mapQ
    (realizationsInKernel A₁ delta.toLinearMap) LinearMap.id (by
      intro v hv
      exact h₀₁ hv)

theorem refinementMap_class (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁) (v : delta.ker) :
    refinementMap A₀ A₁ delta h₀₁ (obstructionClass A₀ delta.toLinearMap v) =
      obstructionClass A₁ delta.toLinearMap v := rfl

theorem refinementMap_surjective (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁) :
    Function.Surjective (refinementMap A₀ A₁ delta h₀₁) := by
  intro z
  refine Submodule.Quotient.induction_on _ z ?_
  intro v
  exact ⟨obstructionClass A₀ delta.toLinearMap v, rfl⟩

theorem refinementMap_comp (A₂ : G₂ →ₗ[ℝ] V)
    (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁)
    (h₁₂ : LinearMap.range A₁ ≤ LinearMap.range A₂) :
    (refinementMap A₁ A₂ delta h₁₂).comp (refinementMap A₀ A₁ delta h₀₁) =
      refinementMap A₀ A₂ delta (h₀₁.trans h₁₂) := by
  ext v
  rfl

variable [(LinearMap.range A₀).HasOrthogonalProjection] [delta.ker.HasOrthogonalProjection]

theorem refinementMap_norm_le (h₀ : delta.toLinearMap.comp A₀ = 0)
    (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁)
    (z : ObstructionSpace A₀ delta.toLinearMap) :
    ‖refinementMap A₀ A₁ delta h₀₁ z‖ ≤ ‖z‖ := by
  let v := minimumRepresentative A₀ delta h₀ z
  have hv : obstructionClass A₀ delta.toLinearMap v = z :=
    class_minimumRepresentative A₀ delta h₀ z
  calc
    ‖refinementMap A₀ A₁ delta h₀₁ z‖ = ‖obstructionClass A₁ delta.toLinearMap v‖ := by
      rw [← hv, refinementMap_class]
    _ ≤ ‖v‖ := Submodule.Quotient.norm_mk_le _ _
    _ = ‖z‖ := minimumRepresentative_norm A₀ delta h₀ z

/-- The same algebraic map becomes a bounded contraction for the quotient norms. -/
def refinementContraction (h₀ : delta.toLinearMap.comp A₀ = 0)
    (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁) :
    ObstructionSpace A₀ delta.toLinearMap →L[ℝ] ObstructionSpace A₁ delta.toLinearMap :=
  (refinementMap A₀ A₁ delta h₀₁).mkContinuous 1 (by
    intro z
    simpa only [one_mul] using refinementMap_norm_le A₀ A₁ delta h₀ h₀₁ z)

theorem refinement_kernel (h₀ : delta.toLinearMap.comp A₀ = 0)
    (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁)
    (z : ObstructionSpace A₀ delta.toLinearMap) :
    refinementMap A₀ A₁ delta h₀₁ z = 0 ↔
      (minimumRepresentative A₀ delta h₀ z : V) ∈ LinearMap.range A₁ := by
  conv_lhs => rw [← class_minimumRepresentative A₀ delta h₀ z, refinementMap_class]
  exact obstructionClass_zero_iff A₁ delta.toLinearMap _

variable [(LinearMap.range A₁).HasOrthogonalProjection]

theorem quotient_refinement_energy (h₀ : delta.toLinearMap.comp A₀ = 0)
    (h₁ : delta.toLinearMap.comp A₁ = 0)
    (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁)
    (z : ObstructionSpace A₀ delta.toLinearMap) :
    ‖z‖^2 = ‖refinementMap A₀ A₁ delta h₀₁ z‖^2 +
      ‖obstruction (LinearMap.range A₀) (LinearMap.range A₁)
        (minimumRepresentative A₀ delta h₀ z : V)‖^2 := by
  let v := minimumRepresentative A₀ delta h₀ z
  have hc₀ := norm_class_eq_obstruction A₀ delta h₀ v
  have hv : obstructionClass A₀ delta.toLinearMap v = z :=
    class_minimumRepresentative A₀ delta h₀ z
  rw [hv] at hc₀
  have hc₁ := norm_class_eq_obstruction A₁ delta h₁ v
  have hf := refinementMap_class A₀ A₁ delta h₀₁ v
  rw [hv] at hf
  rw [← hf] at hc₁
  have he := obstruction_refinement_sq (LinearMap.range A₀) (LinearMap.range A₁)
    delta.ker h₀₁ (range_le_kernel A₁ delta h₁) (v : V)
  rw [← hc₀, ← hc₁] at he
  exact he

theorem quotient_no_loss_iff (h₀ : delta.toLinearMap.comp A₀ = 0)
    (h₁ : delta.toLinearMap.comp A₁ = 0)
    (h₀₁ : LinearMap.range A₀ ≤ LinearMap.range A₁)
    (z : ObstructionSpace A₀ delta.toLinearMap) :
    ‖refinementMap A₀ A₁ delta h₀₁ z‖ = ‖z‖ ↔
      obstruction (LinearMap.range A₀) (LinearMap.range A₁)
        (minimumRepresentative A₀ delta h₀ z : V) = 0 := by
  have he := quotient_refinement_energy A₀ A₁ delta h₀ h₁ h₀₁ z
  constructor
  · intro hn
    rw [hn] at he
    apply norm_eq_zero.mp
    nlinarith [norm_nonneg (obstruction (LinearMap.range A₀) (LinearMap.range A₁)
      (minimumRepresentative A₀ delta h₀ z : V))]
  · intro hz
    rw [hz, norm_zero, zero_pow (by decide), add_zero] at he
    nlinarith [norm_nonneg z, norm_nonneg (refinementMap A₀ A₁ delta h₀₁ z)]

end Komorebi.SufficientResolution.MetricRefinement
