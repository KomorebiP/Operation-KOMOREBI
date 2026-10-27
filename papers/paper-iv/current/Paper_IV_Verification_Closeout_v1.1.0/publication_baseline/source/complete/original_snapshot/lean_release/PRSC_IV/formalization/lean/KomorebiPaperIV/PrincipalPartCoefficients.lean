/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import Mathlib.RingTheory.PowerSeries.WellKnown
import Mathlib.Basic.Complex.Basic
import Mathlib.Data.Nat.Choose.Bounds

namespace Komorebi.PaperIV
noncomputable section

/-- Formal expansion of the normalized pole `(1-z/rho)^(-ell)`. -/
def principalPartSeries (ρ : ℂ) (ℓ : ℕ) : PowerSeries ℂ :=
  PowerSeries.rescale ρ⁻¹ (PowerSeries.invOneSubPow ℂ ℓ).val

theorem principalPartSeries_coefficient (ρ : ℂ) {ℓ : ℕ} (hℓ : 0 < ℓ) (m : ℕ) :
    PowerSeries.coeff m (principalPartSeries ρ ℓ) =
      ((m + ℓ - 1).choose (ℓ - 1) : ℂ) * ρ⁻¹ ^ m := by
  rw [principalPartSeries, PowerSeries.coeff_rescale,
    PowerSeries.invOneSubPow_val_eq_mk_sub_one_add_choose_of_pos ℂ ℓ hℓ,
    PowerSeries.coeff_mk]
  rw [show ℓ - 1 + m = m + ℓ - 1 by omega]
  ring

theorem principalPartSeries_inverse (ρ : ℂ) (ℓ : ℕ) :
    principalPartSeries ρ ℓ * (1 - PowerSeries.C ρ⁻¹ * PowerSeries.X) ^ ℓ = 1 := by
  have h0 := (PowerSeries.invOneSubPow ℂ ℓ).val_inv
  rw [PowerSeries.invOneSubPow_inv_eq_one_sub_pow] at h0
  have h := congrArg (PowerSeries.rescale ρ⁻¹) h0
  simpa only [principalPartSeries, map_mul, map_pow, map_sub, map_one, PowerSeries.rescale_X] using h

/-- Uniform polynomial bound for all lower principal-part orders. -/
theorem lower_principal_part_choose_bound {m ℓ r : ℕ}
    (hm : 1 ≤ m) (hℓ : 1 ≤ ℓ) (hℓr : ℓ < r) :
    (m + ℓ - 1).choose (ℓ - 1) ≤ ℓ ^ (ℓ - 1) * m ^ (r - 2) := by
  calc
    _ ≤ (m + ℓ - 1) ^ (ℓ - 1) := Nat.choose_le_pow _ _
    _ ≤ (ℓ * m) ^ (ℓ - 1) := Nat.pow_le_pow_left (by
      have h := Nat.mul_le_mul_left (ℓ - 1) hm
      have hl : ℓ - 1 + 1 = ℓ := by omega
      have he : (ℓ - 1) * m + m = ℓ * m := by
        simpa only [Nat.add_mul, one_mul] using congrArg (fun x => x * m) hl
      omega) _
    _ = ℓ ^ (ℓ - 1) * m ^ (ℓ - 1) := Nat.mul_pow _ _ _
    _ ≤ ℓ ^ (ℓ - 1) * m ^ (r - 2) := Nat.mul_le_mul_left _ (Nat.pow_le_pow_right hm (by omega))

end
end Komorebi.PaperIV
