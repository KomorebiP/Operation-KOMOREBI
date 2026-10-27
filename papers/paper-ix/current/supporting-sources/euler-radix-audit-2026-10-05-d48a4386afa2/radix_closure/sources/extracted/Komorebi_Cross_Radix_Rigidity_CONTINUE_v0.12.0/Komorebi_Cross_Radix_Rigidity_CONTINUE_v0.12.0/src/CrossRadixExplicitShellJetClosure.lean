import CrossRadixInvariantShellJetHull
import Mathlib.NumberTheory.LegendreSymbol.AddCharacter
import Mathlib.Algebra.Polynomial.Taylor

noncomputable section
open Polynomial
open scoped BigOperators

namespace KomorebiCrossRadix

local instance propDecidableExplicitShellJet (p : Prop) : Decidable p := Classical.propDecidable p

variable {T : ℕ} [NeZero T]

/-- Scalar orthogonality kernel for a general affine pullback on `ZMod T`. -/
lemma affineDFTKernel (m r ξ η : ZMod T) :
    (∑ k : ZMod T,
      ZMod.stdAddChar (-(k * η)) * ZMod.stdAddChar ((m * k + r) * ξ)) =
      if m * ξ = η then (T : ℂ) * ZMod.stdAddChar (r * ξ) else 0 := by
  have hterm (k : ZMod T) :
      ZMod.stdAddChar (-(k * η)) * ZMod.stdAddChar ((m * k + r) * ξ) =
        ZMod.stdAddChar (r * ξ) * ZMod.stdAddChar (k * (m * ξ - η)) := by
    rw [← AddChar.map_add_eq_mul, ← AddChar.map_add_eq_mul]
    congr 1
    ring
  simp_rw [hterm]
  rw [← Finset.mul_sum]
  rw [AddChar.sum_mulShift (m * ξ - η) (ZMod.isPrimitive_stdAddChar T)]
  simp only [ZMod.card]
  by_cases h : m * ξ = η
  · simp [h]
    ring
  · have hz : m * ξ - η ≠ 0 := sub_ne_zero.mpr h
    simp [h, hz]

/-- Fourier inversion in the exact normalization used by Mathlib's `ZMod.dft`. -/
lemma dftInverseFormula {E : Type*} [AddCommGroup E] [Module ℂ E]
    (Φ : ZMod T → E) (x : ZMod T) :
    Φ x = (T : ℂ)⁻¹ • ∑ ξ : ZMod T, ZMod.stdAddChar (ξ * x) • ZMod.dft Φ ξ := by
  calc
    Φ x = (ZMod.dft (N := T) (E := E)).symm (ZMod.dft Φ) x := by
      symm
      exact congrFun ((ZMod.dft (N := T) (E := E)).symm_apply_apply Φ) x
    _ = (T : ℂ)⁻¹ • ∑ ξ : ZMod T,
        ZMod.stdAddChar (ξ * x) • ZMod.dft Φ ξ := by
      exact ZMod.invDFT_apply (ZMod.dft Φ) x

/-- **Exact affine DFT transition law.**  Under pullback by `k ↦ m*k+r`, output frequency
`η` receives exactly the input frequencies `ξ` satisfying `m*ξ=η`; translation contributes
only the standard nonzero phase.  This is valid for nonunit `m`, so aliases are summed. -/
lemma dftAffinePrecomp {E : Type*} [AddCommGroup E] [Module ℂ E]
    (Φ : ZMod T → E) (m r η : ZMod T) :
    ZMod.dft (fun k : ZMod T => Φ (m * k + r)) η =
      ∑ ξ : ZMod T, if m * ξ = η then
        ZMod.stdAddChar (r * ξ) • ZMod.dft Φ ξ else 0 := by
  rw [ZMod.dft_apply]
  simp_rw [dftInverseFormula Φ]
  simp_rw [Finset.smul_sum, smul_smul]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro ξ _
  rw [← Finset.sum_smul]
  by_cases h : m * ξ = η
  · simp only [h, ite_true]
    congr 1
    calc
      (∑ x : ZMod T,
          ZMod.stdAddChar (-(x * η)) *
            ((T : ℂ)⁻¹ * ZMod.stdAddChar (ξ * (m * x + r)))) =
          (T : ℂ)⁻¹ *
            (∑ x : ZMod T,
              ZMod.stdAddChar (-(x * η)) *
                ZMod.stdAddChar ((m * x + r) * ξ)) := by
            rw [Finset.mul_sum]
            apply Finset.sum_congr rfl
            intro x _
            rw [mul_comm ξ (m * x + r)]
            ring
      _ = (T : ℂ)⁻¹ * ((T : ℂ) * ZMod.stdAddChar (r * ξ)) := by
            rw [affineDFTKernel (T := T) m r ξ η]
            simp [h]
      _ = ZMod.stdAddChar (r * ξ) := by
            rw [← mul_assoc, inv_mul_cancel₀ (NeZero.ne (T : ℂ)), one_mul]
  · simp only [h, ite_false]
    rw [← zero_smul ℂ (ZMod.dft Φ ξ)]
    congr 1
    calc
      (∑ x : ZMod T,
          ZMod.stdAddChar (-(x * η)) *
            ((T : ℂ)⁻¹ * ZMod.stdAddChar (ξ * (m * x + r)))) =
          (T : ℂ)⁻¹ *
            (∑ x : ZMod T,
              ZMod.stdAddChar (-(x * η)) *
                ZMod.stdAddChar ((m * x + r) * ξ)) := by
            rw [Finset.mul_sum]
            apply Finset.sum_congr rfl
            intro x _
            rw [mul_comm ξ (m * x + r)]
            ring
      _ = 0 := by
            rw [affineDFTKernel (T := T) m r ξ η]
            simp [h]

/-- The exact Fourier-side polynomial at output frequency `η` after a positive affine profile section. -/
lemma dft_quasiPolynomialSectionProfile
    (d m r : ℕ) (hm : 0 < m) (P : DegreeBoundedProfile T d) (η : ZMod T) :
    ZMod.dft (quasiPolynomialSectionProfile T d m r hm P) η =
      boundedAffinePolynomialEquiv d (m : ℂ) (r : ℂ) (natCast_complex_ne_zero_of_pos hm)
        (∑ ξ : ZMod T, if (m : ZMod T) * ξ = η then
          ZMod.stdAddChar ((r : ZMod T) * ξ) • ZMod.dft P ξ else 0) := by
  let A := boundedAffinePolynomialEquiv d (m : ℂ) (r : ℂ)
    (natCast_complex_ne_zero_of_pos hm)
  calc
    ZMod.dft (quasiPolynomialSectionProfile T d m r hm P) η =
        ∑ k : ZMod T, ZMod.stdAddChar (-(k * η)) •
          A (P ((m : ZMod T) * k + (r : ZMod T))) := by
      rw [ZMod.dft_apply]
      rfl
    _ = A (ZMod.dft (fun k : ZMod T => P ((m : ZMod T) * k + (r : ZMod T))) η) := by
      rw [ZMod.dft_apply]
      rw [map_sum]
      apply Finset.sum_congr rfl
      intro k _
      rw [map_smul]
    _ = A (∑ ξ : ZMod T, if (m : ZMod T) * ξ = η then
          ZMod.stdAddChar ((r : ZMod T) * ξ) • ZMod.dft P ξ else 0) := by
      rw [dftAffinePrecomp]
    _ = boundedAffinePolynomialEquiv d (m : ℂ) (r : ℂ)
        (natCast_complex_ne_zero_of_pos hm)
        (∑ ξ : ZMod T, if (m : ZMod T) * ξ = η then
          ZMod.stdAddChar ((r : ZMod T) * ξ) • ZMod.dft P ξ else 0) := rfl

/-- Affine polynomial substitution has `q`th coefficient equal to the `q`th Hasse derivative
at the translation point, times the nonzero dilation factor `a^q`. -/
lemma boundedAffinePolynomialEquiv_coeff_hasse
    (d q : ℕ) (a b : ℂ) (ha : a ≠ 0) (p : DegreeBoundedPolynomial d) :
    (boundedAffinePolynomialEquiv d a b ha p).1.coeff q =
      (Polynomial.hasseDeriv q p.1).eval b * a ^ q := by
  rw [boundedAffinePolynomialEquiv_apply]
  have hinner : (C a * X + C b : Polynomial ℂ) = (X + C b).comp (C a * X) := by
    simp
  rw [hinner, ← Polynomial.comp_assoc]
  change ((Polynomial.taylor b p.1).comp (C a * X)).coeff q = _
  rw [Polynomial.comp_C_mul_X_coeff, Polynomial.taylor_coeff]

/-- If all input polynomial jets at order at least `q` vanish, then affine substitution cannot
create a `q`th jet. -/
lemma boundedAffinePolynomialEquiv_coeff_eq_zero_of_tail_zero
    (d q : ℕ) (a b : ℂ) (ha : a ≠ 0) (p : DegreeBoundedPolynomial d)
    (hzero : ∀ j : ℕ, q ≤ j → p.1.coeff j = 0) :
    (boundedAffinePolynomialEquiv d a b ha p).1.coeff q = 0 := by
  rw [boundedAffinePolynomialEquiv_coeff_hasse]
  have hd : Polynomial.hasseDeriv q p.1 = 0 := by
    ext n
    rw [Polynomial.hasseDeriv_coeff, Polynomial.coeff_zero]
    rw [hzero (n + q) (Nat.le_add_left q n)]
    simp
  rw [hd]
  simp

end KomorebiCrossRadix

#print axioms KomorebiCrossRadix.dftAffinePrecomp
#print axioms KomorebiCrossRadix.dft_quasiPolynomialSectionProfile
#print axioms KomorebiCrossRadix.boundedAffinePolynomialEquiv_coeff_hasse
#print axioms KomorebiCrossRadix.boundedAffinePolynomialEquiv_coeff_eq_zero_of_tail_zero
