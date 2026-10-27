module
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 8.4, with the positive-budget hypothesis established in block one.
This proves feasibility, global optimality, and uniqueness of the actual log
objective. It does not assume stationary-point optimality or a KKT oracle.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
open scoped BigOperators
variable {E : Type*} [Fintype E]

noncomputable def precisionObjective (c eps : E → ℝ) : ℝ :=
  ∑ e, c e * Real.log (1 / eps e)

noncomputable def optimalTolerance (s c : E → ℝ) (budget : ℝ) (e : E) : ℝ :=
  budget * c e / (s e * ∑ f, c f)

def AllocationFeasible (s : E → ℝ) (budget : ℝ) (eps : E → ℝ) : Prop :=
  (∀ e, 0 < eps e) ∧ ∑ e, s e * eps e = budget

theorem total_cost_positive [Nonempty E] (c : E → ℝ) (hc : ∀ e, 0 < c e) :
    0 < ∑ e, c e := by
  exact Finset.sum_pos (fun e _ => hc e) Finset.univ_nonempty

theorem optimal_tolerance_positive [Nonempty E] (s c : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hb : 0 < budget) (e : E) :
    0 < optimalTolerance s c budget e := by
  exact div_pos (mul_pos hb (hc e)) (mul_pos (hs e) (total_cost_positive c hc))

theorem optimal_tolerance_budget [Nonempty E] (s c : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) :
    ∑ e, s e * optimalTolerance s c budget e = budget := by
  have hC : (∑ e, c e) ≠ 0 := ne_of_gt (total_cost_positive c hc)
  have he : ∀ e, s e * optimalTolerance s c budget e = (budget / ∑ f, c f) * c e := by
    intro e
    dsimp [optimalTolerance]
    field_simp [ne_of_gt (hs e)]
  simp_rw [he]
  rw [← Finset.mul_sum]
  field_simp

theorem optimal_tolerance_feasible [Nonempty E] (s c : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hb : 0 < budget) :
    AllocationFeasible s budget (optimalTolerance s c budget) := by
  exact ⟨optimal_tolerance_positive s c budget hs hc hb,
    optimal_tolerance_budget s c budget hs hc⟩

theorem relative_budget_identity [Nonempty E] (s c eps : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hb : 0 < budget)
    (heps : ∑ e, s e * eps e = budget) :
    ∑ e, c e * (eps e / optimalTolerance s c budget e) = ∑ e, c e := by
  have hC : (∑ e, c e) ≠ 0 := ne_of_gt (total_cost_positive c hc)
  have he : ∀ e, c e * (eps e / optimalTolerance s c budget e) =
      ((∑ f, c f) / budget) * (s e * eps e) := by
    intro e
    dsimp [optimalTolerance]
    field_simp [ne_of_gt (hs e), ne_of_gt (hc e), ne_of_gt hb]
  simp_rw [he]
  rw [← Finset.mul_sum, heps]
  field_simp [ne_of_gt hb]

theorem precision_objective_difference (c eps opt : E → ℝ)
    (heps : ∀ e, 0 < eps e) (hopt : ∀ e, 0 < opt e) :
    precisionObjective c eps - precisionObjective c opt =
      -(∑ e, c e * Real.log (eps e / opt e)) := by
  simp only [precisionObjective, one_div, Real.log_inv, ← Finset.sum_sub_distrib,
    ← Finset.sum_neg_distrib]
  apply Finset.sum_congr rfl
  intro e _
  rw [Real.log_div (ne_of_gt (heps e)) (ne_of_gt (hopt e))]
  ring

/-- Global lower bound from log(x) <= x-1, not a first-order heuristic. -/
theorem precision_allocation_optimal [Nonempty E] (s c : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hb : 0 < budget)
    (eps : E → ℝ) (heps : AllocationFeasible s budget eps) :
    precisionObjective c (optimalTolerance s c budget) ≤ precisionObjective c eps := by
  have ho := optimal_tolerance_positive s c budget hs hc hb
  have hbalance := relative_budget_identity s c eps budget hs hc hb heps.2
  have hlog : (∑ e, c e * Real.log (eps e / optimalTolerance s c budget e)) ≤ 0 := by
    calc
      _ ≤ ∑ e, c e * (eps e / optimalTolerance s c budget e - 1) := by
        apply Finset.sum_le_sum
        intro e _
        exact mul_le_mul_of_nonneg_left
          (Real.log_le_sub_one_of_pos (div_pos (heps.1 e) (ho e))) (le_of_lt (hc e))
      _ = 0 := by
        simp_rw [mul_sub, mul_one]
        rw [Finset.sum_sub_distrib, hbalance, sub_self]
  have hd := precision_objective_difference c eps (optimalTolerance s c budget) heps.1 ho
  linarith

/-- Every distinct feasible vector has strictly larger objective. -/
theorem precision_allocation_strict [Nonempty E] (s c : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hb : 0 < budget)
    (eps : E → ℝ) (heps : AllocationFeasible s budget eps)
    (hne : eps ≠ optimalTolerance s c budget) :
    precisionObjective c (optimalTolerance s c budget) < precisionObjective c eps := by
  classical
  have ho := optimal_tolerance_positive s c budget hs hc hb
  have hbalance := relative_budget_identity s c eps budget hs hc hb heps.2
  obtain ⟨e, he⟩ : ∃ e, eps e ≠ optimalTolerance s c budget e := by
    by_contra hh
    push Not at hh
    exact hne (funext hh)
  have hratio : eps e / optimalTolerance s c budget e ≠ 1 := by
    intro hh
    exact he ((div_eq_one_iff_eq (ne_of_gt (ho e))).1 hh)
  have hlog : (∑ e, c e * Real.log (eps e / optimalTolerance s c budget e)) < 0 := by
    calc
      _ < ∑ e, c e * (eps e / optimalTolerance s c budget e - 1) := by
        apply Finset.sum_lt_sum
        · intro i _
          exact mul_le_mul_of_nonneg_left
            (Real.log_le_sub_one_of_pos (div_pos (heps.1 i) (ho i))) (le_of_lt (hc i))
        · exact ⟨e, Finset.mem_univ e, mul_lt_mul_of_pos_left
            (Real.log_lt_sub_one_of_pos (div_pos (heps.1 e) (ho e)) hratio) (hc e)⟩
      _ = 0 := by
        simp_rw [mul_sub, mul_one]
        rw [Finset.sum_sub_distrib, hbalance, sub_self]
  have hd := precision_objective_difference c eps (optimalTolerance s c budget) heps.1 ho
  linarith

/-- The stated formula is the unique feasible global minimizer. -/
theorem continuous_precision_unique_minimizer [Nonempty E] (s c : E → ℝ) (budget : ℝ)
    (hs : ∀ e, 0 < s e) (hc : ∀ e, 0 < c e) (hb : 0 < budget) :
    AllocationFeasible s budget (optimalTolerance s c budget) ∧
    ∀ eps : E → ℝ, AllocationFeasible s budget eps →
      ((∀ other : E → ℝ, AllocationFeasible s budget other →
          precisionObjective c eps ≤ precisionObjective c other) ↔
        eps = optimalTolerance s c budget) := by
  constructor
  · exact optimal_tolerance_feasible s c budget hs hc hb
  · intro eps heps
    constructor
    · intro hmin
      by_contra hne
      have hlt := precision_allocation_strict s c budget hs hc hb eps heps hne
      have hle := hmin _ (optimal_tolerance_feasible s c budget hs hc hb)
      linarith
    · intro h
      subst eps
      exact precision_allocation_optimal s c budget hs hc hb

end KomorebiPaperVIII

-- FINAL AXIOM AUDITS
#print axioms KomorebiPaperVIII.total_cost_positive
#print axioms KomorebiPaperVIII.optimal_tolerance_positive
#print axioms KomorebiPaperVIII.optimal_tolerance_budget
#print axioms KomorebiPaperVIII.optimal_tolerance_feasible
#print axioms KomorebiPaperVIII.relative_budget_identity
#print axioms KomorebiPaperVIII.precision_objective_difference
#print axioms KomorebiPaperVIII.precision_allocation_optimal
#print axioms KomorebiPaperVIII.precision_allocation_strict
#print axioms KomorebiPaperVIII.continuous_precision_unique_minimizer
#print axioms KomorebiPaperVIII.optimalTolerance
