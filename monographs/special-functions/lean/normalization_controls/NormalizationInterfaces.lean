import CoupledNormalization
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example (p : RationalScales) (n : ℕ) :
    p.derivatives n =
      (oddFactorial n * (p.coefficients n).1, oddFactorial n * (p.coefficients n).2) :=
  rational_derivatives_factorial p n

example (p : RationalScales) (i : Fin 2) (N : ℕ) (x : ℚ) :
    p.arrayPolynomial i N x = p.polynomial i N x := array_polynomial_eq p i N x

example (p : RationalScales) (i : Fin 2) (N : ℕ) :
    (p.ordinaryArray i N).length = N+1 := ordinary_array_length p i N

example (p : RationalScales) : p.derivativeArray 0 = [(1,1)] := rfl

example : (⟨-1,2,1,-2⟩ : RationalScales).derivatives 1 = (-4,-4) := by
  rw [rational_derivatives_one]
  norm_num

example : (⟨1,1,1,1⟩ : RationalScales).derivativeComponent 0 1 / oddFactorial 1 = 1/3 := by
  have h := (derivative_normalization_first (⟨1,1,1,1⟩ : RationalScales)).1
  norm_num at h ⊢
  exact h

example (p : RationalScales) (hs : p.toReal.positive)
    (hc : p.toReal.q < 1 ∧ p.toReal.r < 1 ∧ p.toReal.a < 1 ∧ p.toReal.b < 1)
    (x S : ℚ) (hx : 0 ≤ x) (hxS : x < S) (fuel : ℕ) (ht : p.maxScale^fuel*S < 1)
    (N : ℕ) (i : Fin 2) :
    (p.arrayPolynomial i N x : ℝ) ≤ p.toReal.realComponent i (x : ℝ) ∧
      p.toReal.realComponent i (x : ℝ) ≤
        ((p.arrayPolynomial i N x + rationalDiskMajorant p.maxScale fuel S *
          (x/S)^(2*N+3) : ℚ) : ℝ) :=
  array_endpoint_enclosure p hs hc x S hx hxS fuel ht N i
