import ContinuousObstructionExamples
import Mathlib.Topology.Compactness.Compact
namespace Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples
local instance (n : ℕ) : TopologicalSpace (ZMod n) := ⊥
local instance (n : ℕ) : DiscreteTopology (ZMod n) := ⟨rfl⟩
#synth Infinite ProductSource
#synth CompactSpace ProductSource
#check not_finite
#check not_finite_iff_infinite
#check finite_of_compact_of_discrete
example : ¬ DiscreteTopology ProductSource := by
  intro h
  have : DiscreteTopology ProductSource := h
  have : Finite ProductSource := finite_of_compact_of_discrete
  exact not_finite ProductSource
end Komorebi.StrongArtin.SquareZeroH2.ContinuousExamples
