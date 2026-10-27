import PaperX.FamilyRigidity
import PaperX.SummandBoundary

/-! Independent idempotent lifting does not preserve a decomposition.  The
examples use an actual rank-two Z_2 carrier with trivial C2 action. Distinct
complete families with the same reduction can nevertheless be conjugate by a
matrix congruent to the identity. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.FamilyBoundary
open scoped Matrix BigOperators
open PaperX.RepresentationLimits PaperX.CompletionExamples
open PaperX.PrecisionExamples PaperX.OrthogonalProjectors

private theorem modTwo_two : modTwo (2 : ℤ_[2]) = 0 := by
  rw [show (2 : ℤ_[2]) = 1 + 1 by norm_num, map_add, map_one]
  decide +kernel

abbrev trivialCarrier : MatrixRep ℤ_[2] C2 (Fin 2) := 1

def leftProjector : Matrix (Fin 2) (Fin 2) ℤ_[2] := !![1, 0; 0, 0]
def skewRight (b : ℤ_[2]) : Matrix (Fin 2) (Fin 2) ℤ_[2] := !![0, b; 0, 1]
def adjustedLeft (b : ℤ_[2]) : Matrix (Fin 2) (Fin 2) ℤ_[2] := !![1, -b; 0, 0]
def shear (b : ℤ_[2]) : Matrix (Fin 2) (Fin 2) ℤ_[2] := !![1, b; 0, 1]

theorem independent_idempotents (b : ℤ_[2]) :
    leftProjector * leftProjector = leftProjector ∧
      skewRight b * skewRight b = skewRight b := by
  constructor <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    simp [leftProjector, skewRight, Matrix.mul_apply, Fin.sum_univ_succ]

theorem independent_lifts_same_reduction :
    (skewRight 2).map modTwo = (skewRight 0).map modTwo := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [skewRight, modTwo_two]

theorem independent_lifts_not_orthogonal : leftProjector * skewRight 2 ≠ 0 := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 0 1) h
  norm_num [leftProjector, skewRight, Matrix.mul_apply, Fin.sum_univ_succ] at h01

theorem independent_lifts_not_total : leftProjector + skewRight 2 ≠ 1 := by
  intro h
  have h01 := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℤ_[2] => M 0 1) h
  norm_num [leftProjector, skewRight] at h01

/-- Both independent lifts are genuine equivariant idempotents. -/
theorem independent_lifts_commute (b : ℤ_[2]) (g : C2) :
    trivialCarrier g * leftProjector = leftProjector * trivialCarrier g ∧
      trivialCarrier g * skewRight b = skewRight b * trivialCarrier g := by
  simp [trivialCarrier]

def familyMatrix (b : ℤ_[2]) (i : Fin 2) : Matrix (Fin 2) (Fin 2) ℤ_[2] :=
  if i = 0 then adjustedLeft b else skewRight b

theorem familyMatrix_idempotent (b : ℤ_[2]) (i : Fin 2) :
    familyMatrix b i * familyMatrix b i = familyMatrix b i := by
  fin_cases i <;> ext a c <;> fin_cases a <;> fin_cases c <;>
    simp [familyMatrix, adjustedLeft, skewRight, Matrix.mul_apply, Fin.sum_univ_succ]

theorem familyMatrix_orthogonal (b : ℤ_[2]) (i j : Fin 2) (h : i ≠ j) :
    familyMatrix b i * familyMatrix b j = 0 := by
  fin_cases i <;> fin_cases j
  all_goals try contradiction
  all_goals ext a c; fin_cases a <;> fin_cases c <;>
    simp [familyMatrix, adjustedLeft, skewRight, Matrix.mul_apply, Fin.sum_univ_succ]

theorem familyMatrix_total (b : ℤ_[2]) : ∑ i : Fin 2, familyMatrix b i = 1 := by
  ext a c
  fin_cases a <;> fin_cases c <;>
    simp [familyMatrix, adjustedLeft, skewRight, Fin.sum_univ_succ]

def splitFamily (b : ℤ_[2]) : Family trivialCarrier (Fin 2) where
  projector i := {
    matrix := familyMatrix b i
    idempotent := familyMatrix_idempotent b i
    commutes := by intro g; simp [trivialCarrier] }
  orthogonal := familyMatrix_orthogonal b
  total := familyMatrix_total b

theorem complete_families_same_reduction (i : Fin 2) :
    ((splitFamily 2).projector i).matrix.map modTwo =
      ((splitFamily 0).projector i).matrix.map modTwo := by
  fin_cases i <;> ext a c <;> fin_cases a <;> fin_cases c <;>
    norm_num [splitFamily, familyMatrix, adjustedLeft, skewRight, modTwo_two]

theorem complete_families_distinct : splitFamily 2 ≠ splitFamily 0 := by
  intro h
  have h01 := congrArg (fun E : Family trivialCarrier (Fin 2) =>
    (E.projector 1).matrix 0 1) h
  norm_num [splitFamily, familyMatrix, skewRight] at h01

theorem shear_inverse (b : ℤ_[2]) : shear b * shear (-b) = 1 ∧
    shear (-b) * shear b = 1 := by
  constructor <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    simp [shear, Matrix.mul_apply, Fin.sum_univ_succ]

def shearUnit (b : ℤ_[2]) : (Matrix (Fin 2) (Fin 2) ℤ_[2])ˣ where
  val := shear b
  inv := shear (-b)
  val_inv := (shear_inverse b).1
  inv_val := (shear_inverse b).2

theorem shear_preserves_labels (b : ℤ_[2]) (i : Fin 2) :
    shear b * ((splitFamily 0).projector i).matrix =
      ((splitFamily b).projector i).matrix * shear b := by
  fin_cases i <;> ext a c <;> fin_cases a <;> fin_cases c <;>
    simp [splitFamily, familyMatrix, adjustedLeft, skewRight, shear,
      Matrix.mul_apply, Fin.sum_univ_succ]

theorem shear_congruent_identity : (shear 2).map modTwo = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [shear, modTwo_two]

/-- Nonuniqueness is compatible with the precise labeled conjugacy conclusion. -/
theorem distinct_families_have_identity_congruent_equivariant_conjugacy :
    splitFamily 2 ≠ splitFamily 0 ∧
    ∃ U : (Matrix (Fin 2) (Fin 2) ℤ_[2])ˣ,
      (U : Matrix (Fin 2) (Fin 2) ℤ_[2]).map modTwo = 1 ∧
      (∀ g : C2, trivialCarrier g * U = U * trivialCarrier g) ∧
      ∀ i : Fin 2, (U : Matrix (Fin 2) (Fin 2) ℤ_[2]) *
          ((splitFamily 0).projector i).matrix =
        ((splitFamily 2).projector i).matrix * U := by
  refine ⟨complete_families_distinct, shearUnit 2, shear_congruent_identity, ?_,
    shear_preserves_labels 2⟩
  intro g
  simp [trivialCarrier]

/-- The general rigidity theorem applies to the two explicit distinct families. -/
theorem generic_rigidity_on_distinct_families :
    ∃ U : (Matrix (Fin 2) (Fin 2) ℤ_[2])ˣ,
      (U : Matrix (Fin 2) (Fin 2) ℤ_[2]) =
        FamilyRigidity.comparison (splitFamily 0) (splitFamily 2) ∧
      (U : Matrix (Fin 2) (Fin 2) ℤ_[2]).map
        (Ideal.Quotient.mk (twoIdeal^1)) = 1 ∧
      (∀ g : C2, trivialCarrier g * (U : Matrix (Fin 2) (Fin 2) ℤ_[2]) =
        (U : Matrix (Fin 2) (Fin 2) ℤ_[2]) * trivialCarrier g) ∧
      ∀ i : Fin 2, (U : Matrix (Fin 2) (Fin 2) ℤ_[2]) *
          ((splitFamily 0).projector i).matrix *
          (↑(U⁻¹) : Matrix (Fin 2) (Fin 2) ℤ_[2]) =
        ((splitFamily 2).projector i).matrix := by
  apply FamilyRigidity.exists_conjugating_unit_of_reduction (2 : ℤ_[2])
    PadicInt.irreducible_p.not_isUnit 1 (by decide) (splitFamily 0) (splitFamily 2)
  intro i
  apply (quotient_matrices_eq_iff 1 _ _).mpr
  have htwo : PadicInt.toZModPow 1 (2 : ℤ_[2]) = 0 := by
    rw [show (2 : ℤ_[2]) = 1 + 1 by norm_num, map_add, map_one]
    decide +kernel
  fin_cases i <;> ext a c <;> fin_cases a <;> fin_cases c <;>
    norm_num [splitFamily, familyMatrix, adjustedLeft, skewRight, htwo]

end PaperX.FamilyBoundary
