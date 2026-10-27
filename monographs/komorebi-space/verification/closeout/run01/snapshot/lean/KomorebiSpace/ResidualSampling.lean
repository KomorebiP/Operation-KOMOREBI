import KomorebiSpace.BanachBlocks
import KomorebiSpace.Profiles

set_option autoImplicit false

/-!
# Bounded-gap resampling as a continuous linear cochain map

Contractive bonds and a uniform gap bound give a bounded map on all residual
families. No converse estimate is asserted. Candidate sampling itself is
contractive and does not require a gap bound.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
open scoped NNReal ENNReal
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)
variable (hX : ∀ n, ‖X.down n‖ ≤ 1) (hY : ∀ n, ‖Y.down n‖ ≤ 1)
variable (φ : ℕ → ℕ) (hφ : Monotone φ)

/-- The sampled tower retains the actual composite bonding maps. -/
abbrev resample : BanachTower.{u,v} 𝕜 where
  Obj n := X.Obj (φ n)
  down n := restriction X (hφ (Nat.le_succ n))
  bound := 1
  down_bound n := restriction_contractive X hX (hφ (Nat.le_succ n))

@[simp] theorem resample_down (n : ℕ) :
    (resample X hX φ hφ).down n = restriction X (hφ (Nat.le_succ n)) := rfl

def sampleLinear : Candidates X Y →ₗ[𝕜]
    Candidates (resample X hX φ hφ) (resample Y hY φ hφ) where
  toFun f := ⟨fun n => f (φ n), memℓp_infty ⟨‖f‖, by
    rintro _ ⟨n, rfl⟩
    exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (φ n)⟩⟩
  map_add' f g := by apply lp.ext; rfl
  map_smul' c f := by apply lp.ext; rfl

theorem sampleLinear_bound (f : Candidates X Y) :
    ‖sampleLinear X Y hX hY φ hφ f‖ ≤ ‖f‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg f)
  intro n
  exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (φ n)

def sampleCLM : Candidates X Y →L[𝕜]
    Candidates (resample X hX φ hφ) (resample Y hY φ hφ) :=
  (sampleLinear X Y hX hY φ hφ).mkContinuous 1
    (fun f => by simpa using sampleLinear_bound X Y hX hY φ hφ f)

@[simp] theorem sampleCLM_apply (f : Candidates X Y) (n : ℕ) :
    sampleCLM X Y hX hY φ hφ f n = f (φ n) := rfl

theorem sampleCLM_bound (f : Candidates X Y) :
    ‖sampleCLM X Y hX hY φ hφ f‖ ≤ ‖f‖ := sampleLinear_bound X Y hX hY φ hφ f

theorem sampleCLM_opNorm : ‖sampleCLM X Y hX hY φ hφ‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ (by norm_num)
  intro f
  simpa using sampleCLM_bound X Y hX hY φ hφ f

/-- This identity is available even without bounded gaps. -/
theorem sampled_differential_coordinate (f : Candidates X Y) (n : ℕ) :
    differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (sampleCLM X Y hX hY φ hφ f) n =
      blockDefect X Y f (hφ (Nat.le_succ n)) := rfl

variable (M : ℕ) (hgap : ∀ n, φ (n+1) - φ n ≤ M)

def residualSampleLinear : Residuals X Y →ₗ[𝕜]
    Residuals (resample X hX φ hφ) (resample Y hY φ hφ) where
  toFun r := ⟨fun n => blockSum X Y r (hφ (Nat.le_succ n)), memℓp_infty ⟨(M : ℝ)*‖r‖, by
    rintro _ ⟨n, rfl⟩
    exact (blockSum_uniform_bound X Y hX hY r (hφ (Nat.le_succ n))).trans
      (mul_le_mul_of_nonneg_right (by exact_mod_cast hgap n) (norm_nonneg r))⟩⟩
  map_add' r s := by
    apply lp.ext
    funext n
    exact blockSum_add X Y r s (hφ (Nat.le_succ n))
  map_smul' c r := by
    apply lp.ext
    funext n
    exact blockSum_smul X Y c r (hφ (Nat.le_succ n))

theorem residualSampleLinear_bound (r : Residuals X Y) :
    ‖residualSampleLinear X Y hX hY φ hφ M hgap r‖ ≤ (M : ℝ)*‖r‖ := by
  apply lp.norm_le_of_forall_le (by positivity)
  intro n
  exact (blockSum_uniform_bound X Y hX hY r (hφ (Nat.le_succ n))).trans
    (mul_le_mul_of_nonneg_right (by exact_mod_cast hgap n) (norm_nonneg r))

/-- Actual bounded block-accumulation operator, not a sampled scalar error profile. -/
def residualSampleCLM : Residuals X Y →L[𝕜]
    Residuals (resample X hX φ hφ) (resample Y hY φ hφ) :=
  (residualSampleLinear X Y hX hY φ hφ M hgap).mkContinuous (M : ℝ)
    (residualSampleLinear_bound X Y hX hY φ hφ M hgap)

@[simp] theorem residualSampleCLM_apply (r : Residuals X Y) (n : ℕ) :
    residualSampleCLM X Y hX hY φ hφ M hgap r n =
      blockSum X Y r (hφ (Nat.le_succ n)) := rfl

theorem residualSampleCLM_bound (r : Residuals X Y) :
    ‖residualSampleCLM X Y hX hY φ hφ M hgap r‖ ≤ (M : ℝ)*‖r‖ :=
  residualSampleLinear_bound X Y hX hY φ hφ M hgap r

theorem residualSampleCLM_opNorm :
    ‖residualSampleCLM X Y hX hY φ hφ M hgap‖ ≤ (M : ℝ) :=
  ContinuousLinearMap.opNorm_le_bound _ (by positivity)
    (residualSampleCLM_bound X Y hX hY φ hφ M hgap)

/-- The central commuting square, with both operators already constructed. -/
theorem resampling_chain (f : Candidates X Y) :
    differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (sampleCLM X Y hX hY φ hφ f) =
      residualSampleCLM X Y hX hY φ hφ M hgap (differential X Y f) := by
  apply lp.ext
  funext n
  exact (blockSum_differential X Y f (hφ (Nat.le_succ n))).symm

include hgap in
theorem sampled_residual_bound (f : Candidates X Y) :
    ‖differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (sampleCLM X Y hX hY φ hφ f)‖ ≤ (M : ℝ)*‖differential X Y f‖ := by
  rw [resampling_chain X Y hX hY φ hφ M hgap]
  exact residualSampleCLM_bound X Y hX hY φ hφ M hgap _

/-- Exactness is preserved by any monotone common resampling, even with unbounded gaps. -/
theorem sample_exact (f : Candidates X Y) (hf : Exact X Y f) :
    Exact (resample X hX φ hφ) (resample Y hY φ hφ) (sampleCLM X Y hX hY φ hφ f) := by
  intro n
  apply ContinuousLinearMap.ext
  intro x
  change restriction Y (hφ (Nat.le_succ n)) (f (φ (n+1)) x) =
    f (φ n) (restriction X (hφ (Nat.le_succ n)) x)
  rw [restriction_underlying Y, restriction_underlying X]
  exact Resolution.Adjacent.map_all (fun n => f n)
    (fun k y => congrArg (fun T : X.Obj (k+1) →L[𝕜] Y.Obj k => T y) (hf k))
    (hφ (Nat.le_succ n)) x

include hgap in
/-- Vanishing residual in candidate-sequence norm survives bounded-gap resampling. -/
theorem sampled_residual_tendsto_zero (f : ℕ → Candidates X Y)
    (hf : Filter.Tendsto (fun k => differential X Y (f k)) Filter.atTop (nhds 0)) :
    Filter.Tendsto (fun k => differential (resample X hX φ hφ) (resample Y hY φ hφ)
      (sampleCLM X Y hX hY φ hφ (f k))) Filter.atTop (nhds 0) := by
  have h := (residualSampleCLM X Y hX hY φ hφ M hgap).continuous.tendsto (0 : Residuals X Y)
  have hc := h.comp hf
  simpa only [map_zero, Function.comp_def, ← resampling_chain X Y hX hY φ hφ M hgap] using hc

end BanachTower
end KomorebiSpace
end
