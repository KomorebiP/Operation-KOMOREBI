import Mathlib.Topology.Algebra.InfiniteSum.Real
import Mathlib.Tactic


set_option autoImplicit false

/-!
# Exact accounting for an enumerated grammar

The weight `w g` is the whole-record unnormalized evidence `π(g) L_g(D)`.
Infinite sums are required to be summable; the active set is finite.
-/
namespace Komorebi.LSM.GrammarAccounting

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

theorem finite_ite_sum (A : Finset G) (f : G → ℝ) :
    (∑' g, if g ∈ A then f g else 0) = ∑ g ∈ A, f g := by
  rw [tsum_eq_sum (s := A) (by intro g hg; simp [hg])]
  exact Finset.sum_congr rfl (fun g hg => ite_eq_left hg)

theorem finite_ite_summable (A : Finset G) (f : G → ℝ) :
    Summable (fun g => if g ∈ A then f g else 0) := by
  exact summable_of_ne_finset_zero (s := A) (by intro g hg; simp [hg])

omit [DecidableEq G] in
theorem activeEvidence_le (A : Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) : activeEvidence A w ≤ evidence w := by
  exact hs.sum_le_tsum A (fun g _ => hw g)

omit [DecidableEq G] in
omit [DecidableEq G] in
theorem posterior_summable (w : G → ℝ) (hs : Summable w) : Summable (posterior w) :=
  hs.div_const _

omit [DecidableEq G] in
theorem posterior_sum (w : G → ℝ) (hZ : 0 < evidence w) :
    (∑' g, posterior w g) = 1 := by
  simp only [posterior, tsum_div_const]
  exact div_self (ne_of_gt hZ)

theorem activePosterior_sum (A : Finset G) (w : G → ℝ)
    (hA : 0 < activeEvidence A w) : (∑' g, activePosterior A w g) = 1 := by
  simp only [activePosterior]
  rw [finite_ite_sum, ← Finset.sum_div]
  exact div_self (ne_of_gt hA)

theorem retainedPosterior_sum (A : Finset G) (w : G → ℝ) :
    (∑' g, retainedPosterior A w g) = activeEvidence A w / evidence w := by
  simp only [retainedPosterior]
  rw [finite_ite_sum]
  exact (Finset.sum_div A w (evidence w)).symm

theorem abs_posterior_difference (A : Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w)
    (hA : 0 < activeEvidence A w) (g : G) :
    |posterior w g - activePosterior A w g| =
      posterior w g + activePosterior A w g - 2 * retainedPosterior A w g := by
  have hle := activeEvidence_le A w hw hs
  have hZ : 0 < evidence w := lt_of_lt_of_le hA hle
  by_cases hg : g ∈ A
  · simp only [activePosterior, retainedPosterior, ite_eq_left hg]
    have hpq : posterior w g ≤ w g / activeEvidence A w :=
      div_le_div_of_nonneg_left (hw g) hA hle
    rw [abs_of_nonpos (sub_nonpos.mpr hpq)]
    ring
  · simp only [activePosterior, retainedPosterior, ite_eq_right hg, sub_zero, add_zero, mul_zero]
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

/-- An event in a predictive kernel has probability between zero and one. -/
def predictiveEvent (p kernel : G → ℝ) : ℝ := ∑' g, p g * kernel g

omit [DecidableEq G] in
theorem weighted_summable (p kernel : G → ℝ) (hp : ∀ g, 0 ≤ p g)
    (hs : Summable p) (hk0 : ∀ g, 0 ≤ kernel g) (hk1 : ∀ g, kernel g ≤ 1) :
    Summable (fun g => p g * kernel g) := by
  exact Summable.of_nonneg_of_le (fun g => mul_nonneg (hp g) (hk0 g))
    (fun g => by simpa using mul_le_mul_of_nonneg_left (hk1 g) (hp g)) hs

omit [DecidableEq G] in
/-- A common probability kernel cannot increase total variation, event by event. -/
theorem predictive_event_contraction (p q kernel : G → ℝ)
    (hp0 : ∀ g, 0 ≤ p g) (hq0 : ∀ g, 0 ≤ q g)
    (hp : Summable p) (hq : Summable q)
    (hpsum : ∑' g, p g = 1) (hqsum : ∑' g, q g = 1)
    (hk0 : ∀ g, 0 ≤ kernel g) (hk1 : ∀ g, kernel g ≤ 1) :
    |predictiveEvent p kernel - predictiveEvent q kernel| ≤ totalVariation p q := by
  have hpk := weighted_summable p kernel hp0 hp hk0 hk1
  have hqk := weighted_summable q kernel hq0 hq hk0 hk1
  have hd := hp.sub hq
  have habs : Summable (fun g => |p g - q g|) := by
    apply Summable.of_nonneg_of_le (fun g => abs_nonneg (p g - q g)) _ (hp.add hq)
    intro g
    exact abs_le.mpr ⟨by linarith [hp0 g], by linarith [hq0 g]⟩
  have hl : ∀ g, ((p g - q g) - |p g - q g|) / 2 ≤
      p g * kernel g - q g * kernel g := by
    intro g
    by_cases h : 0 ≤ p g - q g
    · rw [abs_of_nonneg h]
      nlinarith [mul_nonneg h (hk0 g)]
    · have hn := le_of_not_ge h
      rw [abs_of_nonpos hn]
      nlinarith [mul_nonpos_of_nonpos_of_nonneg hn (sub_nonneg.mpr (hk1 g))]
  have hu : ∀ g, p g * kernel g - q g * kernel g ≤
      ((p g - q g) + |p g - q g|) / 2 := by
    intro g
    by_cases h : 0 ≤ p g - q g
    · rw [abs_of_nonneg h]
      nlinarith [mul_nonneg h (sub_nonneg.mpr (hk1 g))]
    · have hn := le_of_not_ge h
      rw [abs_of_nonpos hn]
      nlinarith [mul_nonpos_of_nonpos_of_nonneg hn (hk0 g)]
  have hlow := ((hd.sub habs).div_const 2).tsum_le_tsum hl (hpk.sub hqk)
  have hupp := (hpk.sub hqk).tsum_le_tsum hu ((hd.add habs).div_const 2)
  rw [tsum_div_const, hd.tsum_sub habs, hp.tsum_sub hq,
    hpsum, hqsum, hpk.tsum_sub hqk] at hlow
  rw [tsum_div_const, hd.tsum_add habs, hp.tsum_sub hq,
    hpsum, hqsum, hpk.tsum_sub hqk] at hupp
  exact abs_le.mpr ⟨by dsimp [predictiveEvent, totalVariation]; linarith,
    by dsimp [predictiveEvent, totalVariation]; linarith⟩

/-- Any candidate predictive probability kernels retain the same omitted-mass bound. -/
theorem active_predictive_event_bound (A : Finset G) (w kernel : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) (hA : 0 < activeEvidence A w)
    (hk0 : ∀ g, 0 ≤ kernel g) (hk1 : ∀ g, kernel g ≤ 1) :
    |predictiveEvent (posterior w) kernel - predictiveEvent (activePosterior A w) kernel| ≤
      1 - activeEvidence A w / evidence w := by
  have hZ : 0 < evidence w := lt_of_lt_of_le hA (activeEvidence_le A w hw hs)
  rw [← exact_posterior_tv A w hw hs hA]
  apply predictive_event_contraction
  · exact fun g => div_nonneg (hw g) (le_of_lt hZ)
  · intro g
    simp only [activePosterior]
    split_ifs
    · exact div_nonneg (hw g) (le_of_lt hA)
    · exact le_rfl
  · exact posterior_summable w hs
  · exact finite_ite_summable A _
  · exact posterior_sum w hZ
  · exact activePosterior_sum A w hA
  · exact hk0
  · exact hk1

/-- The actual omitted unnormalized evidence. -/
def omittedEvidence (A : Finset G) (w : G → ℝ) : ℝ :=
  ∑' g, if g ∈ A then 0 else w g

theorem omittedEvidence_eq (A : Finset G) (w : G → ℝ) (hs : Summable w) :
    omittedEvidence A w = evidence w - activeEvidence A w := by
  have hr := finite_ite_summable A w
  calc
    omittedEvidence A w = ∑' g, (w g - if g ∈ A then w g else 0) := by
      apply tsum_congr
      intro g
      by_cases hg : g ∈ A <;> simp [hg]
    _ = (∑' g, w g) - ∑' g, if g ∈ A then w g else 0 := hs.tsum_sub hr
    _ = evidence w - activeEvidence A w := by rw [finite_ite_sum]; rfl

/-- A certified omitted-evidence bound yields the sharpened posterior tail bound. -/
theorem omitted_evidence_bound (A : Finset G) (w : G → ℝ) (bound : ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) (hA : 0 < activeEvidence A w)
    (hb : omittedEvidence A w ≤ bound) :
    1 - activeEvidence A w / evidence w ≤ bound / (activeEvidence A w + bound) := by
  have hle := activeEvidence_le A w hw hs
  have hZ : 0 < evidence w := lt_of_lt_of_le hA hle
  rw [omittedEvidence_eq A w hs] at hb
  have hbound : 0 ≤ bound := le_trans (sub_nonneg.mpr hle) hb
  have hden : 0 < activeEvidence A w + bound := add_pos_of_pos_of_nonneg hA hbound
  rw [show 1 - activeEvidence A w / evidence w =
      (evidence w - activeEvidence A w) / evidence w by field_simp]
  apply (div_le_div_iff₀ hZ hden).mpr
  nlinarith

omit [DecidableEq G] in
/-- An increasing exhaustive active-set sequence tends cofinally to all finite subsets. -/
theorem activeSets_cofinal (A : ℕ → Finset G) (hmono : Monotone A)
    (hexhaust : ∀ g, ∃ n, g ∈ A n) :
    Filter.Tendsto A Filter.atTop Filter.atTop := by
  exact hmono.tendsto_atTop_finset hexhaust

omit [DecidableEq G] in
/-- Exhaustion recovers the full normalizer; no finite-prefix rank assumption is used. -/
theorem active_evidence_tendsto (A : ℕ → Finset G) (w : G → ℝ) (hs : Summable w)
    (hmono : Monotone A) (hexhaust : ∀ g, ∃ n, g ∈ A n) :
    Filter.Tendsto (fun n => activeEvidence (A n) w) Filter.atTop (nhds (evidence w)) := by
  exact hs.hasSum.comp (activeSets_cofinal A hmono hexhaust)

omit [DecidableEq G] in
/-- The exact omitted posterior fraction tends to zero along every exhaustive sequence. -/
theorem posterior_tail_tendsto_zero (A : ℕ → Finset G) (w : G → ℝ)
    (hs : Summable w) (hZ : 0 < evidence w)
    (hmono : Monotone A) (hexhaust : ∀ g, ∃ n, g ∈ A n) :
    Filter.Tendsto (fun n => 1 - activeEvidence (A n) w / evidence w)
      Filter.atTop (nhds 0) := by
  have ht := (active_evidence_tendsto A w hs hmono hexhaust).div_const (evidence w)
  have ht' := (tendsto_const_nhds (x := (1 : ℝ)) (f := Filter.atTop)).sub ht
  simpa only [div_self (ne_of_gt hZ), sub_self] using ht'

omit [DecidableEq G] in
/-- Nonnegative whole-record evidence increases with the active set. -/
theorem active_evidence_monotone (A : ℕ → Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hmono : Monotone A) :
    Monotone (fun n => activeEvidence (A n) w) := by
  intro n m hnm
  exact Finset.sum_le_sum_of_subset_of_nonneg (hmono hnm) (fun g _ _ => hw g)

omit [DecidableEq G] in
/-- Consequently the omitted posterior fraction decreases. -/
theorem posterior_tail_antitone (A : ℕ → Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hZ : 0 < evidence w) (hmono : Monotone A) :
    Antitone (fun n => 1 - activeEvidence (A n) w / evidence w) := by
  intro n m hnm
  have hle := (active_evidence_monotone A w hw hmono) hnm
  have hdiv := div_le_div_of_nonneg_right hle (le_of_lt hZ)
  linarith

/-- The predictive assertion simultaneously covers every event of any output event family. -/
theorem predictive_event_family_bound {E : Type*} (A : Finset G) (w : G → ℝ)
    (kernel : G → E → ℝ) (hw : ∀ g, 0 ≤ w g) (hs : Summable w)
    (hA : 0 < activeEvidence A w)
    (hk0 : ∀ g e, 0 ≤ kernel g e) (hk1 : ∀ g e, kernel g e ≤ 1) :
    ∀ e, |predictiveEvent (posterior w) (fun g => kernel g e) -
      predictiveEvent (activePosterior A w) (fun g => kernel g e)| ≤
        1 - activeEvidence A w / evidence w := by
  intro e
  exact active_predictive_event_bound A w (fun g => kernel g e) hw hs hA
    (fun g => hk0 g e) (fun g => hk1 g e)

/-- Proposition 23: exact posterior error, all-event predictive control and evidence bound. -/
theorem enumerated_grammar_accounting {E : Type*} (A : Finset G) (w : G → ℝ)
    (kernel : G → E → ℝ) (bound : ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) (hA : 0 < activeEvidence A w)
    (hk0 : ∀ g e, 0 ≤ kernel g e) (hk1 : ∀ g e, kernel g e ≤ 1)
    (hb : omittedEvidence A w ≤ bound) :
    (totalVariation (posterior w) (activePosterior A w) =
      1 - activeEvidence A w / evidence w) ∧
    (∀ e, |predictiveEvent (posterior w) (fun g => kernel g e) -
      predictiveEvent (activePosterior A w) (fun g => kernel g e)| ≤
        1 - activeEvidence A w / evidence w) ∧
    (1 - activeEvidence A w / evidence w ≤ bound / (activeEvidence A w + bound)) := by
  exact ⟨exact_posterior_tv A w hw hs hA,
    predictive_event_family_bound A w kernel hw hs hA hk0 hk1,
    omitted_evidence_bound A w bound hw hs hA hb⟩

omit [DecidableEq G] in
/-- Positive full evidence ensures every sufficiently late active posterior is defined. -/
theorem active_evidence_eventually_positive (A : ℕ → Finset G) (w : G → ℝ)
    (hs : Summable w) (hZ : 0 < evidence w)
    (hmono : Monotone A) (hexhaust : ∀ g, ∃ n, g ∈ A n) :
    ∀ᶠ n in Filter.atTop, 0 < activeEvidence (A n) w := by
  exact (active_evidence_tendsto A w hs hmono hexhaust).eventually (Ioi_mem_nhds hZ)

/-- The actual posterior TV error tends to zero, including arbitrary early zero-evidence stages. -/
theorem active_posterior_tv_tendsto_zero (A : ℕ → Finset G) (w : G → ℝ)
    (hw : ∀ g, 0 ≤ w g) (hs : Summable w) (hZ : 0 < evidence w)
    (hmono : Monotone A) (hexhaust : ∀ g, ∃ n, g ∈ A n) :
    Filter.Tendsto (fun n => totalVariation (posterior w) (activePosterior (A n) w))
      Filter.atTop (nhds 0) := by
  have heq : (fun n => 1 - activeEvidence (A n) w / evidence w) =ᶠ[Filter.atTop]
      (fun n => totalVariation (posterior w) (activePosterior (A n) w)) := by
    filter_upwards [active_evidence_eventually_positive A w hs hZ hmono hexhaust] with n hn
    exact (exact_posterior_tv (A n) w hw hs hn).symm
  exact (posterior_tail_tendsto_zero A w hs hZ hmono hexhaust).congr' heq

/-- A small unnormalized tail may still be half the posterior mass. -/
theorem two_program_tail_example :
    totalVariation (posterior (fun _ : Bool => (1 / 100 : ℝ)))
      (activePosterior {false} (fun _ : Bool => (1 / 100 : ℝ))) = 1 / 2 := by
  norm_num [totalVariation, posterior, activePosterior, evidence, activeEvidence, tsum_fintype]

end
end Komorebi.LSM.GrammarAccounting
