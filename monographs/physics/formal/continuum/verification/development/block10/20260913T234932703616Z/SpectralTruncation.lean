module
public import KomorebiPhysics.BoundedSpectral

/-! Exact cutoffs and tail anchors. Strong convergence is proved for every
bounded symbol; norm convergence is characterized by its actual scalar tail. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralTruncation
open BoundedSpectral Filter
open scoped Topology BigOperators lp

/-- Keep the first M entries and set all others to zero. -/
def truncate (a : Symbol) (M : ℕ) : Symbol :=
  ofBound (fun n => if n < M then a n else 0) ‖a‖ (fun n => by
    split_ifs
    · exact lp.norm_apply_le_norm ENNReal.top_ne_zero a n
    · simpa using norm_nonneg a)

theorem truncate_apply (a : Symbol) (M n : ℕ) :
    truncate a M n = if n < M then a n else 0 := rfl

/-- Keep the true low spectrum and a specified scalar tail value. -/
def anchored (a : Symbol) (c : ℂ) (M : ℕ) : Symbol :=
  truncate a M + c • (1 - truncate 1 M)

theorem anchored_apply (a : Symbol) (c : ℂ) (M n : ℕ) :
    anchored a c M n = if n < M then a n else c := by
  change (if n < M then a n else 0) + c * (1 - if n < M then 1 else 0) = _
  split_ifs <;> ring

theorem anchored_zero (a : Symbol) (M : ℕ) : anchored a 0 M = truncate a M := by
  simp [anchored]

/-- The actual coordinate cutoff operator. -/
def cutoff (M : ℕ) : Space →L[ℂ] Space := diagonal (truncate 1 M)

theorem cutoff_apply (M : ℕ) (x : Space) (n : ℕ) :
    cutoff M x n = if n < M then x n else 0 := by
  simp [cutoff, diagonal_apply, truncate_apply]

theorem cutoff_idempotent (M : ℕ) : (cutoff M).comp (cutoff M) = cutoff M := by
  ext x n
  simp only [ContinuousLinearMap.comp_apply, cutoff_apply]
  split_ifs <;> rfl

theorem truncate_sandwich (a : Symbol) (M : ℕ) :
    diagonal (truncate a M) = (cutoff M).comp ((diagonal a).comp (cutoff M)) := by
  ext x n
  simp only [diagonal_apply, truncate_apply, ContinuousLinearMap.comp_apply, cutoff_apply]
  split_ifs <;> simp

theorem anchored_sandwich (a : Symbol) (c : ℂ) (M : ℕ) :
    diagonal (anchored a c M) = (cutoff M).comp ((diagonal a).comp (cutoff M)) +
      c • (ContinuousLinearMap.id ℂ Space - cutoff M) := by
  rw [anchored, diagonal_add, diagonal_smul, diagonal_sub, diagonal_one, truncate_sandwich]
  rfl

theorem truncate_vector_sum (a : Symbol) (M : ℕ) (x : Space) :
    diagonal (truncate a M) x = ∑ n ∈ Finset.range M, lp.single 2 n (diagonal a x n) := by
  apply lp.ext
  funext k
  simp only [diagonal_apply, truncate_apply, lp.coeFn_sum, lp.coeFn_single,
    Finset.sum_apply, Finset.sum_pi_single, Finset.mem_range]
  split_ifs <;> simp

/-- Strong convergence for every bounded diagonal symbol, including phases. -/
theorem truncate_strong (a : Symbol) (x : Space) :
    Tendsto (fun M => diagonal (truncate a M) x) atTop (𝓝 (diagonal a x)) := by
  simpa only [truncate_vector_sum] using
    (lp.hasSum_single (by norm_num : (2 : ENNReal) ≠ ⊤) (diagonal a x)).tendsto_sum_nat

theorem cutoff_strong (x : Space) : Tendsto (fun M => cutoff M x) atTop (𝓝 x) := by
  simpa only [cutoff, diagonal_one, ContinuousLinearMap.id_apply] using truncate_strong 1 x

theorem anchored_strong (a : Symbol) (c : ℂ) (x : Space) :
    Tendsto (fun M => diagonal (anchored a c M) x) atTop (𝓝 (diagonal a x)) := by
  have h := (truncate_strong a x).add
    (((tendsto_const_nhds : Tendsto (fun _ : ℕ => x) atTop (𝓝 x)).sub (cutoff_strong x)).const_smul c)
  simpa only [anchored, diagonal_add, diagonal_smul, diagonal_sub, diagonal_one,
    add_apply, sub_apply, ContinuousLinearMap.smul_apply, ContinuousLinearMap.id_apply,
    cutoff, sub_self, smul_zero, add_zero] using h

theorem error_coordinate (a : Symbol) (c : ℂ) (M n : ℕ) :
    (a - anchored a c M) n = if n < M then 0 else a n - c := by
  change a n - anchored a c M n = _
  rw [anchored_apply]
  split_ifs <;> simp

/-- Norm bound from every retained tail coefficient. -/
theorem error_norm_le (a : Symbol) (c : ℂ) (M : ℕ) {C : ℝ}
    (hC : 0 ≤ C) (h : ∀ n, M ≤ n → ‖a n - c‖ ≤ C) :
    ‖diagonal a - diagonal (anchored a c M)‖ ≤ C := by
  rw [diagonal_norm_sub]
  apply lp.norm_le_of_forall_le hC
  intro n
  rw [error_coordinate]
  split_ifs with hn
  · simpa using hC
  · exact h n (Nat.le_of_not_gt hn)

theorem tail_le_error_norm (a : Symbol) (c : ℂ) (M n : ℕ) (hn : M ≤ n) :
    ‖a n - c‖ ≤ ‖diagonal a - diagonal (anchored a c M)‖ := by
  rw [diagonal_norm_sub]
  have h := lp.norm_apply_le_norm ENNReal.top_ne_zero (a - anchored a c M) n
  simpa only [error_coordinate, ite_eq_right (Nat.not_lt.mpr hn)] using h

/-- Literal tail supremum, indexed by n+M. -/
theorem error_norm_eq_sup (a : Symbol) (c : ℂ) (M : ℕ) :
    ‖diagonal a - diagonal (anchored a c M)‖ = ⨆ k : ℕ, ‖a (k + M) - c‖ := by
  have hb : BddAbove (Set.range (fun k : ℕ => ‖a (k + M) - c‖)) := by
    refine ⟨‖a‖ + ‖c‖, ?_⟩
    rintro _ ⟨k, rfl⟩
    exact (norm_sub_le _ _).trans (add_le_add
      (lp.norm_apply_le_norm ENNReal.top_ne_zero a (k + M)) le_rfl)
  apply le_antisymm
  · apply error_norm_le
    · exact (norm_nonneg (a (0 + M) - c)).trans (le_ciSup hb 0)
    · intro n hn
      obtain ⟨k, rfl⟩ := Nat.exists_eq_add_of_le hn
      simpa only [Nat.add_comm] using le_ciSup hb k
  · apply ciSup_le
    intro k
    exact tail_le_error_norm a c M (k + M) (Nat.le_add_left _ _)

/-- Uniform tail convergence gives genuine operator-norm convergence. -/
theorem anchored_norm_tendsto (a : Symbol) (c : ℂ)
    (ha : Tendsto (fun n => a n) atTop (𝓝 c)) :
    Tendsto (fun M => ‖diagonal a - diagonal (anchored a c M)‖) atTop (𝓝 0) := by
  apply Metric.tendsto_atTop.mpr
  intro ε hε
  obtain ⟨N, hN⟩ := Metric.tendsto_atTop.mp ha (ε / 2) (half_pos hε)
  refine ⟨N, fun M hM => ?_⟩
  rw [dist_zero_right, Real.norm_eq_abs, abs_of_nonneg (norm_nonneg _)]
  apply lt_of_le_of_lt (error_norm_le a c M (le_of_lt (half_pos hε)) ?_) (half_lt_self hε)
  intro n hn
  exact le_of_lt (by simpa only [dist_eq_norm] using hN n (hM.trans hn))

/-- The tail anchor is necessary as well as sufficient. -/
theorem anchored_norm_iff (a : Symbol) (c : ℂ) :
    Tendsto (fun M => ‖diagonal a - diagonal (anchored a c M)‖) atTop (𝓝 0) ↔
      Tendsto (fun n => a n) atTop (𝓝 c) := by
  constructor
  · intro h
    apply Metric.tendsto_atTop.mpr
    intro ε hε
    obtain ⟨N, hN⟩ := Metric.tendsto_atTop.mp h ε hε
    refine ⟨N, fun n hn => ?_⟩
    rw [dist_eq_norm]
    apply lt_of_le_of_lt (tail_le_error_norm a c n n le_rfl)
    simpa only [dist_zero_right, Real.norm_eq_abs, abs_of_nonneg (norm_nonneg _)] using hN n hn
  · exact anchored_norm_tendsto a c

theorem unit_modulus_error (a : Symbol) (ha : ∀ n, ‖a n‖ = 1) (M : ℕ) :
    ‖diagonal a - diagonal (truncate a M)‖ = 1 := by
  rw [← anchored_zero a M]
  apply le_antisymm
  · apply error_norm_le a 0 M (by norm_num)
    intro n _
    simp [ha n]
  · simpa only [sub_zero, ha M] using tail_le_error_norm a 0 M M le_rfl

theorem unit_modulus_not_norm (a : Symbol) (ha : ∀ n, ‖a n‖ = 1) :
    ¬ Tendsto (fun M => ‖diagonal a - diagonal (truncate a M)‖) atTop (𝓝 0) := by
  intro h
  have h1 : Tendsto (fun _ : ℕ => (1 : ℝ)) atTop (𝓝 0) := by
    simpa only [unit_modulus_error a ha] using h
  have : (1 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds h1
  norm_num at this

end SpectralTruncation
end KomorebiPhysics
