import KomorebiLSM.FiniteBayes

/-! P12: exact all-prior closure, with nonempty blocks and the one-block boundary. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteBayes
open scoped BigOperators
universe u v
variable {I : Type u} {A : Type v}
variable [Fintype I] [Fintype A] [DecidableEq A]

def BayesCommutes (c : I → A) (l : I → ℝ) (b : A → ℝ) : Prop :=
  ∀ p, IsPrior p → aggregate c (posterior p l) = posterior (aggregate c p) b

theorem cross_ratio_of_commutes (c : I → A) (l : I → ℝ) (b : A → ℝ)
    (hl : ∀ i, 0 < l i) (hb : ∀ a, 0 < b a) (hc : BayesCommutes c l b)
    (i j : I) (hij : c i ≠ c j) : l i * b (c j) = l j * b (c i) := by
  classical
  have h := congrFun (hc (pairPrior i j) (pairPrior_isPrior i j)) (c i)
  rw [aggregate_pair_posterior c i j hij l hl, aggregate_pairPrior] at h
  have ht := aggregate_pair_posterior id (c i) (c j) hij b hb
  rw [aggregate_id] at ht
  rw [ht] at h
  have hz := ne_of_gt (add_pos (hl i) (hl j))
  have hbz := ne_of_gt (add_pos (hb (c i)) (hb (c j)))
  have hmul := (div_eq_div_iff hz hbz).mp h
  nlinarith

theorem ratio_constant_of_commutes [Nontrivial A] (c : I → A)
    (csurj : Function.Surjective c) (l : I → ℝ) (b : A → ℝ)
    (hl : ∀ i, 0 < l i) (hb : ∀ a, 0 < b a) (hc : BayesCommutes c l b) :
    ∀ i j, l i / b (c i) = l j / b (c j) := by
  have hd : ∀ i j, c i ≠ c j → l i / b (c i) = l j / b (c j) := by
    intro i j hij
    exact (div_eq_div_iff (ne_of_gt (hb (c i))) (ne_of_gt (hb (c j)))).mpr
      (cross_ratio_of_commutes c l b hl hb hc i j hij)
  intro i j
  by_cases hij : c i = c j
  · obtain ⟨a, ha⟩ := exists_ne (c i)
    obtain ⟨k, hk⟩ := csurj a
    have hik : c i ≠ c k := by simpa [hk] using Ne.symm ha
    have hjk : c j ≠ c k := by rw [← hij]; exact hik
    exact (hd i k hik).trans (hd j k hjk).symm
  · exact hd i j hij

theorem bayesian_coarsening_iff [Nontrivial A] (c : I → A)
    (csurj : Function.Surjective c) (l : I → ℝ) (b : A → ℝ)
    (hl : ∀ i, 0 < l i) (hb : ∀ a, 0 < b a) :
    BayesCommutes c l b ↔ ∃ s : ℝ, 0 < s ∧ ∀ i, l i = s * b (c i) := by
  constructor
  · intro hc
    obtain ⟨a0, a1, hne⟩ := exists_pair_ne A
    obtain ⟨i0, hi0⟩ := csurj a0
    refine ⟨l i0 / b (c i0), div_pos (hl i0) (hb (c i0)), ?_⟩
    intro i
    exact (div_eq_iff (ne_of_gt (hb (c i)))).mp
      (ratio_constant_of_commutes c csurj l b hl hb hc i i0)
  · rintro ⟨s, hs, hls⟩ p _
    exact posterior_coarsening_scaled c p l b s (ne_of_gt hs) hls

theorem likelihood_constant_on_fibers [Nontrivial A] (c : I → A)
    (csurj : Function.Surjective c) (l : I → ℝ) (b : A → ℝ)
    (hl : ∀ i, 0 < l i) (hb : ∀ a, 0 < b a) (hc : BayesCommutes c l b)
    (i j : I) (hij : c i = c j) : l i = l j := by
  obtain ⟨s, _, hs⟩ := (bayesian_coarsening_iff c csurj l b hl hb).mp hc
  rw [hs i, hs j, hij]

omit [Fintype A] [DecidableEq A] in
theorem one_block_posterior (p l : I → ℝ) (hz : evidence p l ≠ 0) :
    aggregate (fun _ : I => ()) (posterior p l) () = 1 := by
  simpa [aggregate] using posterior_sum p l hz

omit [Fintype A] [DecidableEq A] in
theorem one_block_commutes (l : I → ℝ) (b : Unit → ℝ)
    (hl : ∀ i, 0 < l i) (hb : ∀ a, 0 < b a) :
    BayesCommutes (fun _ : I => ()) l b := by
  intro p hp
  funext a
  cases a
  rw [one_block_posterior p l (ne_of_gt (evidence_pos p l hp hl))]
  simp [posterior, evidence, aggregate, hp.2, ne_of_gt (hb ())]

end Komorebi.LSM.FiniteBayes
