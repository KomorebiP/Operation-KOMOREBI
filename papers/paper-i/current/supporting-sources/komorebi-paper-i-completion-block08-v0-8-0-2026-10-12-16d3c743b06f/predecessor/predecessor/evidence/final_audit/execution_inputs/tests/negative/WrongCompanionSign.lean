import ScalarExtensionBoundaryConsumers
open PaperIBlock03Tests PaperIBlock06Tests
open Komorebi.PaperICompletion6.OneInvariantFactor
example : companionMatrix quadratic ⟨0, by rw [quadratic_degree]; decide⟩
    ⟨1, by rw [quadratic_degree]; decide⟩ = (1 : ℚ) :=
  quadratic_companion_entries.2.2.1
