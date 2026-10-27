import PaperXI.HeisenbergPrime
import PaperXI.HeisenbergRepresentation
import PaperXI.HeisenbergDimension
import PaperXI.HeisenbergFinite
import PaperXI.HeisenbergCenter
import PaperXI.SchrodingerTrace

/-! Source propositions 7.2 and 7.3 for odd prime p and the canonical
exponential character, with the manuscript's dimension parameter. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergSource
open PaperXI.Heisenberg
open scoped Classical

variable {p : ℕ} [Fact p.Prime]
variable {X : Type*} [AddCommGroup X] [Module (ZMod p) X]

def model (hp : p ≠ 2) : Representation ℂ (Element (ZMod p) X) (X → ℂ) :=
  representation ZMod.stdAddChar (HeisenbergPrime.two_ne_zero hp)

theorem model_formula (hp : p ≠ 2) (a : Element (ZMod p) X) (f : X → ℂ) (u : X) :
    model hp a f u =
      ZMod.stdAddChar (a.central + a.frequency u + (2 : ZMod p)⁻¹ *
        a.frequency a.position) * f (u + a.position) := rfl

theorem center_character (hp : p ≠ 2) (a : Element (ZMod p) X)
    (ha : a ∈ Subgroup.center (Element (ZMod p) X)) :
    model hp a = ZMod.stdAddChar a.central • LinearMap.id := by
  rw [(HeisenbergCenter.center_eq_centralElement (HeisenbergPrime.two_ne_zero hp) a).mp ha]
  exact central_action _ _ _

theorem model_invertible (hp : p ≠ 2) (a : Element (ZMod p) X) :
    IsUnit (model hp a) := representation_isUnit _ _ a

variable [Fintype X]

theorem model_irreducible (hp : p ≠ 2) :
    Representation.IsIrreducible (model (X := X) hp) :=
  irreducible _ HeisenbergPrime.character_nontrivial _

variable [FiniteDimensional (ZMod p) X]

theorem dimension_power : Module.finrank ℂ (X → ℂ) = p ^ Module.finrank (ZMod p) X := by
  simpa only [Nat.card_zmod] using HeisenbergDimension.finrank_function_pow
    (K := ZMod p) (X := X)

theorem dimension_sqrt : Module.finrank ℂ (X → ℂ) =
    Nat.sqrt (Nat.card (X × Module.Dual (ZMod p) X)) :=
  HeisenbergDimension.finrank_function_sqrt

theorem character_support (hp : p ≠ 2) (a : Element (ZMod p) X) :
    LinearMap.trace ℂ (X → ℂ) (model hp a) =
      if a.position = 0 ∧ a.frequency = 0 then
        (p : ℂ) ^ Module.finrank (ZMod p) X * ZMod.stdAddChar a.central else 0 := by
  have hc : Fintype.card X = p ^ Module.finrank (ZMod p) X := by
    rw [← Nat.card_eq_fintype_card,
      Module.natCard_eq_pow_finrank (K := ZMod p) (V := X), Nat.card_zmod]
  simpa only [hc, Nat.cast_pow, model, representation, MonoidHom.coe_mk, OneHom.coe_mk] using
    SchrodingerTrace.character_support HeisenbergPrime.character_nontrivial
      a.position a.frequency a.central

end PaperXI.HeisenbergSource
