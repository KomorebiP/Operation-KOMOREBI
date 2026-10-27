import PaperXI.CyclicInducedCoordinates
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.Group.TypeTags.Finite

/-! The Frobenius-indexed basis of an actual induction from a cyclic degree kernel. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicInduced
open scoped Classical
variable {G : Type*} [Group G] {n : ℕ} [NeZero n]
variable (d : G →* Multiplicative (ZMod n)) (φ : G)
variable (hφ : d φ = Multiplicative.ofAdd (1 : ZMod n))

/-- Negative Frobenius powers represent the covariant-function cosets. -/
def cyclicRep (q : Multiplicative (ZMod n)) : G :=
  φ ^ (-(q.toAdd.val : ℤ))

include hφ in
theorem cyclicRep_degree (q : Multiplicative (ZMod n)) :
    d (cyclicRep φ q) = q⁻¹ := by
  apply Multiplicative.toAdd.injective
  simp [cyclicRep, map_zpow, hφ, toAdd_zpow, zsmul_eq_mul]

omit [NeZero n] in
@[simp] theorem cyclicRep_one : cyclicRep φ (1 : Multiplicative (ZMod n)) = 1 := by
  simp [cyclicRep]

variable (χ : d.ker →* ℂˣ)
/-- The actual induced basis indexed by residues, with representatives `φ^(-j.val)`. -/
def cyclicBasis : Module.Basis (ZMod n) ℂ (IndSpace d χ) :=
  (basis d (cyclicRep φ) (cyclicRep_degree d φ hφ) χ).reindex Multiplicative.toAdd

/-- Actual monomial coefficient in the residue-indexed basis. -/
def cyclicWeight (g : G) (j : ZMod n) : ℂˣ :=
  weight d (cyclicRep φ) (cyclicRep_degree d φ hφ) χ g (Multiplicative.ofAdd j)

@[simp] theorem cyclicBasis_apply (j : ZMod n) :
    cyclicBasis d φ hφ χ j =
      basis d (cyclicRep φ) (cyclicRep_degree d φ hφ) χ (Multiplicative.ofAdd j) := by
  rfl

/-- Every group element translates the Frobenius index by its actual degree. -/
theorem cyclicBasis_action (g : G) (j : ZMod n) :
    induced d χ g (cyclicBasis d φ hφ χ j) =
      (cyclicWeight d φ hφ χ g j : ℂ) •
      cyclicBasis d φ hφ χ (j + (d g).toAdd) := by
  simpa [cyclicBasis_apply, cyclicWeight, add_comm, ofAdd_add, mul_comm] using
    basis_action d (cyclicRep φ) (cyclicRep_degree d φ hφ) χ g (Multiplicative.ofAdd j)

/-- Conjugated inertia character `h ↦ χ(φ⁻ʲ h φʲ)`. -/
def cyclicCharacter (j : ZMod n) : d.ker →* ℂˣ :=
  conjugateCharacter d (cyclicRep φ) χ (Multiplicative.ofAdd j)

@[simp] theorem cyclicCharacter_apply (j : ZMod n) (h : d.ker) :
    cyclicCharacter d φ χ j h =
      χ ⟨φ ^ (-(j.val : ℤ)) * (h : G) * φ ^ (j.val : ℤ), by
        have hh : d h = 1 := h.property
        simp [MonoidHom.mem_ker, hh, map_zpow, zpow_neg]⟩ := by
  apply congrArg χ
  apply Subtype.ext
  simp [conjugate, cyclicRep, zpow_neg]

/-- The subgroup character acts diagonally by the expected Frobenius conjugates. -/
theorem cyclicBasis_action_kernel (h : d.ker) (j : ZMod n) :
    induced d χ h (cyclicBasis d φ hφ χ j) =
      (cyclicCharacter d φ χ j h : ℂ) • cyclicBasis d φ hφ χ j := by
  exact basis_action_kernel d (cyclicRep φ) (cyclicRep_degree d φ hφ) χ h
    (Multiplicative.ofAdd j)

/-- The zeroth line carries the original character. -/
theorem cyclicBasis_action_zero (h : d.ker) :
    induced d χ h (cyclicBasis d φ hφ χ 0) =
      (χ h : ℂ) • cyclicBasis d φ hφ χ 0 := by
  exact basis_action_origin d (cyclicRep φ) (cyclicRep_degree d φ hφ) χ
    (cyclicRep_one φ) h

/-- Frobenius itself advances the residue by one. -/
theorem cyclicBasis_action_phi (j : ZMod n) :
    induced d χ φ (cyclicBasis d φ hφ χ j) =
      (cyclicWeight d φ hφ χ φ j : ℂ) • cyclicBasis d φ hφ χ (j + 1) := by
  simpa [hφ] using cyclicBasis_action d φ hφ χ φ j

end PaperXI.CyclicInduced
