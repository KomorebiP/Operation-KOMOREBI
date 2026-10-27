import AdequateProjectorCyclicObstruction

namespace Komorebi.StrongArtin.RelativeSpectralDetection

open Komorebi.StrongArtin.AdequateProbeDetection
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.AdequateProjectorCyclicObstruction

noncomputable section

variable {k G W ι : Type*} [Field k] [Group G]
  [AddCommGroup W] [Module k W]

/-- Relative spectral detection: every simple conjugation packet which is not
contained in the scalar/cyclic defect line is detected by some projector trace.
Unlike ordinary adequacy, this deliberately allows the scalar defect itself to
survive as a distinguished direction. -/
def DetectsEverySimplePacketOffScalar
    (ρ : Representation k G W)
    (P : ι → Module.End k W) : Prop :=
  ∀ S : (conjugationRepresentation ρ).invtSubmodule, IsAtom S →
    ¬ ((S : Submodule k (Module.End k W)) ≤
      k ∙ (1 : Module.End k W)) →
    ∃ i : ι, ∃ X : Module.End k W,
      X ∈ (S : Submodule k (Module.End k W)) ∧
      projectorTraceProbe (P i) X ≠ 0

/-- A reference projector of nonzero trace detects every nonzero simple packet
that is contained in the scalar line. -/
theorem scalar_simple_packet_detected_by_reference
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (S : (conjugationRepresentation ρ).invtSubmodule)
    (hSatom : IsAtom S)
    (hSscalar : (S : Submodule k (Module.End k W)) ≤
      k ∙ (1 : Module.End k W)) :
    ∃ X : Module.End k W,
      X ∈ (S : Submodule k (Module.End k W)) ∧
      projectorTraceProbe (P i0) X ≠ 0 := by
  have hSsub_ne : (S : Submodule k (Module.End k W)) ≠ ⊥ := by
    intro hbot
    apply hSatom.ne_bot
    ext X
    change X ∈ (S : Submodule k (Module.End k W)) ↔ X ∈ (⊥ : Submodule k (Module.End k W))
    rw [hbot]
  obtain ⟨X, hXS, hXbot⟩ :=
    SetLike.exists_of_lt (bot_lt_iff_ne_bot.mpr hSsub_ne)
  have hXne : X ≠ 0 := by
    intro hX0
    subst X
    exact hXbot (by simp)
  have hXD : X ∈ k ∙ (1 : Module.End k W) := hSscalar hXS
  rw [Submodule.mem_span_singleton] at hXD
  rcases hXD with ⟨a, ha⟩
  have hane : a ≠ 0 := by
    intro ha0
    apply hXne
    rw [← ha]
    simp [ha0]
  refine ⟨X, hXS, ?_⟩
  rw [← ha]
  simp only [map_smul, projectorTraceProbe_id]
  exact mul_ne_zero hane href

/-- **Relative adequacy closure.** Detecting every simple packet off the scalar
cyclic defect, together with one nonzero-trace reference projector, implies
full simple-packet detection for the raw projector traces. No assumption
`char(k) ∤ dim(W)` is required. -/
theorem spectralProjectorDetectsEverySimplePacket_of_offScalar
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hoff : DetectsEverySimplePacketOffScalar ρ P) :
    SpectralProjectorDetectsEverySimplePacket ρ P := by
  intro S hSatom
  by_cases hSscalar : (S : Submodule k (Module.End k W)) ≤
      k ∙ (1 : Module.End k W)
  · obtain ⟨X, hXS, hXne⟩ :=
      scalar_simple_packet_detected_by_reference ρ P i0 href S hSatom hSscalar
    exact ⟨i0, X, hXS, hXne⟩
  · exact hoff S hSatom hSscalar

end
end Komorebi.StrongArtin.RelativeSpectralDetection

#print axioms Komorebi.StrongArtin.RelativeSpectralDetection.scalar_simple_packet_detected_by_reference
#print axioms Komorebi.StrongArtin.RelativeSpectralDetection.spectralProjectorDetectsEverySimplePacket_of_offScalar
