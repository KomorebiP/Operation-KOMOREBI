import PaperXI.CyclicInducedBasis
import PaperXI.TameDegree

/-! Source-facing degree-subgroup coordinates for tame cyclic induction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicInduced
open TameDegree
variable {G : Type*} [Group G] (ν : G →* Multiplicative ℤ)
variable (φ : G) (hφ : ν φ = Multiplicative.ofAdd (1 : ℤ))
variable (n : ℕ) [NeZero n]

include hφ in
omit [NeZero n] in
theorem degreeMod_phi : degreeMod ν n φ = Multiplicative.ofAdd (1 : ZMod n) := by
  simpa using degreeMod_phi_zpow ν φ hφ n (1 : ℤ)

variable (χ : degreeSubgroup ν n →* ℂˣ)
/-- The source's induced representation, using the actual degree-divisibility subgroup. -/
abbrev degreeInduced := induced (degreeMod ν n) χ
abbrev DegreeIndSpace := IndSpace (degreeMod ν n) χ

/-- Frobenius coordinates of the actual induced representation. -/
def degreeBasis : Module.Basis (ZMod n) ℂ (DegreeIndSpace ν n χ) :=
  cyclicBasis (degreeMod ν n) φ (degreeMod_phi ν φ hφ n) χ

def degreeWeight (g : G) (j : ZMod n) : ℂˣ :=
  cyclicWeight (degreeMod ν n) φ (degreeMod_phi ν φ hφ n) χ g j

/-- Frobenius conjugate of the source character on a basis line. -/
def degreeCharacter (j : ZMod n) : degreeSubgroup ν n →* ℂˣ :=
  cyclicCharacter (degreeMod ν n) φ χ j

/-- Translation by degree is the index action on the genuine induced basis. -/
theorem degreeBasis_action (g : G) (j : ZMod n) :
    degreeInduced ν n χ g (degreeBasis ν φ hφ n χ j) =
      (degreeWeight ν φ hφ n χ g j : ℂ) •
      degreeBasis ν φ hφ n χ (translationAction ν n g j) :=
  cyclicBasis_action (degreeMod ν n) φ (degreeMod_phi ν φ hφ n) χ g j

/-- Kernel elements act by the explicit conjugated character. -/
theorem degreeBasis_action_kernel (h : degreeSubgroup ν n) (j : ZMod n) :
    degreeInduced ν n χ h (degreeBasis ν φ hφ n χ j) =
      (degreeCharacter ν φ n χ j h : ℂ) • degreeBasis ν φ hφ n χ j :=
  cyclicBasis_action_kernel (degreeMod ν n) φ (degreeMod_phi ν φ hφ n) χ h j

/-- On the zeroth basis line the character is precisely the inducing character. -/
theorem degreeBasis_action_zero (h : degreeSubgroup ν n) :
    degreeInduced ν n χ h (degreeBasis ν φ hφ n χ 0) =
      (χ h : ℂ) • degreeBasis ν φ hφ n χ 0 :=
  cyclicBasis_action_zero (degreeMod ν n) φ (degreeMod_phi ν φ hφ n) χ h

/-- Frobenius advances the cyclic basis, including its actual wrap scalar. -/
theorem degreeBasis_action_phi (j : ZMod n) :
    degreeInduced ν n χ φ (degreeBasis ν φ hφ n χ j) =
      (degreeWeight ν φ hφ n χ φ j : ℂ) • degreeBasis ν φ hφ n χ (j + 1) :=
  cyclicBasis_action_phi (degreeMod ν n) φ (degreeMod_phi ν φ hφ n) χ j

end PaperXI.CyclicInduced
