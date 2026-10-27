import KomorebiPhysics.CurrentSummationExamples
import KomorebiPhysics.InfiniteCoarseExamples
namespace Control_InfiniteCellWrongEnergy
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (coarse harmonicEigenvalue).atlas.energy (coherentState : Space) 0 = 9/25 := by
  rw [even_probability]
  norm_num
end
end Control_InfiniteCellWrongEnergy

namespace Control_InfiniteCellWrongDerivative
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : HasDerivAt (fun t => (coarse harmonicEigenvalue).atlas.energy
    (evolution harmonicEigenvalue t (coherentState : Space)) 0) (-288/625) 0 := by
  apply even_probability_hasDerivAt.congr_deriv
  norm_num
end
end Control_InfiniteCellWrongDerivative

namespace Control_InfiniteCoarseCurrentsZero
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (coarse harmonicEigenvalue).current coherentState 0 1 = 0 := by
  rw [current_even_from_odd]
  norm_num
end
end Control_InfiniteCoarseCurrentsZero

namespace Control_InfiniteParityCellFinite
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (parity ⁻¹' {(0 : Fin 2)}).Finite := by
  have hn : ¬ (parity ⁻¹' {(0 : Fin 2)}).Finite := even_fiber_infinite
  simp only [hn]
end
end Control_InfiniteParityCellFinite

namespace Control_RowwiseSummabilityIsJoint
open KomorebiPhysics.CurrentSummationExamples
noncomputable section
example : (∀ i : Label, Summable (cycles i)) →
    Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro _
  simp only [not_joint_summable]
end
end Control_RowwiseSummabilityIsJoint

namespace Control_IteratedSumsAreJoint
open KomorebiPhysics.CurrentSummationExamples
open scoped BigOperators
noncomputable section
example : (HasSum (fun i : Label => ∑' j, cycles i j) 0 ∧
    HasSum (fun j : Label => ∑' i, cycles i j) 0) →
    Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro _
  simp only [not_joint_summable]
end
end Control_IteratedSumsAreJoint
