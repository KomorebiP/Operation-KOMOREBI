import PaperXI.HeisenbergGroup

/-! Normal forms and signed commutation in the actual coordinate Heisenberg group. -/
set_option autoImplicit false

namespace PaperXI.Heisenberg
variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

/-- Every group element is a central element followed by a translation and modulation. -/
theorem normal_form (g : Element K X) :
    g = centralElement (g.central - (2 : K)⁻¹ * g.frequency g.position) *
      (translationElement g.position * modulationElement g.frequency) := by
  ext <;> simp

/-- The modulation-translation sign agrees with `T_x f(u) = f(u+x)`. -/
theorem modulation_translation (h2 : (2 : K) ≠ 0)
    (ξ : Module.Dual K X) (x : X) :
    modulationElement ξ * translationElement x =
      centralElement (-ξ x) * (translationElement x * modulationElement ξ) := by
  ext <;> simp
  field_simp
  ring

/-- Translation past modulation contributes the positive scalar character. -/
theorem translation_modulation (h2 : (2 : K) ≠ 0)
    (x : X) (ξ : Module.Dual K X) :
    translationElement x * modulationElement ξ =
      centralElement (ξ x) * (modulationElement ξ * translationElement x) := by
  ext <;> simp
  field_simp
  ring

end PaperXI.Heisenberg
