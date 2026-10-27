import KomorebiRepair.Menu
import Mathlib.Data.List.MinMax
import Mathlib.Data.Finset.Powerset
import Mathlib.Data.Finset.Sort
import Mathlib.Data.List.Sublists

/-! # Executable finite search with proved optimality
The general Boolean minimizer is connected to exhaustive checking of the original
linear equations when all scalar and correction domains are finite.
No decidable feasibility oracle is assumed for arbitrary infinite fields.
-/
namespace KomorebiRepair
open scoped BigOperators

variable {α : Type*}

def bestByCheck (check : α → Bool) (cost : α → ℕ) (xs : List α) : Option α :=
  (xs.filter check).argmin cost

theorem bestByCheck_spec (check : α → Bool) (cost : α → ℕ) (xs : List α)
    (x : α) (h : bestByCheck check cost xs = some x) :
    x ∈ xs ∧ check x = true ∧
      ∀ y ∈ xs, check y = true → cost x ≤ cost y := by
  have hm : x ∈ (xs.filter check).argmin cost := h
  obtain ⟨hmem, hvalid⟩ := List.mem_filter.mp (List.argmin_mem hm)
  refine ⟨hmem, hvalid, ?_⟩
  intro y hy hcheck
  exact List.le_of_mem_argmin (List.mem_filter.mpr ⟨hy, hcheck⟩) hm

theorem bestByCheck_none_iff (check : α → Bool) (cost : α → ℕ) (xs : List α) :
    bestByCheck check cost xs = none ↔ ∀ x ∈ xs, check x ≠ true := by
  exact List.argmin_eq_none.trans List.filter_eq_nil_iff

section FiniteLinear
variable {k U V I J : Type*} [CommRing k]
  [AddCommGroup U] [Module k U] [AddCommGroup V] [Module k V]
  [Fintype k] [Fintype U] [Fintype I] [Fintype J] [LinearOrder J] [DecidableEq V]

/-- A terminating exhaustive check of actual equations, not a quotient-size guess. -/
def repairMenuCheck (D : U →ₗ[k] V) (e : J → V) (r : I → V) (S : Finset J) : Bool :=
  decide (∀ i, ∃ u : U, ∃ a : S → k,
    D u + ∑ j : S, a j • e j = -r i)

omit [Fintype J] in
@[simp] theorem repairMenuCheck_spec (D : U →ₗ[k] V) (e : J → V)
    (r : I → V) (S : Finset J) :
    repairMenuCheck D e r S = true ↔ FamilyRepairable D (menuMap e S) r := by
  simp only [repairMenuCheck, decide_eq_true_eq]
  rfl

def allMenus : List (Finset J) :=
  ((Finset.univ.sort (fun a b : J => a ≤ b)).sublists).map List.toFinset

theorem mem_allMenus (S : Finset J) : S ∈ allMenus (J := J) := by
  let xs := Finset.univ.sort (fun a b : J => a ≤ b)
  let ys := xs.filter (fun j => decide (j ∈ S))
  have hy : ys ∈ xs.sublists := List.mem_sublists.mpr List.filter_sublist
  have heq : ys.toFinset = S := by
    ext j
    simp [ys, xs]
  exact List.mem_map.mpr ⟨ys, hy, heq⟩

/-- Every subset is visited. Additional admissibility is explicit and decidable. -/
def bestRepairMenu (D : U →ₗ[k] V) (e : J → V) (r : I → V)
    (allowed : Finset J → Bool) (cost : Finset J → ℕ) : Option (Finset J) :=
  bestByCheck (fun S => allowed S && repairMenuCheck D e r S) cost
    (allMenus (J := J))

/-- Soundness and global minimum within the entire declared finite menu. -/
theorem menu_optimality_certificate (D : U →ₗ[k] V) (e : J → V) (r : I → V)
    (allowed : Finset J → Bool) (cost : Finset J → ℕ) (S : Finset J)
    (h : bestRepairMenu D e r allowed cost = some S) :
    allowed S = true ∧ FamilyRepairable D (menuMap e S) r ∧
      ∀ T : Finset J, allowed T = true → FamilyRepairable D (menuMap e T) r →
        cost S ≤ cost T := by
  obtain ⟨_, hv, hmin⟩ := bestByCheck_spec _ cost _ S h
  have hv' : allowed S = true ∧ FamilyRepairable D (menuMap e S) r := by
    simpa only [Bool.and_eq_true, repairMenuCheck_spec] using hv
  refine ⟨hv'.1, hv'.2, ?_⟩
  intro T hT hrepair
  apply hmin T (mem_allMenus T)
  simp only [Bool.and_eq_true, repairMenuCheck_spec]
  exact ⟨hT, hrepair⟩

/-- Failure is complete for the declared menu, not for arbitrary external constructions. -/
theorem menu_search_none_iff (D : U →ₗ[k] V) (e : J → V) (r : I → V)
    (allowed : Finset J → Bool) (cost : Finset J → ℕ) :
    bestRepairMenu D e r allowed cost = none ↔
      ∀ S : Finset J, allowed S = true → ¬ FamilyRepairable D (menuMap e S) r := by
  rw [bestRepairMenu, bestByCheck_none_iff]
  constructor
  · intro h S hallow hrepair
    apply h S (mem_allMenus S)
    simpa only [Bool.and_eq_true] using
      And.intro hallow ((repairMenuCheck_spec D e r S).mpr hrepair)
  · intro h S _ hboth
    have hb : allowed S = true ∧ repairMenuCheck D e r S = true := by
      simpa only [Bool.and_eq_true] using hboth
    obtain ⟨hallow, hcheck⟩ := hb
    exact h S hallow ((repairMenuCheck_spec D e r S).mp hcheck)

end FiniteLinear
end KomorebiRepair
