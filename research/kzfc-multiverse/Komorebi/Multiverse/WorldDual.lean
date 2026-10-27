import Komorebi.Multiverse.WorldNetwork

/-!
# Upward and downward multiverse geometry

If `reach a b` means that `b` is an admissible extension of `a`, then common
upper worlds model upward amalgamation while common lower worlds model common
grounds.  The dual network exchanges these two directions exactly.
-/

universe u

namespace Komorebi.Multiverse
namespace WorldNetwork

variable (N : WorldNetwork.{u})

/-- Common lower world, interpreted as a common ground when `reach` is extension. -/
def CommonLower (s : Finset N.World) (g : N.World) : Prop :=
  ∀ w ∈ s, N.reach g w

/-- A family has a common ground/lower world. -/
def JointGroundable (s : Finset N.World) : Prop :=
  ∃ g, N.CommonLower s g

/-- Reverse every accessibility arrow. -/
def dual : WorldNetwork where
  World := N.World
  reach := fun a b => N.reach b a
  refl := N.refl
  trans := fun hab hbc => N.trans hbc hab

@[simp]
theorem dual_dual_reach (a b : N.World) :
    N.dual.dual.reach a b ↔ N.reach a b := Iff.rfl

/-- Upward amalgamation in the dual network is exactly common-ground compatibility. -/
theorem dual_joint_iff_groundable (s : Finset N.World) :
    N.dual.JointAmalgamable s ↔ N.JointGroundable s := Iff.rfl

/-- Groundability is downward closed on finite families. -/
theorem groundable_downward {s t : Finset N.World} (hst : s ⊆ t)
    (ht : N.JointGroundable t) : N.JointGroundable s := by
  obtain ⟨g, hg⟩ := ht
  exact ⟨g, fun w hw => hg w (hst hw)⟩

end WorldNetwork
end Komorebi.Multiverse
