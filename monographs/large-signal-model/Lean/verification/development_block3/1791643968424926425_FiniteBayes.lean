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
end Komorebi.LSM.FiniteBayes
