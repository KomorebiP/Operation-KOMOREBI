/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.DiagonalTrace
import KomorebiPaperIV.InfiniteSymmetric
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic

namespace Komorebi.PaperIV
noncomputable section
open Set Filter InnerProductSpace
open scoped Topology Classical InnerProductSpace

def diagonalCompression {ι : Type} (a : ι → ℂ) (S : Finset ι) : Matrix S S ℂ :=
  fun i j => ⟪diagonalHilbertBasis ι i.val, diagonalOperator a (diagonalHilbertBasis ι j.val)⟫_ℂ

theorem diagonalCompression_eq_diagonal {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (S : Finset ι) :
    diagonalCompression a S = Matrix.diagonal (fun i : S => a i.val) := by
  ext i j
  simp only [diagonalCompression, diagonalHilbertBasis_inner, diagonalOperator_apply ha,
    diagonalHilbertBasis_apply, Matrix.diagonal_apply]
  by_cases h : i = j
  · simp [h]
  · have hv : i.val ≠ j.val := fun he => h (Subtype.ext he)
    simp [h, hv]

theorem diagonalCompression_determinant {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (S : Finset ι) (w : ℂ) :
    Matrix.det (1 - w • diagonalCompression a S) = ∏ i ∈ S, (1 - w * a i) := by
  have he : (1 - w • diagonalCompression a S) = Matrix.diagonal (fun i : S => 1 - w * a i.val) := by
    rw [diagonalCompression_eq_diagonal ha]
    ext i j
    by_cases h : i = j <;> simp [h]
  rw [he, Matrix.det_diagonal]
  exact Finset.prod_coe_sort S (fun i => 1 - w * a i)

/-- Specialized diagonal Fredholm determinant, obtained as a limit of the
actual finite-compression determinants in the next theorem. -/
def diagonalFredholmDeterminant {ι : Type} (a : ι → ℂ) (w : ℂ) : ℂ := ∏' i, (1 - w * a i)

theorem diagonalFredholmDeterminant_compression_limit {ι : Type} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (w : ℂ) :
    Tendsto (fun S : Finset ι => Matrix.det (1 - w • diagonalCompression a S)) atTop
      (𝓝 (diagonalFredholmDeterminant a w)) := by
  have hm : Summable (fun i => ‖w * a i‖) := by simpa only [norm_mul] using ha.mul_left ‖w‖
  simpa only [diagonalCompression_determinant ha, diagonalFredholmDeterminant] using!
    (multipliable_one_sub_of_summable hm).hasProd

def reducedZeroEigenvalue (N : ℕ) (i : ZeroMultiplicityIndex (entireReducedDenominator N)) : ℂ :=
  (indexedZero i)⁻¹

theorem reducedZeroEigenvalue_norm_summable {N : ℕ} (hN : 2 ≤ N) :
    Summable (fun i => ‖reducedZeroEigenvalue N i‖) := by
  simpa [reducedZeroEigenvalue, norm_inv, one_div] using zeroMultiplicity_reciprocal_summable
    (entireReducedDenominator_reciprocal_zeros_summable hN)

def reducedZeroOperator (N : ℕ) := diagonalOperator (reducedZeroEigenvalue N)

theorem reducedZeroOperator_traceClass {N : ℕ} (hN : 2 ≤ N) :
    IsHilbertTraceClass (reducedZeroOperator N) :=
  diagonalOperator_traceClass (reducedZeroEigenvalue_norm_summable hN)

theorem reducedZeroOperator_basis {N : ℕ} (hN : 2 ≤ N)
    (i : ZeroMultiplicityIndex (entireReducedDenominator N)) :
    reducedZeroOperator N (diagonalHilbertBasis _ i) =
      (indexedZero i)⁻¹ • diagonalHilbertBasis _ i :=
  diagonalOperator_apply_basis (reducedZeroEigenvalue_norm_summable hN) i

theorem reducedZeroOperator_fredholm {N : ℕ} (hN : 2 ≤ N) (w : ℂ) :
    diagonalFredholmDeterminant (reducedZeroEigenvalue N) w = entireReducedDenominator N w := by
  calc
    _ = fullCanonicalProduct (entireReducedDenominator N) w := by
      simp only [diagonalFredholmDeterminant, reducedZeroEigenvalue, fullCanonicalProduct, div_eq_mul_inv]
    _ = _ := congrFun (entireReducedDenominator_eq_fullCanonicalProduct hN).symm w

theorem reducedZeroOperator_trace_power {N m : ℕ} (hN : 2 ≤ N) (hm : 0 < m)
    {κ : Type} (b : HilbertBasis κ ℂ (lp (fun _ : ZeroMultiplicityIndex (entireReducedDenominator N) => ℂ) 2)) :
    hilbertBasisTrace b (reducedZeroOperator N ^ m) = kappaCoeff (R := ℂ) N m := by
  rw [reducedZeroOperator, diagonalOperator_pow_trace (reducedZeroEigenvalue_norm_summable hN) m
    (summable_norm_positive_powers (reducedZeroEigenvalue_norm_summable hN) hm),
    kappaCoeff_eq_zeroPowerSum hN hm]
  simp [reducedZeroEigenvalue, zeroPowerSum, one_div, inv_pow]

/-- The actual compression determinants converge uniformly on every compact
set to the manuscript's entire denominator. -/
theorem reducedZeroOperator_finite_determinants_uniform {N : ℕ} (hN : 2 ≤ N)
    {K : Set ℂ} (hK : IsCompact K) :
    TendstoUniformlyOn
      (fun S : Finset (ZeroMultiplicityIndex (entireReducedDenominator N)) =>
        fun w => Matrix.det (1 - w • diagonalCompression (reducedZeroEigenvalue N) S))
      (entireReducedDenominator N) atTop K := by
  have h := (entireReducedDenominator_hadamard_uniform hN hK).tendstoUniformlyOn
  simpa only [diagonalCompression_determinant (reducedZeroEigenvalue_norm_summable hN),
    reducedZeroEigenvalue, div_eq_mul_inv, Finset.prod_fn] using h

end
end Komorebi.PaperIV
