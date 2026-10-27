module
public import AffineObstructionCore
public import Mathlib.Algebra.MvPolynomial.PDeriv
public import PolynomialTaylor

/-!
# Finite polynomial obstruction at a fixed presentation

The Jacobian below is computed from the actual multivariable polynomials.
The one-step criterion uses their Taylor remainder, not a linearization premise.
-/

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialObstruction

open Komorebi.NativeAffine

variable {d e : ℕ}

/-- Evaluation of the given finite list of integer polynomials. -/
def evalSystem (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) : Fin e → ℤ :=
  fun i => MvPolynomial.eval x (F i)

/-- The actual Jacobian, acting on an integer correction vector. -/
def jacobian (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ) :
    (Fin d → ℤ) →ₗ[ℤ] (Fin e → ℤ) where
  toFun t i := ∑ k, MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) * t k
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

theorem evalSystem_apply (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x : Fin d → ℤ) (i : Fin e) :
    evalSystem F x i = MvPolynomial.eval x (F i) := rfl

theorem jacobian_apply (F : Fin e → MvPolynomial (Fin d) ℤ)
    (x t : Fin d → ℤ) (i : Fin e) :
    jacobian F x t i = ∑ k, MvPolynomial.eval x (MvPolynomial.pderiv k (F i)) * t k := rfl

/-- A lower-level solution has an exact integer residual. -/
theorem residual_exists (q L : ℕ)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i) :
    ∃ r : Fin e → ℤ, evalSystem F x = (q : ℤ)^L • r := by
  choose r hr using hx
  exact ⟨r, funext hr⟩

theorem residual_unique (q L : ℕ) (hq : 0 < q)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r s : Fin e → ℤ)
    (hr : evalSystem F x = (q : ℤ)^L • r)
    (hs : evalSystem F x = (q : ℤ)^L • s) : r = s := by
  have hqL : (q : ℤ)^L ≠ 0 := pow_ne_zero _ (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hq))
  ext i
  exact mul_left_cancel₀ hqL (congrFun (hr.symm.trans hs) i)

/-- Subtracting a multiple of the modulus preserves divisibility. -/
theorem dvd_iff_of_dvd_sub (m a b : ℤ) (h : m ∣ a - b) :
    m ∣ a ↔ m ∣ b := by
  constructor
  · intro ha
    simpa using dvd_sub ha h
  · intro hb
    simpa using dvd_add h hb

/-- Taylor expansion transports the exact residual up to the next modulus. -/
theorem taylor_residual_dvd (q L : ℕ) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (t : Fin d → ℤ) (i : Fin e) :
    (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • t) i -
      (q : ℤ)^L * (r + jacobian F x t) i := by
  have hx : MvPolynomial.eval x (F i) = (q : ℤ)^L * r i := congrFun hr i
  have ht := Komorebi.PolynomialTaylor.taylor_step_dvd (F i) x t q L hL
  have hshift : x + (q : ℤ)^L • t = fun k => x k + (q : ℤ)^L * t k := by
    ext k
    simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
  rw [hshift]
  convert ht using 1
  dsimp [evalSystem, jacobian, Komorebi.PolynomialTaylor.directional]
  rw [hx]
  ring

/-- Each integer correction lifts exactly when its actual Jacobian digit cancels
the residual. This is uniform in the polynomial list and the correction. -/
theorem next_level_iff_digit (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r)
    (t : Fin d → ℤ) :
    (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • t) i) ↔
      reduction q e (r + jacobian F x t) = 0 := by
  rw [reduction_zero_iff]
  apply forall_congr'
  intro i
  rw [dvd_iff_of_dvd_sub _ _ _ (taylor_residual_dvd q L hL F x r hr t i)]
  have hqL : (q : ℤ)^L ≠ 0 := pow_ne_zero _ (Int.natCast_ne_zero.mpr (Nat.ne_of_gt hq))
  rw [pow_succ, mul_dvd_mul_iff_left hqL]

/-- The finite cokernel decides the existence of a next-level digit correction. -/
theorem polynomial_lift_iff_obstruction_zero (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r) :
    (∃ t : Fin d → ℤ, ∀ i,
      (q : ℤ)^(L+1) ∣ evalSystem F (x + (q : ℤ)^L • t) i) ↔
      obstruction q (jacobian F x) r = 0 := by
  rw [obstruction_zero_iff_correction]
  exact exists_congr fun t => next_level_iff_digit q L hq hL F x r hr t

/-- The same criterion stated directly for all representatives of the lower
residue vector, rather than a chosen correction parametrization. -/
theorem polynomial_same_residue_lift_iff (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (r : Fin e → ℤ) (hr : evalSystem F x = (q : ℤ)^L • r) :
    (∃ y : Fin d → ℤ,
      (∀ i, (q : ℤ)^L ∣ (y - x) i) ∧
      (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F y i)) ↔
      obstruction q (jacobian F x) r = 0 := by
  rw [← polynomial_lift_iff_obstruction_zero q L hq hL F x r hr]
  constructor
  · rintro ⟨y, hy, hFy⟩
    obtain ⟨t, rfl⟩ := (same_residue_iff ((q : ℤ)^L) x y).mp hy
    exact ⟨t, hFy⟩
  · rintro ⟨t, ht⟩
    exact ⟨x + (q : ℤ)^L • t,
      (same_residue_iff ((q : ℤ)^L) x _).mpr ⟨t, rfl⟩, ht⟩

/-- Every solution of a fixed finite polynomial presentation has an explicit
finite obstruction, with vanishing equivalent to an actual one-step lift.
The modulus may be composite and may equal one. -/
theorem finite_polynomial_obstruction (q L : ℕ) (hq : 0 < q) (hL : 1 ≤ L)
    (F : Fin e → MvPolynomial (Fin d) ℤ) (x : Fin d → ℤ)
    (hx : ∀ i, (q : ℤ)^L ∣ evalSystem F x i) :
    ∃ r : Fin e → ℤ,
      evalSystem F x = (q : ℤ)^L • r ∧
      Finite (Obstruction q (jacobian F x)) ∧
      ((∃ y : Fin d → ℤ,
        (∀ i, (q : ℤ)^L ∣ (y - x) i) ∧
        (∀ i, (q : ℤ)^(L+1) ∣ evalSystem F y i)) ↔
          obstruction q (jacobian F x) r = 0) := by
  obtain ⟨r, hr⟩ := residual_exists q L F x hx
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  exact ⟨r, hr, obstruction_finite q (jacobian F x),
    polynomial_same_residue_lift_iff q L hq hL F x r hr⟩

#print axioms evalSystem
#print axioms jacobian
#print axioms evalSystem_apply
#print axioms jacobian_apply
#print axioms residual_exists
#print axioms residual_unique
#print axioms dvd_iff_of_dvd_sub
#print axioms taylor_residual_dvd
#print axioms next_level_iff_digit
#print axioms polynomial_lift_iff_obstruction_zero
#print axioms polynomial_same_residue_lift_iff
#print axioms finite_polynomial_obstruction

end Komorebi.PolynomialObstruction
