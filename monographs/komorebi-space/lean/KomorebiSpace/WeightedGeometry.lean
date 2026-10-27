import Mathlib.CategoryTheory.Preadditive.Basic
import Mathlib.Basic.ENNReal.Operations

set_option autoImplicit false

/-!
# Optional directed geometry from an independently specified transport cost

A cost is extra data. It must not be silently identified with a compatibility
residual: all zero transports are compatible in the additive setting.
-/
universe u v
namespace KomorebiSpace
open CategoryTheory CategoryTheory.Limits
open scoped ENNReal
noncomputable section

structure TransportCost (C : Type u) [Category.{v} C] where
  cost : {A B : C} → (A ⟶ B) → ℝ≥0∞
  id_zero : ∀ A, cost (𝟙 A) = 0
  comp_le : ∀ {A B D : C} (f : A ⟶ B) (g : B ⟶ D),
    cost (f ≫ g) ≤ cost f + cost g

namespace TransportCost
variable {C : Type u} [Category.{v} C]

def distance (W : TransportCost C) (A B : C) : ℝ≥0∞ := ⨅ f : A ⟶ B, W.cost f

theorem distance_le_cost (W : TransportCost C) {A B : C} (f : A ⟶ B) :
    W.distance A B ≤ W.cost f := iInf_le _ f

@[simp] theorem distance_self (W : TransportCost C) (A : C) : W.distance A A = 0 := by
  apply le_antisymm _ bot_le
  exact (W.distance_le_cost (𝟙 A)).trans_eq (W.id_zero A)

theorem distance_triangle (W : TransportCost C) (A B D : C) :
    W.distance A D ≤ W.distance A B + W.distance B D := by
  apply ENNReal.le_iInf_add_iInf
  intro f g
  exact (W.distance_le_cost (f ≫ g)).trans (W.comp_le f g)

theorem zero_cost_distance (W : TransportCost C) {A B : C}
    (f : A ⟶ B) (hf : W.cost f = 0) : W.distance A B = 0 := by
  exact le_antisymm ((W.distance_le_cost f).trans_eq hf) bot_le

/-- Diagnostic: compatible zero arrows collapse this proposed geometry. -/
theorem collapse_of_zero_arrows [HasZeroMorphisms C] (W : TransportCost C)
    (hzero : ∀ A B, W.cost (0 : A ⟶ B) = 0) (A B : C) :
    W.distance A B = 0 := W.zero_cost_distance 0 (hzero A B)

def symDistance (W : TransportCost C) (A B : C) : ℝ≥0∞ :=
  max (W.distance A B) (W.distance B A)

@[simp] theorem symDistance_self (W : TransportCost C) (A : C) :
    W.symDistance A A = 0 := by simp [symDistance]

theorem symDistance_comm (W : TransportCost C) (A B : C) :
    W.symDistance A B = W.symDistance B A := max_comm _ _

theorem symDistance_triangle (W : TransportCost C) (A B D : C) :
    W.symDistance A D ≤ W.symDistance A B + W.symDistance B D := by
  apply max_le
  · exact (W.distance_triangle A B D).trans
      (add_le_add (le_max_left _ _) (le_max_left _ _))
  · calc
      W.distance D A ≤ W.distance D B + W.distance B A := W.distance_triangle D B A
      _ ≤ W.symDistance B D + W.symDistance A B :=
        add_le_add (le_max_right _ _) (le_max_right _ _)
      _ = W.symDistance A B + W.symDistance B D := add_comm _ _

/-- Zero symmetric cost is an equivalence relation, not an isomorphism criterion. -/
def zeroDistanceSetoid (W : TransportCost C) : Setoid C where
  r := fun A B => W.symDistance A B = 0
  iseqv := ⟨W.symDistance_self,
    fun h => by simpa only [W.symDistance_comm] using h,
    fun {A B D} hAB hBD => by
      apply le_antisymm _ bot_le
      change W.symDistance A D ≤ (0 : ENNReal)
      have ht := W.symDistance_triangle A B D
      simpa only [hAB, hBD, zero_add] using ht⟩

end TransportCost
end
end KomorebiSpace
