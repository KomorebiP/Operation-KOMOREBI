import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.LinearAlgebra.Isomorphisms
import Mathlib.LinearAlgebra.Pi
import Mathlib.LinearAlgebra.FiniteDimensional.Defs

/-! # Target-relative joint reconstruction

Core 8.1. Records and protected targets are actual field-linear maps. The decoder
constructed below has the entire record space as its domain. First it descends
through the kernel quotient to the attainable image, then Mathlib's basis
extension theorem extends it to the full space. This is an algebraic existence
result using classical choice, not an executable decoder or a communication law.

The general theorem does not need finite dimension. `finite_joint_reconstruction`
retains the manuscript's finite-dimensional state space and finite record family.
-/
namespace Komorebi.MachineTheory.JointReconstruction

noncomputable section

variable {K V W T : Type*} [Field K]
variable [AddCommGroup V] [Module K V] [AddCommGroup W] [Module K W]
variable [AddCommGroup T] [Module K T]

/-- Every linear decoder annihilates all ambiguities left by its input record. -/
theorem ker_le_of_decoder (A : V →ₗ[K] W) (Q : V →ₗ[K] T) (D : W →ₗ[K] T)
    (h : Q = D.comp A) : LinearMap.ker A ≤ LinearMap.ker Q := by
  rw [h]
  exact A.ker_le_ker_comp D

/-- Kernel containment says that indistinguishable records have the same target. -/
theorem target_eq_of_record_eq (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) {v w : V} (hvw : A v = A w) :
    Q v = Q w := by
  have hzero : A (v - w) = 0 := by rw [map_sub, hvw, sub_self]
  have hq : Q (v - w) = 0 := h hzero
  exact sub_eq_zero.mp (by simpa only [map_sub] using hq)

/-- Conversely, target constancy on record fibers implies the kernel condition. -/
theorem ker_le_of_target_constant (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : ∀ v w, A v = A w → Q v = Q w) : LinearMap.ker A ≤ LinearMap.ker Q := by
  intro v hv
  change Q v = 0
  have hvw : A v = A 0 := by simpa using hv
  simpa using h v 0 hvw

/-- Exact ambiguity criterion, expressed without a chosen decoder. -/
theorem ker_le_iff_target_constant (A : V →ₗ[K] W) (Q : V →ₗ[K] T) :
    LinearMap.ker A ≤ LinearMap.ker Q ↔ ∀ v w, A v = A w → Q v = Q w :=
  ⟨fun h _ _ hvw => target_eq_of_record_eq A Q h hvw, ker_le_of_target_constant A Q⟩

/-- The quotient construction defines a linear decoder on exactly the attainable image. -/
def imageDecoder (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) : LinearMap.range A →ₗ[K] T :=
  ((LinearMap.ker A).liftQ Q h).comp A.quotKerEquivRange.symm.toLinearMap

/-- On an actually observed record, the image decoder returns the original target. -/
@[simp] theorem imageDecoder_apply (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) (v : V) :
    imageDecoder A Q h (A.rangeRestrict v) = Q v := by
  change (A.ker.liftQ Q h) (A.quotKerEquivRange.symm ⟨A v, _⟩) = Q v
  rw [LinearMap.quotKerEquivRange_symm_apply_image]
  exact Submodule.liftQ_apply A.ker Q v

/-- The image-level reconstruction identity is proved before extension. -/
theorem imageDecoder_comp_rangeRestrict (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) :
    (imageDecoder A Q h).comp A.rangeRestrict = Q := by
  ext v
  exact imageDecoder_apply A Q h v

/-- Extending a basis produces a decoder on the whole record space, with image agreement. -/
theorem exists_decoder_extending_imageDecoder (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) :
    ∃ D : W →ₗ[K] T, D.comp (LinearMap.range A).subtype = imageDecoder A Q h :=
  (imageDecoder A Q h).exists_extend

/-- The extension, rather than just the image decoder, factors the protected target. -/
theorem exists_decoder_of_ker_le (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (h : LinearMap.ker A ≤ LinearMap.ker Q) :
    ∃ D : W →ₗ[K] T, Q = D.comp A := by
  obtain ⟨D,hD⟩ := exists_decoder_extending_imageDecoder A Q h
  refine ⟨D, ?_⟩
  ext v
  have he := LinearMap.congr_fun hD (A.rangeRestrict v)
  change D (A v) = imageDecoder A Q h (A.rangeRestrict v) at he
  exact (he.trans (imageDecoder_apply A Q h v)).symm

/-- Core 8.1: a full-domain linear decoder exists exactly under kernel containment. -/
theorem exists_decoder_iff_ker_le (A : V →ₗ[K] W) (Q : V →ₗ[K] T) :
    (∃ D : W →ₗ[K] T, Q = D.comp A) ↔ LinearMap.ker A ≤ LinearMap.ker Q :=
  ⟨fun ⟨D,hD⟩ => ker_le_of_decoder A Q D hD, exists_decoder_of_ker_le A Q⟩

/-- The same existence criterion in terms of equal record values. -/
theorem exists_decoder_iff_target_constant (A : V →ₗ[K] W) (Q : V →ₗ[K] T) :
    (∃ D : W →ₗ[K] T, Q = D.comp A) ↔ ∀ v w, A v = A w → Q v = Q w := by
  rw [exists_decoder_iff_ker_le, ker_le_iff_target_constant]

/-- Extensions agree on attainable records, without asserting uniqueness off the image. -/
theorem decoders_agree_on_range (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (D E : W →ₗ[K] T) (hD : Q = D.comp A) (hE : Q = E.comp A)
    (r : W) (hr : r ∈ LinearMap.range A) : D r = E r := by
  obtain ⟨v,rfl⟩ := hr
  exact (LinearMap.congr_fun hD v).symm.trans (LinearMap.congr_fun hE v)

/-- A surviving ambiguity with nonzero target forbids every full-domain linear decoder. -/
theorem no_decoder_of_ambiguity (A : V →ₗ[K] W) (Q : V →ₗ[K] T)
    (v : V) (hA : A v = 0) (hQ : Q v ≠ 0) :
    ¬ ∃ D : W →ₗ[K] T, Q = D.comp A := by
  intro hD
  exact hQ ((exists_decoder_iff_ker_le A Q).mp hD hA)

/-- Failure of reconstruction has an actual algebraic ambiguity witness. -/
theorem no_decoder_iff_ambiguity (A : V →ₗ[K] W) (Q : V →ₗ[K] T) :
    (¬ ∃ D : W →ₗ[K] T, Q = D.comp A) ↔ ∃ v : V, A v = 0 ∧ Q v ≠ 0 := by
  rw [exists_decoder_iff_ker_le]
  change (¬ ∀ v, A v = 0 → Q v = 0) ↔ _
  simp only [not_forall, exists_prop]

/-- Full-state recovery is the identity-target specialization, exactly injectivity. -/
theorem full_state_iff_injective (A : V →ₗ[K] W) :
    (∃ D : W →ₗ[K] V, LinearMap.id = D.comp A) ↔ Function.Injective A := by
  rw [exists_decoder_iff_ker_le, LinearMap.ker_id, le_bot_iff, LinearMap.ker_eq_bot]

section Records
variable {ι : Type*} {R : ι → Type*}
variable [∀ i, AddCommGroup (R i)] [∀ i, Module K (R i)]

/-- The accessible joint record is the actual product-valued linear map. -/
def stackRecords (A : (i : ι) → V →ₗ[K] R i) : V →ₗ[K] ((i : ι) → R i) :=
  LinearMap.pi A

/-- Each coordinate of the stacked record is the original participant's record. -/
@[simp] theorem stackRecords_apply (A : (i : ι) → V →ₗ[K] R i) (v : V) (i : ι) :
    stackRecords A v i = A i v := rfl

/-- Sharing removes exactly the directions not common to every record kernel. -/
theorem ker_stackRecords (A : (i : ι) → V →ₗ[K] R i) :
    LinearMap.ker (stackRecords A) = ⨅ i, LinearMap.ker (A i) :=
  LinearMap.ker_pi A

/-- Explicit pointwise form of the common-ambiguity identity. -/
theorem mem_ker_stackRecords (A : (i : ι) → V →ₗ[K] R i) (v : V) :
    v ∈ LinearMap.ker (stackRecords A) ↔ ∀ i, A i v = 0 := by
  rw [ker_stackRecords, Submodule.mem_iInf]
  rfl

/-- Target-relative criterion for the complete accessible family. -/
theorem stacked_decoder_iff (A : (i : ι) → V →ₗ[K] R i) (Q : V →ₗ[K] T) :
    (∃ D : ((i : ι) → R i) →ₗ[K] T, Q = D.comp (stackRecords A)) ↔
      (⨅ i, LinearMap.ker (A i)) ≤ LinearMap.ker Q := by
  rw [exists_decoder_iff_ker_le, ker_stackRecords]

/-- Full-state joint recovery requires the common ambiguity subspace to vanish. -/
theorem stacked_full_state_iff (A : (i : ι) → V →ₗ[K] R i) :
    (∃ D : ((i : ι) → R i) →ₗ[K] V, LinearMap.id = D.comp (stackRecords A)) ↔
      (⨅ i, LinearMap.ker (A i)) = ⊥ := by
  rw [stacked_decoder_iff, LinearMap.ker_id, le_bot_iff]

/-- Source-facing Core 8.1 with finite-dimensional states and finitely many records. -/
theorem finite_joint_reconstruction [Fintype ι] [FiniteDimensional K V]
    (A : (i : ι) → V →ₗ[K] R i) (Q : V →ₗ[K] T) :
    ((∃ D : ((i : ι) → R i) →ₗ[K] T, Q = D.comp (stackRecords A)) ↔
      LinearMap.ker (stackRecords A) ≤ LinearMap.ker Q) ∧
    ((∃ D : ((i : ι) → R i) →ₗ[K] V, LinearMap.id = D.comp (stackRecords A)) ↔
      Function.Injective (stackRecords A)) ∧
    LinearMap.ker (stackRecords A) = ⨅ i, LinearMap.ker (A i) :=
  ⟨exists_decoder_iff_ker_le (stackRecords A) Q,
    full_state_iff_injective (stackRecords A), ker_stackRecords A⟩

end Records
end
end Komorebi.MachineTheory.JointReconstruction
