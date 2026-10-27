import CenteredProbeTransverse
import Mathlib.LinearAlgebra.Trace

namespace Komorebi.StrongArtin.ProjectorTraceTransverse

open Komorebi.StrongArtin.CenteredProbeTransverse
open Komorebi.StrongArtin.ProjectorProbeSurjectivity

noncomputable section

variable {k W ι : Type*} [Field k]
  [AddCommGroup W] [Module k W]

/-- The trace-pairing probe associated with an endomorphism `P`: `X ↦ tr(PX)`.
For the Strong Artin application `P` is a generalized-eigenspace projector. -/
def projectorTraceProbe (P : Module.End k W) : Module.Dual k (Module.End k W) :=
  (LinearMap.trace k W).comp (LinearMap.mulLeft k P)

@[simp] theorem projectorTraceProbe_apply
    (P X : Module.End k W) :
    projectorTraceProbe P X = LinearMap.trace k W (P * X) := rfl

@[simp] theorem projectorTraceProbe_id
    (P : Module.End k W) :
    projectorTraceProbe P (1 : Module.End k W) = LinearMap.trace k W P := by
  simp [projectorTraceProbe]

/-- Center a projector against a reference endomorphism with nonzero trace. -/
def centeredProjector (P P0 : Module.End k W) : Module.End k W :=
  P - (LinearMap.trace k W P / LinearMap.trace k W P0) • P0

/-- The centered projector has zero trace when the reference trace is nonzero. -/
theorem trace_centeredProjector_zero
    (P P0 : Module.End k W)
    (href : LinearMap.trace k W P0 ≠ 0) :
    LinearMap.trace k W (centeredProjector P P0) = 0 := by
  simp [centeredProjector]
  field_simp [href]
  ring

/-- Centering the trace probes against the scalar identity defect is literally
trace pairing with the centered projector combinations. -/
theorem centeredProbe_eq_projectorTraceProbe_centeredProjector
    (P : ι → Module.End k W) (i0 i : ι) :
    centeredProbe (fun j => projectorTraceProbe (P j)) i0 (1 : Module.End k W) i =
      projectorTraceProbe (centeredProjector (P i) (P i0)) := by
  ext X
  simp [centeredProbe, centeredProjector, projectorTraceProbe, sub_mul]

/-- Every centered spectral-projector probe kills every scalar endomorphism. -/
theorem centeredProjectorProbe_scalar_zero
    (P : ι → Module.End k W) (i0 i : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (a : k) :
    projectorTraceProbe (centeredProjector (P i) (P i0))
      (a • (1 : Module.End k W)) = 0 := by
  rw [← centeredProbe_eq_projectorTraceProbe_centeredProjector P i0 i]
  have href' : projectorTraceProbe (P i0) (1 : Module.End k W) ≠ 0 := by
    simpa using href
  have hline := defectLine_le_centeredProbe_kernel
    (fun j => projectorTraceProbe (P j)) i0 i
    (1 : Module.End k W) href'
  apply hline
  exact Submodule.smul_mem _ a (Submodule.mem_span_singleton_self _)

/-- **Actual-projector transverse separation.** If the original spectral-projector
trace probes separate the ambient endomorphism deformation space and one
projector has nonzero trace, then the centered projector probes have joint
kernel exactly the scalar line.

This is the concrete trace-projector realization of the abstract centering
lemma. -/
theorem centeredProjectorProbes_joint_kernel_eq_scalarLine
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hsep : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0) :
    {X : Module.End k W |
      ∀ i : ι, projectorTraceProbe (centeredProjector (P i) (P i0)) X = 0} =
      (k ∙ (1 : Module.End k W) : Set (Module.End k W)) := by
  have href' : projectorTraceProbe (P i0) (1 : Module.End k W) ≠ 0 := by
    simpa using href
  have h := centeredProbe_joint_kernel_eq_defectLine
    (fun j => projectorTraceProbe (P j)) i0
    (1 : Module.End k W) href' hsep
  simpa [centeredProbe_eq_projectorTraceProbe_centeredProjector P i0] using h

/-- Consequently the centered actual projector probes generate all dual
transverse directions modulo the scalar/cyclic line. -/
theorem centeredProjectorProbes_transverse_dual_surjective
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hsep : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0) :
    Function.Surjective
      (probeEvalMap
        (quotientProbe
          (k ∙ (1 : Module.End k W))
          (fun i => projectorTraceProbe (centeredProjector (P i) (P i0)))
          (fun i => by
            intro X hX
            rw [Submodule.mem_span_singleton] at hX
            rcases hX with ⟨a, rfl⟩
            exact centeredProjectorProbe_scalar_zero P i0 i href a))).dualMap := by
  apply dual_quotientProbe_surjective_of_kernel_le_defect
  intro X hX
  have hker := centeredProjectorProbes_joint_kernel_eq_scalarLine P i0 href hsep
  have hm : X ∈ {X : Module.End k W |
      ∀ i : ι, projectorTraceProbe (centeredProjector (P i) (P i0)) X = 0} := hX
  rw [hker] at hm
  exact hm

end
end Komorebi.StrongArtin.ProjectorTraceTransverse

#print axioms Komorebi.StrongArtin.ProjectorTraceTransverse.trace_centeredProjector_zero
#print axioms Komorebi.StrongArtin.ProjectorTraceTransverse.centeredProbe_eq_projectorTraceProbe_centeredProjector
#print axioms Komorebi.StrongArtin.ProjectorTraceTransverse.centeredProjectorProbe_scalar_zero
#print axioms Komorebi.StrongArtin.ProjectorTraceTransverse.centeredProjectorProbes_joint_kernel_eq_scalarLine
#print axioms Komorebi.StrongArtin.ProjectorTraceTransverse.centeredProjectorProbes_transverse_dual_surjective
