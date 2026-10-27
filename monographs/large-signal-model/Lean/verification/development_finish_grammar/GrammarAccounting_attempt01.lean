import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Tactic

/-!
# Exact accounting for an enumerated grammar

The weight `w g` is the whole-record unnormalized evidence `π(g) L_g(D)`.
Infinite sums are required to be summable; the active set is finite.
-/
namespace KomorebiLSM.GrammarAccounting

noncomputable section

open scoped BigOperators

variable {G : Type*} [DecidableEq G]

def evidence (w : G → ℝ) : ℝ := ∑' g, w g

def activeEvidence (A : Finset G) (w : G → ℝ) : ℝ := ∑ g ∈ A, w g

def posterior (w : G → ℝ) (g : G) : ℝ := w g / evidence w

def activePosterior (A : Finset G) (w : G → ℝ) (g : G) : ℝ :=
  if g ∈ A then w g / activeEvidence A w else 0

def retainedPosterior (A : Finset G) (w : G → ℝ) (g : G) : ℝ :=
  if g ∈ A then posterior w g else 0

def totalVariation (p q : G → ℝ) : ℝ := (1 / 2 : ℝ) * ∑' g, |p g - q g|

lemma finite_ite_sum (A : Finset G) (f : G → ℝ) :
    (∑' g, if g ∈ A then f g else 0) = ∑ g ∈ A, f g := by
  rw [tsum_eq_sum (s := A) (by intro g hg; simp [hg])]
  exact Finset.sum_congr rfl (fun g hg => if_pos hg)

lemma finite_ite_summable (A : Finset G) (f : G → ℝ) :
    Summable (fun g => if g ∈ A then f g else 0) := by
  exact summable_of_ne_finset_zero (s := A) (by intro g hg; simp [hg])

lemma activeEvidence_le (A : Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) : activeEvidence A w ≤ evidence w := by
  exact hs.sum_le_tsum A (fun g _ => hw g)

lemma posterior_summable (w : G → ℝ) (hs : Summable w) : Summable (posterior w) :=
  hs.div_const _

lemma posterior_sum (w : G → ℝ) (hZ : 0 < evidence w) :
    (∑' g, posterior w g) = 1 := by
  simp only [posterior, tsum_div_const, ← evidence, div_self (ne_of_gt hZ)]

lemma activePosterior_sum (A : Finset G) (w : G → ℝ)
    (hA : 0 < activeEvidence A w) : (∑' g, activePosterior A w g) = 1 := by
  rw [activePosterior, finite_ite_sum, ← Finset.sum_div]
  exact div_self (ne_of_gt hA)

lemma retainedPosterior_sum (A : Finset G) (w : G → ℝ) :
    (∑' g, retainedPosterior A w g) = activeEvidence A w / evidence w := by
  rw [retainedPosterior, finite_ite_sum]
  exact (Finset.sum_div A w (evidence w)).symm

lemma abs_posterior_difference (A : Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w)
    (hA : 0 < activeEvidence A w) (g : G) :
    |posterior w g - activePosterior A w g| =
      posterior w g + activePosterior A w g - 2 * retainedPosterior A w g := by
  have hle := activeEvidence_le A w hw hs
  have hZ : 0 < evidence w := lt_of_lt_of_le hA hle
  by_cases hg : g ∈ A
  · simp only [activePosterior, retainedPosterior, if_pos hg]
    have hpq : posterior w g ≤ w g / activeEvidence A w :=
      div_le_div_of_nonneg_left (hw g) hA hle
    rw [abs_of_nonpos (sub_nonpos.mpr hpq)]
    ring
  · simp only [activePosterior, retainedPosterior, if_neg hg, sub_zero, add_zero, mul_zero]
    exact abs_of_nonneg (div_nonneg (hw g) (le_of_lt hZ))

/-- The active posterior loses exactly the omitted posterior mass, even for an infinite grammar. -/
theorem exact_posterior_tv (A : Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) (hA : 0 < activeEvidence A w) :
    totalVariation (posterior w) (activePosterior A w) =
      1 - activeEvidence A w / evidence w := by
  have hp := posterior_summable w hs
  have hq : Summable (activePosterior A w) := finite_ite_summable A _
  have hr : Summable (retainedPosterior A w) := finite_ite_summable A _
  have hZ : 0 < evidence w := lt_of_lt_of_le hA (activeEvidence_le A w hw hs)
  unfold totalVariation
  simp_rw [abs_posterior_difference A w hw hs hA]
  rw [(hp.add hq).tsum_sub (hr.mul_left 2), hp.tsum_add hq, tsum_mul_left,
    posterior_sum w hZ, activePosterior_sum A w hA, retainedPosterior_sum]
  ring

end
end KomorebiLSM.GrammarAccounting
