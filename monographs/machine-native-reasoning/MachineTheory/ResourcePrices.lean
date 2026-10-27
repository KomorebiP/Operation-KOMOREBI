import MachineTheory.Planning
import Mathlib.Analysis.Convex.Hull

/-! # Resource prices and their declared uncertainty set

Core 7.3. Event coordinates use old-minus-new signs. A price is a linear conversion
of named additive events, not a hardware timing law. The convex hull below is
Mathlib's actual `convexHull`, not an assumed collection of convenient test prices.
-/
namespace Komorebi.MachineTheory.ResourcePrices
open scoped BigOperators
noncomputable section
variable {E : Type*} [Fintype E]

/-- Positive saving means that the old route consumes more priced events. -/
def saving (delta w : E → ℝ) : ℝ := ∑ i, w i * delta i

@[simp] theorem saving_zero_price (delta : E → ℝ) : saving delta 0 = 0 := by
  simp [saving]

@[simp] theorem saving_zero_events (w : E → ℝ) : saving 0 w = 0 := by
  simp [saving]

theorem saving_price_add (delta w z : E → ℝ) :
    saving delta (w+z) = saving delta w + saving delta z := by
  simp only [saving,Pi.add_apply,add_mul,Finset.sum_add_distrib]

theorem saving_price_smul (delta w : E → ℝ) (a : ℝ) :
    saving delta (a • w) = a * saving delta w := by
  simp only [saving,Pi.smul_apply,smul_eq_mul,mul_assoc,Finset.mul_sum]

theorem saving_event_add (a b w : E → ℝ) :
    saving (a+b) w = saving a w + saving b w := by
  simp only [saving,Pi.add_apply,mul_add,Finset.sum_add_distrib]

theorem saving_event_sub (a b w : E → ℝ) :
    saving (a-b) w = saving a w - saving b w := by
  simp only [saving,Pi.sub_apply,mul_sub,Finset.sum_sub_distrib]

theorem saving_event_smul (delta w : E → ℝ) (a : ℝ) :
    saving (a • delta) w = a * saving delta w := by
  unfold saving
  simp only [Pi.smul_apply,smul_eq_mul,Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  ring

/-- Core 7.3, first equivalence. Coordinate prices can expose any negative saving. -/
theorem all_nonnegative_prices_iff (delta : E → ℝ) :
    (∀ w : E → ℝ, (∀ i, 0 ≤ w i) → 0 ≤ saving delta w) ↔ ∀ i, 0 ≤ delta i := by
  classical
  constructor
  · intro h i
    have hh := h (fun j => if j=i then 1 else 0) (by intro j; split <;> norm_num)
    simpa [saving] using hh
  · intro h w hw
    exact Finset.sum_nonneg (fun i _ => mul_nonneg (hw i) (h i))

/-- A negative coordinate gives an explicit nonnegative counter-price. -/
theorem adverse_price_of_negative (delta : E → ℝ) (i : E) (hi : delta i < 0) :
    ∃ w : E → ℝ, (∀ j, 0 ≤ w j) ∧ saving delta w < 0 := by
  classical
  refine ⟨fun j => if j=i then 1 else 0, ?_, ?_⟩
  · intro j; dsimp; split <;> norm_num
  · simpa [saving] using hi

/-- The zero price excludes strict improvement at every nonnegative price. -/
theorem not_strict_at_all_nonnegative_prices (delta : E → ℝ) :
    ¬ ∀ w : E → ℝ, (∀ i, 0 ≤ w i) → 0 < saving delta w := by
  intro h
  have hz := h 0 (by intro i; exact le_rfl)
  simp at hz

/-- Linear lower-value sets are convex; no continuity or compactness is needed. -/
theorem lower_halfspace_convex (delta : E → ℝ) (b : ℝ) :
    Convex ℝ {w : E → ℝ | b ≤ saving delta w} := by
  intro x hx y hy a c ha hc hac
  change b ≤ saving delta (a • x + c • y)
  rw [saving_price_add,saving_price_smul,saving_price_smul]
  calc
    b = a*b+c*b := by rw [← add_mul,hac,one_mul]
    _ ≤ a*saving delta x+c*saving delta y :=
      add_le_add (mul_le_mul_of_nonneg_left hx ha) (mul_le_mul_of_nonneg_left hy hc)

/-- Testing every generator is equivalent to the same bound on its entire convex hull. -/
theorem hull_lower_bound_iff (delta : E → ℝ) (W : Set (E → ℝ)) (b : ℝ) :
    (∀ w ∈ convexHull ℝ W, b ≤ saving delta w) ↔ ∀ w ∈ W, b ≤ saving delta w := by
  constructor
  · intro h w hw
    exact h w (subset_convexHull ℝ W hw)
  · intro h
    exact convexHull_min h (lower_halfspace_convex delta b)

/-- Core 7.3, second conclusion: the finite minimum is the actual minimum on the hull. -/
theorem finite_price_minimum (delta : E → ℝ) (W : Finset (E → ℝ)) (hne : W.Nonempty) :
    ∃ w ∈ W, saving delta w = Planning.finiteMin W hne (saving delta) ∧
      IsLeast ((saving delta) '' convexHull ℝ (W : Set (E → ℝ)))
        (Planning.finiteMin W hne (saving delta)) := by
  obtain ⟨w,hw,hmin⟩ := Planning.finiteMin_attained W hne (saving delta)
  refine ⟨w,hw,hmin,?_,?_⟩
  · exact ⟨w,subset_convexHull ℝ (W : Set (E → ℝ)) hw,hmin⟩
  · rintro r ⟨z,hz,rfl⟩
    apply (hull_lower_bound_iff delta (W : Set (E → ℝ)) _).mpr ?_ z hz
    intro v hv
    exact Planning.finiteMin_le W hne (saving delta) v hv

/-- The listed minimum is attained, rather than a mere infimum outside the price set. -/
theorem listed_hull_minimizer (delta : E → ℝ) (W : Finset (E → ℝ)) (hne : W.Nonempty) :
    ∃ w ∈ W, w ∈ convexHull ℝ (W : Set (E → ℝ)) ∧
      ∀ z ∈ convexHull ℝ (W : Set (E → ℝ)), saving delta w ≤ saving delta z := by
  obtain ⟨w,hw,he,hmin⟩ := finite_price_minimum delta W hne
  refine ⟨w,hw,subset_convexHull ℝ (W : Set (E → ℝ)) hw,?_⟩
  intro z hz
  rw [he]
  exact hmin.2 ⟨z,hz,rfl⟩

/-- Changing the units requires compensating prices, not keeping their numbers fixed. -/
theorem consistent_unit_change (delta w units : E → ℝ) (hu : ∀ i, units i ≠ 0) :
    saving (fun i => units i * delta i) (fun i => w i / units i) = saving delta w := by
  unfold saving
  apply Finset.sum_congr rfl
  intro i _
  field_simp [hu i]

omit [Fintype E] in
theorem rescaled_price_nonnegative (w units : E → ℝ)
    (hw : ∀ i, 0 ≤ w i) (hu : ∀ i, 0 < units i) :
    ∀ i, 0 ≤ w i / units i := fun i => div_nonneg (hw i) (le_of_lt (hu i))

end
end Komorebi.MachineTheory.ResourcePrices
