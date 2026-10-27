module
public import ConcreteLogical
public import StreamBoundary
open Komorebi.LogicalResolution
example : constantSystem.step () false = false := rfl
example : ¬ (∃ f : Formula Unit Unit Bool 2, ∀ x y : Nat → Bool,
    f.Holds streamSystem (pairEnv x y) ↔ Komorebi.Representation.ObsEq streamSystem x y) := by
  exact stream_behavior_not_finitely_definable
