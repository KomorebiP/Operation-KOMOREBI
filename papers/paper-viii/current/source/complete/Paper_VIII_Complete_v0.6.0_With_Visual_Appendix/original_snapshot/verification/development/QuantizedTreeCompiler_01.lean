module
public import ExactTreeCompiler
import all ExactTreeCompiler
public import BudgetConvolution
import all BudgetConvolution

/-!
Author: Komorebi P.
Paper VIII 9.8: exact quantized-budget compilation on the actual candidate tree
and independently defined legal cuts from the preceding block.
Every finite table result is attained; infeasibility is represented explicitly.
-/
public section
set_option autoImplicit false
set_option maxRecDepth 2048
namespace KomorebiPaperVIII
namespace CandidateTree
open scoped BigOperators
variable {α R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- Integer errors of a legal cut. Splitting itself introduces no error. -/
def cutWeight (w : α → ℕ) : {t : CandidateTree α} → Cut t → ℕ
  | t, .keep _ => w t.root
  | .node _ _ _, .split cs => ∑ i, cutWeight w (cs i)

/-- Exact-weight min-plus recurrence. Unreachable states are `none`. -/
def budgetTable (κ : α → R) (w : α → ℕ) (σ : α → R) :
    CandidateTree α → ℕ → Option R
  | .leaf a, b => BudgetDP.singletonTable (w a) (κ a) b
  | .node a _ ts, b =>
    BudgetDP.choose (BudgetDP.singletonTable (w a) (κ a) b)
      (BudgetDP.add (some (σ a))
        (BudgetDP.combine (fun i => budgetTable κ w σ (ts i)) b))

/-- Theorem 9.8 at every exact weight: lower bound, attainment, and infeasibility. -/
theorem budgetTable_correct (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (b : ℕ) :
    BudgetDP.IsMinimum (budgetTable κ w σ t b)
      (fun z => ∃ c : Cut t, cutWeight w c = b ∧ cutValue κ σ c = z) := by
  induction t generalizing b with
  | leaf a =>
    apply BudgetDP.minimum_congr (BudgetDP.singletonTable_correct (w a) (κ a) b)
    intro z
    constructor
    · rintro ⟨hb, hz⟩
      exact ⟨.keep (.leaf a), hb.symm, hz.symm⟩
    · rintro ⟨c, hb, hz⟩
      cases c
      exact ⟨hb.symm, hz.symm⟩
  | node a n ts ih =>
    let S := fun i b z => ∃ c : Cut (ts i), cutWeight w c = b ∧ cutValue κ σ c = z
    have hchildren := BudgetDP.combine_correct (fun i => budgetTable κ w σ (ts i)) S ih b
    have hshift := BudgetDP.add_correct (some (σ a))
      (BudgetDP.combine (fun i => budgetTable κ w σ (ts i)) b)
      (fun z => z = σ a)
      (fun z => ∃ ws : Fin (n + 1) → ℕ, ∃ cs : Fin (n + 1) → R,
        (∀ i, S i (ws i) (cs i)) ∧ (∑ i, ws i) = b ∧ (∑ i, cs i) = z)
      ⟨rfl, fun z hz => by rw [hz]⟩ hchildren
    have h := BudgetDP.choose_correct
      (BudgetDP.singletonTable (w a) (κ a) b)
      (BudgetDP.add (some (σ a))
        (BudgetDP.combine (fun i => budgetTable κ w σ (ts i)) b))
      _ _ (BudgetDP.singletonTable_correct (w a) (κ a) b) hshift
    apply BudgetDP.minimum_congr h
    intro z
    constructor
    · intro hz
      rcases hz with ⟨hb, hz⟩ | hz
      · exact ⟨.keep (.node a n ts), hb.symm, hz.symm⟩
      · rcases hz with ⟨u, v, hu, ⟨ws, cs, hc, hw, hv⟩, hz⟩
        choose cuts hweights hcosts using hc
        refine ⟨.split cuts, ?_, ?_⟩
        · change (∑ i, cutWeight w (cuts i)) = b
          simpa only [hweights] using hw
        · change σ a + (∑ i, cutValue κ σ (cuts i)) = z
          simpa only [hcosts, hv, hu] using hz.symm
    · rintro ⟨c, hw, hc⟩
      cases c with
      | keep => exact Or.inl ⟨hw.symm, hc.symm⟩
      | split cuts =>
        refine Or.inr ⟨σ a, ∑ i, cutValue κ σ (cuts i), rfl, ?_, hc.symm⟩
        exact ⟨fun i => cutWeight w (cuts i), fun i => cutValue κ σ (cuts i),
          fun i => ⟨cuts i, rfl, rfl⟩, hw, rfl⟩

/-- The actual budget-constrained compiler scans only weights 0,...,B. -/
def compileBudget (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (B : ℕ) : Option R :=
  BudgetDP.withinBudget (budgetTable κ w σ t) B

/-- Exact constrained optimum over independent legal cuts of the original tree. -/
theorem quantized_budget_compiler (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (B : ℕ) :
    BudgetDP.IsMinimum (compileBudget κ w σ t B)
      (fun z => ∃ c : Cut t, cutWeight w c ≤ B ∧ cutValue κ σ c = z) := by
  apply BudgetDP.minimum_congr
    (BudgetDP.withinBudget_correct (budgetTable κ w σ t)
      (fun b z => ∃ c : Cut t, cutWeight w c = b ∧ cutValue κ σ c = z)
      (budgetTable_correct κ w σ t) B)
  intro z
  constructor
  · rintro ⟨b, hb, c, hw, hc⟩
    exact ⟨c, hw ▸ hb, hc⟩
  · rintro ⟨c, hc, hz⟩
    exact ⟨cutWeight w c, hc, c, rfl, hz⟩

/-- Every finite answer is attained by a legal budget-feasible cut and beats all others. -/
theorem compileBudget_some_iff (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (B : ℕ) (v : R) :
    compileBudget κ w σ t B = some v ↔
      (∃ c : Cut t, cutWeight w c ≤ B ∧ cutValue κ σ c = v) ∧
      ∀ c : Cut t, cutWeight w c ≤ B → v ≤ cutValue κ σ c := by
  rw [BudgetDP.minimum_some_iff _ _ (quantized_budget_compiler κ w σ t B)]
  constructor
  · intro h
    exact ⟨h.1, fun c hc => h.2 _ ⟨c, hc, rfl⟩⟩
  · intro h
    refine ⟨h.1, ?_⟩
    rintro z ⟨c, hc, rfl⟩
    exact h.2 c hc

/-- No large finite penalty or zero-cost placeholder can masquerade as infeasibility. -/
theorem compileBudget_none_iff (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (B : ℕ) :
    compileBudget κ w σ t B = none ↔ ¬ ∃ c : Cut t, cutWeight w c ≤ B := by
  rw [BudgetDP.minimum_none_iff _ _ (quantized_budget_compiler κ w σ t B)]
  simp

/-- Increasing the budget cannot worsen a finite optimum. -/
theorem compileBudget_monotone (κ : α → R) (w : α → ℕ) (σ : α → R)
    (t : CandidateTree α) (B C : ℕ) (hBC : B ≤ C) (u v : R)
    (hu : compileBudget κ w σ t B = some u)
    (hv : compileBudget κ w σ t C = some v) : v ≤ u := by
  obtain ⟨⟨c, hc, hcost⟩, _⟩ := (compileBudget_some_iff κ w σ t B u).mp hu
  have h := ((compileBudget_some_iff κ w σ t C v).mp hv).2 c (hc.trans hBC)
  simpa only [hcost] using h
end CandidateTree
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.CandidateTree.budgetTable_correct
#print axioms KomorebiPaperVIII.CandidateTree.quantized_budget_compiler
#print axioms KomorebiPaperVIII.CandidateTree.compileBudget_some_iff
#print axioms KomorebiPaperVIII.CandidateTree.compileBudget_none_iff
#print axioms KomorebiPaperVIII.CandidateTree.compileBudget_monotone
#print axioms KomorebiPaperVIII.CandidateTree.budgetTable
#print axioms KomorebiPaperVIII.CandidateTree.compileBudget
