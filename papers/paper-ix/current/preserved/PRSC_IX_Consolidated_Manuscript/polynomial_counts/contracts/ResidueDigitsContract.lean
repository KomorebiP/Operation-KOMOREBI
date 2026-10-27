module
public import ResidueLiftDigits

@[expose] public section
noncomputable section
set_option autoImplicit false
namespace Komorebi.ResidueDigitsContract

/-- The target contains actual next-level residue vectors retaining the lower
residue, not arbitrary integer representatives or all next-level roots. -/
def explicit_residue_digit_equivalence (q L : ℕ) (hq : 0 < q) {d : ℕ}
    (x : Fin d → ℤ) :
    (Fin d → ZMod q) ≃
      {y : Fin d → ZMod (q^(L+1)) //
        ∀ i, (q : ℤ)^L ∣ ((y i).val : ℤ) - x i} :=
  ResidueLiftDigits.digitEquivResidue q L hq x

/-- The forward map is exactly the prescribed digit shift. -/
theorem explicit_residue_digit_formula (q L : ℕ) (hq : 0 < q) {d : ℕ}
    (x : Fin d → ℤ) (t : Fin d → ZMod q) (i : Fin d) :
    (explicit_residue_digit_equivalence q L hq x t).val i =
      ((x i + (q : ℤ)^L * ((t i).val : ℤ) : ℤ) : ZMod (q^(L+1))) := rfl

end Komorebi.ResidueDigitsContract
