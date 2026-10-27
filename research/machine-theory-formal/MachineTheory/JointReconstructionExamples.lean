import MachineTheory.JointReconstruction
import Mathlib.LinearAlgebra.Prod
import Mathlib.Algebra.Field.ZMod
import Mathlib.Algebra.CharP.Two
import Mathlib.Tactic.NormNum

/-! # Exact binary joint reconstruction and its limits

The source's two-dimensional state is `(b,s)` over `ZMod 2`. Sharing the
records `(b+s,s)` recovers both coordinates, including the calibration bit.
The separate three-dimensional example adds a distinct nuisance coordinate
`n`. This extra coordinate is invisible to both records, while `b` is still
recoverable. No communication or recipient execution cost is inferred.
-/
namespace Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

abbrev F₂ := ZMod 2
abbrev State₂ := F₂ × F₂

def physical₂ : State₂ →ₗ[F₂] F₂ := LinearMap.fst F₂ F₂ F₂
def calibration₂ : State₂ →ₗ[F₂] F₂ := LinearMap.snd F₂ F₂ F₂
def display₂ : State₂ →ₗ[F₂] F₂ := physical₂ + calibration₂
def joint₂ : State₂ →ₗ[F₂] State₂ := display₂.prod calibration₂
def decodeTarget : State₂ →ₗ[F₂] F₂ := physical₂ + calibration₂
def decodeState : State₂ →ₗ[F₂] State₂ := decodeTarget.prod calibration₂

/-- The source's explicit inverse recovers the entire two-coordinate state. -/
theorem exact_binary_inverse : decodeState.comp joint₂ = LinearMap.id := by
  apply LinearMap.ext
  intro x
  apply Prod.ext
  · simp [decodeState, decodeTarget, joint₂, display₂, physical₂, calibration₂,
      CharTwo.add_cancel_right]
  · simp [decodeState, joint₂, calibration₂]

theorem exact_binary_target : physical₂ = decodeTarget.comp joint₂ := by
  apply LinearMap.ext
  intro x
  simp [decodeTarget, joint₂, display₂, physical₂, calibration₂,
    CharTwo.add_cancel_right]

theorem exact_binary_injective : Function.Injective joint₂ := by
  intro x y h
  have he := congrArg decodeState h
  change (decodeState.comp joint₂) x = (decodeState.comp joint₂) y at he
  simpa only [exact_binary_inverse, LinearMap.id_apply] using he

/-- Agent A's accessible display cannot recover the target, even by a nonlinear function. -/
theorem display_alone_impossible :
    ¬ ∃ D : F₂ → F₂, ∀ x, D (display₂ x) = physical₂ x := by
  rintro ⟨D, hD⟩
  have h0 := hD (0,0)
  have h1 := hD (1,1)
  norm_num [display₂, physical₂, calibration₂] at h0 h1
  exact zero_ne_one (h0.symm.trans h1)

/-- Agent B's accessible calibration also cannot recover the physical target. -/
theorem calibration_alone_impossible :
    ¬ ∃ D : F₂ → F₂, ∀ x, D (calibration₂ x) = physical₂ x := by
  rintro ⟨D, hD⟩
  have h0 := hD (0,0)
  have h1 := hD (1,0)
  norm_num [physical₂, calibration₂] at h0 h1
  exact zero_ne_one (h0.symm.trans h1)

/-- The two kernels intersect trivially although each single record loses a direction. -/
theorem binary_kernel_intersection :
    LinearMap.ker joint₂ = LinearMap.ker display₂ ⊓ LinearMap.ker calibration₂ ∧
    LinearMap.ker joint₂ = ⊥ := by
  constructor
  · exact LinearMap.ker_prod display₂ calibration₂
  · exact LinearMap.ker_eq_bot.mpr exact_binary_injective

theorem lost_direction_is_removed :
    (1,1) ∈ LinearMap.ker display₂ ∧ (1,1) ∉ LinearMap.ker joint₂ := by
  norm_num [LinearMap.mem_ker, display₂, joint₂, physical₂, calibration₂]
  decide

abbrev State₃ := F₂ × (F₂ × F₂)
def physical₃ : State₃ →ₗ[F₂] F₂ := LinearMap.fst F₂ F₂ (F₂ × F₂)
def calibration₃ : State₃ →ₗ[F₂] F₂ :=
  (LinearMap.fst F₂ F₂ F₂).comp (LinearMap.snd F₂ F₂ (F₂ × F₂))
def nuisance₃ : State₃ →ₗ[F₂] F₂ :=
  (LinearMap.snd F₂ F₂ F₂).comp (LinearMap.snd F₂ F₂ (F₂ × F₂))
def display₃ : State₃ →ₗ[F₂] F₂ := physical₃ + calibration₃
def joint₃ : State₃ →ₗ[F₂] State₂ := display₃.prod calibration₃

theorem extra_nuisance_target_reconstructed : physical₃ = decodeTarget.comp joint₃ := by
  apply LinearMap.ext
  intro x
  simp [decodeTarget, joint₃, display₃, physical₃, calibration₃, physical₂,
    calibration₂, CharTwo.add_cancel_right]

theorem extra_nuisance_not_injective : ¬ Function.Injective joint₃ := by
  intro h
  have he := h (show joint₃ (0,0,0) = joint₃ (0,0,1) by
    simp [joint₃, display₃, physical₃, calibration₃])
  have hn := congrArg (fun x : State₃ => x.2.2) he
  exact zero_ne_one hn

/-- The general criterion certifies this target despite the unresolved extra dimension. -/
theorem extra_nuisance_kernel_condition :
    LinearMap.ker joint₃ ≤ LinearMap.ker physical₃ :=
  JointReconstruction.ker_le_of_decoder (K := F₂) joint₃ physical₃ decodeTarget
    extra_nuisance_target_reconstructed

theorem extra_nuisance_no_full_linear_decoder :
    ¬ ∃ D : State₂ →ₗ[F₂] State₃, LinearMap.id = D.comp joint₃ := by
  intro h
  exact extra_nuisance_not_injective
    ((JointReconstruction.full_state_iff_injective (K := F₂) joint₃).mp h)

/-- Unlike the source's calibration bit, this additional nuisance remains unrecoverable. -/
theorem extra_nuisance_not_reconstructed :
    ¬ ∃ D : State₂ → F₂, ∀ x, D (joint₃ x) = nuisance₃ x := by
  rintro ⟨D, hD⟩
  have h0 := hD (0,0,0)
  have h1 := hD (0,0,1)
  norm_num [joint₃, display₃, physical₃, calibration₃, nuisance₃] at h0 h1
  exact zero_ne_one (h0.symm.trans h1)

/-- A record with proper range still permits a total linear decoder. -/
def embeddedRecord : F₂ →ₗ[F₂] State₂ := (LinearMap.id : F₂ →ₗ[F₂] F₂).prod 0
def extension₀ : State₂ →ₗ[F₂] F₂ := physical₂
def extension₁ : State₂ →ₗ[F₂] F₂ := physical₂ + calibration₂

theorem proper_range_extensions :
    extension₀.comp embeddedRecord = LinearMap.id ∧
    extension₁.comp embeddedRecord = LinearMap.id := by
  constructor <;> apply LinearMap.ext <;> intro x <;>
    simp [extension₀, extension₁, embeddedRecord, physical₂, calibration₂]

theorem proper_range_not_surjective : ¬ Function.Surjective embeddedRecord := by
  intro h
  obtain ⟨x, hx⟩ := h (0,1)
  have he := congrArg Prod.snd hx
  norm_num [embeddedRecord] at he

/-- Values outside the record range are unconstrained by the reconstruction identity. -/
theorem extensions_differ_outside_range : extension₀ ≠ extension₁ := by
  intro h
  have he := LinearMap.congr_fun h (0,1)
  norm_num [extension₀, extension₁, physical₂, calibration₂] at he

end
end Komorebi.MachineTheory.JointReconstructionExamples
