/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.FiniteModels
import KomorebiPaperIV.EntireBridge
import Mathlib.Analysis.Normed.Module.FiniteDimension

namespace Komorebi.PaperIV
noncomputable section

/-- The ordinary exponential power series in a finite-dimensional algebra. -/
def finiteAlgebraExponential {A : Type*} [Ring A] [Algebra ℂ A]
    [TopologicalSpace A] (x : A) (z : ℂ) : A :=
  ∑' m : ℕ, (z^m / (m.factorial : ℂ)) • x^m

section General
variable {A : Type*} [CommRing A] [Algebra ℂ A]
  [TopologicalSpace A] [ContinuousAdd A] [ContinuousSMul ℂ A]

/-- Pointwise convergence and section coordinates when `x^N = 1`. -/
theorem hasSum_cyclicAlgebra_exponential {N : ℕ} (hN : 0 < N)
    {omega : ℂ} (ho : IsPrimitiveRoot omega N) (x : A) (hx : x^N = 1)
    (lambda z : ℂ) :
    HasSum (fun m : ℕ => ((lambda*z)^m / (m.factorial : ℂ)) • x^m)
      (∑ j : Fin N, entireTransfer N j.val omega lambda z • x^j.val) := by
  have h := hasSum_sum (s := Finset.univ) (fun j (_ : j ∈ (Finset.univ : Finset (Fin N))) =>
    (hasSum_entireTransfer hN j.isLt ho lambda z).smul_const (x^j.val))
  apply h.congr_fun
  intro m
  have hxmod : x^m = x^(m%N) := by
    calc
      x^m = x^(m%N + N*(m/N)) := by rw [Nat.mod_add_div]
      _ = x^(m%N) := by rw [pow_add, pow_mul, hx]; simp
  rw [hxmod, Finset.sum_eq_single (⟨m%N, Nat.mod_lt m hN⟩ : Fin N)]
  · simp only [coeff_transferSection, transferSectionCoeff, ite_true]
    congr 1
    simp [mul_pow, div_eq_mul_inv, mul_assoc, mul_left_comm, mul_comm]
  · intro j _ hj
    have hne : m%N ≠ j.val := by intro he; apply hj; exact Fin.ext he.symm
    simp [coeff_transferSection, transferSectionCoeff, hne]
  · simp

/-- Pointwise convergence and section coordinates when `x^N = -1`. -/
theorem hasSum_signedAlgebra_exponential {N : ℕ} (hN : 0 < N)
    {omega rho : ℂ} (ho : IsPrimitiveRoot omega N) (hr : rho^N = -1)
    (x : A) (hx : x^N = -1) (z : ℂ) :
    HasSum (fun m : ℕ => (z^m / (m.factorial : ℂ)) • x^m)
      (∑ j : Fin N, entireSigned N j.val omega rho z • x^j.val) := by
  have h := hasSum_sum (s := Finset.univ) (fun j (_ : j ∈ (Finset.univ : Finset (Fin N))) =>
    (hasSum_entireSigned hN j.isLt ho hr z).smul_const (x^j.val))
  apply h.congr_fun
  intro m
  have hxmod : x^m = (-1 : A)^(m/N) * x^(m%N) := by
    calc
      x^m = x^(m%N + N*(m/N)) := by rw [Nat.mod_add_div]
      _ = _ := by rw [pow_add, pow_mul, hx]; ring
  rw [hxmod, Finset.sum_eq_single (⟨m%N, Nat.mod_lt m hN⟩ : Fin N)]
  · simp only [coeff_signedSection, signedSectionCoeff, ite_true]
    simp only [Algebra.smul_def, div_eq_mul_inv, map_mul, map_pow, map_neg, map_one, map_inv₀, map_natCast]
    ring
  · intro j _ hj
    have hne : m%N ≠ j.val := by intro he; apply hj; exact Fin.ext he.symm
    simp [coeff_signedSection, signedSectionCoeff, hne]
  · simp

end General

/-- The coefficient sup norm supplies the canonical finite-dimensional quotient topology. -/
instance cyclicAlgebraNormedAddCommGroup (N : ℕ) [NeZero N] :
    NormedAddCommGroup (CyclicAlgebra ℂ N) :=
  NormedAddCommGroup.induced _ _
    (cyclicAlgebraPowerBasis ℂ N (Nat.pos_of_ne_zero (NeZero.ne N))).basis.equivFun
    (cyclicAlgebraPowerBasis ℂ N (Nat.pos_of_ne_zero (NeZero.ne N))).basis.equivFun.injective

instance cyclicAlgebraNormedSpace (N : ℕ) [NeZero N] : NormedSpace ℂ (CyclicAlgebra ℂ N) :=
  NormedSpace.induced ℂ _ _
    (cyclicAlgebraPowerBasis ℂ N (Nat.pos_of_ne_zero (NeZero.ne N))).basis.equivFun

instance signedAlgebraNormedAddCommGroup (N : ℕ) [NeZero N] :
    NormedAddCommGroup (SignedCyclicAlgebra ℂ N) :=
  NormedAddCommGroup.induced _ _
    (signedCyclicAlgebraPowerBasis ℂ N (Nat.pos_of_ne_zero (NeZero.ne N))).basis.equivFun
    (signedCyclicAlgebraPowerBasis ℂ N (Nat.pos_of_ne_zero (NeZero.ne N))).basis.equivFun.injective

instance signedAlgebraNormedSpace (N : ℕ) [NeZero N] : NormedSpace ℂ (SignedCyclicAlgebra ℂ N) :=
  NormedSpace.induced ℂ _ _
    (signedCyclicAlgebraPowerBasis ℂ N (Nat.pos_of_ne_zero (NeZero.ne N))).basis.equivFun

/-- Theorem 6.2 in the actual cyclic quotient algebra, at every complex argument. -/
theorem cyclicAlgebra_pointwise_exponential {N : ℕ} [NeZero N]
    {omega : ℂ} (ho : IsPrimitiveRoot omega N) (lambda z : ℂ) :
    finiteAlgebraExponential (cyclicGenerator ℂ N) (lambda*z) =
      ∑ j : Fin N, entireTransfer N j.val omega lambda z • (cyclicGenerator ℂ N)^j.val := by
  exact (hasSum_cyclicAlgebra_exponential (Nat.pos_of_ne_zero (NeZero.ne N)) ho
    (cyclicGenerator ℂ N) (cyclicGenerator_pow ℂ N) lambda z).tsum_eq

/-- Theorem 6.2 in the actual signed quotient algebra, at every complex argument. -/
theorem signedAlgebra_pointwise_exponential {N : ℕ} [NeZero N]
    {omega rho : ℂ} (ho : IsPrimitiveRoot omega N) (hr : rho^N = -1) (z : ℂ) :
    finiteAlgebraExponential (signedCyclicGenerator ℂ N) z =
      ∑ j : Fin N, entireSigned N j.val omega rho z • (signedCyclicGenerator ℂ N)^j.val := by
  exact (hasSum_signedAlgebra_exponential (Nat.pos_of_ne_zero (NeZero.ne N)) ho hr
    (signedCyclicGenerator ℂ N) (signedCyclicGenerator_pow ℂ N) z).tsum_eq

end
end Komorebi.PaperIV
