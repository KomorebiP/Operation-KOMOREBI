import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Data.Finset.Max
import Mathlib.Tactic

namespace Komorebi.AVOC.FiniteCalibration

open Finset

/-- Exact binomial count law. Its connection to operation logs is an explicit
stationary independent sampling contract, not a fact inferred from a log. -/
def mass (n k : Nat) (p : ℚ) : ℚ :=
  (n.choose k : ℚ) * p ^ k * (1 - p) ^ (n - k)

theorem mass_nonneg (n k : Nat) {p : ℚ} (h0 : 0 ≤ p) (h1 : p ≤ 1) :
    0 ≤ mass n k p := by
  unfold mass
  positivity

theorem mass_sum_one (n : Nat) (p : ℚ) :
    ∑ k ∈ range (n + 1), mass n k p = 1 := by
  have h := add_pow p (1 - p) n
  have hsum : p + (1 - p) = 1 := by ring
  rw [hsum, one_pow] at h
  calc
    _ = ∑ k ∈ range (n+1), p^k * (1-p)^(n-k) * (n.choose k : ℚ) := by
      apply sum_congr rfl
      intro k hk
      unfold mass
      ring
    _ = 1 := h.symm

def threshold (n : Nat) (alpha : ℚ) : ℚ := alpha / (n + 1 : Nat)

def cellLower (m i : Nat) : ℚ := (i : ℚ) / m
def cellUpper (m i : Nat) : ℚ := ((i + 1 : Nat) : ℚ) / m

/-- A simple polynomial upper envelope on the entire cell, including endpoints. -/
def envelope (n k m i : Nat) : ℚ :=
  (n.choose k : ℚ) * (cellUpper m i) ^ k * (1 - cellLower m i) ^ (n - k)

def retained (n k m : Nat) (alpha : ℚ) : Finset Nat :=
  (range m).filter (fun i => threshold n alpha < envelope n k m i)

def lower (n k m : Nat) (alpha : ℚ) : ℚ :=
  if h : (retained n k m alpha).Nonempty then
    cellLower m ((retained n k m alpha).min' h) else 0

def upper (n k m : Nat) (alpha : ℚ) : ℚ :=
  if h : (retained n k m alpha).Nonempty then
    cellUpper m ((retained n k m alpha).max' h) else 1

def Contains (n k m : Nat) (alpha p : ℚ) : Prop :=
  lower n k m alpha ≤ p ∧ p ≤ upper n k m alpha

instance containsDecidable (n k m : Nat) (alpha p : ℚ) :
    Decidable (Contains n k m alpha p) := inferInstanceAs (Decidable (_ ∧ _))

theorem retained_lt {n k m i : Nat} {alpha : ℚ}
    (hi : i ∈ retained n k m alpha) : i < m :=
  mem_range.mp (mem_filter.mp hi).1

theorem cellLower_nonneg (m i : Nat) : 0 ≤ cellLower m i := by
  unfold cellLower
  positivity

theorem cellUpper_le_one {m i : Nat} (hi : i < m) : cellUpper m i ≤ 1 := by
  have hm : (0 : ℚ) < m := by exact_mod_cast (Nat.zero_lt_of_lt hi)
  unfold cellUpper
  apply (div_le_iff₀ hm).mpr
  norm_num
  exact_mod_cast hi

theorem cellLower_le_cellUpper (m i : Nat) : cellLower m i ≤ cellUpper m i := by
  apply div_le_div_of_nonneg_right _ (by positivity)
  exact_mod_cast Nat.le_succ i

theorem lower_nonneg (n k m : Nat) (alpha : ℚ) : 0 ≤ lower n k m alpha := by
  unfold lower
  split
  · exact cellLower_nonneg _ _
  · rfl

theorem upper_le_one (n k m : Nat) (alpha : ℚ) : upper n k m alpha ≤ 1 := by
  unfold upper
  split
  next h => exact cellUpper_le_one (retained_lt (max'_mem _ h))
  · rfl

theorem lower_le_upper (n k m : Nat) (alpha : ℚ) :
    lower n k m alpha ≤ upper n k m alpha := by
  unfold lower upper
  split
  next h =>
    have hminmax := min'_le_max' (retained n k m alpha) h
    dsimp [cellLower,cellUpper]
    apply div_le_div_of_nonneg_right _ (by positivity)
    exact_mod_cast hminmax.trans (Nat.le_succ _)
  · norm_num

theorem retained_cell_in_hull {n k m i : Nat} {alpha p : ℚ}
    (hi : i ∈ retained n k m alpha)
    (hlo : cellLower m i ≤ p) (hhi : p ≤ cellUpper m i) :
    Contains n k m alpha p := by
  have hn : (retained n k m alpha).Nonempty := ⟨i,hi⟩
  unfold Contains lower upper
  simp only [dite_eq_left hn]
  constructor
  · apply le_trans _ hlo
    apply div_le_div_of_nonneg_right _ (by positivity)
    exact_mod_cast min'_le _ _ hi
  · apply le_trans hhi
    apply div_le_div_of_nonneg_right _ (by positivity)
    exact_mod_cast Nat.succ_le_succ (le_max' _ _ hi)

theorem natural_cell_cover (n : Nat) (x : ℚ) (hx0 : 0 ≤ x)
    (hxn : x ≤ (n + 1 : Nat)) :
    ∃ i : Nat, i ≤ n ∧ (i : ℚ) ≤ x ∧ x ≤ (i + 1 : Nat) := by
  induction n with
  | zero => exact ⟨0, le_rfl, by simpa using hx0, hxn⟩
  | succ n ih =>
    by_cases h : x ≤ (n + 1 : Nat)
    · obtain ⟨i,hin,hil,hiu⟩ := ih h
      exact ⟨i, hin.trans (Nat.le_succ _), hil, hiu⟩
    · exact ⟨n+1,le_rfl,le_of_lt (lt_of_not_ge h),hxn⟩

/-- No grid membership assumption on the true probability is needed. -/
theorem grid_covers (m : Nat) (hm : 0 < m) {p : ℚ}
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    ∃ i : Nat, i < m ∧ cellLower m i ≤ p ∧ p ≤ cellUpper m i := by
  cases m with
  | zero => omega
  | succ n =>
    have hn : (0 : ℚ) < (n+1 : Nat) := by positivity
    have hx0 : 0 ≤ p * (n+1 : Nat) := mul_nonneg hp0 (le_of_lt hn)
    have hx1 : p * (n+1 : Nat) ≤ (n+1 : Nat) := by nlinarith
    obtain ⟨i,hin,hil,hiu⟩ := natural_cell_cover n (p * (n+1 : Nat)) hx0 hx1
    refine ⟨i, Nat.lt_succ_of_le hin, ?_, ?_⟩
    · exact (div_le_iff₀ hn).mpr hil
    · exact (le_div_iff₀ hn).mpr hiu

theorem mass_le_envelope (n k m i : Nat) {p : ℚ}
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1)
    (hlo : cellLower m i ≤ p) (hhi : p ≤ cellUpper m i) :
    mass n k p ≤ envelope n k m i := by
  unfold mass envelope
  have hu : 0 ≤ cellUpper m i := hp0.trans hhi
  apply mul_le_mul
  · exact mul_le_mul_of_nonneg_left (pow_le_pow_left₀ hp0 hhi k) (by positivity)
  · exact pow_le_pow_left₀ (sub_nonneg.mpr hp1) (by linarith) (n-k)
  · positivity
  · positivity

theorem excluded_mass_le (n k m : Nat) (hm : 0 < m) {alpha p : ℚ}
    (hp0 : 0 ≤ p) (hp1 : p ≤ 1) (hout : ¬ Contains n k m alpha p) :
    mass n k p ≤ threshold n alpha := by
  obtain ⟨i,him,hil,hiu⟩ := grid_covers m hm hp0 hp1
  have hnot : i ∉ retained n k m alpha := by
    intro hi
    exact hout (retained_cell_in_hull hi hil hiu)
  have henv : envelope n k m i ≤ threshold n alpha := by
    by_contra h
    apply hnot
    exact mem_filter.mpr ⟨mem_range.mpr him, lt_of_not_ge h⟩
  exact (mass_le_envelope n k m i hp0 hp1 hil hiu).trans henv

/-- Exact probability mass of confidence-band failure at a fixed sample size. -/
def missMass (n m : Nat) (alpha p : ℚ) : ℚ :=
  ∑ k ∈ range (n+1), if Contains n k m alpha p then 0 else mass n k p

/-- Universal finite-sample coverage for every rational true probability in [0,1].
No calibration premise or unexplained error radius is assumed. -/
theorem missMass_le (n m : Nat) (hm : 0 < m) {alpha p : ℚ}
    (ha : 0 ≤ alpha) (hp0 : 0 ≤ p) (hp1 : p ≤ 1) :
    missMass n m alpha p ≤ alpha := by
  unfold missMass
  calc
    _ ≤ ∑ _k ∈ range (n+1), threshold n alpha := by
      apply sum_le_sum
      intro k hk
      split
      · unfold threshold; positivity
      · exact excluded_mass_le n k m hm hp0 hp1 ‹_›
    _ = alpha := by
      simp [threshold]
      field_simp

/-- Ten checked successes give a proper interval, not empirical certainty. -/
theorem ten_successes_retained : retained 10 10 10 (1/10) = {6,7,8,9} := by
  ext i
  by_cases hi : i < 10
  · interval_cases i <;> norm_num [retained,threshold,envelope,cellLower,cellUpper]
  · have h6 : i ≠ 6 := by omega
    have h7 : i ≠ 7 := by omega
    have h8 : i ≠ 8 := by omega
    have h9 : i ≠ 9 := by omega
    simp [retained,hi,h6,h7,h8,h9]

theorem ten_successes_lower : lower 10 10 10 (1/10) = 3/5 := by
  norm_num [lower,ten_successes_retained,cellLower,min']

theorem ten_successes_upper : upper 10 10 10 (1/10) = 1 := by
  norm_num [upper,ten_successes_retained,cellUpper,max']

/-- A symmetric all-failure sample also gives a nontrivial exact band. -/
theorem ten_failures_retained : retained 10 0 10 (1/10) = {0,1,2,3} := by
  ext i
  by_cases hi : i < 10
  · interval_cases i <;> norm_num [retained,threshold,envelope,cellLower,cellUpper]
  · have h0 : i ≠ 0 := by omega
    have h1 : i ≠ 1 := by omega
    have h2 : i ≠ 2 := by omega
    have h3 : i ≠ 3 := by omega
    simp [retained,hi,h0,h1,h2,h3]

theorem ten_failures_lower : lower 10 0 10 (1/10) = 0 := by
  norm_num [lower,ten_failures_retained,cellLower,min']

theorem ten_failures_upper : upper 10 0 10 (1/10) = 2/5 := by
  norm_num [upper,ten_failures_retained,cellUpper,max']

/-- At n=1 and p=1/2, the singleton empirical estimate misses in both outcomes. -/
theorem empirical_singleton_counterexample :
    (∑ k ∈ range 2,
      if (k : ℚ) = (1/2 : ℚ) then 0 else mass 1 k (1/2)) = 1 := by
  norm_num [sum_range_succ, mass]

theorem ten_trial_half_model_coverage :
    missMass 10 10 (1/10) (1/2) ≤ 1/10 :=
  missMass_le 10 10 (by decide) (by norm_num) (by norm_num) (by norm_num)

end Komorebi.AVOC.FiniteCalibration
