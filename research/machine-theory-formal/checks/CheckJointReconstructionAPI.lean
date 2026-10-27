import MachineTheory.JointReconstruction
import MachineTheory.JointReconstructionExamples

/-! Source-facing restatements retain actual linear maps and full-domain decoders. -/
open Komorebi.MachineTheory

section General
variable {K V W T : Type*} [Field K]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
variable [AddCommGroup T] [Module K T]

example (A : V →ₗ[K] W) (Q : V →ₗ[K] T) :
    (∃ D : W →ₗ[K] T, Q = D.comp A) ↔ LinearMap.ker A ≤ LinearMap.ker Q :=
  JointReconstruction.exists_decoder_iff_ker_le A Q

example (A : V →ₗ[K] W) :
    (∃ D : W →ₗ[K] V, LinearMap.id = D.comp A) ↔ Function.Injective A :=
  JointReconstruction.full_state_iff_injective A

example (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) :
    ∃ D : W →ₗ[K] T,
      D.comp (LinearMap.range A).subtype = JointReconstruction.imageDecoder A Q h :=
  JointReconstruction.exists_decoder_extending_imageDecoder A Q h

example {ι : Type*} [Fintype ι] [FiniteDimensional K V] {R : ι → Type*}
    [∀ i, AddCommGroup (R i)] [∀ i, Module K (R i)]
    (A : (i : ι) → V →ₗ[K] R i) (Q : V →ₗ[K] T) :
    ((∃ D : ((i : ι) → R i) →ₗ[K] T, Q = D.comp (LinearMap.pi A)) ↔
      LinearMap.ker (LinearMap.pi A) ≤ LinearMap.ker Q) ∧
    ((∃ D : ((i : ι) → R i) →ₗ[K] V, LinearMap.id = D.comp (LinearMap.pi A)) ↔
      Function.Injective (LinearMap.pi A)) ∧
    LinearMap.ker (LinearMap.pi A) = ⨅ i, LinearMap.ker (A i) :=
  JointReconstruction.finite_joint_reconstruction A Q
end General

open JointReconstructionExamples

example : decodeState.comp joint₂ = LinearMap.id ∧
    (¬ ∃ D : F₂ → F₂, ∀ x, D (display₂ x) = physical₂ x) ∧
    (¬ ∃ D : F₂ → F₂, ∀ x, D (calibration₂ x) = physical₂ x) :=
  ⟨exact_binary_inverse, display_alone_impossible, calibration_alone_impossible⟩

example : (∃ D : State₂ →ₗ[F₂] F₂, physical₃ = D.comp joint₃) ∧
    ¬ Function.Injective joint₃ :=
  ⟨JointReconstruction.exists_decoder_of_ker_le joint₃ physical₃
    extra_nuisance_kernel_condition, extra_nuisance_not_injective⟩

example : extension₀.comp embeddedRecord = LinearMap.id ∧
    extension₁.comp embeddedRecord = LinearMap.id ∧
    extension₀ ≠ extension₁ ∧ ¬ Function.Surjective embeddedRecord :=
  ⟨proper_range_extensions.1, proper_range_extensions.2,
    extensions_differ_outside_range, proper_range_not_surjective⟩
