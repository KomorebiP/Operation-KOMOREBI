/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.HypergeometricCompletion
import KomorebiPaperIV.EntireBridge
import Mathlib.Analysis.SpecialFunctions.RegularizedHypergeometric

namespace Komorebi.PaperIV
noncomputable section
open Finset

/-- Exactly the manuscript's denominator parameters, with the parameter 1 omitted. -/
def residueHypergeometricParameters (N j : ℕ) : Multiset ℂ :=
  ((range N).erase (N-j-1)).val.map (fun a => ((j+a+1 : ℕ) : ℂ)/(N : ℂ))

theorem residueHypergeometricParameters_card {N j : ℕ} (hj : j < N) :
    (residueHypergeometricParameters N j).card = N-1 := by
  rw [residueHypergeometricParameters, Multiset.card_map]
  change ((range N).erase (N-j-1)).card = N-1
  rw [Finset.card_erase_of_mem (show N-j-1 ∈ range N by simp; omega), card_range]

theorem residueHypergeometricParameters_re_pos {N j : ℕ} (hN : 0 < N)
    {c : ℂ} (hc : c ∈ residueHypergeometricParameters N j) : 0 < c.re := by
  obtain ⟨a, _, rfl⟩ := Multiset.mem_map.mp hc
  have hNr : (0 : ℝ) < N := by exact_mod_cast hN
  simpa using div_pos (show (0 : ℝ) < (j+a+1 : ℕ) by positivity) hNr

private theorem pochhammer_ratCast (q : ℕ) (x : ℚ) :
    (((ascPochhammer ℚ q).eval x : ℚ) : ℂ) = (ascPochhammer ℂ q).eval (x : ℂ) := by
  simpa using (Polynomial.eval_map_apply (f := Rat.castHom ℂ)
    (p := ascPochhammer ℚ q) x).symm

private theorem residuePochhammerProduct_erase {N j : ℕ} (hN : 0 < N) (hj : j < N) (q : ℕ) :
    (residuePochhammerProduct N j q : ℂ) = (q.factorial : ℂ) *
      ((residueHypergeometricParameters N j).map (ascPochhammer ℂ q).eval).prod := by
  have ho := congrArg (fun x : ℚ => (x : ℂ))
    (omitted_residuePochhammer_eq_factorial hN hj q)
  simp only [pochhammer_ratCast, Rat.cast_div, Rat.cast_natCast] at ho
  have he := Finset.mul_prod_erase (range N)
    (fun a => (ascPochhammer ℂ q).eval (((j+a+1 : ℕ) : ℂ)/(N : ℂ)))
    (show N-j-1 ∈ range N by simp; omega)
  rw [ho] at he
  rw [residuePochhammerProduct, Rat.cast_prod]
  simp only [pochhammer_ratCast, Rat.cast_div, Rat.cast_natCast]
  simpa only [residueHypergeometricParameters, Multiset.map_map,
    Finset.prod_eq_multiset_prod, Function.comp_apply] using he.symm

/-- Gamma normalization converts Mathlib's regularized coefficients to ordinary coefficients. -/
theorem regularized_zeroF_normalization (b : Multiset ℂ)
    (hb : ∀ c ∈ b, ∀ k : ℕ, c ≠ -(k : ℂ)) (q : ℕ) :
    (b.map Complex.Gamma).prod * Complex.regularizedHGFunCoeff 0 b q =
      ((q.factorial : ℂ) * (b.map (ascPochhammer ℂ q).eval).prod)⁻¹ := by
  have hn : (b.map Complex.Gamma).prod ≠ 0 := by
    apply Multiset.prod_ne_zero
    intro hc
    obtain ⟨a, ha, he⟩ := Multiset.mem_map.mp hc
    exact Complex.Gamma_ne_zero (hb a ha) he
  have hp : (b.map (ascPochhammer ℂ q).eval).prod =
      (b.map (fun c => Complex.Gamma (c+q))).prod / (b.map Complex.Gamma).prod := by
    rw [← Multiset.prod_map_div]
    congr 1
    apply Multiset.map_congr rfl
    intro c hc
    exact (Complex.Gamma_add_nat_div_Gamma_eq c (hb c hc)).symm
  rw [Complex.regularizedHGFunCoeff, hp]
  simp only [Multiset.map_zero, Multiset.prod_zero, one_div]
  field_simp

/-- Ordinary `₀F_{N-1}` with the paper's literal parameter multiset. -/
def residueHypergeometric (N j : ℕ) (w : ℂ) : ℂ :=
  ((residueHypergeometricParameters N j).map Complex.Gamma).prod *
    Complex.regularizedHGFun 0 (residueHypergeometricParameters N j) w

theorem residueHypergeometric_hasSum {N j : ℕ} (hN : 0 < N) (hj : j < N) (w : ℂ) :
    HasSum (fun q => (residueZeroFCoeff N j q : ℂ) * w^q)
      (residueHypergeometric N j w) := by
  let b := residueHypergeometricParameters N j
  have hb : ∀ c ∈ b, ∀ k : ℕ, c ≠ -(k : ℂ) := by
    intro c hc k he
    have hp := residueHypergeometricParameters_re_pos hN hc
    rw [he] at hp
    simp only [Complex.neg_re, Complex.natCast_re] at hp
    have hk : (0 : ℝ) ≤ k := Nat.cast_nonneg k
    linarith
  have hs := (Complex.regularizedHGFunSeries 0 b).hasSum (x := w) (by
    rw [Complex.radius_regularizedHGFunSeries_eq_top (by simp)]
    simp)
  have h := hs.mul_left (b.map Complex.Gamma).prod
  change HasSum _ (residueHypergeometric N j w) at h
  apply h.congr_fun
  intro q
  simp only [Complex.regularizedHGFunSeries, FormalMultilinearSeries.ofScalars_apply_eq,
    smul_eq_mul, ← mul_assoc, regularized_zeroF_normalization b hb]
  rw [← residuePochhammerProduct_erase hN hj]
  simp [residueZeroFCoeff]

/-- The pointwise hypergeometric formula, with ordinary normalization and exactly N-1 parameters. -/
theorem entireTransfer_hypergeometric {N j : ℕ} (hN : 0 < N) (hj : j < N)
    {omega : ℂ} (ho : IsPrimitiveRoot omega N) (lambda z : ℂ) :
    entireTransfer N j omega lambda z =
      (lambda*z)^j / (j.factorial : ℂ) *
        residueHypergeometric N j ((lambda*z)^N / (N : ℂ)^N) := by
  let f := fun m => PowerSeries.coeff m (transferSection N j lambda) * z^m
  have hi : Function.Injective (fun q : ℕ => N*q+j) := by
    intro a b h
    exact Nat.eq_of_mul_eq_mul_left hN (Nat.add_right_cancel h)
  have hf : ∀ m, m ∉ Set.range (fun q : ℕ => N*q+j) → f m = 0 := by
    intro m hm
    have he : m%N ≠ j := by
      intro he
      apply hm
      use m/N
      change N*(m/N)+j=m
      rw [← he, Nat.add_comm, Nat.mod_add_div]
    simp [f, coeff_transferSection, transferSectionCoeff, he]
  have ha := (hi.hasSum_iff hf).2 (hasSum_entireTransfer hN hj ho lambda z)
  have hh := (residueHypergeometric_hasSum hN hj ((lambda*z)^N / (N : ℂ)^N)).mul_left
    ((lambda*z)^j / (j.factorial : ℂ))
  apply ha.unique
  apply hh.congr_fun
  intro q
  dsimp [Function.comp_def, f]
  rw [coeff_transferSection, transferSectionCoeff,
    show (N*q+j)%N = j by simp [Nat.add_mod, Nat.mod_eq_of_lt hj]]
  simp only [one_div, map_inv₀, map_natCast]
  have hn := congrArg (fun a : ℚ => (a : ℂ)) (residueZeroFCoeff_normalization hN j q)
  push_cast at hn
  rw [← hn]
  simp only [div_eq_mul_inv, mul_pow, inv_pow, ← pow_mul]
  rw [pow_add, pow_add]
  simp only [ite_true]
  ring

end
end Komorebi.PaperIV
