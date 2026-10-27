import AdequateProbeDetection
import ProjectorTraceTransverse

namespace Komorebi.StrongArtin.ConjugationProjectorProbes

open Komorebi.StrongArtin.ProjectorTraceTransverse

noncomputable section

variable {k G W ι : Type*} [Field k] [Group G]
  [AddCommGroup W] [Module k W]
  [MulAction G ι]

/-- Conjugation of endomorphisms by a linear representation. -/
def conjugationRepresentation (ρ : Representation k G W) :
    Representation k G (Module.End k W) where
  toFun g := LinearMap.mulLeftRight k (ρ g, ρ g⁻¹)
  map_one' := by
    ext X
    simp
  map_mul' g h := by
    ext X
    simp [mul_assoc]

@[simp] theorem conjugationRepresentation_apply
    (ρ : Representation k G W) (g : G) (X : Module.End k W) :
    conjugationRepresentation ρ g X = ρ g * X * ρ g⁻¹ := rfl

/-- Spectral projectors indexed equivariantly by conjugacy data. -/
def ProjectorCovariant
    (ρ : Representation k G W)
    (P : ι → Module.End k W) : Prop :=
  ∀ g i, P (g • i) = ρ g * P i * ρ g⁻¹

/-- Trace probes attached to a conjugation-covariant projector family are
covariant for the conjugation representation. This is the exact invariance
needed to make their common kernel a `G`-subrepresentation. -/
theorem projectorTraceProbe_covariant
    [FiniteDimensional k W]
    (ρ : Representation k G W)
    (P : ι → Module.End k W)
    (hP : ProjectorCovariant ρ P) :
    ∀ g i X,
      projectorTraceProbe (P (g • i))
          (conjugationRepresentation ρ g X) =
        projectorTraceProbe (P i) X := by
  intro g i X
  rw [projectorTraceProbe_apply, conjugationRepresentation_apply, hP g i]
  have hleft : ρ g⁻¹ * ρ g = (1 : Module.End k W) := by
    rw [← map_mul]
    simp
  calc
    LinearMap.trace k W ((ρ g * P i * ρ g⁻¹) * (ρ g * X * ρ g⁻¹))
        = LinearMap.trace k W (ρ g * (P i * X) * ρ g⁻¹) := by
            congr 1
            simp only [mul_assoc]
            rw [← mul_assoc (ρ g⁻¹) (ρ g) (X * ρ g⁻¹), hleft]
            simp
    _ = LinearMap.trace k W (P i * X) := by
          rw [LinearMap.trace_mul_comm k (ρ g * (P i * X)) (ρ g⁻¹)]
          simp only [← mul_assoc]
          rw [hleft]
          simp


end
end Komorebi.StrongArtin.ConjugationProjectorProbes

#print axioms Komorebi.StrongArtin.ConjugationProjectorProbes.conjugationRepresentation_apply
#print axioms Komorebi.StrongArtin.ConjugationProjectorProbes.projectorTraceProbe_covariant
