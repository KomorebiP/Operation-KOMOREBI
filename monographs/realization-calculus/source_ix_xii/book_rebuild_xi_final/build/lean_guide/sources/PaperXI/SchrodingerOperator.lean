import Mathlib.Analysis.SpecialFunctions.Complex.CircleAddChar
import Mathlib.LinearAlgebra.Dual.Defs
import Mathlib.RepresentationTheory.Basic

/-! The literal Schrödinger operators in the manuscript's sign convention. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.Schrodinger
open scoped BigOperators

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

def operator (ψ : AddChar K ℂ) (x : X) (ξ : Module.Dual K X) (z : K) :
    Module.End ℂ (X → ℂ) where
  toFun f u := ψ (z + ξ u + (2 : K)⁻¹ * ξ x) * f (u + x)
  map_add' f g := by
    funext u
    simp only [Pi.add_apply]
    ring
  map_smul' a f := by
    funext u
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    ring

@[simp] theorem operator_apply (ψ : AddChar K ℂ) (x : X) (ξ : Module.Dual K X)
    (z : K) (f : X → ℂ) (u : X) :
    operator ψ x ξ z f u = ψ (z + ξ u + (2 : K)⁻¹ * ξ x) * f (u + x) := rfl

def translation (x : X) : Module.End ℂ (X → ℂ) where
  toFun f u := f (u + x)
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

@[simp] theorem translation_apply (x : X) (f : X → ℂ) (u : X) :
    translation x f u = f (u + x) := rfl

def modulation (ψ : AddChar K ℂ) (ξ : Module.Dual K X) :
    Module.End ℂ (X → ℂ) where
  toFun f u := ψ (ξ u) * f u
  map_add' f g := by
    funext u
    simp only [Pi.add_apply]
    ring
  map_smul' a f := by
    funext u
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    ring

@[simp] theorem modulation_apply (ψ : AddChar K ℂ) (ξ : Module.Dual K X)
    (f : X → ℂ) (u : X) : modulation ψ ξ f u = ψ (ξ u) * f u := rfl

theorem operator_translation (ψ : AddChar K ℂ) (x : X) :
    operator ψ x 0 0 = translation x := by
  ext f u
  simp [translation]

theorem operator_modulation (ψ : AddChar K ℂ) (ξ : Module.Dual K X) :
    operator ψ 0 ξ 0 = modulation ψ ξ := by
  ext f u
  simp [modulation]

theorem operator_central (ψ : AddChar K ℂ) (z : K) :
    operator ψ (0 : X) 0 z = ψ z • LinearMap.id := by
  ext f u
  simp

theorem operator_one (ψ : AddChar K ℂ) :
    operator ψ (0 : X) 0 0 = LinearMap.id := by
  rw [operator_central]
  simp

/-- The phase identity verifies the manuscript's half-symplectic cocycle. -/
theorem phase_add (h2 : (2 : K) ≠ 0) (x y u : X) (ξ η : Module.Dual K X)
    (z t : K) :
    (z + ξ u + (2 : K)⁻¹ * ξ x) +
      (t + η (u + x) + (2 : K)⁻¹ * η y) =
    z + t + (2 : K)⁻¹ * (η x - ξ y) +
      (ξ + η) u + (2 : K)⁻¹ * (ξ + η) (x + y) := by
  simp only [map_add, LinearMap.add_apply]
  field_simp
  ring

theorem operator_mul (ψ : AddChar K ℂ) (h2 : (2 : K) ≠ 0)
    (x y : X) (ξ η : Module.Dual K X) (z t : K) :
    operator ψ x ξ z * operator ψ y η t =
      operator ψ (x + y) (ξ + η) (z + t + (2 : K)⁻¹ * (η x - ξ y)) := by
  ext f u
  change ψ (z + ξ u + (2 : K)⁻¹ * ξ x) *
    (ψ (t + η (u + x) + (2 : K)⁻¹ * η y) * f ((u + x) + y)) = _
  rw [← mul_assoc, ← ψ.map_add_eq_mul, phase_add h2]
  simp [add_assoc]

end PaperXI.Schrodinger
