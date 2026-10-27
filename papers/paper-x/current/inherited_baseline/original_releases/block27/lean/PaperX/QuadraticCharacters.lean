import PaperX.QuadraticAlgebra
import PaperX.CompletionExamples

/-! Quadratic coordinate points are exactly unit-valued characters of the
actual cyclic group `Multiplicative (ZMod 2)`. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.QuadraticCharacters
open PaperX.QuadraticAlgebra PaperX.CompletionExamples

theorem generator_sq : generator ^ 2 = 1 := by decide +kernel

theorem generator_ne_one : generator ≠ 1 := by decide +kernel

theorem c2_cases (g : C2) : g = 1 ∨ g = generator := by
  revert g
  decide +kernel

variable {B : Type*} [CommRing B]

/-- A quadratic root is a unit, with itself as its inverse. -/
def rootUnit (x : Root B) : Bˣ where
  val := x.val
  inv := x.val
  val_inv := by simpa only [pow_two] using x.property
  inv_val := by simpa only [pow_two] using x.property

@[simp] theorem rootUnit_val (x : Root B) : (rootUnit x : B) = x.val := rfl

theorem rootUnit_sq (x : Root B) : rootUnit x * rootUnit x = 1 := by
  apply Units.ext
  exact (pow_two x.val).symm.trans x.property

/-- The character associated with an actual root of `X^2 - 1`. -/
def ofRoot (x : Root B) : C2 →* Bˣ where
  toFun g := if g = 1 then 1 else rootUnit x
  map_one' := by simp
  map_mul' g h := by
    rcases c2_cases g with rfl | rfl <;> rcases c2_cases h with rfl | rfl
    · simp
    · simp
    · simp
    · have hg : generator * generator = 1 := by simpa only [pow_two] using generator_sq
      simp [hg, generator_ne_one, rootUnit_sq]

@[simp] theorem ofRoot_generator (x : Root B) :
    (ofRoot x generator : B) = x.val := by
  simp [ofRoot, generator_ne_one]

theorem ofRoot_apply_val (x : Root B) (g : C2) :
    (ofRoot x g : B) = if g = 1 then 1 else x.val := by
  split_ifs with h <;> simp [ofRoot, h]

/-- Evaluating any C2 character produces a root of the coordinate equation. -/
def toRoot (χ : C2 →* Bˣ) : Root B :=
  ⟨(χ generator : B), by
    have h : χ generator ^ 2 = 1 := by rw [← map_pow, generator_sq, map_one]
    simpa only [Units.val_pow_eq_pow_val, Units.val_one] using
      congrArg (fun u : Bˣ => (u : B)) h⟩

/-- Evaluation at the specified generator determines a character. -/
theorem character_ext {χ ψ : C2 →* Bˣ}
    (h : (χ generator : B) = (ψ generator : B)) : χ = ψ := by
  apply MonoidHom.ext
  intro g
  rcases c2_cases g with rfl | rfl
  · simp
  · exact Units.ext h

/-- No nontriviality, reducedness, or invertibility-of-two assumption is used. -/
def characterEquiv : Root B ≃ (C2 →* Bˣ) where
  toFun := ofRoot
  invFun := toRoot
  left_inv x := by
    apply Subtype.ext
    exact ofRoot_generator x
  right_inv χ := by
    apply character_ext
    exact ofRoot_generator (toRoot χ)

variable {C : Type*} [CommRing C]

/-- Reduction of roots agrees with reduction of the associated characters. -/
theorem map_ofRoot (f : B →+* C) (x : Root B) :
    (Units.map f.toMonoidHom).comp (ofRoot x) = ofRoot (mapRoot f x) := by
  apply character_ext
  simp

variable (R : Type*) [CommRing R] [Algebra R B]

/-- The full quotient-ring-point to finite-group-character equivalence. -/
def pointCharacterEquiv : (CoordinateRing R →ₐ[R] B) ≃ (C2 →* Bˣ) :=
  (pointEquiv R).trans characterEquiv

end PaperX.QuadraticCharacters
