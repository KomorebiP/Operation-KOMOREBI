module

public import PolynomialObstruction
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialControls

open MvPolynomial PolynomialObstruction

def squarePolynomial : MvPolynomial (Fin 1) ℤ := X 0 ^ 2

/-- The first-order remainder can survive modulo the next base at depth zero. -/
theorem zero_depth_taylor_failure :
    ¬ (2 : ℤ) ∣
      eval (fun _ : Fin 1 => (1 : ℤ)) squarePolynomial -
        eval (fun _ : Fin 1 => (0 : ℤ)) squarePolynomial -
        PolynomialTaylor.directional squarePolynomial (fun _ => 0) (fun _ => 1) := by
  norm_num [squarePolynomial, PolynomialTaylor.directional, pderiv_pow]

def squareMinusTwo : Fin 1 → MvPolynomial (Fin 1) ℤ :=
  fun _ => X 0 ^ 2 - C 2

theorem even_square_cannot_be_two_mod_four (y : ℤ) (hy : (2 : ℤ) ∣ y) :
    ¬ (4 : ℤ) ∣ y ^ 2 - 2 := by
  obtain ⟨t, rfl⟩ := hy
  intro h
  have hs : (4 : ℤ) ∣ (2 * t) ^ 2 := ⟨t ^ 2, by ring⟩
  have htwo : (4 : ℤ) ∣ 2 := by
    simpa using dvd_sub hs h
  norm_num at htwo

/-- A singular lower root can have a nonzero one-step obstruction. -/
theorem singular_root_without_lift :
    (∀ i, (2 : ℤ) ∣ evalSystem squareMinusTwo (fun _ => 0) i) ∧
    jacobian squareMinusTwo (fun _ => 0) = 0 ∧
    ¬ (∃ y : Fin 1 → ℤ,
      (∀ i, (2 : ℤ) ∣ y i) ∧
      (∀ i, (4 : ℤ) ∣ evalSystem squareMinusTwo y i)) := by
  refine ⟨?_, ?_, ?_⟩
  · intro i
    simp only [evalSystem, squareMinusTwo, map_sub, map_pow, eval_X, eval_C]
    norm_num
  · apply LinearMap.ext
    intro t
    ext i
    change (∑ k, eval (fun _ : Fin 1 => (0 : ℤ)) (pderiv k (squareMinusTwo i)) * t k) = 0
    simp only [squareMinusTwo, map_sub, pderiv_pow, pderiv_C, map_mul, map_pow, eval_X]
    simp
  · rintro ⟨y, hy, hF⟩
    have heven : (2 : ℤ) ∣ y 0 := by simpa using hy 0
    have hfour : (4 : ℤ) ∣ y 0 ^ 2 - 2 := by
      simpa [evalSystem, squareMinusTwo] using hF 0
    exact even_square_cannot_be_two_mod_four (y 0) heven hfour

def linearZero : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0
def linearTwo : Fin 1 → MvPolynomial (Fin 1) ℤ := fun _ => X 0 - C 2

/-- Each equation lifts the same lower residue separately. -/
theorem separate_polynomial_lifts :
    (∃ y : Fin 1 → ℤ,
      (∀ i, (2 : ℤ) ∣ y i) ∧
      (∀ i, (4 : ℤ) ∣ evalSystem linearZero y i)) ∧
    (∃ y : Fin 1 → ℤ,
      (∀ i, (2 : ℤ) ∣ y i) ∧
      (∀ i, (4 : ℤ) ∣ evalSystem linearTwo y i)) := by
  constructor
  · refine ⟨fun _ => 0, ?_, ?_⟩ <;> intro i <;> norm_num [evalSystem, linearZero]
  · refine ⟨fun _ => 2, ?_, ?_⟩ <;> intro i <;> norm_num [evalSystem, linearTwo]

/-- Those separate lifts have no common next-level representative. -/
theorem no_common_polynomial_lift :
    ¬ (∃ y : Fin 1 → ℤ,
      (∀ i, (2 : ℤ) ∣ y i) ∧
      (∀ i, (4 : ℤ) ∣ evalSystem linearZero y i) ∧
      (∀ i, (4 : ℤ) ∣ evalSystem linearTwo y i)) := by
  rintro ⟨y, _, hF, hG⟩
  have hzero : (4 : ℤ) ∣ y 0 := by simpa [evalSystem, linearZero] using hF 0
  have htwo : (4 : ℤ) ∣ y 0 - 2 := by simpa [evalSystem, linearTwo] using hG 0
  have hbad : (4 : ℤ) ∣ 2 := by
    simpa using dvd_sub hzero htwo
  norm_num at hbad

end Komorebi.PolynomialControls
