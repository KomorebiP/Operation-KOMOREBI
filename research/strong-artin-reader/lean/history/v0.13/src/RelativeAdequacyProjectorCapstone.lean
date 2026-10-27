import RelativeSpectralDetection
import FiniteProjectorProbeExtraction

namespace Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone

open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.AdequateProjectorCyclicObstruction
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ActualProjectorCyclicObstruction
open Komorebi.StrongArtin.CyclicTransverseObstruction
open Komorebi.StrongArtin.FiniteProjectorProbeExtraction

noncomputable section

variable {k G W ι : Type*} [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι]

/-- Relative spectral detection away from the scalar cyclic line already gives
raw separation of all projector traces once one reference projector has nonzero
trace. -/
theorem raw_separation_of_relative_spectral_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P) :
    ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0 := by
  apply raw_projector_traces_separate_of_simple_packet_detection ρ P hP
  exact spectralProjectorDetectsEverySimplePacket_of_offScalar ρ P i0 href hoff

/-- **Relative-adequacy quotient-prime obstruction theorem.** Full ordinary
adequacy is not required at the linear-algebra layer: it is enough to detect
every simple conjugation packet outside the retained scalar/cyclic line and to
have one nonzero-trace reference projector. Then the complete first-order
obstruction vanishes exactly when the cyclic residual vanishes. -/
theorem full_obstruction_eq_zero_iff_cyclic_residual_zero_of_relative_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (b : k × Module.Dual k
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))) :
    obstructionClass
        (blockJacobian (0 : k →ₗ[k] k)
          (centeredProjectorCorrectionMap P i0 href)) b = 0 ↔
      b.1 = 0 := by
  apply full_obstruction_eq_zero_iff_cyclic_residual_zero_of_projector_detection
  exact raw_separation_of_relative_spectral_detection ρ P i0 href hP hoff

/-- Exactly one first-order obstruction dimension survives under relative
spectral detection: the deliberately retained scalar/cyclic defect. -/
theorem full_obstruction_finrank_eq_one_of_relative_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P) :
    Module.finrank k
      ((k × Module.Dual k
          (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))) ⧸
        LinearMap.range
          (blockJacobian (0 : k →ₗ[k] k)
            (centeredProjectorCorrectionMap P i0 href))) = 1 := by
  apply full_obstruction_finrank_eq_one_of_projector_detection P i0 href
  exact raw_separation_of_relative_spectral_detection ρ P i0 href hP hoff

/-- **Finite relative Taylor--Wiles target.** Under only relative spectral
packet detection, a finite basis of actual centered quotient-projector probes
exists. Its cardinality is exactly the transverse deformation dimension. -/
theorem exists_finite_transverse_projector_probe_basis_of_relative_detection
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P) :
    ∃ t : Finset (Module.Dual k
        (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))),
      (t : Set (Module.Dual k
        (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))) ⊆
          Set.range (centeredQuotientProjectorProbe P i0 href) ∧
      t.card = Module.finrank k
        (Module.End k W ⧸ (k ∙ (1 : Module.End k W))) ∧
      Submodule.span k (t : Set (Module.Dual k
        (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))) = ⊤ ∧
      LinearIndepOn k
        (fun x : Module.Dual k
          (Module.End k W ⧸ (k ∙ (1 : Module.End k W))) => x)
        (t : Set (Module.Dual k
          (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))) := by
  apply exists_finite_transverse_projector_probe_basis ρ P i0 href hP
  exact spectralProjectorDetectsEverySimplePacket_of_offScalar ρ P i0 href hoff

end
end Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone

#print axioms Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone.raw_separation_of_relative_spectral_detection
#print axioms Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone.full_obstruction_eq_zero_iff_cyclic_residual_zero_of_relative_detection
#print axioms Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone.full_obstruction_finrank_eq_one_of_relative_detection
#print axioms Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone.exists_finite_transverse_projector_probe_basis_of_relative_detection
