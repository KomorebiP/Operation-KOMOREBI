module
public import FiniteUnits
public import Mathlib.NumberTheory.Padics.PadicIntegers
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.FrobeniusSquare
variable (p : ℕ) [Fact p.Prime]

/-- Fermat congruence lifts through one additional p-power, including nonunits. -/
theorem power_defect_divisible (a : ℕ) :
    (p:ℤ)^2 ∣ (a:ℤ)^(p^2)-(a:ℤ)^p := by
  have h := FiniteUnits.power_lift_congruence p 1
    ((a:ZMod (p^(1+1)))^p) (a:ZMod (p^(1+1))) (by
      simp only [map_pow, map_natCast]
      exact ZMod.pow_card (a:ZMod p))
  have he : (a:ZMod (p^2))^(p^2)-(a:ZMod (p^2))^p=0 := by
    simpa only [pow_one, ←pow_mul, ←pow_two, sub_eq_zero] using h
  rw [←Nat.cast_pow]
  apply (ZMod.intCast_zmod_eq_zero_iff_dvd _ _).mp
  push_cast
  exact he

/-- The normalized spectral defect is an actual p-adic integer. -/
theorem normalized_defect_integral (a : ℕ) :
    (p:ℚ_[p])⁻¹*((p:ℚ_[p])⁻¹*((a:ℚ_[p])^(p^2)-(a:ℚ_[p])^p))
      ∈ PadicInt.subring p := by
  obtain ⟨z,hz⟩ := power_defect_divisible p a
  have h : (a:ℚ_[p])^(p^2)-(a:ℚ_[p])^p=(p:ℚ_[p])^2*(z:ℚ_[p]) := by
    exact_mod_cast hz
  have hp : (p:ℚ_[p])≠0 := Nat.cast_ne_zero.mpr (Fact.out : p.Prime).ne_zero
  rw [h]
  have he : (p:ℚ_[p])⁻¹*((p:ℚ_[p])⁻¹*((p:ℚ_[p])^2*(z:ℚ_[p])))=(z:ℚ_[p]) := by
    field_simp
  rw [he]
  exact intCast_mem _ z

end KomorebiPaperIX.FrobeniusSquare
