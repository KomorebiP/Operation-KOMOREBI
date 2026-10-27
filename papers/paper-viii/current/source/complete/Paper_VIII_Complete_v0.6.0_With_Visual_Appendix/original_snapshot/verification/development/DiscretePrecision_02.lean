module
public import BudgetConvolution
import all BudgetConvolution

/-!
Author: Komorebi P.
Paper VIII 8.7: exact discrete precision assignment with an explicit guarded
residual budget. Costs are exact field values, not floating-point sentinels.
One option is independently selected for every edge, including zero-error options.
An empty option list correctly makes the whole assignment infeasible.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
namespace BudgetDP
variable {R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- Independently defined legal assignments, with one listed option per edge. -/
inductive Assignment : List (List (ℕ × R)) → Type _ where
  | nil : Assignment []
  | cons {opts : List (ℕ × R)} {edges : List (List (ℕ × R))}
      (choice : ℕ × R) (allowed : choice ∈ opts) (rest : Assignment edges) :
      Assignment (opts :: edges)

namespace Assignment

def weight : {edges : List (List (ℕ × R))} → Assignment edges → ℕ
  | _, .nil => 0
  | _, .cons o _ rest => weight rest + o.1

def cost : {edges : List (List (ℕ × R))} → Assignment edges → R
  | _, .nil => 0
  | _, .cons o _ rest => cost rest + o.2
end Assignment

/-- The recurrence iterates over the current edge's options, not all assignments.
The guard is necessary because natural subtraction otherwise truncates at zero. -/
def discreteTable : List (List (ℕ × R)) → ℕ → Option R
  | [], b => singletonTable 0 0 b
  | opts :: edges, b =>
    bestOver (fun o => if o.1 ≤ b then
      add (discreteTable edges (b - o.1)) (some o.2) else none) opts

/-- Exact-weight semantics of the dynamic program. -/
theorem discreteTable_correct (edges : List (List (ℕ × R))) (b : ℕ) :
    IsMinimum (discreteTable edges b)
      (fun z => ∃ a : Assignment edges, a.weight = b ∧ a.cost = z) := by
  induction edges generalizing b with
  | nil =>
    apply minimum_congr (singletonTable_correct 0 (0 : R) b)
    intro z
    constructor
    · rintro ⟨hb, hz⟩
      exact ⟨.nil, hb.symm, hz.symm⟩
    · rintro ⟨a, hb, hz⟩
      cases a
      exact ⟨hb.symm, hz.symm⟩
  | cons opts edges ih =>
    let S := fun (o : ℕ × R) z =>
      ∃ a : Assignment edges, a.weight + o.1 = b ∧ a.cost + o.2 = z
    have h : ∀ o ∈ opts, IsMinimum
        (if o.1 ≤ b then add (discreteTable edges (b - o.1)) (some o.2) else none) (S o) := by
      intro o _
      by_cases hob : o.1 ≤ b
      · simp only [hob, ↓reduceIte]
        apply minimum_congr
          (add_correct (discreteTable edges (b - o.1)) (some o.2)
            (fun z => ∃ a : Assignment edges, a.weight = b - o.1 ∧ a.cost = z)
            (fun z => z = o.2) (ih _) ⟨rfl, fun z hz => by rw [hz]⟩)
        intro z
        constructor
        · rintro ⟨u, v, ⟨a, hw, hc⟩, hv, hz⟩
          refine ⟨a, ?_, ?_⟩
          · omega
          · rw [hc, ← hv]
            exact hz.symm
        · rintro ⟨a, hw, hc⟩
          exact ⟨a.cost, o.2, ⟨a, by omega, rfl⟩, rfl, hc.symm⟩
      · simp only [hob, ↓reduceIte, IsMinimum]
        rintro z ⟨a, hw, hc⟩
        omega
    apply minimum_congr (bestOver_correct opts _ S h)
    intro z
    constructor
    · rintro ⟨o, ho, a, hw, hc⟩
      exact ⟨.cons o ho a, hw, hc⟩
    · rintro ⟨a, hw, hc⟩
      cases a with
      | cons o ho a => exact ⟨o, ho, a, hw, hc⟩

/-- The finite discrete precision optimizer. -/
def discreteBudget (edges : List (List (ℕ × R))) (B : ℕ) : Option R :=
  withinBudget (discreteTable edges) B

/-- Theorem 8.7: an attained global minimum under the declared quantized budget. -/
theorem discrete_precision_program (edges : List (List (ℕ × R))) (B : ℕ) :
    IsMinimum (discreteBudget edges B)
      (fun z => ∃ a : Assignment edges, a.weight ≤ B ∧ a.cost = z) := by
  apply minimum_congr (withinBudget_correct (discreteTable edges)
    (fun b z => ∃ a : Assignment edges, a.weight = b ∧ a.cost = z)
    (discreteTable_correct edges) B)
  intro z
  constructor
  · rintro ⟨b, hb, a, hw, hc⟩
    exact ⟨a, hw ▸ hb, hc⟩
  · rintro ⟨a, ha, hz⟩
    exact ⟨a.weight, ha, a, rfl, hz⟩

/-- A finite answer is a feasible assignment cost, not merely a relaxation. -/
theorem discreteBudget_some_iff (edges : List (List (ℕ × R))) (B : ℕ) (v : R) :
    discreteBudget edges B = some v ↔
      (∃ a : Assignment edges, a.weight ≤ B ∧ a.cost = v) ∧
        ∀ a : Assignment edges, a.weight ≤ B → v ≤ a.cost := by
  rw [minimum_some_iff _ _ (discrete_precision_program edges B)]
  constructor
  · intro h
    exact ⟨h.1, fun a ha => h.2 _ ⟨a, ha, rfl⟩⟩
  · intro h
    refine ⟨h.1, ?_⟩
    rintro z ⟨a, ha, rfl⟩
    exact h.2 a ha

/-- Infeasibility is exactly the absence of a complete legal assignment. -/
theorem discreteBudget_none_iff (edges : List (List (ℕ × R))) (B : ℕ) :
    discreteBudget edges B = none ↔ ¬ ∃ a : Assignment edges, a.weight ≤ B := by
  rw [minimum_none_iff _ _ (discrete_precision_program edges B)]
  simp

/-- Regression: an over-budget option is not accepted through truncated subtraction. -/
theorem over_budget_option_rejected :
    discreteBudget ([[(1, (0 : ℚ))]]) 0 = none := by decide

/-- Regression: a zero-weight option remains admissible at a zero budget. -/
theorem zero_budget_option_accepted :
    discreteBudget ([[(0, (3 : ℚ)), (1, (0 : ℚ))]]) 0 = some 3 := by
  norm_num [discreteBudget, withinBudget, bestOver, discreteTable, singletonTable, choose, add]

/-- Regression: no available type on an edge is infeasible, not free. -/
theorem empty_precision_options_rejected :
    discreteBudget ([[]] : List (List (ℕ × ℚ))) 3 = none := by decide

/-- Regression: the empty problem has cost zero and consumes no error budget. -/
theorem empty_precision_problem :
    discreteBudget ([] : List (List (ℕ × ℚ))) 0 = some 0 := by decide
end BudgetDP
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.BudgetDP.discreteTable_correct
#print axioms KomorebiPaperVIII.BudgetDP.discrete_precision_program
#print axioms KomorebiPaperVIII.BudgetDP.discreteBudget_some_iff
#print axioms KomorebiPaperVIII.BudgetDP.discreteBudget_none_iff
#print axioms KomorebiPaperVIII.BudgetDP.over_budget_option_rejected
#print axioms KomorebiPaperVIII.BudgetDP.zero_budget_option_accepted
#print axioms KomorebiPaperVIII.BudgetDP.empty_precision_options_rejected
#print axioms KomorebiPaperVIII.BudgetDP.empty_precision_problem
#print axioms KomorebiPaperVIII.BudgetDP.discreteTable
#print axioms KomorebiPaperVIII.BudgetDP.discreteBudget
