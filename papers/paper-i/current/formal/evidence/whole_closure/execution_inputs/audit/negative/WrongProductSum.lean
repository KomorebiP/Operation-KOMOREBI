-- Deliberate negative control: this product's seed rank is max(2,1)=2, not3.
import PaperICompletion8.SemisimpleExistence
import Mathlib.Algebra.Quaternion
set_option autoImplicit false
namespace WrongProductSumFixture
open Komorebi.PaperICompletion8.DivisionProduct Komorebi.PaperICompletion8.RegularMultiplicity
abbrev H := Quaternion ℚ
def MixedD : Bool → Type := fun b ↦ if b then ℚ else H
noncomputable instance mixedDivision (b : Bool) : DivisionRing (MixedD b) := by
  cases b <;> dsimp [MixedD] <;> infer_instance
def dims : Bool → ℕ := fun b ↦ if b then 1 else 2
def mults : Bool → ℕ := fun b ↦ if b then 1 else 3
example : Komorebi.SeedRankBasics.seedRank
    (DivisionProductAlgebra (D := MixedD) dims) (MultiplicityModule (D := MixedD) dims mults) = 3 := by
  have positive (b : Bool) : 0 < dims b := by cases b <;> decide
  have count : maxCeilDiv dims mults = 2 := by decide
  have correct : Komorebi.SeedRankBasics.seedRank
      (DivisionProductAlgebra (D := MixedD) dims) (MultiplicityModule (D := MixedD) dims mults) = 2 := by
    rw [multiplicity_seedRank dims mults positive, count]
    norm_num
  exact correct
end WrongProductSumFixture
