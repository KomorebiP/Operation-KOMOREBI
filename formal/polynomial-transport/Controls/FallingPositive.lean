import KomorebiPolynomial.FallingPackets
import KomorebiPolynomial.FallingProduct
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

/-! Concrete correspondence controls for the finite polynomial coordinate change. -/

set_option autoImplicit false
open Polynomial
open scoped BigOperators
open Komorebi.Polynomial.FallingFactorial
open Komorebi.Polynomial.FallingPackets
open Komorebi.Polynomial.FallingProduct
open Komorebi.Polynomial.Packets

namespace Komorebi.Polynomial.Controls.FallingPositive

/-- The forward map uses descending factorials, with no factorial divisor. -/
theorem phi_square :
    fallingEquiv ((X : ℚ[X]) ^ 2) = X ^ 2 - X := by
  rw [fallingEquiv_X_pow, descPochhammer_succ_right ℚ 1, descPochhammer_one]
  norm_num
  ring

/-- The opposite direction has the second-Stirling coefficients. -/
theorem inverse_phi_square :
    fallingEquiv.symm ((X : ℚ[X]) ^ 2) = X ^ 2 + X := by
  rw [fallingEquiv_symm_X_pow]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond]
  ring

/-- The complete fifth-degree inverse displayed in the guide. -/
theorem inverse_phi_fifth :
    fallingEquiv.symm ((X : ℚ[X]) ^ 5) =
      X + 15 * X ^ 2 + 25 * X ^ 3 + 10 * X ^ 4 + X ^ 5 := by
  rw [fallingEquiv_symm_X_pow]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond]

/-- Even falling degree is different from even ordinary degree. -/
theorem even_square :
    fallingPacket 2 0 ((X : ℚ[X]) ^ 2) = X ^ 2 - X := by
  rw [fallingPacket_apply, inverse_phi_square]
  change fallingEquiv (packetLinear 2 0 (X ^ 2 + X)) = _
  rw [map_add]
  have hX : packet 2 0 (X : ℚ[X]) = 0 := by
    simpa using (packet_X_pow (R := ℚ) 2 0 1)
  simp only [packetLinear_apply, packet_X_pow, hX]
  rw [ite_eq_left (by decide), add_zero, phi_square]

/-- The odd falling packet of a square is nonzero. -/
theorem odd_square :
    fallingPacket 2 1 ((X : ℚ[X]) ^ 2) = X := by
  rw [fallingPacket_apply, inverse_phi_square]
  change fallingEquiv (packetLinear 2 1 (X ^ 2 + X)) = _
  rw [map_add]
  have hX : packet 2 1 (X : ℚ[X]) = X := by
    simpa using (packet_X_pow (R := ℚ) 2 1 1)
  have hφX : fallingEquiv (X : ℚ[X]) = X := by
    simpa using fallingEquiv_X_pow 1
  simp only [packetLinear_apply, packet_X_pow, hX]
  norm_num [hφX]

/-- Reversing the conjugation produces the opposite linear term. -/
theorem reverse_even_square :
    fallingEquiv.symm (packet 2 0 (fallingEquiv ((X : ℚ[X]) ^ 2))) =
      X ^ 2 + X := by
  rw [phi_square]
  change fallingEquiv.symm (packetLinear 2 0 (X ^ 2 - X)) = _
  rw [map_sub]
  have hX : packet 2 0 (X : ℚ[X]) = 0 := by
    simpa using (packet_X_pow (R := ℚ) 2 0 1)
  simp only [packetLinear_apply, packet_X_pow, hX]
  norm_num [inverse_phi_square]

/-- The first displayed packet of `X^5` evaluates to 600 at four. -/
theorem fifth_residue_zero_at_four :
    (fallingPacket 3 0 ((X : ℚ[X]) ^ 5)).eval 4 = 600 := by
  have hexp := power_eq_stirling_sum 5
  simp only [← smul_eq_C_mul] at hexp
  rw [hexp, fallingPacket_expansion]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond,
    descPochhammer_succ_right, descPochhammer_zero, smul_eq_C_mul]

/-- The second displayed packet of `X^5` evaluates to 244 at four. -/
theorem fifth_residue_one_at_four :
    (fallingPacket 3 1 ((X : ℚ[X]) ^ 5)).eval 4 = 244 := by
  have hexp := power_eq_stirling_sum 5
  simp only [← smul_eq_C_mul] at hexp
  rw [hexp, fallingPacket_expansion]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond,
    descPochhammer_succ_right, descPochhammer_zero, smul_eq_C_mul]

/-- The third displayed packet of `X^5` evaluates to 180 at four. -/
theorem fifth_residue_two_at_four :
    (fallingPacket 3 2 ((X : ℚ[X]) ^ 5)).eval 4 = 180 := by
  have hexp := power_eq_stirling_sum 5
  simp only [← smul_eq_C_mul] at hexp
  rw [hexp, fallingPacket_expansion]
  norm_num [Finset.sum_range_succ, Nat.stirlingSecond,
    descPochhammer_succ_right, descPochhammer_zero, smul_eq_C_mul]

/-- Transported degrees two and two wrap around to residue one modulo three. -/
theorem product_wraparound :
    fallingPacket 3 1 (fallingProduct (descPochhammer ℚ 2) (descPochhammer ℚ 2)) =
      descPochhammer ℚ 4 := by
  rw [fallingProduct_descPochhammer, fallingPacket_basis]
  norm_num

end Komorebi.Polynomial.Controls.FallingPositive
