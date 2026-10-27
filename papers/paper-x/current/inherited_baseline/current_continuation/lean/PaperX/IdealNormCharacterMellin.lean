import PaperX.IdealNormWeightedAttachment
import PaperX.RealAxisMellinMoment
import Mathlib.MeasureTheory.Function.Floor

/-! Measurability and the real-axis Mellin transform for actual ideal
norm-weighted sums in one ideal class. -/

set_option autoImplicit false
noncomputable section

open Ideal MeasureTheory NumberField Filter Set Asymptotics
open scoped nonZeroDivisors Classical Topology

namespace PaperX.IdealNormWeighted

open PaperX.RealAxisMellinMoment

variable (K : Type*) [Field K] [NumberField K]

/-- Integral ideal norms make every fixed norm-weighted class sum constant on
integer steps. -/
theorem classNormSum_eq_floor (C : ClassGroup (𝓞 K)) (f : ℕ → ℂ) (x : ℝ) :
    classNormSum K C f x = classNormSum K C f (Int.floor x : ℝ) := by
  unfold classNormSum
  let e : BoundedClassIdeals K C x ≃ BoundedClassIdeals K C (Int.floor x : ℝ) :=
    Equiv.subtypeEquivProp (by
      funext I
      apply propext
      have hn : ((absNorm (I : Ideal (𝓞 K)) : ℤ) : ℝ) =
          (absNorm (I : Ideal (𝓞 K)) : ℝ) := by norm_cast
      rw [and_congr_left_iff]
      intro _
      rw [← hn, Int.cast_le, Int.le_floor])
  exact finsum_eq_of_bijective e e.bijective (fun _ => rfl)

/-- Actual ideal norm-weighted class sums are measurable on the real line. -/
theorem measurable_classNormSum (C : ClassGroup (𝓞 K)) (f : ℕ → ℂ) :
    Measurable (classNormSum K C f) := by
  have h : Measurable (fun n : ℤ => classNormSum K C f (n : ℝ)) :=
    measurable_of_countable _
  convert h.comp (Int.measurable_floor (R := ℝ)) using 1
  funext x
  exact classNormSum_eq_floor K C f x

/-- Mellin transform of an actual norm-weighted ideal-class summatory function,
with real parameter `h = s - 1`. -/
def normMellin (C : ClassGroup (𝓞 K)) (f : ℕ → ℂ) (h : ℝ) : ℂ :=
  mellinIntegral (classNormSum K C f) h

end PaperX.IdealNormWeighted
