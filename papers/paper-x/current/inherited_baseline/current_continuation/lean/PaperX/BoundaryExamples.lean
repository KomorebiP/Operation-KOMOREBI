import PaperX.Residual
import PaperX.Compactness

/-!
Hypothesis checks and exact finite models. These examples distinguish a root
from a branch and finite-level occupancy from a universal arithmetic claim.
-/
set_option autoImplicit false
namespace PaperX.BoundaryExamples
open PaperX.Compactness

/-- Finite, nonempty levels with a non-surjective transition at every depth. -/
def pruningTower : Tower where
  Level := fun _ => Bool
  parent := fun _ _ => false

theorem pruning_finite : FiniteLevels pruningTower := by
  intro n
  change ∃ xs : List Bool, ∀ x : Bool, x ∈ xs
  refine ⟨[false, true], ?_⟩
  intro x
  cases x <;> simp

theorem pruning_nonempty (n : Nat) : Nonempty (pruningTower.Level n) := ⟨false⟩

theorem pruning_nonsurjective (n : Nat) :
    ¬ ∃ x : pruningTower.Level (n+1), pruningTower.parent n x = true := by
  rintro ⟨x, hx⟩
  cases hx

theorem pruning_has_branch : Nonempty (Branch pruningTower) :=
  finite_branch_compactness pruningTower pruning_finite pruning_nonempty

theorem pruning_branch_values (b : Branch pruningTower) (n : Nat) :
    b.value n = false := (b.compatible n).symm

/-- An occupied root whose next level is empty. -/
def dyingTower : Tower where
  Level := fun n => {x : Fin 1 // n = 0}
  parent := fun n x => False.elim (by have h := x.2; omega)

theorem dying_has_root : Nonempty (dyingTower.Level 0) := ⟨⟨0, rfl⟩⟩

theorem dying_finite : FiniteLevels dyingTower := by
  intro n
  by_cases hn : n = 0
  · subst n
    change ∃ xs : List {x : Fin 1 // (0 : Nat) = 0}, ∀ x, x ∈ xs
    refine ⟨[⟨0, rfl⟩], ?_⟩
    intro x
    have hx : x = ⟨0, rfl⟩ := by
      apply Subtype.ext
      apply Fin.ext
      have h := x.1.2
      omega
    exact List.mem_singleton.mpr hx
  · refine ⟨[], ?_⟩
    intro x
    exact False.elim (hn x.2)

theorem dying_empty_level : ¬ Nonempty (dyingTower.Level 1) := by
  rintro ⟨x⟩
  have h := x.2
  omega

theorem root_not_enough : ¬ Nonempty (Branch dyingTower) :=
  empty_level_obstruction dyingTower 1 dying_empty_level

/-- Removing finiteness invalidates the compactness inference. Each level has
all natural numbers >= its depth, and reduction preserves the number. -/
def escapingTower : Tower where
  Level := fun n => {k : Nat // n ≤ k}
  parent := fun n x => ⟨x.1, by have h := x.2; omega⟩

theorem escaping_levels_nonempty (n : Nat) : Nonempty (escapingTower.Level n) :=
  ⟨⟨n, Nat.le_refl n⟩⟩

theorem escaping_no_branch : ¬ Nonempty (Branch escapingTower) := by
  rintro ⟨b⟩
  have constant : ∀ n, (b.value n).1 = (b.value 0).1 := by
    intro n
    induction n with
    | zero => rfl
    | succ n ih =>
      have hp := congrArg Subtype.val (b.compatible n)
      change (b.value (n+1)).1 = (b.value n).1 at hp
      exact hp.trans ih
  have hbound := (b.value ((b.value 0).1 + 1)).2
  have heq := constant ((b.value 0).1 + 1)
  omega

/-- Exact scalar finite-level root enumeration; no probabilistic arithmetic. -/
def roots (p depth : Nat) : List Nat :=
  (List.range (p^depth)).filter (fun x => (x*x+1) % (p^depth) == 0)

theorem roots_mod2 : roots 2 1 = [1] := by decide

theorem roots_mod4 : roots 2 2 = [] := by decide

theorem roots_mod3 : roots 3 1 = [] := by decide

theorem roots_mod7 : roots 7 1 = [] := by decide

theorem roots_mod5 : roots 5 1 = [2, 3] := by decide

theorem roots_mod25 : roots 5 2 = [7, 18] := by decide

/-- The sign characters merge mod 2 but separate mod 4. -/
theorem signs_same_mod2 : (1 : Int) % 2 = (-1 : Int) % 2 := by decide

theorem signs_different_mod4 : (1 : Int) % 4 ≠ (-1 : Int) % 4 := by decide

/-- Matrix arithmetic over the two-element field, represented by Fin 2. -/
def add2 (x y : Fin 2) : Fin 2 := ⟨(x.1+y.1)%2, Nat.mod_lt _ (by decide)⟩
def mul2 (x y : Fin 2) : Fin 2 := ⟨(x.1*y.1)%2, Nat.mod_lt _ (by decide)⟩
abbrev Matrix2 := Fin 2 → Fin 2 → Fin 2

def identity2 : Matrix2 := fun i j => if i = j then 1 else 0

def matmul2 (a b : Matrix2) : Matrix2 := fun i j =>
  add2 (mul2 (a i 0) (b 0 j)) (mul2 (a i 1) (b 1 j))

def trace2 (a : Matrix2) : Fin 2 := add2 (a 0 0) (a 1 1)

theorem identity2_idempotent : matmul2 identity2 identity2 = identity2 := by
  funext i j
  revert i j
  decide

theorem identity2_trace_zero : trace2 identity2 = 0 := by decide

theorem identity2_nonzero : identity2 ≠ (fun _ _ => 0) := by
  intro h
  have he := congrFun (congrFun h 0) 0
  change (1 : Fin 2) = 0 at he
  exact (by decide : (1 : Fin 2) ≠ 0) he

end PaperX.BoundaryExamples
