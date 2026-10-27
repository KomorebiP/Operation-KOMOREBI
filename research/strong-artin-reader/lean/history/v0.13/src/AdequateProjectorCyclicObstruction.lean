import AdequateProbeDetection
import ConjugationProjectorProbes
import ActualProjectorCyclicObstruction

namespace Komorebi.StrongArtin.AdequateProjectorCyclicObstruction

open Komorebi.StrongArtin.AdequateProbeDetection
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ActualProjectorCyclicObstruction
open Komorebi.StrongArtin.CyclicTransverseObstruction

noncomputable section

variable {k G W ι : Type*} [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι]

/-- The precise representation-theoretic spectral detection hypothesis used by
this block: every simple invariant packet for conjugation on `End(W)` is seen by
one trace-projector probe. This isolates the projector clause from the other
(global/cohomological) hypotheses of automorphy lifting. -/
def SpectralProjectorDetectsEverySimplePacket
    (ρ : Representation k G W)
    (P : ι → Module.End k W) : Prop :=
  DetectsEverySimplePacket
    (conjugationRepresentation ρ)
    (fun i => projectorTraceProbe (P i))

/-- Conjugation covariance plus simple-packet projector detection implies that
the raw trace-projector family jointly separates the full endomorphism space. -/
theorem raw_projector_traces_separate_of_simple_packet_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W)
    (hP : ProjectorCovariant ρ P)
    (hdet : SpectralProjectorDetectsEverySimplePacket ρ P) :
    ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0 := by
  apply separates_of_detectsEverySimplePacket
    (conjugationRepresentation ρ)
    (fun i => projectorTraceProbe (P i))
  · exact projectorTraceProbe_covariant ρ P hP
  · exact hdet

/-- Hence, after centering against one projector with nonzero trace, the actual
projector correction map is surjective on the quotient by the scalar/cyclic
defect direction. -/
theorem centered_projector_transverse_surjective_of_simple_packet_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W)
    (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hdet : SpectralProjectorDetectsEverySimplePacket ρ P) :
    Function.Surjective (centeredProjectorCorrectionMap P i0 href) := by
  apply centeredProjectorCorrectionMap_surjective P i0 href
  exact raw_projector_traces_separate_of_simple_packet_detection ρ P hP hdet

/-- **Adequacy-projector quotient-prime obstruction capstone.** Under the
simple-packet spectral detection clause and conjugation covariance, all
first-order transverse obstruction directions are removed. The full obstruction
vanishes exactly when the retained scalar cyclic residual vanishes. -/
theorem full_obstruction_eq_zero_iff_cyclic_residual_zero_of_simple_packet_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W)
    (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hdet : SpectralProjectorDetectsEverySimplePacket ρ P)
    (b : k × Module.Dual k
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))) :
    obstructionClass
        (blockJacobian (0 : k →ₗ[k] k)
          (centeredProjectorCorrectionMap P i0 href)) b = 0 ↔
      b.1 = 0 := by
  apply full_obstruction_eq_zero_iff_cyclic_residual_zero_of_projector_detection
  exact raw_projector_traces_separate_of_simple_packet_detection ρ P hP hdet

/-- Numerical form of the capstone: exactly one first-order obstruction
dimension remains after simple-packet spectral detection, namely the scalar
cyclic defect. -/
theorem full_obstruction_finrank_eq_one_of_simple_packet_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W)
    (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hdet : SpectralProjectorDetectsEverySimplePacket ρ P) :
    Module.finrank k
      ((k × Module.Dual k
          (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))) ⧸
        LinearMap.range
          (blockJacobian (0 : k →ₗ[k] k)
            (centeredProjectorCorrectionMap P i0 href))) = 1 := by
  apply full_obstruction_finrank_eq_one_of_projector_detection P i0 href
  exact raw_projector_traces_separate_of_simple_packet_detection ρ P hP hdet

end
end Komorebi.StrongArtin.AdequateProjectorCyclicObstruction

#print axioms Komorebi.StrongArtin.AdequateProjectorCyclicObstruction.raw_projector_traces_separate_of_simple_packet_detection
#print axioms Komorebi.StrongArtin.AdequateProjectorCyclicObstruction.centered_projector_transverse_surjective_of_simple_packet_detection
#print axioms Komorebi.StrongArtin.AdequateProjectorCyclicObstruction.full_obstruction_eq_zero_iff_cyclic_residual_zero_of_simple_packet_detection
#print axioms Komorebi.StrongArtin.AdequateProjectorCyclicObstruction.full_obstruction_finrank_eq_one_of_simple_packet_detection
