import AVOC.Bayesian

namespace Komorebi.AVOC

universe u v

/-- Probability of a finite event under a certified rational belief. -/
def eventProb
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (E : Finset Ω) : ℚ :=
  ∑ ω ∈ E, b.prob ω

/-- Event probabilities are nonnegative. -/
theorem eventProb_nonneg
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (E : Finset Ω) :
    0 ≤ eventProb b E := by
  unfold eventProb
  apply Finset.sum_nonneg
  intro ω hω
  exact b.nonneg ω

/-- The sure event has probability one. -/
theorem eventProb_univ
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) :
    eventProb b Finset.univ = 1 := by
  simpa [eventProb] using b.sum_one

/-- Event probability is monotone under event inclusion. -/
theorem eventProb_mono
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) {E F : Finset Ω}
    (hEF : E ⊆ F) :
    eventProb b E ≤ eventProb b F := by
  unfold eventProb
  exact Finset.sum_le_sum_of_subset_of_nonneg hEF (by
    intro ω hωF hωE
    exact b.nonneg ω)

/-- Probabilities add exactly on disjoint finite events. -/
theorem eventProb_union_of_disjoint
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    (b : RationalBelief Ω) {E F : Finset Ω}
    (hdisj : Disjoint E F) :
    eventProb b (E ∪ F) = eventProb b E + eventProb b F := by
  unfold eventProb
  exact Finset.sum_union hdisj

/-- Finite union bound for two events. -/
theorem eventProb_union_le_add
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    (b : RationalBelief Ω) (E F : Finset Ω) :
    eventProb b (E ∪ F) ≤ eventProb b E + eventProb b F := by
  have hsum := Finset.sum_union_inter (s₁ := E) (s₂ := F) (f := b.prob)
  have hinter := eventProb_nonneg b (E ∩ F)
  unfold eventProb at hsum hinter ⊢
  linarith

/-- Intersections are no more probable than either constituent event. -/
theorem eventProb_inter_le_left
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    (b : RationalBelief Ω) (E F : Finset Ω) :
    eventProb b (E ∩ F) ≤ eventProb b E := by
  exact eventProb_mono b Finset.inter_subset_left

/-- Intersections are no more probable than either constituent event. -/
theorem eventProb_inter_le_right
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    (b : RationalBelief Ω) (E F : Finset Ω) :
    eventProb b (E ∩ F) ≤ eventProb b F := by
  exact eventProb_mono b Finset.inter_subset_right

/-- Event probability is at most one. -/
theorem eventProb_le_one
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    (b : RationalBelief Ω) (E : Finset Ω) :
    eventProb b E ≤ 1 := by
  rw [← eventProb_univ b]
  exact eventProb_mono b (by intro ω hω; simp)

end Komorebi.AVOC
