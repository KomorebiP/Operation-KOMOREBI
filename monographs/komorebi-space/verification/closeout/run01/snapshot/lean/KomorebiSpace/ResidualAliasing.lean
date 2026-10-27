import KomorebiSpace.ResidualSampling
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# Residual aliasing and the sharp dependence on block length

Even sampling hides a nonzero alternating fine defect in an actual bounded
candidate. Separately, the block-accumulation operator has norm exactly M on
identity real towers sampled every M stages. These are all-level Lean proofs.
-/
noncomputable section
namespace KomorebiSpace
namespace ResidualAliasing
open BanachTower
open scoped NNReal ENNReal

abbrev scalar : BanachTower ℝ where
  Obj _ := ℝ
  down _ := ContinuousLinearMap.id ℝ ℝ
  bound := 1
  down_bound _ := ContinuousLinearMap.norm_id_le

theorem scalar_contractive (n : ℕ) : ‖scalar.down n‖ ≤ 1 :=
  ContinuousLinearMap.norm_id_le

@[simp] theorem scalar_restriction {i j : ℕ} (h : i ≤ j) :
    restriction scalar h = ContinuousLinearMap.id ℝ ℝ := by
  induction j, h using Nat.le_induction with
  | base => simp
  | succ j hj ih =>
    rw [restriction_succ scalar hj, ih]
    apply ContinuousLinearMap.ext
    intro x
    rfl

def stride (m n : ℕ) : ℕ := m*n

theorem stride_monotone (m : ℕ) : Monotone (stride m) :=
  fun _ _ h => Nat.mul_le_mul_left m h

@[simp] theorem stride_gap (m n : ℕ) : stride m (n+1) - stride m n = m := by
  simp [stride, Nat.mul_add]

theorem stride_cofinal (m : ℕ) (hm : 0 < m) : Resolution.UnboundedSchedule (stride m) := by
  intro n
  refine ⟨n, ?_⟩
  change n ≤ m*n
  nlinarith

abbrev sampled (m : ℕ) := resample scalar scalar_contractive (stride m) (stride_monotone m)

abbrev sample (m : ℕ) := sampleCLM scalar scalar scalar_contractive scalar_contractive
  (stride m) (stride_monotone m)

abbrev coarsen (m : ℕ) := residualSampleCLM scalar scalar scalar_contractive scalar_contractive
  (stride m) (stride_monotone m) m (fun n => (stride_gap m n).le)

@[simp] theorem sampled_down (m n : ℕ) :
    (sampled m).down n = ContinuousLinearMap.id ℝ ℝ := scalar_restriction _

/-- The candidate alternates between the identity and twice the identity. -/
def level (n : ℕ) : ℝ →L[ℝ] ℝ :=
  (1 + Profiles.alternating n) • ContinuousLinearMap.id ℝ ℝ

theorem level_bound (n : ℕ) : ‖level n‖ ≤ 2 := by
  unfold level Profiles.alternating
  split_ifs <;> norm_num [norm_smul, ContinuousLinearMap.norm_id]

def candidate : Candidates scalar scalar :=
  ⟨level, memℓp_infty ⟨2, by rintro _ ⟨n, rfl⟩; exact level_bound n⟩⟩

@[simp] theorem candidate_even (n : ℕ) : candidate (2*n) = ContinuousLinearMap.id ℝ ℝ := by
  change level (2*n) = _
  simp [level]

@[simp] theorem candidate_odd (n : ℕ) : candidate (2*n+1) = (2 : ℝ) • ContinuousLinearMap.id ℝ ℝ := by
  change level (2*n+1) = _
  norm_num [level]

@[simp] theorem fine_defect_even (n : ℕ) :
    differential scalar scalar candidate (2*n) = ContinuousLinearMap.id ℝ ℝ := by
  rw [differential_apply, candidate_even, candidate_odd]
  apply ContinuousLinearMap.ext
  intro x
  change 2*x-x=x
  ring

@[simp] theorem fine_defect_odd (n : ℕ) :
    differential scalar scalar candidate (2*n+1) = -ContinuousLinearMap.id ℝ ℝ := by
  rw [differential_apply, show 2*n+1+1=2*(n+1) by omega, candidate_even, candidate_odd]
  apply ContinuousLinearMap.ext
  intro x
  change x-2*x = -x
  ring

theorem fine_residual_norm : ‖differential scalar scalar candidate‖ = 1 := by
  apply le_antisymm
  · apply lp.norm_le_of_forall_le (by norm_num)
    intro n
    have hn : n = 2*(n/2) ∨ n = 2*(n/2)+1 := by omega
    rcases hn with h | h
    · rw [h, fine_defect_even]
      exact ContinuousLinearMap.norm_id_le
    · rw [h, fine_defect_odd, norm_neg]
      exact ContinuousLinearMap.norm_id_le
  · have h := lp.norm_apply_le_norm ENNReal.top_ne_zero (differential scalar scalar candidate) (2*0)
    rw [fine_defect_even, ContinuousLinearMap.norm_id] at h
    exact h

@[simp] theorem sampled_candidate (n : ℕ) :
    sample 2 candidate n = ContinuousLinearMap.id ℝ ℝ := candidate_even n

theorem sampled_candidate_exact : Exact (sampled 2) (sampled 2) (sample 2 candidate) := by
  intro n
  simp [stride]

theorem sampled_residual_zero :
    differential (sampled 2) (sampled 2) (sample 2 candidate) = 0 :=
  (exact_iff_differential_zero _ _ _).mp sampled_candidate_exact

theorem candidate_not_exact : ¬ Exact scalar scalar candidate := by
  intro h
  have hz := (exact_iff_differential_zero _ _ _).mp h
  have hn := fine_residual_norm
  rw [hz, norm_zero] at hn
  norm_num at hn

/-- A coarse exact candidate with nonzero seed hides fine incompatibility. -/
theorem coarsening_hides_nonzero_residual :
    ¬ Exact scalar scalar candidate ∧
    Exact (sampled 2) (sampled 2) (sample 2 candidate) ∧
    sample 2 candidate 0 1 = 1 :=
  ⟨candidate_not_exact, sampled_candidate_exact, by rw [sampled_candidate]; rfl⟩

theorem coarsen_not_injective : ¬ Function.Injective (coarsen 2) := by
  intro hi
  have hc : coarsen 2 (differential scalar scalar candidate) = coarsen 2 0 := by
    rw [map_zero]
    exact (resampling_chain scalar scalar scalar_contractive scalar_contractive
      (stride 2) (stride_monotone 2) 2 (fun n => (stride_gap 2 n).le) candidate).symm.trans
      sampled_residual_zero
  have hz := hi hc
  have hn := fine_residual_norm
  rw [hz, norm_zero] at hn
  norm_num at hn

/-- No positive lower comparison bound is possible, even on residuals of actual candidates. -/
theorem no_positive_reverse_bound (c : ℝ) (hc : 0 < c) :
    ¬ (∀ f : Candidates scalar scalar, c*‖differential scalar scalar f‖ ≤
      ‖differential (sampled 2) (sampled 2) (sample 2 f)‖) := by
  intro h
  have he := h candidate
  rw [fine_residual_norm, sampled_residual_zero, norm_zero, mul_one] at he
  exact (not_le_of_gt hc) he

/-- Test input for the norm of the block map; it is not claimed to be a fine defect. -/
def unitResidual : Residuals scalar scalar :=
  ⟨fun _ => ContinuousLinearMap.id ℝ ℝ, memℓp_infty ⟨1, by
    rintro _ ⟨n, rfl⟩
    exact ContinuousLinearMap.norm_id_le⟩⟩

theorem unitResidual_norm : ‖unitResidual‖ = 1 := by
  apply le_antisymm
  · apply lp.norm_le_of_forall_le (by norm_num)
    intro n
    exact ContinuousLinearMap.norm_id_le
  · have h := lp.norm_apply_le_norm ENNReal.top_ne_zero unitResidual 0
    change ‖ContinuousLinearMap.id ℝ ℝ‖ ≤ ‖unitResidual‖ at h
    simpa using h

theorem blockSum_unit {i j : ℕ} (h : i ≤ j) :
    blockSum scalar scalar unitResidual h = ((j-i : ℕ) : ℝ) • ContinuousLinearMap.id ℝ ℝ := by
  induction j, h using Nat.le_induction with
  | base => simp
  | succ j hj ih =>
    rw [blockSum_succ scalar scalar unitResidual hj, scalar_restriction, ih]
    have hs : j+1-i = (j-i)+1 := by omega
    rw [hs, Nat.cast_add, Nat.cast_one]
    apply ContinuousLinearMap.ext
    intro x
    change x + (↑(j-i) * x) = (↑(j-i)+1)*x
    ring

@[simp] theorem coarsen_unit_coordinate (m n : ℕ) :
    coarsen m unitResidual n = (m : ℝ) • ContinuousLinearMap.id ℝ ℝ := by
  change blockSum scalar scalar unitResidual (stride_monotone m (Nat.le_succ n)) = _
  rw [blockSum_unit, stride_gap]

theorem coarsen_unit_norm (m : ℕ) : ‖coarsen m unitResidual‖ = (m : ℝ) := by
  apply le_antisymm
  · have h := residualSampleCLM_bound scalar scalar scalar_contractive scalar_contractive
      (stride m) (stride_monotone m) m (fun n => (stride_gap m n).le) unitResidual
    simpa [unitResidual_norm] using h
  · have h := lp.norm_apply_le_norm ENNReal.top_ne_zero (coarsen m unitResidual) 0
    rw [coarsen_unit_coordinate] at h
    simpa [norm_smul, ContinuousLinearMap.norm_id, Real.norm_of_nonneg (Nat.cast_nonneg m)] using h

/-- The M factor is sharp for maps on all residual families. -/
theorem coarsen_opNorm (m : ℕ) : ‖coarsen m‖ = (m : ℝ) := by
  apply le_antisymm
  · exact residualSampleCLM_opNorm scalar scalar scalar_contractive scalar_contractive
      (stride m) (stride_monotone m) m (fun n => (stride_gap m n).le)
  · have h := (coarsen m).le_opNorm unitResidual
    simpa [unitResidual_norm, coarsen_unit_norm] using h

end ResidualAliasing
end KomorebiSpace
end
