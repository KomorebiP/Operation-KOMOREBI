import PaperX.Compactness
import Mathlib.Data.Fintype.EquivFin
import Mathlib.Data.Fintype.Sigma
import Mathlib.Basic.Finite.Sigma
import Mathlib.Logic.Equiv.Sum

/-!
Lifting compatible classes to compatible representatives using finite fibers.
The fibers above a fixed quotient branch form their own inverse system.
Surjectivity of its transition maps is neither required nor asserted.
-/
set_option autoImplicit false

namespace PaperX.FiniteFiberBranches
open PaperX.Compactness

/-- A map of towers commutes with each immediate reduction. -/
structure TowerMap (T Q : Tower) where
  map : (k : ℕ) → T.Level k → Q.Level k
  parent_commutes : ∀ k x,
    map k (T.parent k x) = Q.parent k (map (k + 1) x)

variable {T Q : Tower}

/-- A tower map sends actual compatible representatives to compatible classes. -/
def mapBranch (f : TowerMap T Q) (b : Branch T) : Branch Q where
  value k := f.map k (b.value k)
  compatible k := by
    rw [← f.parent_commutes, b.compatible]

/-- The fiber above each member of a fixed compatible class branch. -/
def fiberTower (f : TowerMap T Q) (b : Branch Q) : Tower where
  Level k := {x : T.Level k // f.map k x = b.value k}
  parent k x := ⟨T.parent k x.val, by
    rw [f.parent_commutes, x.property, b.compatible]⟩

/-- Type-theoretic finiteness gives the complete finite lists required by the
elementary compactness theorem. -/
theorem finite_levels (S : Tower) (h : ∀ k, Finite (S.Level k)) :
    FiniteLevels S := by
  intro k
  let : Finite (S.Level k) := h k
  let : Fintype (S.Level k) := Fintype.ofFinite _
  classical
  exact ⟨Finset.univ.toList, by simp⟩

/-- A fixed compatible class branch has an exactly compatible representative
branch if its fibers are finite and nonempty. The full quotient levels may be
infinite, and no reduction map is assumed surjective. -/
theorem lift_branch_of_fibers (f : TowerMap T Q) (b : Branch Q)
    (finite : ∀ k, Finite {x : T.Level k // f.map k x = b.value k})
    (occupied : ∀ k, ∃ x, f.map k x = b.value k) :
    ∃ a : Branch T, ∀ k, f.map k (a.value k) = b.value k := by
  obtain ⟨c⟩ := finite_branch_compactness (fiberTower f b)
    (finite_levels _ finite)
    (fun k => let ⟨x, hx⟩ := occupied k; ⟨x, hx⟩)
  let a : Branch T := {
    value k := (c.value k).val
    compatible k := congrArg Subtype.val (c.compatible k)
  }
  exact ⟨a, fun k => (c.value k).property⟩

/-- Levelwise surjective quotient maps with finite fibers lift every quotient
branch, without assuming surjectivity for the parent maps. -/
theorem lift_branch (f : TowerMap T Q)
    (surjective : ∀ k, Function.Surjective (f.map k))
    (finite : ∀ k y, Finite {x : T.Level k // f.map k x = y})
    (b : Branch Q) :
    ∃ a : Branch T, ∀ k, f.map k (a.value k) = b.value k :=
  lift_branch_of_fibers f b (fun k => finite k (b.value k))
    (fun k => surjective k (b.value k))

/-- A finite codomain and finite fibers imply a finite domain. Surjectivity is
not needed here: the disjoint union of the fibers already enumerates it. -/
theorem finite_of_fibers {A B : Type*} (f : A → B) [Finite B]
    (finite : ∀ y, Finite {x : A // f x = y}) : Finite A := by
  let : ∀ y, Finite {x : A // f x = y} := finite
  exact Finite.of_equiv _ (Equiv.sigmaFiberEquiv f)

/-- Finitely many classes, each with finitely many representatives, give a
finite actual level. This does not infer finiteness from coefficient rings alone. -/
theorem finite_domain_levels (f : TowerMap T Q)
    (classes : ∀ k, Finite (Q.Level k))
    (fibers : ∀ k y, Finite {x : T.Level k // f.map k x = y}) :
    ∀ k, Finite (T.Level k) := by
  intro k
  let : Finite (Q.Level k) := classes k
  exact finite_of_fibers (f.map k) (fibers k)

end PaperX.FiniteFiberBranches
