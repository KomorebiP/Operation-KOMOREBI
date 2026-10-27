module
public import PolynomialObstruction

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialDigitBridge
open Komorebi.NativeAffine Komorebi.PolynomialObstruction
variable {d e : ℕ}

/-- Canonical integer representatives of correction digits. -/
def integerLift (q : ℕ) (t : Fin d → ZMod q) : Fin d → ℤ :=
  fun i => (t i).val

/-- The actual Jacobian over the finite coefficient ring. -/
def digitJacobian (q : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) : (Fin d → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q) where
  toFun t i := ∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod q) * t k
  map_add' t u := by
    ext i
    simp [mul_add, Finset.sum_add_distrib]
  map_smul' a t := by
    ext i
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k _
    ring

theorem reduction_integerLift (q : ℕ) (hq : 0 < q) (t : Fin d → ZMod q) :
    reduction q d (integerLift q t) = t := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  ext i
  change (((t i).val : ℤ) : ZMod q) = t i
  rw [Int.cast_natCast, ZMod.natCast_zmod_val]

/-- Reducing the original integer Jacobian gives exactly the finite-ring map. -/
theorem reduction_jacobian (q : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) :
    digitJacobian q F x (reduction q d t) = reduction q e (jacobian F x t) := by
  ext i
  change (∑ k, (MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) : ZMod q) * (t k : ZMod q)) =
    ((∑ k, MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) * t k : ℤ) : ZMod q)
  simp

/-- A finite correction digit solves the linearized residual equation. -/
abbrev DigitSolutions (q : ℕ) (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) (r : Fin e → ℤ) :=
  {t : Fin d → ZMod q // reduction q e r + digitJacobian q F x t = 0}

/-- Actual polynomial liftability for each finite correction digit. -/
theorem digit_solution_iff (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (t : Fin d → ZMod q) :
    (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • integerLift q t) i) ↔
      reduction q e r + digitJacobian q F x t = 0 := by
  rw [next_level_iff_digit q L hq hL F x r hr]
  rw [map_add, ← reduction_jacobian, reduction_integerLift q hq t]

/-- Every integer correction projects to a finite digit solution and conversely. -/
theorem digit_solutions_nonempty_iff (q : ℕ) (hq : 0 < q)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) (r : Fin e → ℤ) :
    Nonempty (DigitSolutions q F x r) ↔ obstruction q (jacobian F x) r = 0 := by
  rw [obstruction_zero_iff_correction]
  constructor
  · rintro ⟨⟨t, ht⟩⟩
    refine ⟨integerLift q t, ?_⟩
    rw [map_add, ← reduction_jacobian, reduction_integerLift q hq t]
    exact ht
  · rintro ⟨t, ht⟩
    refine ⟨⟨reduction q d t, ?_⟩⟩
    rw [reduction_jacobian]
    simpa only [map_add] using ht

end Komorebi.PolynomialDigitBridge
