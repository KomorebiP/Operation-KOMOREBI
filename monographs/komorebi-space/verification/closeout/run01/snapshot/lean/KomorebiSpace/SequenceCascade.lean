import KomorebiSpace.CascadeDensity
import Mathlib.Analysis.Normed.Lp.lpSpace
import Mathlib.Tactic.NormNum

set_option autoImplicit false

/-!
# A concrete infinite cascade with exact reconstruction domain c₀

This is a separate coordinate-shift coarsening model. It is not an assertion
that the transported dyadic maps equal shifts. All operators and norm bounds
are constructed on the actual space of bounded real sequences.
-/
noncomputable section
namespace KomorebiSpace
namespace SequenceCascade
open Filter
open scoped Topology ENNReal NNReal

abbrev Space := lp (fun _ : ℕ => ℝ) (∞ : ℝ≥0∞)

/-- Delete the first coordinate. -/
def tail (f : Space) : Space :=
  ⟨fun k => f (k+1), memℓp_infty ⟨‖f‖, by
    rintro _ ⟨k, rfl⟩
    exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (k+1)⟩⟩

@[simp] theorem tail_apply (f : Space) (k : ℕ) : tail f k = f (k+1) := rfl

theorem tail_bound (f : Space) : ‖tail f‖ ≤ ‖f‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg f)
  intro k
  exact lp.norm_apply_le_norm ENNReal.top_ne_zero f (k+1)

def downLinear : Space →ₗ[ℝ] Space where
  toFun := tail
  map_add' := by intros; apply lp.ext; rfl
  map_smul' := by intros; apply lp.ext; rfl

def down : Space →L[ℝ] Space := downLinear.mkContinuous 1 (fun f => by
  change ‖tail f‖ ≤ 1*‖f‖
  simpa only [one_mul] using tail_bound f)

/-- Insert zero as the first coordinate. -/
def prepend (f : Space) : Space :=
  ⟨(fun k => match k with | 0 => 0 | k+1 => f k), memℓp_infty ⟨‖f‖, by
    rintro _ ⟨k, rfl⟩
    cases k with
    | zero => simpa only [norm_zero] using norm_nonneg f
    | succ k => exact lp.norm_apply_le_norm ENNReal.top_ne_zero f k⟩⟩

@[simp] theorem prepend_zero (f : Space) : prepend f 0 = 0 := rfl
@[simp] theorem prepend_succ (f : Space) (k : ℕ) : prepend f (k+1) = f k := rfl

theorem prepend_bound (f : Space) : ‖prepend f‖ ≤ ‖f‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg f)
  intro k
  cases k with
  | zero => simpa only [prepend_zero, norm_zero] using norm_nonneg f
  | succ k => exact lp.norm_apply_le_norm ENNReal.top_ne_zero f k

def upLinear : Space →ₗ[ℝ] Space where
  toFun := prepend
  map_add' := by
    intro f g
    apply lp.ext
    funext k
    cases k <;> simp only [prepend_zero, prepend_succ, lp.coeFn_add, Pi.add_apply, add_zero]
  map_smul' := by
    intro c f
    apply lp.ext
    funext k
    cases k <;> simp only [prepend_zero, prepend_succ, lp.coeFn_smul, Pi.smul_apply,
      smul_zero, RingHom.id_apply]

def up : Space →L[ℝ] Space := upLinear.mkContinuous 1 (fun f => by
  change ‖prepend f‖ ≤ 1*‖f‖
  simpa only [one_mul] using prepend_bound f)

@[simp] theorem down_up (f : Space) : down (up f) = f := by
  apply lp.ext
  rfl

/-- A single fully specified infinite coarsening cascade. -/
abbrev system : CoarseningCascade ℝ where
  Obj _ := Space
  down _ := down
  splitting _ := { lift := up, right_inv := down_up }

@[simp] theorem level_apply (f : Space) (N k : ℕ) :
    system.level f N k = f (k+N) := by
  induction N generalizing k with
  | zero => rfl
  | succ N ih =>
    change system.level f N (k+1) = f (k+(N+1))
    rw [ih, show k+1+N = k+(N+1) by omega]

/-- The restored datum is padded by N leading zeros. -/
theorem restore_apply (f : Space) (N k : ℕ) :
    system.restore N f k = if N ≤ k then f (k-N) else 0 := by
  induction N generalizing f k with
  | zero => change f k = if 0 ≤ k then f (k-0) else 0; simp
  | succ N ih =>
    change system.restore N (up f) k = _
    rw [ih]
    by_cases h : N+1 ≤ k
    · have hNk : N ≤ k := by omega
      have he : k-N = (k-(N+1))+1 := by omega
      rw [ite_eq_left hNk, ite_eq_left h, he]
      rfl
    · rw [ite_eq_right h]
      by_cases hNk : N ≤ k
      · have he : k-N = 0 := by omega
        rw [ite_eq_left hNk, he]
        rfl
      · rw [ite_eq_right hNk]

/-- The original-space remainder is exactly the tail mask. -/
theorem remainder_apply (f : Space) (N k : ℕ) :
    system.remainder N f k = if N ≤ k then f k else 0 := by
  rw [CoarseningCascade.remainder_apply, restore_apply]
  split_ifs with h
  · rw [level_apply, Nat.sub_add_cancel h]
  · rfl

theorem remainder_bound (f : Space) (N : ℕ) : ‖system.remainder N f‖ ≤ ‖f‖ := by
  apply lp.norm_le_of_forall_le (norm_nonneg f)
  intro k
  rw [remainder_apply]
  split_ifs
  · exact lp.norm_apply_le_norm ENNReal.top_ne_zero f k
  · simpa only [norm_zero] using norm_nonneg f

theorem remainder_opNorm (N : ℕ) : ‖system.remainder N‖ ≤ 1 := by
  apply ContinuousLinearMap.opNorm_le_bound _ (by norm_num)
  intro f
  simpa only [one_mul] using remainder_bound f N

/-- A concrete identification, not a declaration of a new convergence predicate. -/
theorem recoverable_iff_vanishes (f : Space) :
    f ∈ system.recoverable ↔ Tendsto (fun n => f n) atTop (𝓝 0) := by
  constructor
  · intro h
    apply tendsto_zero_iff_norm_tendsto_zero.mpr
    apply squeeze_zero (fun _ => norm_nonneg _) _
      (tendsto_zero_iff_norm_tendsto_zero.mp h)
    intro N
    have hh := lp.norm_apply_le_norm ENNReal.top_ne_zero (system.remainder N f) N
    rw [remainder_apply f N N, ite_eq_left (le_refl N)] at hh
    exact hh
  · intro h
    apply tendsto_zero_iff_norm_tendsto_zero.mpr
    apply Metric.tendsto_atTop.mpr
    intro ε hε
    have hn := tendsto_zero_iff_norm_tendsto_zero.mp h
    obtain ⟨N, hN⟩ := Metric.tendsto_atTop.mp hn (ε/2) (by positivity)
    refine ⟨N, fun n hnN => ?_⟩
    have hb : ‖system.remainder n f‖ ≤ ε/2 := by
      apply lp.norm_le_of_forall_le (by positivity)
      intro k
      rw [remainder_apply]
      split_ifs with hnk
      · have hk := hN k (hnN.trans hnk)
        have : ‖f k‖ < ε/2 := by
          simpa only [Real.dist_eq, sub_zero, abs_of_nonneg (norm_nonneg _)] using hk
        exact this.le
      · simp only [norm_zero]; positivity
    have hh : ‖system.remainder n f‖ < ε := by linarith
    simpa only [Real.dist_eq, sub_zero, abs_of_nonneg (norm_nonneg _)] using hh

/-- Explicit natural-order infinite reconstruction for every c₀ sequence. -/
theorem reconstruct_vanishing (f : Space)
    (hf : Tendsto (fun n => f n) atTop (𝓝 0)) :
    Tendsto (fun N => ∑ n ∈ Finset.range N, system.detailTerm f n) atTop (𝓝 f) := by
  apply (system.ordered_reconstruction_iff f).2
  exact (recoverable_iff_vanishes f).2 hf

/-- No nonzero datum is invisible to every detail, even on the whole l-infinity space. -/
theorem persistent_eq_bot : system.persistent = ⊥ := by
  apply le_antisymm _ bot_le
  intro f hf
  rw [Submodule.mem_bot]
  apply lp.ext
  funext k
  have hh := congrArg (fun g : Space => g k) (hf (k+1))
  rw [remainder_apply, ite_eq_right (by omega)] at hh
  exact hh.symm

/-- The constant-one sequence is bounded. -/
def ones : Space :=
  ⟨fun _ => 1, memℓp_infty ⟨1, by rintro _ ⟨n, rfl⟩; norm_num⟩⟩

/-- Its remainder never vanishes in norm despite the trivial persistent subspace. -/
theorem ones_remainder_norm (N : ℕ) : ‖system.remainder N ones‖ = 1 := by
  apply le_antisymm
  · apply lp.norm_le_of_forall_le (by norm_num)
    intro k
    rw [remainder_apply]
    split_ifs <;> norm_num [ones]
  · have hh := lp.norm_apply_le_norm ENNReal.top_ne_zero (system.remainder N ones) N
    rw [remainder_apply ones N N, ite_eq_left (le_refl N)] at hh
    simpa only [ones, norm_one] using hh

theorem ones_not_recoverable : ones ∉ system.recoverable := by
  intro h
  have hh := tendsto_zero_iff_norm_tendsto_zero.mp h
  have heq : (fun N => ‖system.remainder N ones‖) = (fun _ : ℕ => (1 : ℝ)) :=
    funext ones_remainder_norm
  rw [heq] at hh
  have he : (1 : ℝ) = 0 := tendsto_nhds_unique tendsto_const_nhds hh
  norm_num at he

/-- Trivial persistent kernel and bounded remainders do not imply universal reconstruction. -/
theorem stability_and_separation_not_enough :
    system.persistent = ⊥ ∧ (∀ N, ‖system.remainder N‖ ≤ 1) ∧
    ∃ f : Space, f ∉ system.recoverable :=
  ⟨persistent_eq_bot, remainder_opNorm, ones, ones_not_recoverable⟩

/-- Each retained original-space detail is precisely a single coordinate. -/
theorem detailTerm_apply (f : Space) (n k : ℕ) :
    system.detailTerm f n k = if k = n then f k else 0 := by
  rw [CoarseningCascade.detailTerm_eq_remainder_sub]
  change (system.remainder n f) k - (system.remainder (n+1) f) k = _
  rw [remainder_apply, remainder_apply]
  by_cases hkn : k = n
  · subst k
    simp
  · by_cases hnk : n ≤ k
    · have hsucc : n+1 ≤ k := by omega
      simp [hnk, hsucc, hkn]
    · have hsucc : ¬ n+1 ≤ k := by omega
      simp [hnk, hsucc, hkn]

/-- A nontrivial infinite family inside the recoverable domain. -/
def geometric (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) : Space :=
  ⟨fun n => q^n, memℓp_infty ⟨1, by
    rintro _ ⟨n, rfl⟩
    change ‖q^n‖ ≤ 1
    rw [Real.norm_eq_abs, abs_of_nonneg (pow_nonneg hq0 n)]
    exact pow_le_one₀ hq0 hq1.le⟩⟩

@[simp] theorem geometric_apply (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) (n : ℕ) :
    geometric q hq0 hq1 n = q^n := rfl

theorem geometric_recoverable (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) :
    geometric q hq0 hq1 ∈ system.recoverable := by
  apply (recoverable_iff_vanishes _).2
  exact tendsto_pow_atTop_nhds_zero_of_lt_one hq0 hq1

/-- Exact error, not merely an upper estimate, at every truncation depth. -/
theorem geometric_remainder_norm (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) (N : ℕ) :
    ‖system.remainder N (geometric q hq0 hq1)‖ = q^N := by
  apply le_antisymm
  · apply lp.norm_le_of_forall_le (pow_nonneg hq0 N)
    intro k
    rw [remainder_apply]
    split_ifs with h
    · rw [geometric_apply, Real.norm_eq_abs, abs_of_nonneg (pow_nonneg hq0 k)]
      obtain ⟨j, rfl⟩ := Nat.exists_eq_add_of_le h
      rw [pow_add]
      have hh : q^j ≤ 1 := pow_le_one₀ hq0 hq1.le
      simpa only [mul_one] using mul_le_mul_of_nonneg_left hh (pow_nonneg hq0 N)
    · simpa only [norm_zero] using pow_nonneg hq0 N
  · have hh := lp.norm_apply_le_norm ENNReal.top_ne_zero
      (system.remainder N (geometric q hq0 hq1)) N
    rw [remainder_apply (geometric q hq0 hq1) N N, ite_eq_left (le_refl N),
      geometric_apply, Real.norm_eq_abs, abs_of_nonneg (pow_nonneg hq0 N)] at hh
    exact hh

theorem geometric_reconstruction_error (q : ℝ) (hq0 : 0 ≤ q) (hq1 : q < 1) (N : ℕ) :
    ‖geometric q hq0 hq1 - system.reconstructed N (geometric q hq0 hq1)‖ = q^N := by
  exact (system.partial_error (geometric q hq0 hq1) N).trans
    (geometric_remainder_norm q hq0 hq1 N)


end SequenceCascade
end KomorebiSpace
end
