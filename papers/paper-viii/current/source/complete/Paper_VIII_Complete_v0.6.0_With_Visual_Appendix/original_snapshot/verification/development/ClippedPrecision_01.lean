module
public import ContinuousPrecision
public import Mathlib.Topology.Order.IntermediateValue
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 8.5. A continuous capped water-filling construction, including
existence, global optimality, uniqueness of the vector, and the multiplier
boundary. The scale t is the reciprocal of the manuscript's multiplier.
-/
@[expose] public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators
variable {E : Type*} [Fintype E]

noncomputable def clippedTolerance (s c m : E → ℝ) (t : ℝ) (e : E) : ℝ :=
  min (m e) (t * (c e / s e))

noncomputable def clippedTotal (s c m : E → ℝ) (t : ℝ) : ℝ :=
  ∑ e, s e * clippedTolerance s c m t e

def ClippedFeasible (s m : E → ℝ) (budget : ℝ) (eps : E → ℝ) : Prop :=
  AllocationFeasible s budget eps ∧ ∀ e, eps e ≤ m e

theorem clipped_positive (s c m : E → ℝ) (t : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e)
    (ht : 0 < t) (e : E) : 0 < clippedTolerance s c m t e := by
  exact lt_min (hm e) (mul_pos ht (div_pos (hc e) (hs e)))

theorem clipped_total_continuous (s c m : E → ℝ) : Continuous (clippedTotal s c m) := by
  unfold clippedTotal clippedTolerance
  fun_prop

theorem clipped_total_mono (s c m : E → ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) : Monotone (clippedTotal s c m) := by
  intro t u htu
  apply Finset.sum_le_sum
  intro e _
  exact mul_le_mul_of_nonneg_left
    (min_le_min_left _ (mul_le_mul_of_nonneg_right htu (le_of_lt (div_pos (hc e) (hs e)))))
    (le_of_lt (hs e))

theorem clipped_total_zero (s c m : E → ℝ) (hm : ∀ e, 0 < m e) :
    clippedTotal s c m 0 = 0 := by
  simp [clippedTotal, clippedTolerance, le_of_lt (hm _)]

/-- A finite positive scale at which every coordinate is saturated. -/
noncomputable def saturationScale (s c m : E → ℝ) : ℝ := ∑ e, m e * s e / c e

theorem saturation_scale_positive [Nonempty E] (s c m : E → ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e) :
    0 < saturationScale s c m := by
  exact Finset.sum_pos (fun e _ => div_pos (mul_pos (hm e) (hs e)) (hc e))
    Finset.univ_nonempty

theorem saturation_scale_attains (s c m : E → ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e) :
    clippedTolerance s c m (saturationScale s c m) = m := by
  funext e
  apply min_eq_left
  have he : m e * s e / c e ≤ saturationScale s c m :=
    Finset.single_le_sum (fun i _ => le_of_lt (div_pos (mul_pos (hm i) (hs i)) (hc i)))
      (Finset.mem_univ e)
  have h := mul_le_mul_of_nonneg_right he (le_of_lt (div_pos (hc e) (hs e)))
  have hcancel : (m e * s e / c e) * (c e / s e) = m e := by
    field_simp
  rwa [hcancel] at h

/-- IVT supplies a scale from the budget itself; no multiplier is assumed. -/
theorem clipped_scale_exists [Nonempty E] (s c m : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e)
    (hb : 0 < budget) (hcap : budget ≤ ∑ e, s e * m e) :
    ∃ t, 0 < t ∧ clippedTotal s c m t = budget := by
  have hT := saturation_scale_positive s c m hs hc hm
  have hend : clippedTotal s c m (saturationScale s c m) = ∑ e, s e * m e := by
    simp only [clippedTotal, saturation_scale_attains s c m hs hc hm]
  have hmem : budget ∈ Set.Icc (clippedTotal s c m 0)
      (clippedTotal s c m (saturationScale s c m)) := by
    rw [clipped_total_zero s c m hm, hend]
    exact ⟨hb.le, hcap⟩
  obtain ⟨t, ht, heq⟩ := intermediate_value_Icc hT.le
    (clipped_total_continuous s c m).continuousOn hmem
  refine ⟨t, ?_, heq⟩
  by_contra hn
  have ht0 : t = 0 := le_antisymm (le_of_not_gt hn) ht.1
  subst t
  rw [clipped_total_zero s c m hm] at heq
  linarith

/-- Strict increase holds below saturation, not on the constant endpoint ray. -/
theorem clipped_total_strict_below_cap (s c m : E → ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (t u : ℝ) (htu : t < u)
    (hbelow : clippedTotal s c m t < ∑ e, s e * m e) :
    clippedTotal s c m t < clippedTotal s c m u := by
  classical
  obtain ⟨e, he⟩ : ∃ e, clippedTolerance s c m t e < m e := by
    by_contra hh
    push Not at hh
    have hall : ∀ e, clippedTolerance s c m t e = m e :=
      fun e => le_antisymm (min_le_left _ _) (hh e)
    simp only [clippedTotal, hall] at hbelow
    exact lt_irrefl _ hbelow
  apply Finset.sum_lt_sum
  · intro i _
    exact mul_le_mul_of_nonneg_left
      (min_le_min_left _ (mul_le_mul_of_nonneg_right htu.le (le_of_lt (div_pos (hc i) (hs i)))))
      (hs i).le
  · refine ⟨e, Finset.mem_univ e, mul_lt_mul_of_pos_left ?_ (hs e)⟩
    exact lt_min he (lt_of_le_of_lt (min_le_right _ _)
      (mul_lt_mul_of_pos_right htu (div_pos (hc e) (hs e))))

theorem clipped_scale_unique (s c m : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e)
    (hcap : budget < ∑ e, s e * m e) (t u : ℝ)
    (ht : clippedTotal s c m t = budget) (hu : clippedTotal s c m u = budget) : t = u := by
  apply le_antisymm
  · by_contra h
    have hl := clipped_total_strict_below_cap s c m hs hc u t (lt_of_not_ge h)
      (by simpa [hu] using hcap)
    linarith
  · by_contra h
    have hl := clipped_total_strict_below_cap s c m hs hc t u (lt_of_not_ge h)
      (by simpa [ht] using hcap)
    linarith

/-- Coordinate supporting inequality, including saturated coordinates. -/
theorem clipped_supporting_inequality (s c m t x : ℝ)
    (hs : 0 < s) (hc : 0 < c) (hm : 0 < m) (ht : 0 < t) (hx : x ≤ m) :
    c * (x / min m (t * (c/s)) - 1) ≤ (s/t) * (x - min m (t * (c/s))) := by
  by_cases h : m ≤ t * (c/s)
  · rw [min_eq_left h]
    have hcross : s*m ≤ c*t := by
      have hh : m*s ≤ t*c := (le_div_iff₀ hs).1 (by simpa [mul_div_assoc] using h)
      nlinarith
    have hcoef : s/t ≤ c/m := (div_le_div_iff₀ ht hm).2 hcross
    have hi := mul_le_mul_of_nonpos_right hcoef (sub_nonpos.mpr hx)
    have hid : c*(x/m-1) = (c/m)*(x-m) := by field_simp; ring
    rwa [← hid] at hi
  · rw [min_eq_right (le_of_not_ge h)]
    have hid : c * (x / (t*(c/s)) - 1) = (s/t) * (x - t*(c/s)) := by
      field_simp
      <;> ring
    exact hid.le

/-- The tangent bound sums to zero for every feasible clipped competitor. -/
theorem clipped_relative_sum_le_zero (s c m : E → ℝ) (budget t : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e)
    (ht : 0 < t) (hbudget : clippedTotal s c m t = budget)
    (eps : E → ℝ) (heps : ClippedFeasible s m budget eps) :
    ∑ e, c e * (eps e / clippedTolerance s c m t e - 1) ≤ 0 := by
  calc
    _ ≤ ∑ e, (s e/t) * (eps e-clippedTolerance s c m t e) := by
      apply Finset.sum_le_sum
      intro e _
      exact clipped_supporting_inequality _ _ _ _ _ (hs e) (hc e) (hm e) ht (heps.2 e)
    _ = 0 := by
      simp_rw [div_mul_eq_mul_div, mul_sub]
      rw [← Finset.sum_div, Finset.sum_sub_distrib, heps.1.2]
      change (budget - clippedTotal s c m t) / t = 0
      rw [hbudget, sub_self, zero_div]

theorem clipped_allocation_optimal (s c m : E → ℝ) (budget t : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e)
    (ht : 0 < t) (hbudget : clippedTotal s c m t = budget)
    (eps : E → ℝ) (heps : ClippedFeasible s m budget eps) :
    precisionObjective c (clippedTolerance s c m t) ≤ precisionObjective c eps := by
  have ho := clipped_positive s c m t hs hc hm ht
  have hlog : (∑ e, c e * Real.log (eps e / clippedTolerance s c m t e)) ≤ 0 := by
    calc
      _ ≤ ∑ e, c e * (eps e / clippedTolerance s c m t e - 1) := by
        apply Finset.sum_le_sum
        intro e _
        exact mul_le_mul_of_nonneg_left
          (Real.log_le_sub_one_of_pos (div_pos (heps.1.1 e) (ho e))) (hc e).le
      _ ≤ 0 := clipped_relative_sum_le_zero s c m budget t hs hc hm ht hbudget eps heps
  have hd := precision_objective_difference c eps (clippedTolerance s c m t) heps.1.1 ho
  linarith

theorem clipped_allocation_strict (s c m : E → ℝ) (budget t : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e)
    (ht : 0 < t) (hbudget : clippedTotal s c m t = budget)
    (eps : E → ℝ) (heps : ClippedFeasible s m budget eps)
    (hne : eps ≠ clippedTolerance s c m t) :
    precisionObjective c (clippedTolerance s c m t) < precisionObjective c eps := by
  classical
  have ho := clipped_positive s c m t hs hc hm ht
  obtain ⟨e, he⟩ : ∃ e, eps e ≠ clippedTolerance s c m t e := by
    by_contra h
    push Not at h
    exact hne (funext h)
  have hr : eps e / clippedTolerance s c m t e ≠ 1 := by
    intro h
    exact he ((div_eq_one_iff_eq (ho e).ne').1 h)
  have hlog : (∑ e, c e * Real.log (eps e / clippedTolerance s c m t e)) < 0 := by
    calc
      _ < ∑ e, c e * (eps e / clippedTolerance s c m t e - 1) := by
        apply Finset.sum_lt_sum
        · intro i _
          exact mul_le_mul_of_nonneg_left
            (Real.log_le_sub_one_of_pos (div_pos (heps.1.1 i) (ho i))) (hc i).le
        · exact ⟨e, Finset.mem_univ e, mul_lt_mul_of_pos_left
            (Real.log_lt_sub_one_of_pos (div_pos (heps.1.1 e) (ho e)) hr) (hc e)⟩
      _ ≤ 0 := clipped_relative_sum_le_zero s c m budget t hs hc hm ht hbudget eps heps
  have hd := precision_objective_difference c eps (clippedTolerance s c m t) heps.1.1 ho
  linarith

/-- Full feasibility and the unique minimizing vector at every positive feasible budget. -/
theorem clipped_unique_minimizer [Nonempty E] (s c m : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hm : ∀ e, 0 < m e)
    (hb : 0 < budget) (hcap : budget ≤ ∑ e, s e * m e) :
    ∃ t, 0 < t ∧ ClippedFeasible s m budget (clippedTolerance s c m t) ∧
      ∀ eps, ClippedFeasible s m budget eps →
        ((∀ other, ClippedFeasible s m budget other →
            precisionObjective c eps ≤ precisionObjective c other) ↔
          eps = clippedTolerance s c m t) := by
  obtain ⟨t, ht, heq⟩ := clipped_scale_exists s c m budget hs hc hm hb hcap
  have hf : ClippedFeasible s m budget (clippedTolerance s c m t) :=
    ⟨⟨clipped_positive s c m t hs hc hm ht, heq⟩, fun _ => min_le_left _ _⟩
  refine ⟨t, ht, hf, ?_⟩
  intro eps heps
  constructor
  · intro hmin
    by_contra hne
    have hl := clipped_allocation_strict s c m budget t hs hc hm ht heq eps heps hne
    have hu := hmin _ hf
    linarith
  · intro h
    subst eps
    exact fun other hother => clipped_allocation_optimal s c m budget t hs hc hm ht heq other hother

/-- The parameter is the reciprocal of the manuscript's multiplier. -/
theorem clipped_multiplier_formula (s c m : E → ℝ) (t : ℝ) (ht : 0 < t) :
    clippedTolerance s c m t = fun e => min (m e) (c e / ((1/t)*s e)) := by
  funext e
  congr 1
  field_simp

/-- At the endpoint different positive multipliers can give the same optimum. -/
theorem clipped_endpoint_nonunique_multiplier :
    min (1 : ℝ) (1 / ((1:ℝ)*1)) = 1 ∧
    min (1 : ℝ) (1 / (((1:ℝ)/2)*1)) = 1 ∧ (1:ℝ) ≠ 1/2 := by
  norm_num

end KomorebiPaperVIII

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.clipped_positive
#print axioms KomorebiPaperVIII.clipped_total_continuous
#print axioms KomorebiPaperVIII.clipped_total_mono
#print axioms KomorebiPaperVIII.clipped_total_zero
#print axioms KomorebiPaperVIII.saturation_scale_positive
#print axioms KomorebiPaperVIII.saturation_scale_attains
#print axioms KomorebiPaperVIII.clipped_scale_exists
#print axioms KomorebiPaperVIII.clipped_total_strict_below_cap
#print axioms KomorebiPaperVIII.clipped_scale_unique
#print axioms KomorebiPaperVIII.clipped_supporting_inequality
#print axioms KomorebiPaperVIII.clipped_relative_sum_le_zero
#print axioms KomorebiPaperVIII.clipped_allocation_optimal
#print axioms KomorebiPaperVIII.clipped_allocation_strict
#print axioms KomorebiPaperVIII.clipped_unique_minimizer
#print axioms KomorebiPaperVIII.clipped_multiplier_formula
#print axioms KomorebiPaperVIII.clipped_endpoint_nonunique_multiplier
