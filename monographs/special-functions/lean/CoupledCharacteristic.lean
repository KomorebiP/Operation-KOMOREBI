import CoupledRescaling
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics
import Mathlib.Topology.Order.IntermediateValue
import Mathlib.LinearAlgebra.Matrix.Charpoly.Eigs
import Mathlib.Analysis.Normed.Algebra.Spectrum
import Mathlib.Analysis.Complex.Polynomial.Basic

/-! # The positive characteristic exponent of the coupled scales

All powers in the determinant balance are real powers. This file separates
the matrix/exponent prerequisites from the later analytic growth theorem.
-/

set_option autoImplicit false
set_option maxHeartbeats 1500000

noncomputable section

open Filter Set
open scoped Topology Matrix ENNReal NNReal

namespace Komorebi.SpecialFunctions.Coupled.Scales

def characteristicBalance (s : Scales) (t : ℝ) : ℝ :=
  (1 - s.q ^ t) * (1 - s.b ^ t) - (s.a * s.r) ^ t

theorem characteristicBalance_zero (s : Scales) : s.characteristicBalance 0 = -1 := by
  simp [characteristicBalance]

theorem rpow_contraction_bounds {x t : ℝ} (hx : 0 < x) (hx1 : x < 1) (ht : 0 < t) :
    0 < x ^ t ∧ x ^ t < 1 := by
  exact ⟨Real.rpow_pos_of_pos hx t, by
    simpa using Real.rpow_lt_rpow_of_exponent_gt hx hx1 ht⟩

theorem characteristicBalance_continuous (s : Scales) (hs : s.positive) :
    Continuous s.characteristicBalance := by
  exact ((continuous_const.sub (Real.continuous_const_rpow (ne_of_gt hs.1))).mul
    (continuous_const.sub (Real.continuous_const_rpow (ne_of_gt hs.2.2.2)))).sub
      (Real.continuous_const_rpow (ne_of_gt (mul_pos hs.2.2.1 hs.2.1)))

theorem characteristicBalance_strictMono (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    StrictMonoOn s.characteristicBalance (Ici 0) := by
  intro x hx y _ hxy
  have hq := Real.rpow_lt_rpow_of_exponent_gt hs.1 hstrict.1 hxy
  have hb := Real.rpow_lt_rpow_of_exponent_gt hs.2.2.2 hstrict.2.2.2 hxy
  have hq0 : 0 ≤ 1 - s.q ^ x := by
    have h := Real.rpow_le_rpow_of_exponent_ge hs.1 hstrict.1.le hx
    simpa using sub_nonneg.mpr h
  have hb0 : 0 ≤ 1 - s.b ^ x := by
    have h := Real.rpow_le_rpow_of_exponent_ge hs.2.2.2 hstrict.2.2.2.le hx
    simpa using sub_nonneg.mpr h
  have hprod : (1 - s.q ^ x) * (1 - s.b ^ x) ≤
      (1 - s.q ^ y) * (1 - s.b ^ y) :=
    mul_le_mul (by linarith only [hq]) (by linarith only [hb]) hb0 (by linarith only [hq0, hq])
  have har0 : 0 < s.a * s.r := mul_pos hs.2.2.1 hs.2.1
  have har1 : s.a * s.r < 1 :=
    lt_trans (mul_lt_mul_of_pos_right hstrict.2.2.1 hs.2.1) (by simpa using hstrict.2.1)
  have har := Real.rpow_lt_rpow_of_exponent_gt har0 har1 hxy
  dsimp [characteristicBalance]
  linarith only [hprod, har]

theorem characteristicBalance_tendsto (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    Tendsto s.characteristicBalance atTop (𝓝 1) := by
  have hq := tendsto_rpow_atTop_of_base_lt_one s.q (by linarith [hs.1]) hstrict.1
  have hb := tendsto_rpow_atTop_of_base_lt_one s.b (by linarith [hs.2.2.2]) hstrict.2.2.2
  have har0 : 0 < s.a * s.r := mul_pos hs.2.2.1 hs.2.1
  have har1 : s.a * s.r < 1 :=
    lt_trans (mul_lt_mul_of_pos_right hstrict.2.2.1 hs.2.1) (by simpa using hstrict.2.1)
  have har := tendsto_rpow_atTop_of_base_lt_one (s.a * s.r) (by linarith) har1
  have h1 : Tendsto (fun _ : ℝ => (1 : ℝ)) atTop (𝓝 1) := tendsto_const_nhds
  convert ((h1.sub hq).mul (h1.sub hb)).sub har using 1 <;> norm_num
  funext t
  rfl

theorem characteristic_exponent_exists_unique (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃! t : ℝ, 0 < t ∧ (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t := by
  have hev : ∀ᶠ t in atTop, 0 < s.characteristicBalance t :=
    (s.characteristicBalance_tendsto hs hstrict).eventually (Ioi_mem_nhds (by norm_num))
  obtain ⟨T, hT0, hT⟩ := (hev.and (eventually_gt_atTop (0 : ℝ))).exists
  have hC := s.characteristicBalance_continuous hs
  obtain ⟨t, ht, hroot⟩ := intermediate_value_Icc hT.le hC.continuousOn
    (show (0 : ℝ) ∈ Icc (s.characteristicBalance 0) (s.characteristicBalance T) by
      exact ⟨by rw [characteristicBalance_zero]; norm_num, hT0.le⟩)
  have htpos : 0 < t := by
    have htne : t ≠ 0 := by
      intro he
      rw [he, characteristicBalance_zero] at hroot
      norm_num at hroot
    exact lt_of_le_of_ne ht.1 htne.symm
  have heq : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t := sub_eq_zero.mp hroot
  refine ⟨t, ⟨htpos, heq⟩, ?_⟩
  intro u hu
  apply (s.characteristicBalance_strictMono hs hstrict).injOn hu.1.le htpos.le
  exact (sub_eq_zero.mpr hu.2).trans hroot.symm

def characteristicExponent (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) : ℝ :=
  Classical.choose (s.characteristic_exponent_exists_unique hs hstrict)

theorem characteristicExponent_spec (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    0 < s.characteristicExponent hs hstrict ∧
      (1 - s.q ^ (s.characteristicExponent hs hstrict)) *
        (1 - s.b ^ (s.characteristicExponent hs hstrict)) =
          (s.a * s.r) ^ (s.characteristicExponent hs hstrict) :=
  (Classical.choose_spec (s.characteristic_exponent_exists_unique hs hstrict)).1

def characteristicMatrix (s : Scales) (t : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  !![s.q ^ t, s.r ^ t; s.a ^ t, s.b ^ t]

def characteristicMatrixC (s : Scales) (t : ℝ) : Matrix (Fin 2) (Fin 2) ℂ :=
  (s.characteristicMatrix t).map (algebraMap ℝ ℂ)

def characteristicVector (s : Scales) (t : ℝ) : Fin 2 → ℝ := ![s.r ^ t, 1 - s.q ^ t]

def characteristicLeftVector (s : Scales) (t : ℝ) : Fin 2 → ℝ := ![s.a ^ t, 1 - s.q ^ t]

def characteristicNormalizer (s : Scales) (t : ℝ) : ℝ :=
  max (s.characteristicVector t 0) (s.characteristicVector t 1)

def normalizedCharacteristicVector (s : Scales) (t : ℝ) : Fin 2 → ℝ :=
  (s.characteristicNormalizer t)⁻¹ • s.characteristicVector t

theorem characteristicVector_positive (s : Scales) (hs : s.positive)
    (hq : s.q < 1) {t : ℝ} (ht : 0 < t) (i : Fin 2) :
    0 < s.characteristicVector t i := by
  fin_cases i
  · exact Real.rpow_pos_of_pos hs.2.1 t
  · exact sub_pos.mpr (rpow_contraction_bounds hs.1 hq ht).2

theorem characteristicLeftVector_positive (s : Scales) (hs : s.positive)
    (hq : s.q < 1) {t : ℝ} (ht : 0 < t) (i : Fin 2) :
    0 < s.characteristicLeftVector t i := by
  fin_cases i
  · exact Real.rpow_pos_of_pos hs.2.2.1 t
  · exact sub_pos.mpr (rpow_contraction_bounds hs.1 hq ht).2

theorem characteristic_right_eigenvector (s : Scales) (hs : s.positive) {t : ℝ}
    (he : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t) :
    s.characteristicMatrix t *ᵥ s.characteristicVector t = s.characteristicVector t := by
  rw [Real.mul_rpow hs.2.2.1.le hs.2.1.le] at he
  funext i
  fin_cases i <;>
    simp [characteristicMatrix, characteristicVector, Matrix.mulVec, dotProduct, Fin.sum_univ_two] <;>
    nlinarith only [he]

theorem characteristic_left_eigenvector (s : Scales) (hs : s.positive) {t : ℝ}
    (he : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t) :
    (s.characteristicMatrix t)ᵀ *ᵥ s.characteristicLeftVector t = s.characteristicLeftVector t := by
  rw [Real.mul_rpow hs.2.2.1.le hs.2.1.le] at he
  funext i
  fin_cases i <;>
    simp [characteristicMatrix, characteristicLeftVector, Matrix.mulVec, dotProduct, Fin.sum_univ_two] <;>
    nlinarith only [he]

theorem characteristicNormalizer_positive (s : Scales) (hs : s.positive)
    (hq : s.q < 1) {t : ℝ} (ht : 0 < t) : 0 < s.characteristicNormalizer t :=
  lt_of_lt_of_le (s.characteristicVector_positive hs hq ht 0) (le_max_left _ _)

theorem normalizedCharacteristicVector_positive (s : Scales) (hs : s.positive)
    (hq : s.q < 1) {t : ℝ} (ht : 0 < t) (i : Fin 2) :
    0 < s.normalizedCharacteristicVector t i :=
  mul_pos (inv_pos.mpr (s.characteristicNormalizer_positive hs hq ht))
    (s.characteristicVector_positive hs hq ht i)

theorem normalizedCharacteristicVector_max (s : Scales) (hs : s.positive)
    (hq : s.q < 1) {t : ℝ} (ht : 0 < t) :
    max (s.normalizedCharacteristicVector t 0) (s.normalizedCharacteristicVector t 1) = 1 := by
  have hd := s.characteristicNormalizer_positive hs hq ht
  change max ((s.characteristicNormalizer t)⁻¹ * _) ((s.characteristicNormalizer t)⁻¹ * _) = 1
  rw [← mul_max_of_nonneg _ _ (inv_pos.mpr hd).le]
  exact inv_mul_cancel₀ (ne_of_gt hd)

theorem normalized_characteristic_eigenvector (s : Scales) (hs : s.positive) {t : ℝ}
    (he : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t) :
    s.characteristicMatrix t *ᵥ s.normalizedCharacteristicVector t =
      s.normalizedCharacteristicVector t := by
  rw [normalizedCharacteristicVector, Matrix.mulVec_smul, s.characteristic_right_eigenvector hs he]

theorem characteristic_second_eigenvalue_bound (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {t : ℝ} (ht : 0 < t) :
    |s.q ^ t + s.b ^ t - 1| < 1 := by
  have hq := rpow_contraction_bounds hs.1 hstrict.1 ht
  have hb := rpow_contraction_bounds hs.2.2.2 hstrict.2.2.2 ht
  rw [abs_lt]
  constructor <;> linarith

theorem characteristic_spectrum (s : Scales) (hs : s.positive) {t : ℝ}
    (he : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t) :
    spectrum ℂ (s.characteristicMatrixC t) =
      {1, ((s.q ^ t + s.b ^ t - 1 : ℝ) : ℂ)} := by
  rw [Real.mul_rpow hs.2.2.1.le hs.2.1.le] at he
  have hc : (1 - ((s.q ^ t : ℝ) : ℂ)) * (1 - ((s.b ^ t : ℝ) : ℂ)) =
      ((s.a ^ t : ℝ) : ℂ) * ((s.r ^ t : ℝ) : ℂ) := by exact_mod_cast he
  ext z
  rw [Matrix.mem_spectrum_iff_isRoot_charpoly, Polynomial.IsRoot, Matrix.eval_charpoly]
  have hd : (Matrix.scalar (Fin 2) z - s.characteristicMatrixC t).det =
      (z - 1) * (z - ((s.q ^ t + s.b ^ t - 1 : ℝ) : ℂ)) := by
    norm_num [Matrix.det_fin_two, characteristicMatrixC, characteristicMatrix, Matrix.scalar]
    linear_combination hc
  rw [hd, mul_eq_zero]
  simp only [sub_eq_zero, Set.mem_insert_iff, Set.mem_singleton_iff]

theorem characteristic_spectralRadius (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {t : ℝ} (ht : 0 < t)
    (he : (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t) :
    spectralRadius ℂ (s.characteristicMatrixC t) = 1 := by
  have hbound := s.characteristic_second_eigenvalue_bound hs hstrict ht
  have hn : (‖((s.q ^ t + s.b ^ t - 1 : ℝ) : ℂ)‖₊ : ℝ≥0∞) ≤ 1 := by
    exact_mod_cast (le_of_lt (show ‖((s.q ^ t + s.b ^ t - 1 : ℝ) : ℂ)‖ < 1 by
      simpa only [Complex.norm_real, Real.norm_eq_abs] using hbound))
  rw [spectralRadius_eq_of_unital]
  apply le_antisymm
  · refine iSup₂_le fun z hz => ?_
    rw [s.characteristic_spectrum hs he, Set.mem_insert_iff, Set.mem_singleton_iff] at hz
    rcases hz with rfl | rfl
    · simp
    · exact hn
  · have hm : (1 : ℂ) ∈ spectrum ℂ (s.characteristicMatrixC t) := by
      rw [s.characteristic_spectrum hs he]
      simp
    exact le_iSup₂_of_le (1 : ℂ) hm (by simp)

theorem characteristic_mem_spectrum_iff (s : Scales) (t : ℝ) (z : ℂ) :
    z ∈ spectrum ℂ (s.characteristicMatrixC t) ↔
      (z - ((s.q ^ t : ℝ) : ℂ)) * (z - ((s.b ^ t : ℝ) : ℂ)) -
        ((s.r ^ t : ℝ) : ℂ) * ((s.a ^ t : ℝ) : ℂ) = 0 := by
  rw [Matrix.mem_spectrum_iff_isRoot_charpoly, Polynomial.IsRoot, Matrix.eval_charpoly]
  norm_num [Matrix.det_fin_two, characteristicMatrixC, characteristicMatrix, Matrix.scalar]

theorem characteristic_spectrum_real (s : Scales) (hs : s.positive) (t : ℝ)
    {z : ℂ} (hz : z ∈ spectrum ℂ (s.characteristicMatrixC t)) : z.im = 0 := by
  have he := (s.characteristic_mem_spectrum_iff t z).mp hz
  have hre := congrArg Complex.re he
  have him := congrArg Complex.im he
  norm_num [Complex.mul_re, Complex.mul_im] at hre him
  by_contra hne
  have hp : z.im * (2 * z.re - s.q ^ t - s.b ^ t) = 0 := by
    nlinarith only [him]
  have hx : z.re = (s.q ^ t + s.b ^ t) / 2 := by
    have h := (mul_eq_zero.mp hp).resolve_left hne
    linarith only [h]
  rw [hx] at hre
  have hprod : 0 < s.r ^ t * s.a ^ t :=
    mul_pos (Real.rpow_pos_of_pos hs.2.1 t) (Real.rpow_pos_of_pos hs.2.2.1 t)
  nlinarith [sq_nonneg (s.q ^ t - s.b ^ t), sq_nonneg z.im]

theorem characteristic_spectrum_norm_attained (s : Scales) (t : ℝ) :
    ∃ z ∈ spectrum ℂ (s.characteristicMatrixC t),
      (‖z‖₊ : ℝ≥0∞) = spectralRadius ℂ (s.characteristicMatrixC t) := by
  have hf : (spectrum ℂ (s.characteristicMatrixC t)).Finite := by
    apply (Polynomial.finite_setOfPred_isRoot (s.characteristicMatrixC t).charpoly_monic.ne_zero).subset
    intro z hz
    exact Matrix.mem_spectrum_iff_isRoot_charpoly.mp hz
  have hn := spectrum.nonempty_of_isAlgClosed_of_finiteDimensional ℂ (s.characteristicMatrixC t)
  obtain ⟨z, hz, hmax⟩ := hf.isCompact.exists_isMaxOn hn continuous_nnnorm.continuousOn
  refine ⟨z, hz, ?_⟩
  rw [spectralRadius_eq_of_unital]
  apply le_antisymm
  · exact le_iSup₂_of_le z hz le_rfl
  · refine iSup₂_le fun w hw => ?_
    exact_mod_cast hmax hw

theorem characteristic_spectralRadius_iff (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) {t : ℝ} (ht : 0 < t) :
    spectralRadius ℂ (s.characteristicMatrixC t) = 1 ↔
      (1 - s.q ^ t) * (1 - s.b ^ t) = (s.a * s.r) ^ t := by
  constructor
  · intro hrad
    obtain ⟨z, hz, hn⟩ := s.characteristic_spectrum_norm_attained t
    have hnNN : ‖z‖₊ = 1 := by exact_mod_cast hn.trans hrad
    have hn1 : ‖z‖ = 1 := by
      simpa only [NNReal.coe_one, coe_nnnorm] using congrArg (fun r : ℝ≥0 => (r : ℝ)) hnNN
    have him := s.characteristic_spectrum_real hs t hz
    have hzreal : z = (z.re : ℂ) := Complex.ext (by simp) (by simpa using him)
    have habs : |z.re| = |(1 : ℝ)| := by
      rw [hzreal, Complex.norm_real, Real.norm_eq_abs] at hn1
      simpa only [abs_one] using hn1
    have he := (s.characteristic_mem_spectrum_iff t z).mp hz
    rcases abs_eq_abs.mp habs with hre | hre
    · have hz1 : z = 1 := by rw [hzreal, hre]; norm_num
      rw [hz1] at he
      have hr : (1 - s.q ^ t) * (1 - s.b ^ t) = s.r ^ t * s.a ^ t := by
        exact_mod_cast (sub_eq_zero.mp he)
      rw [Real.mul_rpow hs.2.2.1.le hs.2.1.le]
      nlinarith only [hr]
    · have hz1 : z = -1 := by rw [hzreal, hre]; norm_num
      rw [hz1] at he
      have hr : (-1 - s.q ^ t) * (-1 - s.b ^ t) - s.r ^ t * s.a ^ t = 0 := by
        exact_mod_cast he
      have hq := rpow_contraction_bounds hs.1 hstrict.1 ht
      have hb := rpow_contraction_bounds hs.2.2.2 hstrict.2.2.2 ht
      have ha := rpow_contraction_bounds hs.2.2.1 hstrict.2.2.1 ht
      have hR := rpow_contraction_bounds hs.2.1 hstrict.2.1 ht
      have hprod : s.r ^ t * s.a ^ t < 1 :=
        lt_trans (mul_lt_mul_of_pos_right hR.2 ha.1) (by simpa using ha.2)
      nlinarith [mul_pos hq.1 hb.1]
  · exact s.characteristic_spectralRadius hs hstrict ht

theorem characteristic_spectral_exponent_exists_unique (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃! t : ℝ, 0 < t ∧ spectralRadius ℂ (s.characteristicMatrixC t) = 1 := by
  obtain ⟨t, ht, hu⟩ := s.characteristic_exponent_exists_unique hs hstrict
  refine ⟨t, ⟨ht.1, (s.characteristic_spectralRadius_iff hs hstrict ht.1).mpr ht.2⟩, ?_⟩
  intro u hU
  exact hu u ⟨hU.1, (s.characteristic_spectralRadius_iff hs hstrict hU.1).mp hU.2⟩

end Komorebi.SpecialFunctions.Coupled.Scales
