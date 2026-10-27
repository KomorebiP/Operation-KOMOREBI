import Komorebi.Multiverse.WorldNetwork

/-!
# Transported data and compatibility residuals over world networks

A transport system assigns mathematical data to each world and coherent maps
along admissible reachability arrows.  Equality after transport is the
zero-residual condition.  The definitions make no assumption that all worlds
amalgamate.
-/

universe u v

namespace Komorebi.Multiverse

/-- Covariant data transported along world extensions. -/
structure TransportSystem (N : WorldNetwork.{u}) where
  Fiber : N.World → Type v
  map : ∀ {a b : N.World}, N.reach a b → Fiber a → Fiber b
  map_refl : ∀ (a : N.World) (x : Fiber a), map (N.refl a) x = x
  map_trans : ∀ {a b c : N.World} (hab : N.reach a b) (hbc : N.reach b c)
    (x : Fiber a), map (N.trans hab hbc) x = map hbc (map hab x)

namespace TransportSystem

variable {N : WorldNetwork.{u}} (F : TransportSystem.{u,v} N)

/-- Two local data are compatible at a specified common upper world. -/
def CompatibleAt {a b u : N.World} (hau : N.reach a u) (hbu : N.reach b u)
    (x : F.Fiber a) (y : F.Fiber b) : Prop :=
  F.map hau x = F.map hbu y

/-- Pairwise residual vanishing: there is some common world in which the two
transported data agree. -/
def PairCompatible {a b : N.World} (x : F.Fiber a) (y : F.Fiber b) : Prop :=
  ∃ u : N.World, ∃ hau : N.reach a u, ∃ hbu : N.reach b u,
    F.CompatibleAt hau hbu x y

/-- Data indexed by every member of a finite family of worlds. -/
structure LocalFamily (s : Finset N.World) where
  value : ∀ w : N.World, w ∈ s → F.Fiber w

/-- All local values glue at one common world to one transported value. -/
def JointCompatible {s : Finset N.World} (x : F.LocalFamily s) : Prop :=
  ∃ u : N.World, ∃ hu : N.CommonUpper s u, ∃ z : F.Fiber u,
    ∀ w (hw : w ∈ s), F.map (hu w hw) (x.value w hw) = z

/-- Every pair of local values has a zero residual in some common upper world. -/
def PairwiseCompatible {s : Finset N.World} (x : F.LocalFamily s) : Prop :=
  ∀ a (ha : a ∈ s) b (hb : b ∈ s), F.PairCompatible (x.value a ha) (x.value b hb)

/-- Higher data obstruction: all pairwise residuals vanish but there is no
single coherent joint realization. -/
def HigherDataObstruction {s : Finset N.World} (x : F.LocalFamily s) : Prop :=
  F.PairwiseCompatible x ∧ ¬ F.JointCompatible x

/-- Joint compatibility necessarily supplies an underlying world amalgamation. -/
theorem world_joint_of_data_joint {s : Finset N.World} {x : F.LocalFamily s}
    (h : F.JointCompatible x) : N.JointAmalgamable s := by
  obtain ⟨u, hu, _, _⟩ := h
  exact ⟨u, hu⟩

/-- Therefore an obstruction in the world geometry automatically blocks every
possible joint gluing of transported data over that family. -/
theorem not_jointCompatible_of_world_obstructed {s : Finset N.World}
    (h : N.Obstructed s) (x : F.LocalFamily s) : ¬ F.JointCompatible x := by
  intro hx
  exact h (F.world_joint_of_data_joint hx)

/-- A jointly compatible family is pairwise compatible. -/
theorem pairwiseCompatible_of_joint {s : Finset N.World} {x : F.LocalFamily s}
    (h : F.JointCompatible x) : F.PairwiseCompatible x := by
  obtain ⟨u, hu, z, hz⟩ := h
  intro a ha b hb
  refine ⟨u, hu a ha, hu b hb, ?_⟩
  exact (hz a ha).trans (hz b hb).symm

/-- Constant transport system: the same type and identity transport in every world. -/
def constant (N : WorldNetwork.{u}) (A : Type v) : TransportSystem N where
  Fiber := fun _ => A
  map := fun _ x => x
  map_refl := fun _ _ => rfl
  map_trans := fun _ _ _ => rfl

end TransportSystem
end Komorebi.Multiverse
