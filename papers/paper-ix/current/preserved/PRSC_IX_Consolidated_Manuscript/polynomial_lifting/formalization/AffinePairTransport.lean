module
public import AffineObstructionCore

/-!
# Exact transport for two affine lifting conditions

Author: Komorebi P.
The same correction vector must satisfy both residual-digit equations.
The modulus is any positive natural number; level zero is included.
-/

@[expose] public section
set_option autoImplicit false

namespace Komorebi.AffinePair
open Komorebi.NativeAffine

variable {d e f : ℕ}

/-- Two systems lift at a single vector representing the original residue. -/
def HasJointLift (p L : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b : Fin e → ℤ) (c : Fin f → ℤ) (x : Fin d → ℤ) : Prop :=
  ∃ y : Fin d → ℤ,
    (∀ i, (p : ℤ)^L ∣ (y - x) i) ∧
    (∀ i, (p : ℤ)^(L+1) ∣ (A y - b) i) ∧
    (∀ i, (p : ℤ)^(L+1) ∣ (B y - c) i)

theorem next_level_iff_digit (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (b r : Fin e → ℤ) (x t : Fin d → ℤ)
    (hr : A x - b = (p : ℤ)^L • r) :
    (∀ i, (p : ℤ)^(L+1) ∣ (A (x + (p : ℤ)^L • t) - b) i) ↔
    reduction p e (r + A t) = 0 := by
  rw [reduction_zero_iff]
  have hq : (p : ℤ)^L ≠ 0 :=
    pow_ne_zero _ (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hp))
  constructor <;> intro h i
  · have hi := h i
    rw [affine_residual_transport _ A b r x t hr] at hi
    change (p : ℤ)^(L+1) ∣ (p : ℤ)^L * (r + A t) i at hi
    rwa [pow_succ, mul_dvd_mul_iff_left hq] at hi
  · rw [affine_residual_transport _ A b r x t hr]
    change (p : ℤ)^(L+1) ∣ (p : ℤ)^L * (r + A t) i
    rw [pow_succ, mul_dvd_mul_iff_left hq]
    exact h i

theorem joint_lift_iff_digit_correction (p L : ℕ) (hp : 0 < p)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b r : Fin e → ℤ) (c s : Fin f → ℤ) (x : Fin d → ℤ)
    (hr : A x - b = (p : ℤ)^L • r)
    (hs : B x - c = (p : ℤ)^L • s) :
    HasJointLift p L A B b c x ↔
    ∃ t : Fin d → ℤ, reduction p e (r + A t) = 0 ∧
      reduction p f (s + B t) = 0 := by
  constructor
  · rintro ⟨y, hy, hA, hB⟩
    obtain ⟨t, rfl⟩ := (same_residue_iff ((p : ℤ)^L) x y).mp hy
    exact ⟨t, (next_level_iff_digit p L hp A b r x t hr).mp hA,
      (next_level_iff_digit p L hp B c s x t hs).mp hB⟩
  · rintro ⟨t, hA, hB⟩
    refine ⟨x + (p : ℤ)^L • t,
      (same_residue_iff ((p : ℤ)^L) x _).mpr ⟨t, rfl⟩, ?_, ?_⟩
    · exact (next_level_iff_digit p L hp A b r x t hr).mpr hA
    · exact (next_level_iff_digit p L hp B c s x t hs).mpr hB

/-- With any known individual correction, its whole solution set is a fiber
of the actual reduced coefficient map. -/
theorem digit_correction_iff_same_image (p : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (r : Fin e → ℤ) (u t : Fin d → ℤ)
    (hu : reduction p e (r + A u) = 0) :
    reduction p e (r + A t) = 0 ↔ digitMap p A t = digitMap p A u := by
  have hu' : reduction p e r + digitMap p A u = 0 := by
    simpa only [map_add, digitMap, LinearMap.comp_apply] using hu
  have ht : reduction p e (r + A t) = reduction p e r + digitMap p A t := by
    simp only [map_add, digitMap, LinearMap.comp_apply]
  rw [ht]
  constructor
  · intro h
    exact add_left_cancel (h.trans hu'.symm)
  · intro h
    rwa [h]

end Komorebi.AffinePair

#print axioms Komorebi.AffinePair.HasJointLift
#print axioms Komorebi.AffinePair.next_level_iff_digit
#print axioms Komorebi.AffinePair.joint_lift_iff_digit_correction
#print axioms Komorebi.AffinePair.digit_correction_iff_same_image
