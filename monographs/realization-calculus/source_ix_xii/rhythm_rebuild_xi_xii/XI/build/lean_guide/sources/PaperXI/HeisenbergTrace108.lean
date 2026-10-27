import Mathlib.RepresentationTheory.Character
import Mathlib.Analysis.Complex.Basic

/-! The finite Heisenberg character formula, derived from scalar restriction
and detection by actual commutators. No trace-support hypothesis is supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergTrace108
open Representation
variable {K W : Type*} [Group K] [AddCommGroup W] [Module ℂ W]
  [FiniteDimensional ℂ W]
  (H : Subgroup K) (θ : H →* ℂˣ) (ρ : Representation ℂ K W)
  (hscalar : ∀ h : H, ρ h = (θ h : ℂ) • LinearMap.id)

include hscalar in
theorem character_on_subgroup (h : H) :
    ρ.character h = (Module.finrank ℂ W : ℂ) * (θ h : ℂ) := by
  simp [Representation.character, hscalar, mul_comm]

omit [FiniteDimensional ℂ W] in
include hscalar in
/-- A commutator with nontrivial central character forces trace zero. -/
theorem character_zero_of_commutator (x y : K) (z : H)
    (he : y * x * y⁻¹ = (z : K) * x) (hz : θ z ≠ 1) : ρ.character x = 0 := by
  have ht := ρ.char_conj x y
  rw [he] at ht
  have hs : ρ.character ((z : K) * x) = (θ z : ℂ) * ρ.character x := by
    simp [Representation.character, map_mul, hscalar, Module.End.mul_eq_comp]
  rw [hs] at ht
  have hc : (θ z : ℂ) - 1 ≠ 0 := by
    intro h
    apply hz
    apply Units.ext
    exact sub_eq_zero.mp h
  apply (mul_eq_zero.mp (show ((θ z : ℂ) - 1) * ρ.character x = 0 by
    rw [sub_mul, one_mul, ht, sub_self])).resolve_left hc

omit [FiniteDimensional ℂ W] in
include hscalar in
theorem character_off_subgroup
    (hdetect : ∀ x : K, x ∉ H → ∃ y : K, ∃ z : H,
      y * x * y⁻¹ = (z : K) * x ∧ θ z ≠ 1)
    (x : K) (hx : x ∉ H) : ρ.character x = 0 := by
  obtain ⟨y, z, he, hz⟩ := hdetect x hx
  exact character_zero_of_commutator H θ ρ hscalar x y z he hz

end PaperXI.HeisenbergTrace108
