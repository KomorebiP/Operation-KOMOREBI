import KomorebiPolynomial.RootsOfUnity
import KomorebiPolynomial.FallingPackets
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-! Exact finite Fourier controls, including the normalization and character sign. -/

set_option autoImplicit false
open Polynomial
open scoped BigOperators
open Komorebi.Polynomial.RootsOfUnity
open Komorebi.Polynomial.FallingFactorial
open Komorebi.Polynomial.FallingPackets
open Komorebi.Polynomial.Packets

namespace Komorebi.Polynomial.Controls.FourierPositive

/-- Order one gives identity on every finite complex polynomial. -/
theorem order_one (p : ℂ[X]) : average 1 0 1 p = p := by
  simp [average]

/-- A normalized even projector fixes the constant polynomial. -/
theorem order_two_constant : average 2 0 (-1) (1 : ℂ[X]) = 1 := by
  rw [average_eq_packet (by decide) (by decide)
    (IsPrimitiveRoot.neg_one 0 (by decide))]
  simpa using (packet_X_pow (R := ℂ) 2 0 0)

/-- Order four detects the negative character convention. -/
theorem order_four_degree_one : average 4 1 Complex.I (X : ℂ[X]) = X := by
  rw [average_eq_packet (by decide) (by decide) Complex.isPrimitiveRoot_I]
  simpa using (packet_X_pow (R := ℂ) 4 1 1)

/-- The same monomial belongs to residue one, not residue three. -/
theorem order_four_other_residue : average 4 3 Complex.I (X : ℂ[X]) = 0 := by
  rw [average_eq_packet (by decide) (by decide) Complex.isPrimitiveRoot_I]
  simpa using (packet_X_pow (R := ℂ) 4 3 1)

/-- A root of unity of the wrong order fails to filter odd degree. -/
theorem nonprimitive_even_X : average 2 0 1 (X : ℂ[X]) = X := by
  ext k
  simp only [average, coeff_smul, finsetSum_coeff, comp_C_mul_X_coeff, smul_eq_mul]
  norm_num [Finset.sum_range_succ]
  ring

/-- Omitting division by the order doubles the constant polynomial's coefficient. -/
theorem unnormalized_even_constant :
    (∑ ℓ ∈ Finset.range 2,
      ((-1 : ℂ) ^ (-((0 * ℓ : ℕ) : ℤ))) •
        (1 : ℂ[X]).comp (C ((-1 : ℂ) ^ ℓ) * X)).coeff 0 = 2 := by
  norm_num [Finset.sum_range_succ]

/-- The positive character sign annihilates `X` in the would-be residue-one packet. -/
theorem positive_character_degree_one :
    ((1 / (4 : ℂ)) • ∑ ℓ ∈ Finset.range 4,
      (Complex.I ^ ((1 * ℓ : ℕ) : ℤ)) •
        (X : ℂ[X]).comp (C (Complex.I ^ ℓ) * X)).coeff 1 = 0 := by
  norm_num [coeff_smul, finsetSum_coeff, comp_C_mul_X_coeff,
    Finset.sum_range_succ, pow_succ, Complex.I_mul_I]

/-- The actual rational coordinate bridge commutes with complex averaging. -/
theorem transported_fourier_coordinates (p : ℚ[X]) :
    average 4 1 Complex.I ((fallingEquiv.symm p).map (algebraMap ℚ ℂ)) =
      (fallingEquiv.symm (fallingPacket 4 1 p)).map (algebraMap ℚ ℂ) := by
  rw [average_rat_map_eq_packet (by decide) (by decide) Complex.isPrimitiveRoot_I]
  simp

end Komorebi.Polynomial.Controls.FourierPositive
