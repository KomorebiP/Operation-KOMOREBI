module
public import AffineSharedCorrection
public import Mathlib.Tactic.NormNum

@[expose] public section
set_option autoImplicit false

namespace Komorebi.AffinePairControls
open Komorebi.NativeAffine Komorebi.AffinePair

abbrev oneId : (Fin 1 → ℤ) →ₗ[ℤ] (Fin 1 → ℤ) := LinearMap.id

/-- Two individually solvable congruences need not have a common lift. -/
theorem two_individual_lifts :
    (∃ y : ℤ, (4 : ℤ) ∣ y) ∧ (∃ y : ℤ, (4 : ℤ) ∣ y - 2) := by
  exact ⟨⟨0, dvd_zero _⟩, ⟨2, by norm_num⟩⟩

theorem incompatible_mod_four :
    ¬ HasJointLift 2 1 oneId oneId (fun _ => 0) (fun _ => 2) (fun _ => 0) := by
  rintro ⟨y, _, hA, hB⟩
  have h0 := hA 0
  have h2 := hB 0
  norm_num [oneId] at h0 h2
  omega

/-- The theorem's allowed composite-modulus and level-zero endpoint is real. -/
theorem composite_level_zero :
    HasJointLift 4 0 oneId oneId (fun _ => 5) (fun _ => 9) (fun _ => 0) := by
  refine ⟨fun _ => 1, ?_, ?_, ?_⟩ <;> intro i <;> norm_num [oneId]

theorem modulus_one (d e f L : ℕ)
    (A : (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ))
    (B : (Fin d → ℤ) →ₗ[ℤ] (Fin f → ℤ))
    (b : Fin e → ℤ) (c : Fin f → ℤ) (x : Fin d → ℤ) :
    HasJointLift 1 L A B b c x := by
  refine ⟨x, ?_, ?_, ?_⟩ <;> intro i <;> simp

end Komorebi.AffinePairControls

#print axioms Komorebi.AffinePairControls.oneId
#print axioms Komorebi.AffinePairControls.two_individual_lifts
#print axioms Komorebi.AffinePairControls.incompatible_mod_four
#print axioms Komorebi.AffinePairControls.composite_level_zero
#print axioms Komorebi.AffinePairControls.modulus_one
