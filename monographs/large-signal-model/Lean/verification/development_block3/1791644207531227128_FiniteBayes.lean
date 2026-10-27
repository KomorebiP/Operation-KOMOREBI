import Mathlib.Algebra.BigOperators.Field
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity

/-! Finite Bayesian updates and aggregation. Priors and denominators are explicit. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteBayes
open scoped BigOperators
universe u v w
variable {I : Type u} {A : Type v} {B : Type w}

noncomputable def aggregate [Fintype I] [DecidableEq A]
    (c : I → A) (p : I → ℝ) (a : A) : ℝ :=
  ∑ i, if c i = a then p i else 0

noncomputable def evidence [Fintype I] (p l : I → ℝ) : ℝ := ∑ i, p i * l i

noncomputable def posterior [Fintype I] (p l : I → ℝ) (i : I) : ℝ :=
  p i * l i / evidence p l

def IsPrior [Fintype I] (p : I → ℝ) : Prop :=
  (∀ i, 0 ≤ p i) ∧ ∑ i, p i = 1

section Aggregation
variable [Fintype I] [Fintype A] [DecidableEq A]

theorem aggregate_sum (c : I → A) (p : I → ℝ) : ∑ a, aggregate c p a = ∑ i, p i := by
  simp only [aggregate]
  rw [Finset.sum_comm]
  simp

omit [Fintype A] in
theorem aggregate_nonneg (c : I → A) (p : I → ℝ) (hp : ∀ i, 0 ≤ p i) (a : A) :
    0 ≤ aggregate c p a := by
  apply Finset.sum_nonneg
  intro i _
  split_ifs
  · exact hp i
  · exact le_rfl

theorem aggregate_prior (c : I → A) (p : I → ℝ) (hp : IsPrior p) :
    IsPrior (aggregate c p) := by
  exact ⟨aggregate_nonneg c p hp.1, (aggregate_sum c p).trans hp.2⟩

omit [Fintype A] in
theorem aggregate_add (c : I → A) (p q : I → ℝ) :
    aggregate c (fun i => p i + q i) = fun a => aggregate c p a + aggregate c q a := by
  funext a
  simp only [aggregate, ← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro i _
  split_ifs <;> simp

omit [Fintype A] in
theorem aggregate_scale (c : I → A) (p : I → ℝ) (s : ℝ) :
    aggregate c (fun i => s * p i) = fun a => s * aggregate c p a := by
  funext a
  simp only [aggregate, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  split_ifs <;> simp

theorem aggregate_weighted_sum (c : I → A) (p : I → ℝ) (f : A → ℝ) :
    (∑ a, aggregate c p a * f a) = ∑ i, p i * f (c i) := by
  simp only [aggregate, Finset.sum_mul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  simp [ite_mul]

theorem aggregate_comp [Fintype B] [DecidableEq B]
    (c : I → A) (d : A → B) (p : I → ℝ) :
    aggregate d (aggregate c p) = aggregate (d ∘ c) p := by
  funext b
  have h := aggregate_weighted_sum c p (fun a => if d a = b then 1 else 0)
  simpa [aggregate, mul_ite] using h

omit [Fintype A] [DecidableEq A] in
theorem aggregate_id [DecidableEq I] (p : I → ℝ) : aggregate id p = p := by
  funext i
  simp [aggregate]

end Aggregation

section Updates
variable [Fintype I]

theorem evidence_pos (p l : I → ℝ) (hp : IsPrior p) (hl : ∀ i, 0 < l i) :
    0 < evidence p l := by
  obtain ⟨i, hi⟩ : ∃ i, 0 < p i := by
    by_contra h
    push Not at h
    have hz : ∑ i, p i = 0 := Finset.sum_eq_zero (fun i _ => le_antisymm (h i) (hp.1 i))
    linarith [hp.2]
  apply Finset.sum_pos'
  · intro j _; exact mul_nonneg (hp.1 j) (le_of_lt (hl j))
  · exact ⟨i, Finset.mem_univ i, mul_pos hi (hl i)⟩

theorem posterior_sum (p l : I → ℝ) (hz : evidence p l ≠ 0) :
    ∑ i, posterior p l i = 1 := by
  simp only [posterior, ← Finset.sum_div]
  exact div_self hz

theorem posterior_prior (p l : I → ℝ) (hp : IsPrior p)
    (hl : ∀ i, 0 ≤ l i) (hz : 0 < evidence p l) : IsPrior (posterior p l) := by
  exact ⟨fun i => div_nonneg (mul_nonneg (hp.1 i) (hl i)) hz.le, posterior_sum p l (ne_of_gt hz)⟩

theorem posterior_likelihood_scale (p l : I → ℝ) (s : ℝ) (hs : s ≠ 0) :
    posterior p (fun i => s * l i) = posterior p l := by
  have hz : evidence p (fun i => s * l i) = s * evidence p l := by
    simp only [evidence, Finset.mul_sum]; apply Finset.sum_congr rfl; intro i _; ring
  funext i
  simp only [posterior, hz]
  rw [show p i * (s * l i) = s * (p i * l i) by ring, mul_div_mul_left _ _ hs]

end Updates
section Coarsening
variable [Fintype I] [Fintype A] [DecidableEq A]

omit [Fintype A] in
theorem aggregate_div (c : I → A) (p : I → ℝ) (s : ℝ) :
    aggregate c (fun i => p i / s) = fun a => aggregate c p a / s := by
  simpa only [div_eq_mul_inv, mul_comm] using aggregate_scale c p s⁻¹

omit [Fintype A] in
theorem aggregate_mul_pullback (c : I → A) (p : I → ℝ) (b : A → ℝ) :
    aggregate c (fun i => p i * b (c i)) = fun a => aggregate c p a * b a := by
  funext a
  simp only [aggregate, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i _
  by_cases h : c i = a <;> simp [h]

theorem evidence_pullback (c : I → A) (p : I → ℝ) (b : A → ℝ) :
    evidence p (b ∘ c) = evidence (aggregate c p) b := by
  exact (aggregate_weighted_sum c p b).symm

theorem posterior_coarsening_pullback (c : I → A) (p : I → ℝ) (b : A → ℝ) :
    aggregate c (posterior p (b ∘ c)) = posterior (aggregate c p) b := by
  unfold posterior
  rw [aggregate_div, evidence_pullback]
  simp only [Function.comp_apply, aggregate_mul_pullback]

theorem posterior_coarsening_scaled (c : I → A) (p l : I → ℝ) (b : A → ℝ)
    (s : ℝ) (hs : s ≠ 0) (hl : ∀ i, l i = s * b (c i)) :
    aggregate c (posterior p l) = posterior (aggregate c p) b := by
  have heq : l = fun i => s * (b ∘ c) i := funext hl
  rw [heq, posterior_likelihood_scale p (b ∘ c) s hs]
  exact posterior_coarsening_pullback c p b

end Coarsening

section PointPriors
variable [Fintype I] [DecidableEq I]

def pointMass (i : I) (j : I) : ℝ := if j = i then 1 else 0

noncomputable def pairPrior (i j : I) (k : I) : ℝ := (1/2) * pointMass i k + (1/2) * pointMass j k

theorem pointMass_test (i : I) (f : I → ℝ) : ∑ k, pointMass i k * f k = f i := by
  simp [pointMass, ite_mul]

theorem pairPrior_test (i j : I) (f : I → ℝ) :
    ∑ k, pairPrior i j k * f k = (f i + f j) / 2 := by
  simp only [pairPrior, add_mul, mul_assoc, Finset.sum_add_distrib, ← Finset.mul_sum,
    pointMass_test]
  ring

theorem pairPrior_isPrior (i j : I) : IsPrior (pairPrior i j) := by
  constructor
  · intro k; simp only [pairPrior, pointMass]; positivity
  · have h := pairPrior_test i j (fun _ => 1)
    norm_num at h ⊢
    exact h

theorem pairPrior_evidence (i j : I) (l : I → ℝ) :
    evidence (pairPrior i j) l = (l i + l j)/2 := pairPrior_test i j l

variable [Fintype A] [DecidableEq A]

omit [Fintype A] in
theorem aggregate_pointMass (c : I → A) (i : I) :
    aggregate c (pointMass i) = pointMass (c i) := by
  funext a
  simp only [aggregate]
  rw [Finset.sum_eq_single i]
  · simp [pointMass, eq_comm]
  · intro j _ h; simp [pointMass, h]
  · intro h; exact False.elim (h (Finset.mem_univ i))

omit [Fintype A] in
theorem aggregate_pairPrior (c : I → A) (i j : I) :
    aggregate c (pairPrior i j) = pairPrior (c i) (c j) := by
  unfold pairPrior
  rw [aggregate_add, aggregate_scale, aggregate_scale, aggregate_pointMass, aggregate_pointMass]

omit [Fintype A] in
theorem aggregate_pair_weight (c : I → A) (i j : I) (l : I → ℝ) (a : A) :
    aggregate c (fun k => pairPrior i j k * l k) a =
      ((if c i = a then l i else 0) + (if c j = a then l j else 0))/2 := by
  have h := pairPrior_test i j (fun k => if c k = a then l k else 0)
  simpa only [aggregate, mul_ite, mul_zero] using h

omit [Fintype A] in
theorem aggregate_pair_posterior (c : I → A) (i j : I) (hij : c i ≠ c j)
    (l : I → ℝ) (hl : ∀ k, 0 < l k) :
    aggregate c (posterior (pairPrior i j) l) (c i) = l i/(l i+l j) := by
  have hz : l i + l j ≠ 0 := ne_of_gt (add_pos (hl i) (hl j))
  unfold posterior
  simp only [aggregate_div, aggregate_pair_weight, pairPrior_evidence]
  simp [Ne.symm hij]
  field_simp

end PointPriors
end Komorebi.LSM.FiniteBayes
