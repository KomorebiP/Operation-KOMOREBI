import KomorebiSpace.BanachReindexing
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# Cofinal schedule invariance is not sup-norm invariance

An actual exact transport on constant real Banach stages has level maps 2^(-n) id.
Sampling n+1 is cofinal but changes its candidate sup norm from 1 to 1/2.
Both bonding maps are surjective. The phenomenon is not an empty-limit artifact.
-/

noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace ScheduleNormObstruction
open BanachTower

abbrev source : BanachTower ℝ where
  Obj _ := ℝ
  down _ := (1/2 : ℝ) • ContinuousLinearMap.id ℝ ℝ
  bound := 1/2
  down_bound _ := by norm_num [norm_smul, ContinuousLinearMap.norm_id]

abbrev target : BanachTower ℝ where
  Obj _ := ℝ
  down _ := ContinuousLinearMap.id ℝ ℝ
  bound := 1
  down_bound _ := ContinuousLinearMap.norm_id_le

def levelMap (n : ℕ) : ℝ →L[ℝ] ℝ :=
  ((1/2 : ℝ)^n) • ContinuousLinearMap.id ℝ ℝ

@[simp] theorem levelMap_norm (n : ℕ) : ‖levelMap n‖ = (1/2 : ℝ)^n := by
  rw [levelMap, norm_smul, ContinuousLinearMap.norm_id, mul_one]
  exact Real.norm_of_nonneg (pow_nonneg (by norm_num) n)

theorem levelMap_bound (n : ℕ) : ‖levelMap n‖ ≤ 1 := by
  rw [levelMap_norm]
  exact pow_le_one₀ (by norm_num) (by norm_num)

def geometricCandidate : Candidates source target :=
  ⟨levelMap, memℓp_infty ⟨1, by
    rintro _ ⟨n, rfl⟩
    exact levelMap_bound n⟩⟩

theorem geometricCandidate_exact : Exact source target geometricCandidate := by
  intro n
  apply ContinuousLinearMap.ext
  intro x
  change (1/2 : ℝ)^(n+1) * x = (1/2 : ℝ)^n * ((1/2 : ℝ) * x)
  rw [pow_succ, mul_assoc]

theorem geometricCandidate_norm : ‖geometricCandidate‖ = 1 := by
  apply le_antisymm
  · exact lp.norm_le_of_forall_le (by norm_num) levelMap_bound
  · have h := lp.norm_apply_le_norm ENNReal.top_ne_zero geometricCandidate 0
    change ‖levelMap 0‖ ≤ ‖geometricCandidate‖ at h
    simpa only [levelMap_norm, pow_zero] using h

def sampledCandidate : Candidates source target := (1/2 : ℝ) • geometricCandidate

/-- This is exactly the levelwise subsequence, not an unrelated rescaling. -/
theorem sampledCandidate_coordinate (n : ℕ) :
    sampledCandidate n = geometricCandidate (n+1) := by
  apply ContinuousLinearMap.ext
  intro x
  change (1/2 : ℝ) * ((1/2 : ℝ)^n * x) = (1/2 : ℝ)^(n+1) * x
  rw [pow_succ]
  ring

theorem sampledCandidate_exact : Exact source target sampledCandidate := by
  intro n
  rw [sampledCandidate_coordinate, sampledCandidate_coordinate]
  exact geometricCandidate_exact (n+1)

theorem sampledCandidate_norm : ‖sampledCandidate‖ = (1/2 : ℝ) := by
  rw [sampledCandidate, norm_smul, geometricCandidate_norm]
  norm_num

theorem cofinal_sampling_changes_norm :
    ‖geometricCandidate‖ ≠ ‖sampledCandidate‖ := by
  rw [geometricCandidate_norm, sampledCandidate_norm]
  norm_num

theorem source_down_surjective (n : ℕ) : Function.Surjective (source.down n) := by
  intro x
  refine ⟨2*x, ?_⟩
  change (1/2 : ℝ) * (2*x) = x
  ring

theorem target_down_surjective (n : ℕ) : Function.Surjective (target.down n) := by
  intro x
  exact ⟨x, rfl⟩

end ScheduleNormObstruction
end KomorebiSpace
end
