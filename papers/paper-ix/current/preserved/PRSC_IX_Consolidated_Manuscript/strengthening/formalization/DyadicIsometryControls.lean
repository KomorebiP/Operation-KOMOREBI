module
public import DyadicFourIsometry
public import Mathlib.NumberTheory.Padics.RingHoms

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.DyadicIsometryControls

open DyadicFourIsometry

/-- A concrete value confirms the normalization and its sign. -/
theorem address_zero_at_one : isometry 0 (by decide) (1 : ℤ_[2]) = -1 := by
  have hr : DyadicPacketRational.packet 0 1 = (-1 : ℚ) := by
    norm_num [DyadicPacketRational.packet, Congruential.unnormalized,
      DyadicFourLeastPeriods.originalBonus, DyadicFourPrefix.bonus,
      DyadicFourPrefix.coeff_0_1]
  apply Subtype.ext
  have h := isometry_nat 0 (by decide) 1
  simpa [hr] using h

/-- The next exact value detects that the isometry is not additive. -/
theorem address_zero_at_two : isometry 0 (by decide) (2 : ℤ_[2]) = 34 := by
  have hr : DyadicPacketRational.packet 0 2 = (34 : ℚ) := by
    norm_num [DyadicPacketRational.packet, Congruential.unnormalized,
      DyadicFourLeastPeriods.originalBonus, DyadicFourPrefix.bonus,
      DyadicFourPrefix.coeff_0_2]
  apply Subtype.ext
  have h := isometry_nat 0 (by decide) 2
  change ((isometry 0 (by decide) (2 : ℤ_[2])) : ℚ_[2]) = (34 : ℚ_[2])
  simpa [hr] using h

/-- A metric isometry does not thereby become an additive or ring homomorphism. -/
theorem address_zero_not_additive :
    ¬ ∀ x y : ℤ_[2], isometry 0 (by decide) (x + y) =
      isometry 0 (by decide) x + isometry 0 (by decide) y := by
  intro h
  have hh := h 1 1
  norm_num [address_zero_at_one, address_zero_at_two] at hh

/-- The inverse recovers the nontrivial second rational sample. -/
theorem address_zero_inverse_at_thirty_four :
    (isometry 0 (by decide)).symm (34 : ℤ_[2]) = 2 := by
  rw [← address_zero_at_two]
  exact (isometry 0 (by decide)).symm_apply_apply 2

/-- The unnormalized address-zero packet stays in the odd residue class. -/
theorem original_address_zero_ne_zero (x : ℤ_[2]) :
    originalExtension 0 (by decide) x ≠ 0 := by
  intro hx
  have h := congrArg (PadicInt.toZMod : ℤ_[2] →+* ZMod 2) hx
  have ht : PadicInt.toZMod (2 : ℤ_[2]) = (0 : ZMod 2) := by
    change PadicInt.toZMod ((2 : ℕ) : ℤ_[2]) = 0
    rw [map_natCast]
    exact ZMod.natCast_self 2
  norm_num [originalExtension, DyadicFourLeastPeriods.originalBonus,
    DyadicFourPrefix.bonus, ht] at h

/-- The original affine image is not the whole dyadic integer ring. -/
theorem original_address_zero_not_surjective :
    ¬ Function.Surjective (originalExtension 0 (by decide)) := by
  intro h
  obtain ⟨x, hx⟩ := h 0
  exact original_address_zero_ne_zero x hx

end KomorebiPaperIX.DyadicIsometryControls
