module
public import Mathlib.Algebra.Order.Field.Basic
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Algebra.BigOperators.Field
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 9.4--9.7 and 9.11: exact finite-branching tree compilation.
Prunings are an independent inductive type. The recurrence is proved both a
lower bound for every pruning and attained by the constructed pruning.
The ordered field parameter permits exact rational execution and real models.
-/

public section
set_option autoImplicit false
set_option maxRecDepth 2048
namespace KomorebiPaperVIII
open scoped BigOperators

inductive CandidateTree (α : Type*) where
  | leaf (label : α)
  | node (label : α) (arity : ℕ) (children : Fin (arity + 1) → CandidateTree α)

namespace CandidateTree
variable {α : Type*}

def root : CandidateTree α → α
  | .leaf a => a
  | .node a _ _ => a

/-- A legal pruning either keeps a node or independently prunes every child. -/
inductive Cut : CandidateTree α → Type _ where
  | keep (t : CandidateTree α) : Cut t
  | split {a : α} {n : ℕ} {ts : Fin (n + 1) → CandidateTree α}
      (cs : ∀ i, Cut (ts i)) : Cut (.node a n ts)

variable {R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- The independently defined additive objective of a legal pruning. -/
def cutValue (keep overhead : α → R) : {t : CandidateTree α} → Cut t → R
  | t, .keep _ => keep t.root
  | .node a _ _, .split cs => overhead a + ∑ i, cutValue keep overhead (cs i)

def optimalValue (keep overhead : α → R) : CandidateTree α → R
  | .leaf a => keep a
  | .node a _ ts => min (keep a) (overhead a + ∑ i, optimalValue keep overhead (ts i))

/-- An actual pruning is returned, with ties resolved in favor of keeping. -/
def compile (keep overhead : α → R) : (t : CandidateTree α) → Cut t
  | .leaf a => .keep (.leaf a)
  | .node a n ts =>
    if keep a ≤ overhead a + ∑ i, optimalValue keep overhead (ts i) then
      .keep (.node a n ts)
    else .split (fun i => compile keep overhead (ts i))

theorem optimalValue_le_cut (keep overhead : α → R) (t : CandidateTree α) (c : Cut t) :
    optimalValue keep overhead t ≤ cutValue keep overhead c := by
  induction t with
  | leaf a => cases c; exact le_rfl
  | node a n ts ih =>
    cases c with
    | keep => exact min_le_left _ _
    | split cs =>
      exact (min_le_right _ _).trans
        (add_le_add_left (Finset.sum_le_sum (fun i _ => ih i (cs i))) _)

theorem compile_attains (keep overhead : α → R) (t : CandidateTree α) :
    cutValue keep overhead (compile keep overhead t) = optimalValue keep overhead t := by
  induction t with
  | leaf a => rfl
  | node a n ts ih =>
    by_cases h : keep a ≤ overhead a + ∑ i, optimalValue keep overhead (ts i)
    · simp [compile, h, cutValue, root, optimalValue, min_eq_left h]
    · simp [compile, h, cutValue, ih, optimalValue, min_eq_right (le_of_not_ge h)]

/-- Exactness includes both lower-bound correctness and an attaining witness. -/
theorem exact_tree_compiler (keep overhead : α → R) (t : CandidateTree α) :
    (∀ c : Cut t, optimalValue keep overhead t ≤ cutValue keep overhead c) ∧
    ∃ c : Cut t, cutValue keep overhead c = optimalValue keep overhead t := by
  exact ⟨optimalValue_le_cut keep overhead t, compile keep overhead t,
    compile_attains keep overhead t⟩

theorem compile_minimizes (keep overhead : α → R) (t : CandidateTree α) (c : Cut t) :
    cutValue keep overhead (compile keep overhead t) ≤ cutValue keep overhead c := by
  rw [compile_attains]
  exact optimalValue_le_cut keep overhead t c

/-- Cost plus multiplier times error equals the local-score objective. -/
theorem lagrangian_decomposition (κ ε σ : α → R) (λ : R)
    {t : CandidateTree α} (c : Cut t) :
    cutValue (fun a => κ a + λ * ε a) σ c =
      cutValue κ σ c + λ * cutValue ε (fun _ => 0) c := by
  induction c with
  | keep t => rfl
  | @split a n ts cs ih =>
    simp only [cutValue, ih, Finset.sum_add_distrib, zero_add, Finset.mul_sum]
    ring

theorem exact_lagrangian_compiler (κ ε σ : α → R) (λ : R) (t : CandidateTree α)
    (c : Cut t) :
    let best := compile (fun a => κ a + λ * ε a) σ t
    cutValue κ σ best + λ * cutValue ε (fun _ => 0) best ≤
      cutValue κ σ c + λ * cutValue ε (fun _ => 0) c := by
  dsimp
  simpa only [← lagrangian_decomposition] using
    compile_minimizes (fun a => κ a + λ * ε a) σ t c

/-- Aggregation is proved at the actual pruning level, including split costs. -/
theorem cutValue_weighted_family {J : Type*} [Fintype J]
    (setup σ : α → R) (weights : J → R) (κ : J → α → R)
    {t : CandidateTree α} (c : Cut t) :
    cutValue (fun a => setup a + ∑ j, weights j * κ j a) σ c =
      cutValue setup σ c + ∑ j, weights j * cutValue (κ j) (fun _ => 0) c := by
  induction c with
  | keep t => rfl
  | @split a n ts cs ih =>
    simp only [cutValue, ih, Finset.sum_add_distrib, zero_add, Finset.mul_sum]
    rw [Finset.sum_comm (f := fun i j => weights j * cutValue (κ j) (fun _ => 0) (cs i))]
    ring

theorem shared_family_compiler {J : Type*} [Fintype J]
    (setup σ : α → R) (weights : J → R) (κ ε : J → α → R)
    (λ : R) (t : CandidateTree α) (c : Cut t) :
    let agg := fun a => setup a + ∑ j, weights j * (κ j a + λ * ε j a)
    let best := compile agg σ t
    cutValue setup σ best +
        ∑ j, weights j * (cutValue (κ j) (fun _ => 0) best +
          λ * cutValue (ε j) (fun _ => 0) best) ≤
      cutValue setup σ c +
        ∑ j, weights j * (cutValue (κ j) (fun _ => 0) c +
          λ * cutValue (ε j) (fun _ => 0) c) := by
  dsimp
  have h := compile_minimizes
    (fun a => setup a + ∑ j, weights j * (κ j a + λ * ε j a)) σ t c
  simpa only [cutValue_weighted_family, lagrangian_decomposition] using h

/-- Two genuinely optimal prunings have a monotone error/cost frontier. -/
theorem monotone_lagrangian_frontier (κ ε σ : α → R)
    (λ₁ λ₂ : R) (hλ₁ : 0 ≤ λ₁) (hλ : λ₁ < λ₂)
    {t : CandidateTree α} (c₁ c₂ : Cut t)
    (h₁ : ∀ c : Cut t, cutValue κ σ c₁ + λ₁ * cutValue ε (fun _ => 0) c₁ ≤
      cutValue κ σ c + λ₁ * cutValue ε (fun _ => 0) c)
    (h₂ : ∀ c : Cut t, cutValue κ σ c₂ + λ₂ * cutValue ε (fun _ => 0) c₂ ≤
      cutValue κ σ c + λ₂ * cutValue ε (fun _ => 0) c) :
    cutValue ε (fun _ => 0) c₂ ≤ cutValue ε (fun _ => 0) c₁ ∧
      cutValue κ σ c₁ ≤ cutValue κ σ c₂ := by
  have h12 := h₁ c₂
  have h21 := h₂ c₁
  have he : cutValue ε (fun _ => 0) c₂ ≤ cutValue ε (fun _ => 0) c₁ := by
    nlinarith
  exact ⟨he, by nlinarith⟩

theorem positive_lagrangian_pareto (κ ε σ : α → R) (λ : R) (hλ : 0 < λ)
    {t : CandidateTree α} (best : Cut t)
    (hbest : ∀ c : Cut t, cutValue κ σ best + λ * cutValue ε (fun _ => 0) best ≤
      cutValue κ σ c + λ * cutValue ε (fun _ => 0) c) :
    ¬ ∃ c : Cut t, cutValue κ σ c ≤ cutValue κ σ best ∧
      cutValue ε (fun _ => 0) c ≤ cutValue ε (fun _ => 0) best ∧
      (cutValue κ σ c < cutValue κ σ best ∨
       cutValue ε (fun _ => 0) c < cutValue ε (fun _ => 0) best) := by
  rintro ⟨c, hc, he, hs⟩
  have hb := hbest c
  rcases hs with h | h <;> nlinarith

/-- Strict score gaps withstand perturbations strictly smaller than half the gap. -/
theorem keep_decision_stable (K S K' S' : R) (h : K < S)
    (hK : |K' - K| < (S - K) / 2) (hS : |S' - S| < (S - K) / 2) :
    K' < S' := by
  have hk := (abs_lt.mp hK).2
  have hs := (abs_lt.mp hS).1
  linarith

theorem split_decision_stable (K S K' S' : R) (h : S < K)
    (hK : |K' - K| < (K - S) / 2) (hS : |S' - S| < (K - S) / 2) :
    S' < K' := by
  exact keep_decision_stable S K S' K' h hS hK

end CandidateTree
end KomorebiPaperVIII
