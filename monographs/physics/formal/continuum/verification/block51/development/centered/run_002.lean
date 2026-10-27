import KomorebiPhysics.Relativistic3DGeneratorBridge
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Sinc

/-!
# Centered Fourier operators on the full coefficient space

The operators act on the same infinite Fourier space as the continuum Dirac
Hamiltonian. The value assigned at zero spacing is auxiliary zero, since the
continuously filled modal symbol at zero is unbounded on the full space.
All centered evaluations and convergence claims use nonzero spacing.
Copyright (c) 2026 Komorebi P. Released under the MIT license.
-/
noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000
open Filter
open scoped ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics.Relativistic3DCenteredConvergence
open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DFourierGenerator
open Relativistic3DFourierL2Generator
open Relativistic3DFourierHilbertStability
open Relativistic3DFullFourierEvolution
open Relativistic3DUnboundedDirac
open Relativistic3DWeightedDomain
open Relativistic3DGeneratorBridge

abbrev Mode := Relativistic3DFullFourierEvolution.Mode
abbrev CoeffL2 := Relativistic3DFullFourierEvolution.CoeffL2
abbrev HilbertSpinor := Relativistic3DFourierHilbertStability.HilbertSpinor

/-- The Hermitian Clifford symbol at arbitrary real spatial momentum. -/
def hilbertSymbol (m px py pz : ℝ) : HilbertSpinorEnd :=
  (px : ℂ) • alphaXHilbertOperator + (py : ℂ) • alphaYHilbertOperator +
    (pz : ℂ) • alphaZHilbertOperator + (m : ℂ) • betaHilbertOperator

theorem hilbertSymbol_symmetric (m px py pz : ℝ) :
    (hilbertSymbol m px py pz : HilbertSpinor →ₗ[ℂ] HilbertSpinor).IsSymmetric := by
  exact (((real_smul_hilbertClifford_symmetric _ hermitianX).add
    (real_smul_hilbertClifford_symmetric _ hermitianY)).add
    (real_smul_hilbertClifford_symmetric _ hermitianZ)).add
    (real_smul_hilbertClifford_symmetric _ hermitianBeta)

theorem hilbertSymbol_sq (m px py pz : ℝ) (ψ : HilbertSpinor) :
    hilbertSymbol m px py pz (hilbertSymbol m px py pz ψ) =
      (symbolEnergySq m px py pz : ℂ) • ψ := by
  change spinorToHilbert (continuumDiracSymbol m px py pz
    (continuumDiracSymbol m px py pz (hilbertToSpinor ψ))) = _
  rw [continuumDiracSymbol_sq]
  rfl

theorem norm_hilbertSymbol_sq (m px py pz : ℝ) (ψ : HilbertSpinor) :
    ‖hilbertSymbol m px py pz ψ‖ ^ 2 =
      (m ^ 2 + px ^ 2 + py ^ 2 + pz ^ 2) * ‖ψ‖ ^ 2 := by
  have hi : inner ℂ (hilbertSymbol m px py pz ψ) (hilbertSymbol m px py pz ψ) =
      (symbolEnergySq m px py pz : ℂ) * inner ℂ ψ ψ := by
    calc
      _ = inner ℂ ψ (hilbertSymbol m px py pz (hilbertSymbol m px py pz ψ)) :=
        hilbertSymbol_symmetric m px py pz ψ (hilbertSymbol m px py pz ψ)
      _ = _ := by rw [hilbertSymbol_sq, inner_smul_right]
  rw [norm_sq_eq_re_inner (𝕜 := ℂ), hi, inner_self_eq_norm_sq_to_K]
  simp [symbolEnergySq, Complex.mul_re, pow_two]

theorem centered_mode_eq_symbol (m h : ℝ) (n : Mode) :
    centralHilbertModeOperator m h n =
      hilbertSymbol m (sinQuot (modeMomentum n 0) h)
        (sinQuot (modeMomentum n 1) h) (sinQuot (modeMomentum n 2) h) := rfl

theorem centered_mode_sub_eq_symbol (m h : ℝ) (n : Mode) :
    centralHilbertModeOperator m h n - continuumHilbertModeOperator m n =
      hilbertSymbol 0 (sinQuot (modeMomentum n 0) h - modeMomentum n 0)
        (sinQuot (modeMomentum n 1) h - modeMomentum n 1)
        (sinQuot (modeMomentum n 2) h - modeMomentum n 2) := by
  simp only [centralHilbertModeOperator, continuumHilbertModeOperator,
    hilbertSymbol, Complex.ofReal_sub, Complex.ofReal_zero]
  module

theorem norm_centered_mode_sub_sq (m h : ℝ) (n : Mode) (ψ : HilbertSpinor) :
    ‖centralHilbertModeOperator m h n ψ - continuumHilbertModeOperator m n ψ‖ ^ 2 =
      ((sinQuot (modeMomentum n 0) h - modeMomentum n 0) ^ 2 +
       (sinQuot (modeMomentum n 1) h - modeMomentum n 1) ^ 2 +
       (sinQuot (modeMomentum n 2) h - modeMomentum n 2) ^ 2) * ‖ψ‖ ^ 2 := by
  change ‖(centralHilbertModeOperator m h n - continuumHilbertModeOperator m n) ψ‖ ^ 2 = _
  rw [centered_mode_sub_eq_symbol, norm_hilbertSymbol_sq]
  simp

theorem sinQuot_eq_mul_sinc (k h : ℝ) : sinQuot k h = k * Real.sinc (k*h) := by
  by_cases hh : h = 0
  · simp [hh, sinQuot, Relativistic1DContinuumLimit.sinQuot]
  by_cases hk : k = 0
  · simp [hk, sinQuot, Relativistic1DContinuumLimit.sinQuot]
  rw [Real.sinc_of_ne_zero (mul_ne_zero hk hh)]
  simp only [sinQuot, Relativistic1DContinuumLimit.sinQuot, hh, ite_false]
  field_simp

theorem abs_sinQuot_le (k h : ℝ) : |sinQuot k h| ≤ |k| := by
  rw [sinQuot_eq_mul_sinc, abs_mul]
  exact (mul_le_mul_of_nonneg_left (Real.abs_sinc_le_one _) (abs_nonneg k)).trans_eq
    (mul_one _)

@[fun_prop] theorem continuous_sinQuot (k : ℝ) : Continuous (fun h => sinQuot k h) := by
  simp_rw [sinQuot_eq_mul_sinc]
  exact continuous_const.mul (Real.continuous_sinc.comp (continuous_const.mul continuous_id))

theorem abs_sinQuot_le_inv (k h : ℝ) (hh : h ≠ 0) : |sinQuot k h| ≤ |h|⁻¹ := by
  simp only [sinQuot, Relativistic1DContinuumLimit.sinQuot, hh, ite_false, abs_div]
  simpa only [one_div] using div_le_div_of_nonneg_right (Real.abs_sin_le_one (k*h)) (abs_nonneg h)

/-- A uniformly bounded family of mode maps acts continuously on the same ℓ² space. -/
def boundedModewiseOperator (A : Mode → HilbertSpinorEnd) (C : ℝ) (hC : 0 ≤ C)
    (hA : ∀ n ψ, ‖A n ψ‖ ≤ C * ‖ψ‖) : CoeffL2 →L[ℂ] CoeffL2 :=
  let F : CoeffL2 →ₗ[ℂ] CoeffL2 :=
    { toFun := fun f => ⟨fun n => A n (f n), by
        let v : CoeffL2 := (C : ℂ) • f
        apply Memℓp.mono v.prop.norm
        intro n
        change ‖A n (f n)‖ ≤ ‖v n‖
        simpa only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul, Complex.norm_real,
          Real.norm_eq_abs, abs_of_nonneg hC] using hA n (f n)⟩
      map_add' := by
        intro f g
        apply lp.ext
        funext n
        exact (A n).map_add _ _
      map_smul' := by
        intro c f
        apply lp.ext
        funext n
        exact (A n).map_smul _ _ }
  F.mkContinuous C (by
    intro f
    let v : CoeffL2 := (C : ℂ) • f
    have hm : ‖F f‖ ≤ ‖v‖ := lp.norm_mono (by norm_num) (fun n => by
      change ‖A n (f n)‖ ≤ ‖v n‖
      simpa only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul, Complex.norm_real,
        Real.norm_eq_abs, abs_of_nonneg hC] using hA n (f n))
    simpa only [v, norm_smul, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hC] using hm)

@[simp] theorem boundedModewiseOperator_apply (A : Mode → HilbertSpinorEnd)
    (C : ℝ) (hC : 0 ≤ C) (hA : ∀ n ψ, ‖A n ψ‖ ≤ C * ‖ψ‖)
    (f : CoeffL2) (n : Mode) : boundedModewiseOperator A C hC hA f n = A n (f n) := rfl

theorem boundedModewiseOperator_norm_le (A : Mode → HilbertSpinorEnd)
    (C : ℝ) (hC : 0 ≤ C) (hA : ∀ n ψ, ‖A n ψ‖ ≤ C * ‖ψ‖) :
    ‖boundedModewiseOperator A C hC hA‖ ≤ C := by
  apply ContinuousLinearMap.opNorm_le_bound _ hC
  intro f
  let v : CoeffL2 := (C : ℂ) • f
  have hm : ‖boundedModewiseOperator A C hC hA f‖ ≤ ‖v‖ :=
    lp.norm_mono (by norm_num) (fun n => by
      change ‖A n (f n)‖ ≤ ‖v n‖
      simpa only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul, Complex.norm_real,
        Real.norm_eq_abs, abs_of_nonneg hC] using hA n (f n))
  simpa only [v, norm_smul, Complex.norm_real, Real.norm_eq_abs, abs_of_nonneg hC] using hm

theorem centered_mode_bound (m h : ℝ) (hh : h ≠ 0) (n : Mode) (ψ : HilbertSpinor) :
    ‖centralHilbertModeOperator m h n ψ‖ ≤ Real.sqrt (m^2 + 3 * h⁻¹^2) * ‖ψ‖ := by
  have hx := pow_le_pow_left₀ (abs_nonneg _) (abs_sinQuot_le_inv (modeMomentum n 0) h hh) 2
  have hy := pow_le_pow_left₀ (abs_nonneg _) (abs_sinQuot_le_inv (modeMomentum n 1) h hh) 2
  have hz := pow_le_pow_left₀ (abs_nonneg _) (abs_sinQuot_le_inv (modeMomentum n 2) h hh) 2
  simp only [sq_abs, ← abs_inv] at hx hy hz
  have hs : 0 ≤ m^2 + 3 * h⁻¹^2 := by positivity
  have he := norm_hilbertSymbol_sq m (sinQuot (modeMomentum n 0) h)
    (sinQuot (modeMomentum n 1) h) (sinQuot (modeMomentum n 2) h) ψ
  rw [← centered_mode_eq_symbol] at he
  apply (sq_le_sq₀ (norm_nonneg _) (mul_nonneg (Real.sqrt_nonneg _) (norm_nonneg _))).mp
  rw [he, mul_pow, Real.sq_sqrt hs]
  apply mul_le_mul_of_nonneg_right _ (sq_nonneg ‖ψ‖)
  linarith

/-- Centered bounded operator. Its value at zero spacing is auxiliary zero. -/
def centeredCoeffOperator (m h : ℝ) : CoeffL2 →L[ℂ] CoeffL2 :=
  if hh : h = 0 then 0 else
    boundedModewiseOperator (centralHilbertModeOperator m h)
      (Real.sqrt (m^2 + 3*h⁻¹^2)) (Real.sqrt_nonneg _) (centered_mode_bound m h hh)

@[simp] theorem centeredCoeffOperator_apply (m h : ℝ) (hh : h ≠ 0)
    (f : CoeffL2) (n : Mode) :
    centeredCoeffOperator m h f n = centralHilbertModeOperator m h n (f n) := by
  simp [centeredCoeffOperator, hh]

theorem centeredCoeffOperator_norm_le (m h : ℝ) (hh : h ≠ 0) :
    ‖centeredCoeffOperator m h‖ ≤ Real.sqrt (m^2 + 3*h⁻¹^2) := by
  simp only [centeredCoeffOperator, hh, dite_false]
  exact boundedModewiseOperator_norm_le _ _ _ _

theorem centeredCoeffOperator_symmetric (m h : ℝ) :
    (centeredCoeffOperator m h : CoeffL2 →ₗ[ℂ] CoeffL2).IsSymmetric := by
  by_cases hh : h = 0
  · simp [centeredCoeffOperator, hh]
  intro f g
  rw [lp.inner_eq_tsum, lp.inner_eq_tsum]
  apply tsum_congr
  intro n
  change inner ℂ (centeredCoeffOperator m h f n) (g n) =
    inner ℂ (f n) (centeredCoeffOperator m h g n)
  simp only [centeredCoeffOperator_apply m h hh]
  exact centralHilbertModeOperator_symmetric m h n (f n) (g n)

theorem centeredCoeffOperator_selfAdjoint (m h : ℝ) : IsSelfAdjoint (centeredCoeffOperator m h) :=
  (centeredCoeffOperator_symmetric m h).isSelfAdjoint

theorem centered_mode_norm_le_continuum (m h : ℝ) (n : Mode) (ψ : HilbertSpinor) :
    ‖centralHilbertModeOperator m h n ψ‖ ≤ ‖continuumHilbertModeOperator m n ψ‖ := by
  have hx := pow_le_pow_left₀ (abs_nonneg _) (abs_sinQuot_le (modeMomentum n 0) h) 2
  have hy := pow_le_pow_left₀ (abs_nonneg _) (abs_sinQuot_le (modeMomentum n 1) h) 2
  have hz := pow_le_pow_left₀ (abs_nonneg _) (abs_sinQuot_le (modeMomentum n 2) h) 2
  simp only [sq_abs] at hx hy hz
  have he := norm_hilbertSymbol_sq m (sinQuot (modeMomentum n 0) h)
    (sinQuot (modeMomentum n 1) h) (sinQuot (modeMomentum n 2) h) ψ
  rw [← centered_mode_eq_symbol] at he
  have hc := norm_continuumHilbertModeOperator_sq m n ψ
  simp only [modeEnergySq, symbolEnergySq] at hc
  have hp := sq_nonneg ‖ψ‖
  nlinarith [mul_le_mul_of_nonneg_right (show
    m^2 + (sinQuot (modeMomentum n 0) h)^2 + (sinQuot (modeMomentum n 1) h)^2 +
      (sinQuot (modeMomentum n 2) h)^2 ≤
    m^2 + (modeMomentum n 0)^2 + (modeMomentum n 1)^2 + (modeMomentum n 2)^2
      by linarith) hp, norm_nonneg (centralHilbertModeOperator m h n ψ),
    norm_nonneg (continuumHilbertModeOperator m n ψ)]

/-- The filled modal symbol is continuous from both signs of spacing. -/
theorem centered_mode_tendsto (m : ℝ) (n : Mode) :
    Tendsto (fun h => centralHilbertModeOperator m h n) (𝓝 0)
      (𝓝 (continuumHilbertModeOperator m n)) := by
  have hc : Continuous (fun h => centralHilbertModeOperator m h n) := by
    unfold centralHilbertModeOperator
    fun_prop
  have hz : centralHilbertModeOperator m 0 n = continuumHilbertModeOperator m n := by
    simp [centralHilbertModeOperator, continuumHilbertModeOperator,
      sinQuot, Relativistic1DContinuumLimit.sinQuot]
  simpa only [hz] using hc.tendsto 0

/-- Full graph-domain convergence with no higher regularity hypothesis. -/
theorem centered_graph_tendsto (m : ℝ) (f : continuumDiracDomain m) :
    Tendsto (fun h => centeredCoeffOperator m h f.1) (𝓝[≠] 0)
      (𝓝 (continuumDiracOutput m f)) := by
  let v : CoeffL2 := (2 : ℂ) • continuumDiracOutput m f
  apply coeff_tendsto (bound := fun n => ‖v n‖)
  · simpa using (lp.memℓp v).summable (by norm_num : 0 < (2 : ENNReal).toReal)
  · intro n
    have hc := (((ContinuousLinearMap.apply ℂ HilbertSpinor) (f.1 n)).continuous.tendsto
      (continuumHilbertModeOperator m n)).comp (centered_mode_tendsto m n)
    have he : (fun h => centeredCoeffOperator m h f.1 n) =ᶠ[𝓝[≠] 0]
        (fun h => centralHilbertModeOperator m h n (f.1 n)) := by
      filter_upwards [self_mem_nhdsWithin] with h hh
      exact centeredCoeffOperator_apply m h hh f.1 n
    exact (hc.mono_left nhdsWithin_le_nhds).congr' he.symm
  · filter_upwards [self_mem_nhdsWithin] with h hh n
    rw [centeredCoeffOperator_apply m h hh, continuumDiracOutput_apply]
    calc
      _ ≤ ‖centralHilbertModeOperator m h n (f.1 n)‖ +
          ‖continuumHilbertModeOperator m n (f.1 n)‖ := norm_sub_le _ _
      _ ≤ ‖continuumHilbertModeOperator m n (f.1 n)‖ +
          ‖continuumHilbertModeOperator m n (f.1 n)‖ :=
        add_le_add (centered_mode_norm_le_continuum m h n (f.1 n)) le_rfl
      _ = ‖v n‖ := by
        simp only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul, continuumDiracOutput_apply]
        norm_num
        ring

open Relativistic3DTorusFourierEvolution

abbrev TorusSpinorL2 := Relativistic3DTorusFourierEvolution.TorusSpinorL2

/-- Fourier transport of the bounded centered operator on physical torus fields. -/
def physicalCenteredOperator (m h : ℝ) : TorusSpinorL2 →L[ℂ] TorusSpinorL2 :=
  torusFourierEquiv.symm.toContinuousLinearEquiv.toContinuousLinearMap.comp
    ((centeredCoeffOperator m h).comp torusFourierEquiv.toContinuousLinearEquiv.toContinuousLinearMap)

@[simp] theorem torusFourierEquiv_physicalCenteredOperator_apply (m h : ℝ)
    (f : TorusSpinorL2) :
    torusFourierEquiv (physicalCenteredOperator m h f) = centeredCoeffOperator m h (torusFourierEquiv f) := by
  change torusFourierEquiv (torusFourierEquiv.symm
    (centeredCoeffOperator m h (torusFourierEquiv f))) = _
  exact torusFourierEquiv.apply_symm_apply _

/-- Full physical-domain convergence uses the existing unitary Fourier equivalence. -/
theorem physical_centered_graph_tendsto (m : ℝ) (f : physicalDiracDomain m) :
    Tendsto (fun h => physicalCenteredOperator m h f.1) (𝓝[≠] 0)
      (𝓝 (physicalDiracPMap m f)) := by
  have hc := torusFourierEquiv.symm.continuous.tendsto
    (continuumDiracOutput m (physicalToCoeffDomain m f))
  exact hc.comp (centered_graph_tendsto m (physicalToCoeffDomain m f))

end KomorebiPhysics.Relativistic3DCenteredConvergence
