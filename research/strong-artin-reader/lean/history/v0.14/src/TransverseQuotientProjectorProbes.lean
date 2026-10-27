import TransverseAdjointRepresentation
import RelativeAdequacyProjectorCapstone

namespace Komorebi.StrongArtin.TransverseQuotientProjectorProbes

open Komorebi.StrongArtin.ProjectorProbeSurjectivity
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.RelativeSpectralDetection
open Komorebi.StrongArtin.RelativeAdequacyProjectorCapstone
open Komorebi.StrongArtin.TransverseAdjointRepresentation

noncomputable section

universe u i

variable {k G W : Type u} {ι : Type i}
  [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι]

/-- The centered trace probes attached to actual projectors, descended to the
adjoint quotient by the scalar/cyclic line. -/
def transverseProjectorProbe
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0) :
    ι → Module.Dual k (transverseAdjointRep ρ) :=
  quotientProbe
    (scalarLine (k := k) (W := W))
    (fun i => projectorTraceProbe (centeredProjector (P i) (P i0)))
    (fun i => by
      intro X hX
      rw [Submodule.mem_span_singleton] at hX
      rcases hX with ⟨a, rfl⟩
      exact centeredProjectorProbe_scalar_zero P i0 i href a)

omit [Fintype G] [FiniteDimensional k W] [MulAction G ι] in
@[simp] theorem transverseProjectorProbe_mk
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 i : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (X : Module.End k W) :
    transverseProjectorProbe ρ P i0 href i
        ((scalarLine (k := k) (W := W)).mkQ X) =
      projectorTraceProbe (centeredProjector (P i) (P i0)) X := by
  rfl

/-- Under the v0.13 relative spectral hypothesis, the descended centered
projector traces separate the transverse adjoint quotient itself. -/
theorem transverseProjectorProbes_separate
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P) :
    ∀ q : transverseAdjointRep ρ,
      (∀ i : ι, transverseProjectorProbe ρ P i0 href i q = 0) → q = 0 := by
  have hraw : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0 :=
    raw_separation_of_relative_spectral_detection ρ P i0 href hP hoff
  apply quotientProbe_separates_of_kernel_le_defect
  intro X hX
  have hker := centeredProjectorProbes_joint_kernel_eq_scalarLine
    P i0 href hraw
  have hm : X ∈ {Y : Module.End k W |
      ∀ i : ι,
        projectorTraceProbe (centeredProjector (P i) (P i0)) Y = 0} := hX
  rw [hker] at hm
  exact hm

/-- Consequently every nonzero class of the transverse quotient is detected by
one actual centered spectral-projector trace. -/
theorem exists_transverseProjectorProbe_ne_zero
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hoff : DetectsEverySimplePacketOffScalar ρ P)
    (q : transverseAdjointRep ρ)
    (hq : q ≠ 0) :
    ∃ i : ι, transverseProjectorProbe ρ P i0 href i q ≠ 0 := by
  by_contra h
  push Not at h
  exact hq (transverseProjectorProbes_separate ρ P i0 href hP hoff q h)

end
end Komorebi.StrongArtin.TransverseQuotientProjectorProbes

#print axioms Komorebi.StrongArtin.TransverseQuotientProjectorProbes.transverseProjectorProbes_separate
#print axioms Komorebi.StrongArtin.TransverseQuotientProjectorProbes.exists_transverseProjectorProbe_ne_zero
