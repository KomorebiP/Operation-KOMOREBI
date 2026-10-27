module
public import Mathlib.Algebra.Order.Field.Basic
public import Mathlib.Algebra.Order.BigOperators.Group.Finset
public import Mathlib.Data.Fin.Tuple.Basic
public import Mathlib.Data.List.OfFn
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Exact min-plus dynamic programming with explicit infeasible states.
`none` denotes infeasible, never zero cost and never a finite sentinel.
All optima are proved attained, not only lower bounds on attainable costs.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
namespace BudgetDP
open scoped BigOperators
variable {R : Type*} [Field R] [LinearOrder R] [IsStrictOrderedRing R]

/-- Semantics of a table entry, relative to an independently defined feasible set. -/
def IsMinimum (o : Option R) (S : R → Prop) : Prop :=
  match o with
  | none => ∀ z, ¬ S z
  | some v => S v ∧ ∀ z, S z → v ≤ z

/-- Infeasible options are ignored. Ties choose the left entry. -/
def choose (x y : Option R) : Option R :=
  match x, y with
  | none, y => y
  | x, none => x
  | some a, some b => if a ≤ b then some a else some b

/-- Independent feasible components add; infeasibility is absorbing. -/
def add (x y : Option R) : Option R :=
  match x, y with
  | some a, some b => some (a + b)
  | _, _ => none

/-- A finite minimum is computed, not postulated. -/
def bestOver {ι : Type*} (f : ι → Option R) : List ι → Option R
  | [] => none
  | x :: xs => choose (f x) (bestOver f xs)

/-- Min-plus convolution splits the exact error weight in every possible way. -/
def convolution (F G : ℕ → Option R) (b : ℕ) : Option R :=
  bestOver (fun k => add (F k) (G (b - k))) (List.range (b + 1))

theorem minimum_congr {o : Option R} {S T : R → Prop}
    (h : IsMinimum o S) (he : ∀ z, S z ↔ T z) : IsMinimum o T := by
  cases o with
  | none => exact fun z hz => h z ((he z).mpr hz)
  | some v => exact ⟨(he v).mp h.1, fun z hz => h.2 z ((he z).mpr hz)⟩

theorem choose_correct (x y : Option R) (S T : R → Prop)
    (hx : IsMinimum x S) (hy : IsMinimum y T) :
    IsMinimum (choose x y) (fun z => S z ∨ T z) := by
  cases x with
  | none =>
    cases y with
    | none => exact fun z hz => hz.elim (hx z) (hy z)
    | some b =>
      exact ⟨Or.inr hy.1, fun z hz => hz.elim (fun h => False.elim (hx z h)) (hy.2 z)⟩
  | some a =>
    cases y with
    | none =>
      exact ⟨Or.inl hx.1, fun z hz => hz.elim (hx.2 z) (fun h => False.elim (hy z h))⟩
    | some b =>
      by_cases hab : a ≤ b
      · simp only [choose, if_pos hab]
        exact ⟨Or.inl hx.1, fun z hz => hz.elim (hx.2 z) (fun h => hab.trans (hy.2 z h))⟩
      · simp only [choose, if_neg hab]
        exact ⟨Or.inr hy.1, fun z hz => hz.elim
          (fun h => (le_of_not_ge hab).trans (hx.2 z h)) (hy.2 z)⟩

theorem add_correct (x y : Option R) (S T : R → Prop)
    (hx : IsMinimum x S) (hy : IsMinimum y T) :
    IsMinimum (add x y) (fun z => ∃ u v, S u ∧ T v ∧ z = u + v) := by
  cases x with
  | none =>
    cases y <;> intro z hz
    all_goals obtain ⟨u, v, hu, hv, he⟩ := hz; exact hx u hu
  | some a =>
    cases y with
    | none =>
      intro z hz
      obtain ⟨u, v, hu, hv, he⟩ := hz
      exact hy v hv
    | some b =>
      refine ⟨⟨a, b, hx.1, hy.1, rfl⟩, ?_⟩
      intro z hz
      obtain ⟨u, v, hu, hv, rfl⟩ := hz
      exact add_le_add (hx.2 u hu) (hy.2 v hv)

theorem bestOver_correct {ι : Type*} (xs : List ι) (f : ι → Option R)
    (S : ι → R → Prop) (h : ∀ i ∈ xs, IsMinimum (f i) (S i)) :
    IsMinimum (bestOver f xs) (fun z => ∃ i ∈ xs, S i z) := by
  induction xs with
  | nil => simp [bestOver, IsMinimum]
  | cons i xs ih =>
    have hc := choose_correct (f i) (bestOver f xs) (S i)
      (fun z => ∃ j ∈ xs, S j z) (h i (by simp))
      (ih (fun j hj => h j (by simp [hj])))
    apply minimum_congr hc
    intro z
    simp

/-- Every feasible split is represented, and the returned finite value is attained. -/
theorem convolution_correct (F G : ℕ → Option R) (S T : ℕ → R → Prop)
    (hF : ∀ b, IsMinimum (F b) (S b)) (hG : ∀ b, IsMinimum (G b) (T b)) (b : ℕ) :
    IsMinimum (convolution F G b)
      (fun z => ∃ k l u v, k + l = b ∧ S k u ∧ T l v ∧ z = u + v) := by
  have h := bestOver_correct (List.range (b + 1))
    (fun k => add (F k) (G (b - k)))
    (fun k z => ∃ u v, S k u ∧ T (b - k) v ∧ z = u + v)
    (fun k _ => add_correct (F k) (G (b - k)) (S k) (T (b - k)) (hF k) (hG (b - k)))
  apply minimum_congr h
  intro z
  constructor
  · rintro ⟨k, hk, u, v, hu, hv, hz⟩
    have hk' : k < b + 1 := List.mem_range.mp hk
    exact ⟨k, b - k, u, v, by omega, hu, hv, hz⟩
  · rintro ⟨k, l, u, v, hkl, hu, hv, hz⟩
    have hk : k < b + 1 := by omega
    have hl : b - k = l := by omega
    exact ⟨k, List.mem_range.mpr hk, u, v, hu, hl ▸ hv, hz⟩

/-- A singleton feasible cost, at exactly its declared weight. -/
def singletonTable (w : ℕ) (c : R) (b : ℕ) : Option R :=
  if b = w then some c else none

theorem singletonTable_correct (w : ℕ) (c : R) (b : ℕ) :
    IsMinimum (singletonTable w c b) (fun z => b = w ∧ z = c) := by
  by_cases h : b = w
  · simp [singletonTable, h, IsMinimum]
  · simp [singletonTable, h, IsMinimum]

/-- Min-plus combination for arbitrary finite branching, including no children. -/
def combine : {n : ℕ} → (Fin n → ℕ → Option R) → ℕ → Option R
  | 0, _ => singletonTable 0 0
  | n + 1, F => convolution (F 0) (combine (fun i : Fin n => F i.succ))

/-- The result is the minimum over all independently chosen component weights and costs. -/
theorem combine_correct {n : ℕ} (F : Fin n → ℕ → Option R)
    (S : Fin n → ℕ → R → Prop) (hF : ∀ i b, IsMinimum (F i b) (S i b)) (b : ℕ) :
    IsMinimum (combine F b)
      (fun z => ∃ w : Fin n → ℕ, ∃ c : Fin n → R,
        (∀ i, S i (w i) (c i)) ∧ (∑ i, w i) = b ∧ (∑ i, c i) = z) := by
  induction n generalizing b with
  | zero =>
    apply minimum_congr (singletonTable_correct 0 (0 : R) b)
    intro z
    simp
  | succ n ih =>
    have h := convolution_correct (F 0) (combine (fun i : Fin n => F i.succ))
      (S 0)
      (fun l v => ∃ w : Fin n → ℕ, ∃ c : Fin n → R,
        (∀ i, S i.succ (w i) (c i)) ∧ (∑ i, w i) = l ∧ (∑ i, c i) = v)
      (hF 0) (fun l => ih (fun i => F i.succ) (fun i => S i.succ) (fun i => hF i.succ) l) b
    apply minimum_congr h
    intro z
    constructor
    · rintro ⟨k, l, u, v, hkl, hu, ⟨w, c, hc, hw, hv⟩, hz⟩
      refine ⟨Fin.cons k w, Fin.cons u c, ?_, ?_, ?_⟩
      · intro i
        refine Fin.cases ?_ (fun j => ?_) i
        · exact hu
        · exact hc j
      · simp only [Fin.sum_univ_succ, Fin.cons_zero, Fin.cons_succ, hw]
        exact hkl
      · simp only [Fin.sum_univ_succ, Fin.cons_zero, Fin.cons_succ, hv]
        exact hz.symm
    · rintro ⟨w, c, hc, hw, hz⟩
      refine ⟨w 0, ∑ i : Fin n, w i.succ, c 0, ∑ i : Fin n, c i.succ,
        ?_, hc 0, ⟨fun i => w i.succ, fun i => c i.succ, fun i => hc i.succ, rfl, rfl⟩, ?_⟩
      · simpa only [Fin.sum_univ_succ] using hw
      · simpa only [Fin.sum_univ_succ] using hz.symm

/-- Return the best feasible exact-weight entry up to a budget. -/
def withinBudget (F : ℕ → Option R) (B : ℕ) : Option R :=
  bestOver F (List.range (B + 1))

theorem withinBudget_correct (F : ℕ → Option R) (S : ℕ → R → Prop)
    (hF : ∀ b, IsMinimum (F b) (S b)) (B : ℕ) :
    IsMinimum (withinBudget F B) (fun z => ∃ b, b ≤ B ∧ S b z) := by
  apply minimum_congr (bestOver_correct (List.range (B + 1)) F S (fun b _ => hF b))
  intro z
  simp only [List.mem_range, Nat.lt_succ_iff]

/-- A finite answer contains an attaining feasible cost. -/
theorem minimum_some_iff (F : Option R) (S : R → Prop) (h : IsMinimum F S) (c : R) :
    F = some c ↔ S c ∧ ∀ z, S z → c ≤ z := by
  constructor
  · intro hf; subst F; exact h
  · intro hc
    cases F with
    | none => exact False.elim (h c hc.1)
    | some v => have he : v = c := le_antisymm (h.2 c hc.1) (hc.2 v h.1); simp [he]

/-- The sentinel is returned exactly when the feasible set is empty. -/
theorem minimum_none_iff (F : Option R) (S : R → Prop) (h : IsMinimum F S) :
    F = none ↔ ¬ ∃ z, S z := by
  cases F with
  | none => simp only [Option.none.injEq, true_iff]; exact fun ⟨z, hz⟩ => h z hz
  | some v => simp only [Option.some_ne_none, false_iff, not_not]; exact ⟨v, h.1⟩
end BudgetDP
end KomorebiPaperVIII

#print axioms KomorebiPaperVIII.BudgetDP.minimum_congr
#print axioms KomorebiPaperVIII.BudgetDP.choose_correct
#print axioms KomorebiPaperVIII.BudgetDP.add_correct
#print axioms KomorebiPaperVIII.BudgetDP.bestOver_correct
#print axioms KomorebiPaperVIII.BudgetDP.convolution_correct
#print axioms KomorebiPaperVIII.BudgetDP.singletonTable_correct
#print axioms KomorebiPaperVIII.BudgetDP.combine_correct
#print axioms KomorebiPaperVIII.BudgetDP.withinBudget_correct
#print axioms KomorebiPaperVIII.BudgetDP.minimum_some_iff
#print axioms KomorebiPaperVIII.BudgetDP.minimum_none_iff
