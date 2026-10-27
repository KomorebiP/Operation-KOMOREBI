import Mathlib.NumberTheory.NumberField.Discriminant.Different
import Mathlib.NumberTheory.RamificationInertia.Galois
import Mathlib.FieldTheory.Galois.IsGaloisGroup
open NumberField
variable (L : Type*) [Field L] [NumberField L] [Normal ℚ L]
#synth Algebra.IsSeparable ℚ L
#synth IsGalois ℚ L
#synth IsGaloisGroup Gal(L/ℚ) ℚ L
#check IsGaloisGroup.of_isFractionRing
#check Ideal.ramificationIdx_eq_one
#check Subgroup.eq_bot_iff_card
#check MonoidHom.ker_eq_bot_iff
#check MonoidHom.injective_iff_ker_eq_bot
