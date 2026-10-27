import AdequateProjectorCyclicObstruction
import FiniteProbeExtraction

namespace Komorebi.StrongArtin.FiniteProjectorProbeExtraction

open Komorebi.StrongArtin.AdequateProjectorCyclicObstruction
open Komorebi.StrongArtin.ConjugationProjectorProbes
open Komorebi.StrongArtin.ProjectorTraceTransverse
open Komorebi.StrongArtin.ProjectorProbeSurjectivity
open Komorebi.StrongArtin.FiniteProbeExtraction

noncomputable section

variable {k G W ι : Type*} [Field k] [Group G] [Fintype G]
  [AddCommGroup W] [Module k W] [FiniteDimensional k W]
  [MulAction G ι]

/-- The actual centered spectral-projector probes descended to the quotient by
the scalar/cyclic defect line. -/
def centeredQuotientProjectorProbe
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0) :
    ι → Module.Dual k
      (Module.End k W ⧸ (k ∙ (1 : Module.End k W))) :=
  quotientProbe
    (k ∙ (1 : Module.End k W))
    (fun i => projectorTraceProbe (centeredProjector (P i) (P i0)))
    (fun i => by
      intro X hX
      rw [Submodule.mem_span_singleton] at hX
      rcases hX with ⟨a, rfl⟩
      exact centeredProjectorProbe_scalar_zero P i0 i href a)

/-- Under conjugation covariance and simple-packet detection, the centered
projector probes separate the quotient by the scalar/cyclic line. -/
theorem centeredQuotientProjectorProbe_separates
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hdet : SpectralProjectorDetectsEverySimplePacket ρ P) :
    ∀ q : Module.End k W ⧸ (k ∙ (1 : Module.End k W)),
      (∀ i : ι, centeredQuotientProjectorProbe P i0 href i q = 0) → q = 0 := by
  let D : Submodule k (Module.End k W) := k ∙ (1 : Module.End k W)
  let C : ι → Module.Dual k (Module.End k W) :=
    fun i => projectorTraceProbe (centeredProjector (P i) (P i0))
  have hraw : ∀ X : Module.End k W,
      (∀ i : ι, projectorTraceProbe (P i) X = 0) → X = 0 :=
    raw_projector_traces_separate_of_simple_packet_detection ρ P hP hdet
  have hker := centeredProjectorProbes_joint_kernel_eq_scalarLine P i0 href hraw
  have hvan : ∀ i : ι, D ≤ LinearMap.ker (C i) := by
    intro i X hX
    change projectorTraceProbe (centeredProjector (P i) (P i0)) X = 0
    rw [Submodule.mem_span_singleton] at hX
    rcases hX with ⟨a, rfl⟩
    exact centeredProjectorProbe_scalar_zero P i0 i href a
  have hsepD : ∀ X : Module.End k W, (∀ i : ι, C i X = 0) → X ∈ D := by
    intro X hX
    have hm : X ∈ {Y : Module.End k W | ∀ i : ι, C i Y = 0} := hX
    change X ∈ (D : Set (Module.End k W))
    simpa [C, D] using (show X ∈ (k ∙ (1 : Module.End k W) : Set (Module.End k W)) by
      rw [← hker]
      exact hm)
  change ∀ q, (∀ i, quotientProbe D C hvan i q = 0) → q = 0
  exact quotientProbe_separates_of_kernel_le_defect D C hvan hsepD

/-- **Finite Taylor--Wiles probe extraction.** The infinite/ambient
spectral-projector family contains a finite linearly independent family of
actual centered quotient probes spanning the complete transverse dual. The
number selected is exactly the transverse deformation dimension. -/
theorem exists_finite_transverse_projector_probe_basis
    (ρ : Representation k G W)
    (P : ι → Module.End k W) (i0 : ι)
    (href : LinearMap.trace k W (P i0) ≠ 0)
    (hP : ProjectorCovariant ρ P)
    (hdet : SpectralProjectorDetectsEverySimplePacket ρ P) :
    ∃ t : Finset (Module.Dual k
        (Module.End k W ⧸ (k ∙ (1 : Module.End k W)))),
      (t : Set (Module.Dual k (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))) ⊆ Set.range (centeredQuotientProjectorProbe P i0 href) ∧
      t.card = Module.finrank k
        (Module.End k W ⧸ (k ∙ (1 : Module.End k W))) ∧
      Submodule.span k (t : Set (Module.Dual k (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))) = ⊤ ∧
      LinearIndepOn k (fun x : Module.Dual k (Module.End k W ⧸ (k ∙ (1 : Module.End k W))) => x) (t : Set (Module.Dual k (Module.End k W ⧸ (k ∙ (1 : Module.End k W))))) := by
  apply exists_finite_probe_basis_of_separates
    (centeredQuotientProjectorProbe P i0 href)
  exact centeredQuotientProjectorProbe_separates ρ P i0 href hP hdet

end
end Komorebi.StrongArtin.FiniteProjectorProbeExtraction

#print axioms Komorebi.StrongArtin.FiniteProjectorProbeExtraction.centeredQuotientProjectorProbe_separates
#print axioms Komorebi.StrongArtin.FiniteProjectorProbeExtraction.exists_finite_transverse_projector_probe_basis
