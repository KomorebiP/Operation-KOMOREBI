import PaperX.IdealClassQuantitativeAttachment
import Mathlib.MeasureTheory.Function.Floor

/-! The ordinary ideal-class counting functions are actual step functions on
the integer norm scale, and hence measurable. No regularity of an abstract
counting function is assumed. -/

set_option autoImplicit false
noncomputable section

open Ideal MeasureTheory NumberField
open scoped nonZeroDivisors

namespace PaperX.IdealClassCharacter

open PaperX.IdealClassQuantitative

variable (K : Type*) [Field K] [NumberField K]

/-- Integral ideal norms make the count constant on each integer step. -/
theorem classCount_eq_floor (C : ClassGroup (𝓞 K)) (x : ℝ) :
    classCount K C x = classCount K C (Int.floor x : ℝ) := by
  unfold classCount
  apply Nat.card_congr
  apply Equiv.subtypeEquivProp
  funext I
  apply propext
  have hn : ((absNorm (I : Ideal (𝓞 K)) : ℤ) : ℝ) =
      (absNorm (I : Ideal (𝓞 K)) : ℝ) := by norm_cast
  rw [← hn, Int.cast_le, Int.le_floor]

/-- Actual ordinary class counts are measurable on all of the real line. -/
theorem measurable_classCount (C : ClassGroup (𝓞 K)) :
    Measurable (classCount K C) := by
  have h : Measurable (fun n : ℤ => classCount K C (n : ℝ)) :=
    measurable_of_countable _
  convert h.comp (Int.measurable_floor (R := ℝ)) using 1
  funext x
  exact classCount_eq_floor K C x

end PaperX.IdealClassCharacter
