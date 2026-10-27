import PaperX.ClassCompletionExamples

/-! Compatible classes do not make arbitrarily chosen matrix frames compatible.
The obstruction here is deliberately removable by an actual basis change. -/
set_option autoImplicit false
namespace PaperX.ClassFramingBoundary
open PaperX.RepresentationLimits PaperX.RepresentationClasses
open PaperX.CompletionExamples
open scoped Matrix

def swapMatrix (R : Type) [CommRing R] : Matrix (Fin 2) (Fin 2) R := !![0,1;1,0]

theorem swap_square (R : Type) [CommRing R] : swapMatrix R * swapMatrix R = 1 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [swapMatrix, Matrix.mul_apply, Fin.sum_univ_succ]

def swapUnit (R : Type) [CommRing R] : (Matrix (Fin 2) (Fin 2) R)ˣ where
  val := swapMatrix R
  inv := swapMatrix R
  val_inv := swap_square R
  inv_val := swap_square R

def reduceNine : ZMod 9 →+* ZMod 3 := ZMod.castHom (by decide) (ZMod 3)

def lowerFrame : MatrixRep (ZMod 3) C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom (ZMod 3)) signRep

def ordinaryUpper : MatrixRep (ZMod 9) C2 (Fin 2) :=
  changeCoefficients (Int.castRingHom (ZMod 9)) signRep

def chosenUpper : MatrixRep (ZMod 9) C2 (Fin 2) :=
  conjugate (swapUnit (ZMod 9)) ordinaryUpper

theorem lower_generator : lowerFrame generator = !![1,0;0,-1] := by decide +kernel

theorem upper_generator : chosenUpper generator = !![-1,0;0,1] := by decide +kernel

theorem lower_polynomial : (lowerFrame generator).charpoly = Polynomial.X^2-1 := by
  change ((signRep generator).map (Int.castRingHom (ZMod 3))).charpoly = _
  rw [Matrix.charpoly_map, integer_charpoly]
  simp

theorem upper_polynomial : (chosenUpper generator).charpoly = Polynomial.X^2-1 := by
  rw [chosenUpper, PaperX.ClassInvariants.charpoly_conjugate]
  change ((signRep generator).map (Int.castRingHom (ZMod 9))).charpoly = _
  rw [Matrix.charpoly_map, integer_charpoly]
  simp

theorem ordinary_reduces : changeCoefficients reduceNine ordinaryUpper = lowerFrame := by
  apply MonoidHom.ext
  intro g
  ext i j
  simp [ordinaryUpper, lowerFrame, changeCoefficients_apply]

theorem classes_compatible :
    changeClassCoefficients reduceNine (classOf chosenUpper) = classOf lowerFrame := by
  change classOf (changeCoefficients reduceNine chosenUpper) = classOf lowerFrame
  apply classOf_eq.mpr
  have h : Conjugate ordinaryUpper chosenUpper := ⟨swapUnit (ZMod 9), rfl⟩
  have hr := changeCoefficients_conjugacy reduceNine h
  rw [ordinary_reduces] at hr
  exact conjugate_symm hr

/-- The selected representative upstairs has swapped eigenlines, so its raw
matrix reduction differs from the selected representative downstairs. -/
theorem chosen_frames_incompatible : changeCoefficients reduceNine chosenUpper ≠ lowerFrame := by
  intro h
  have hc := congrArg (fun ρ : MatrixRep (ZMod 3) C2 (Fin 2) => ρ generator 0 0) h
  have hn : changeCoefficients reduceNine chosenUpper generator 0 0 ≠
      lowerFrame generator 0 0 := by decide +kernel
  exact hn hc

/-- A genuine change of basis repairs this mismatch. No lifting of arbitrary
invertible matrices is assumed. -/
theorem reframing_repairs :
    changeCoefficients reduceNine (conjugate ((swapUnit (ZMod 9))⁻¹) chosenUpper) =
      lowerFrame := by
  rw [chosenUpper, ← conjugate_mul]
  simp only [inv_mul_cancel, conjugate_one]
  exact ordinary_reduces

end PaperX.ClassFramingBoundary
