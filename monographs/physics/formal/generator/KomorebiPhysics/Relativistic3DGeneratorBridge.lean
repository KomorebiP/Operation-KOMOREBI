import KomorebiPhysics.Relativistic3DWeightedDiracDomain
import Mathlib.Analysis.SpecialFunctions.Exponential
import Mathlib.Analysis.Normed.Group.Tannery
import Mathlib.Analysis.Calculus.Deriv.Slope
import Mathlib.Analysis.Calculus.MeanValue

/-!
# The strong generator of the free Fourier Dirac group

The proofs concern the existing infinite coefficient Hilbert space and actual
physical Fourier equivalence. They do not identify a finite sampled lattice.
Copyright (c) 2026 Komorebi P. Released under the MIT license.
-/
noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

open Filter
open scoped ENNReal BigOperators Topology lp LinearPMap

namespace KomorebiPhysics
namespace Relativistic3DGeneratorBridge

open Relativistic3DFourierHilbertStability
open Relativistic3DFullFourierEvolution
open Relativistic3DTorusFourierEvolution
open Relativistic3DUnboundedDirac
open Relativistic3DWeightedDomain

local instance : NormedAlgebra ℚ HilbertSpinorEnd :=
  NormedAlgebra.restrictScalars ℚ ℂ HilbertSpinorEnd


/-- Exact commutation of continuum evolution with any finite Fourier cutoff.
This finite identity is an ingredient, not a proof of strong differentiability. -/
theorem continuum_evolution_commutes_cutoff (m t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    continuumCoeffPropagator m t (coeffTruncation S f) =
      coeffTruncation S (continuumCoeffPropagator m t f) := by
  classical
  apply lp.ext
  funext n
  by_cases hn : n ∈ S
  · simp [continuumCoeffPropagator_apply, coeffTruncation_apply, hn]
  · simp [continuumCoeffPropagator_apply, coeffTruncation_apply, hn]

/-- Exact commutation of centered evolution with any finite Fourier cutoff. -/
theorem centered_evolution_commutes_cutoff (m h t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    centralCoeffPropagator m h t (coeffTruncation S f) =
      coeffTruncation S (centralCoeffPropagator m h t f) := by
  classical
  apply lp.ext
  funext n
  by_cases hn : n ∈ S
  · simp [centralCoeffPropagator_apply, coeffTruncation_apply, hn]
  · simp [centralCoeffPropagator_apply, coeffTruncation_apply, hn]

/-- Physical Fourier cutoff, defined using the existing linear isometry. -/
def physicalCutoff (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    Relativistic3DTorusFourierEvolution.TorusSpinorL2 :=
  torusFourierEquiv.symm (coeffTruncation S (torusFourierEquiv f))

/-- The physical continuum evolution commutes with the physical Fourier cutoff. -/
theorem physical_evolution_commutes_cutoff (m t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    continuumTorusUnitary m t (physicalCutoff S f) =
      physicalCutoff S (continuumTorusUnitary m t f) := by
  apply torusFourierEquiv.injective
  simp only [torusFourierEquiv_continuumTorusUnitary_apply,
    physicalCutoff, LinearIsometryEquiv.apply_symm_apply]
  simpa [continuumCoeffUnitary_apply] using
    (continuum_evolution_commutes_cutoff m t S (torusFourierEquiv f))

/-- The physical centered evolution commutes with the same Fourier cutoff. -/
theorem physical_centered_evolution_commutes_cutoff (m h t : ℝ)
    (S : Finset Relativistic3DFullFourierEvolution.Mode)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    centralTorusUnitary m h t (physicalCutoff S f) =
      physicalCutoff S (centralTorusUnitary m h t f) := by
  apply torusFourierEquiv.injective
  simp only [torusFourierEquiv_centralTorusUnitary_apply,
    physicalCutoff, LinearIsometryEquiv.apply_symm_apply]
  simpa [centralCoeffUnitary_apply] using
    (centered_evolution_commutes_cutoff m h t S (torusFourierEquiv f))


/-- Square-summable domination promotes spinor coordinate limits to Hilbert limits. -/
theorem coeff_tendsto_zero {X : Type*} {l : Filter X}
    {u : X → Relativistic3DFullFourierEvolution.CoeffL2} {bound : Relativistic3DFullFourierEvolution.Mode → ℝ}
    (hs : Summable (fun n => bound n ^ 2))
    (hc : ∀ n, Tendsto (fun a => u a n) l (𝓝 0))
    (hb : ∀ᶠ a in l, ∀ n, ‖u a n‖ ≤ bound n) :
    Tendsto u l (𝓝 0) := by
  have ht : Tendsto (fun a => ∑' n, ‖u a n‖ ^ 2) l (𝓝 0) := by
    simpa only [tsum_zero] using tendsto_tsum_of_dominated_convergence
      (g := fun _ : Relativistic3DFullFourierEvolution.Mode => (0 : ℝ)) hs
      (fun n => by simpa using (hc n).norm.pow 2)
      (by
        filter_upwards [hb] with a ha n
        rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
        exact pow_le_pow_left₀ (norm_nonneg _) (ha n) 2)
  have he : ∀ a, (∑' n, ‖u a n‖ ^ 2) = ‖u a‖ ^ 2 := by
    intro a
    simpa using (lp.norm_rpow_eq_tsum (by norm_num : 0 < (2 : ENNReal).toReal) (u a)).symm
  simp_rw [he] at ht
  have hn := Real.continuous_sqrt.continuousAt.tendsto.comp ht
  have hn' : Tendsto (fun a => ‖u a‖) l (𝓝 0) := by
    simpa only [Function.comp_def, Real.sqrt_sq (norm_nonneg _), Real.sqrt_zero] using hn
  exact tendsto_zero_iff_norm_tendsto_zero.mpr hn'

/-- Dominated convergence for errors about an arbitrary coefficient field. -/
theorem coeff_tendsto {X : Type*} {l : Filter X}
    {u : X → Relativistic3DFullFourierEvolution.CoeffL2}
    {f : Relativistic3DFullFourierEvolution.CoeffL2}
    {bound : Relativistic3DFullFourierEvolution.Mode → ℝ}
    (hs : Summable (fun n => bound n ^ 2))
    (hc : ∀ n, Tendsto (fun a => u a n) l (𝓝 (f n)))
    (hb : ∀ᶠ a in l, ∀ n, ‖u a n - f n‖ ≤ bound n) :
    Tendsto u l (𝓝 f) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  apply tendsto_zero_iff_norm_tendsto_zero.mp
  apply coeff_tendsto_zero hs
  · intro n
    simpa only [lp.coeFn_sub, Pi.sub_apply, sub_self] using (hc n).sub_const (f n)
  · exact hb

/-- Time scaling is real scalar multiplication of the Schrödinger generator. -/
theorem timeScaled_eq_real_smul (t : ℝ) (A : HilbertSpinorEnd) :
    hilbertTimeScaledOperator t A = t • ((-Complex.I) • A) := by
  ext ψ j
  simp [hilbertTimeScaledOperator, Complex.real_smul]
  ring

/-- The actual modal exponential has its ordinary real-time derivative. -/
theorem mode_orbit_hasDerivAt (m : ℝ) (n : Relativistic3DFullFourierEvolution.Mode)
    (ψ : Relativistic3DFourierHilbertStability.HilbertSpinor) (t : ℝ) :
    HasDerivAt (fun s => continuumHilbertModePropagator m n s ψ)
      ((-Complex.I) • continuumHilbertModePropagator m n t
        (continuumHilbertModeOperator m n ψ)) t := by
  have h := hasDerivAt_exp_smul_const
    ((-Complex.I) • continuumHilbertModeOperator m n) t
  have he := (((ContinuousLinearMap.apply ℂ
    Relativistic3DFourierHilbertStability.HilbertSpinor) ψ).restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt t h
  simpa [continuumHilbertModePropagator, timeScaled_eq_real_smul,
    mul_apply_eq_comp, Function.comp_def] using he

/-- Exact zero-time value of every continuum mode. -/
@[simp] theorem mode_propagator_zero (m : ℝ) (n : Relativistic3DFullFourierEvolution.Mode) :
    continuumHilbertModePropagator m n 0 = 1 := by
  have hz : hilbertTimeScaledOperator 0 (continuumHilbertModeOperator m n) = 0 := by
    ext ψ j
    simp [hilbertTimeScaledOperator]
  rw [continuumHilbertModePropagator, hz, NormedSpace.exp_zero]

/-- Sharp increment bound uses Hψ, not the unbounded supremum of mode norms. -/
theorem mode_increment_bound (m : ℝ) (n : Relativistic3DFullFourierEvolution.Mode)
    (ψ : Relativistic3DFourierHilbertStability.HilbertSpinor) (s t : ℝ) :
    ‖continuumHilbertModePropagator m n s ψ - continuumHilbertModePropagator m n t ψ‖ ≤
      |s-t| * ‖continuumHilbertModeOperator m n ψ‖ := by
  have h := Convex.norm_image_sub_le_of_norm_hasDerivWithin_le
    (s := Set.univ)
    (fun x _ => (mode_orbit_hasDerivAt m n ψ x).hasDerivWithinAt)
    (C := ‖continuumHilbertModeOperator m n ψ‖)
    (fun x _ => by
      simp only [norm_smul, norm_neg, Complex.norm_I, one_mul,
        norm_continuumHilbertModePropagator]
      exact le_rfl)
    (convex_univ : Convex ℝ (Set.univ : Set ℝ)) (Set.mem_univ t) (Set.mem_univ s)
  simpa [Real.norm_eq_abs, mul_comm] using h

/-- Strong continuity holds for every square-summable spinor field. -/
theorem continuum_orbit_continuous (m : ℝ)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    Continuous (fun t => continuumCoeffPropagator m t f) := by
  apply continuous_iff_continuousAt.mpr
  intro t
  let v : Relativistic3DFullFourierEvolution.CoeffL2 := (2 : ℂ) • f
  apply coeff_tendsto (bound := fun n => ‖v n‖)
  · simpa using (lp.memℓp v).summable (by norm_num : 0 < (2 : ENNReal).toReal)
  · intro n
    simpa only [continuumCoeffPropagator_apply] using
      (mode_orbit_hasDerivAt m n (f n) t).continuousAt.tendsto
  · apply Filter.Eventually.of_forall
    intro s n
    calc
      _ ≤ ‖continuumCoeffPropagator m s f n‖ + ‖continuumCoeffPropagator m t f n‖ :=
        norm_sub_le _ _
      _ = ‖f n‖ + ‖f n‖ := by
        simp only [continuumCoeffPropagator_apply, norm_continuumHilbertModePropagator]
      _ = ‖v n‖ := by
        simp only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul]
        norm_num
        ring

/-- The full coefficient group is the identity at zero time. -/
@[simp] theorem continuum_coeff_zero (m : ℝ)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    continuumCoeffPropagator m 0 f = f := by
  apply lp.ext
  funext n
  simp [continuumCoeffPropagator_apply]

/-- Every modal slope is bounded by the corresponding Hamiltonian output. -/
theorem coefficient_slope_bound (m : ℝ)
    (f : continuumDiracDomain m) (s t : ℝ)
    (n : Relativistic3DFullFourierEvolution.Mode) :
    ‖slope (fun u => continuumCoeffPropagator m u f.1) t s n‖ ≤
      ‖continuumDiracOutput m f n‖ := by
  by_cases h : s = t
  · subst s
    simp only [slope_same, lp.coeFn_zero, Pi.zero_apply, norm_zero]
    exact norm_nonneg _
  · have hab : |s-t| ≠ 0 := abs_ne_zero.mpr (sub_ne_zero.mpr h)
    simp only [slope_def_module, lp.coeFn_smul, lp.coeFn_sub, Pi.smul_apply,
      Pi.sub_apply, norm_smul, Real.norm_eq_abs, abs_inv, continuumCoeffPropagator_apply]
    calc
      _ ≤ |s-t|⁻¹ * (|s-t| * ‖continuumHilbertModeOperator m n (f.1 n)‖) :=
        mul_le_mul_of_nonneg_left (mode_increment_bound m n (f.1 n) s t)
          (inv_nonneg.mpr (abs_nonneg _))
      _ = ‖continuumDiracOutput m f n‖ := by
        rw [← mul_assoc, inv_mul_cancel₀ hab, one_mul, continuumDiracOutput_apply]

/-- Full Hilbert-space differentiation on the maximal graph domain. -/
theorem continuum_orbit_hasDerivAt (m : ℝ)
    (f : continuumDiracDomain m) (t : ℝ) :
    HasDerivAt (fun s => continuumCoeffPropagator m s f.1)
      ((-Complex.I) • continuumCoeffPropagator m t (continuumDiracOutput m f)) t := by
  let v : Relativistic3DFullFourierEvolution.CoeffL2 := (2 : ℂ) • continuumDiracOutput m f
  apply hasDerivAt_iff_tendsto_slope.mpr
  apply coeff_tendsto (bound := fun n => ‖v n‖)
  · simpa using (lp.memℓp v).summable (by norm_num : 0 < (2 : ENNReal).toReal)
  · intro n
    have h := (mode_orbit_hasDerivAt m n (f.1 n) t).tendsto_slope
    simp only [slope_fun_def, vsub_eq_sub] at h
    simpa only [slope_def_module, lp.coeFn_smul, lp.coeFn_sub, Pi.smul_apply,
      Pi.sub_apply, continuumCoeffPropagator_apply, continuumDiracOutput_apply] using h
  · apply Filter.Eventually.of_forall
    intro s n
    calc
      _ ≤ ‖slope (fun u => continuumCoeffPropagator m u f.1) t s n‖ +
          ‖((-Complex.I) • continuumCoeffPropagator m t (continuumDiracOutput m f)) n‖ :=
        norm_sub_le _ _
      _ ≤ ‖continuumDiracOutput m f n‖ + ‖continuumDiracOutput m f n‖ := by
        apply add_le_add (coefficient_slope_bound m f s t n)
        simp only [lp.coeFn_smul, Pi.smul_apply, norm_smul, norm_neg,
          Complex.norm_I, one_mul, continuumCoeffPropagator_apply,
          norm_continuumHilbertModePropagator, le_refl]
      _ = ‖v n‖ := by
        simp only [v, lp.coeFn_smul, Pi.smul_apply, norm_smul]
        norm_num
        ring

/-- At zero, the strong derivative is exactly minus i times the maximal Hamiltonian. -/
theorem continuum_orbit_hasDerivAt_zero (m : ℝ) (f : continuumDiracDomain m) :
    HasDerivAt (fun t => continuumCoeffPropagator m t f.1)
      ((-Complex.I) • continuumDiracOutput m f) 0 := by
  simpa only [continuum_coeff_zero] using continuum_orbit_hasDerivAt m f 0

/-- An ambient derivative determines every modal coordinate. -/
theorem derivative_coordinates_zero (m : ℝ)
    {f y : Relativistic3DFullFourierEvolution.CoeffL2}
    (h : HasDerivAt (fun t => continuumCoeffPropagator m t f) y 0)
    (n : Relativistic3DFullFourierEvolution.Mode) :
    y n = (-Complex.I) • continuumHilbertModeOperator m n (f n) := by
  have he := ((lp.evalCLM ℂ (fun _ : Relativistic3DFullFourierEvolution.Mode =>
    Relativistic3DFourierHilbertStability.HilbertSpinor) 2 n).restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt 0 h
  have he' : HasDerivAt (fun t => continuumHilbertModePropagator m n t (f n)) (y n) 0 := by
    change HasDerivAt (fun t => continuumHilbertModePropagator m n t (f n)) (y n) 0 at he
    exact he
  exact he'.unique (by simpa only [mode_propagator_zero, one_apply_eq_self] using
    mode_orbit_hasDerivAt m n (f n) 0)

/-- Converse domain inclusion, with no differentiability assumption hidden in the domain. -/
theorem mem_domain_of_hasDerivAt_zero (m : ℝ)
    {f y : Relativistic3DFullFourierEvolution.CoeffL2}
    (h : HasDerivAt (fun t => continuumCoeffPropagator m t f) y 0) :
    f ∈ continuumDiracDomain m := by
  change Memℓp (diracCoeff m f) 2
  convert lp.memℓp (Complex.I • y) using 1
  funext n
  simp only [lp.coeFn_smul, Pi.smul_apply, derivative_coordinates_zero m h n,
    smul_smul]
  simp [diracCoeff]

/-- Exact maximal generator domain of the already constructed coefficient group. -/
theorem differentiableAt_zero_iff_mem_domain (m : ℝ)
    (f : Relativistic3DFullFourierEvolution.CoeffL2) :
    DifferentiableAt ℝ (fun t => continuumCoeffPropagator m t f) 0 ↔
      f ∈ continuumDiracDomain m := by
  constructor
  · intro h
    exact mem_domain_of_hasDerivAt_zero m h.hasDerivAt
  · intro hf
    exact (continuum_orbit_hasDerivAt_zero m ⟨f, hf⟩).differentiableAt

/-- The velocity is continuous without requiring a second Hamiltonian moment. -/
theorem continuum_velocity_continuous (m : ℝ) (f : continuumDiracDomain m) :
    Continuous (fun t => (-Complex.I) • continuumCoeffPropagator m t (continuumDiracOutput m f)) :=
  (continuum_orbit_continuous m (continuumDiracOutput m f)).const_smul (-Complex.I)

/-- The ambient strong derivative has constant norm equal to the Hamiltonian norm. -/
theorem continuum_derivative_norm (m : ℝ) (f : continuumDiracDomain m) (t : ℝ) :
    ‖deriv (fun s => continuumCoeffPropagator m s f.1) t‖ = ‖continuumDiracOutput m f‖ := by
  rw [(continuum_orbit_hasDerivAt m f t).deriv, norm_smul, norm_neg,
    Complex.norm_I, one_mul, norm_continuumCoeffPropagator]

/-- The physical evolution is the actual Fourier-conjugated coefficient group. -/
theorem physical_evolution_eq_fourier (m t : ℝ)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    continuumTorusUnitary m t f = torusFourierEquiv.symm
      (continuumCoeffPropagator m t (torusFourierEquiv f)) := rfl

/-- The physical partial operator is synthesized from the maximal coefficient output. -/
theorem physical_output_eq_fourier (m : ℝ) (f : physicalDiracDomain m) :
    physicalDiracPMap m f = torusFourierEquiv.symm
      (continuumDiracOutput m (physicalToCoeffDomain m f)) := rfl

/-- Strong continuity on the actual physical torus Hilbert space. -/
theorem physical_orbit_continuous (m : ℝ)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    Continuous (fun t => continuumTorusUnitary m t f) := by
  simpa only [Function.comp_def, physical_evolution_eq_fourier] using
    torusFourierEquiv.symm.continuous.comp (continuum_orbit_continuous m (torusFourierEquiv f))

/-- The physical group is the identity at zero. -/
@[simp] theorem physical_unitary_zero (m : ℝ)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    continuumTorusUnitary m 0 f = f := by
  simp only [physical_evolution_eq_fourier, continuum_coeff_zero,
    LinearIsometryEquiv.symm_apply_apply]

/-- The physical orbit has a strong derivative at every time on the maximal domain. -/
theorem physical_orbit_hasDerivAt (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
    HasDerivAt (fun s => continuumTorusUnitary m s f.1)
      ((-Complex.I) • continuumTorusUnitary m t (physicalDiracPMap m f)) t := by
  have hc := continuum_orbit_hasDerivAt m (physicalToCoeffDomain m f) t
  have hp := (torusFourierEquiv.symm.toContinuousLinearEquiv.toContinuousLinearMap.restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt t hc
  change HasDerivAt (fun s => torusFourierEquiv.symm
    (continuumCoeffPropagator m s (torusFourierEquiv f.1)))
    (torusFourierEquiv.symm ((-Complex.I) • continuumCoeffPropagator m t
      (continuumDiracOutput m (physicalToCoeffDomain m f)))) t at hp
  simpa only [physical_evolution_eq_fourier, physical_output_eq_fourier,
    LinearIsometryEquiv.apply_symm_apply, map_smul] using hp

/-- The physical strong generator is minus i times the existing partial Hamiltonian. -/
theorem physical_orbit_hasDerivAt_zero (m : ℝ) (f : physicalDiracDomain m) :
    HasDerivAt (fun t => continuumTorusUnitary m t f.1)
      ((-Complex.I) • physicalDiracPMap m f) 0 := by
  simpa only [physical_unitary_zero] using physical_orbit_hasDerivAt m f 0

/-- A physical derivative forces the exact Hamiltonian domain, not a smaller core. -/
theorem physical_mem_domain_of_hasDerivAt_zero (m : ℝ)
    {f y : Relativistic3DTorusFourierEvolution.TorusSpinorL2}
    (h : HasDerivAt (fun t => continuumTorusUnitary m t f) y 0) :
    f ∈ physicalDiracDomain m := by
  have hf := (torusFourierEquiv.toContinuousLinearEquiv.toContinuousLinearMap.restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt 0 h
  have hc : HasDerivAt (fun t => continuumCoeffPropagator m t (torusFourierEquiv f))
      (torusFourierEquiv y) 0 := by
    change HasDerivAt (fun t => torusFourierEquiv (continuumTorusUnitary m t f))
      (torusFourierEquiv y) 0 at hf
    simpa only [torusFourierEquiv_continuumTorusUnitary_apply, continuumCoeffUnitary_apply] using hf
  exact mem_domain_of_hasDerivAt_zero m hc

/-- Exact physical generator-domain identification. -/
theorem physical_differentiableAt_zero_iff_mem_domain (m : ℝ)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    DifferentiableAt ℝ (fun t => continuumTorusUnitary m t f) 0 ↔
      f ∈ physicalDiracDomain m := by
  constructor
  · intro h
    exact physical_mem_domain_of_hasDerivAt_zero m h.hasDerivAt
  · intro hf
    exact (physical_orbit_hasDerivAt_zero m ⟨f, hf⟩).differentiableAt

/-- First-order Fourier regularity is exactly differentiability at zero time. -/
theorem physical_differentiableAt_zero_iff_summable_h1 (m : ℝ)
    (f : Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
    DifferentiableAt ℝ (fun t => continuumTorusUnitary m t f) 0 ↔
      Summable (fun n => h1ModeTerm (torusFourierEquiv f) n) := by
  rw [physical_differentiableAt_zero_iff_mem_domain,
    mem_physicalDiracDomain_iff_summable_h1]

/-- The value of the physical strong generator as an ordinary derivative. -/
theorem physical_deriv_zero (m : ℝ) (f : physicalDiracDomain m) :
    deriv (fun t => continuumTorusUnitary m t f.1) 0 =
      (-Complex.I) • physicalDiracPMap m f :=
  (physical_orbit_hasDerivAt_zero m f).deriv

/-- The physical velocity is continuous with only first-order Fourier regularity. -/
theorem physical_velocity_continuous (m : ℝ) (f : physicalDiracDomain m) :
    Continuous (fun t => (-Complex.I) • continuumTorusUnitary m t (physicalDiracPMap m f)) :=
  (physical_orbit_continuous m (physicalDiracPMap m f)).const_smul (-Complex.I)

/-- The physical orbit has constant speed equal to its Hamiltonian-output norm. -/
theorem physical_derivative_norm (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
    ‖deriv (fun s => continuumTorusUnitary m s f.1) t‖ = ‖physicalDiracPMap m f‖ := by
  rw [(physical_orbit_hasDerivAt m f t).deriv, norm_smul, norm_neg,
    Complex.norm_I, one_mul, norm_continuumTorusUnitary]

/-- Differentiating a shifted orbit uses only the established group law. -/
theorem physical_shifted_orbit_hasDerivAt_zero (m : ℝ)
    (f : physicalDiracDomain m) (t : ℝ) :
    HasDerivAt (fun s => continuumTorusUnitary m s (continuumTorusUnitary m t f.1))
      ((-Complex.I) • continuumTorusUnitary m t (physicalDiracPMap m f)) 0 := by
  have hs : HasDerivAt (fun s : ℝ => s + t) 1 0 := (hasDerivAt_id 0).add_const t
  have hshift := (physical_orbit_hasDerivAt m f t).scomp_of_eq 0 hs (by simp)
  simpa only [Function.comp_def, one_smul, continuumTorusUnitary_add_time] using hshift

/-- The complete maximal physical domain is invariant under the actual unitary group. -/
theorem physical_domain_invariant (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
    continuumTorusUnitary m t f.1 ∈ physicalDiracDomain m :=
  physical_mem_domain_of_hasDerivAt_zero m (physical_shifted_orbit_hasDerivAt_zero m f t)

/-- The evolved physical-domain vector retains its domain proof. -/
def physicalEvolvedDomain (m t : ℝ) (f : physicalDiracDomain m) : physicalDiracDomain m :=
  ⟨continuumTorusUnitary m t f.1, physical_domain_invariant m f t⟩

/-- Exact Hamiltonian/evolution commutation includes the transported domain witness. -/
theorem physical_hamiltonian_commutes (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
    physicalDiracPMap m (physicalEvolvedDomain m t f) =
      continuumTorusUnitary m t (physicalDiracPMap m f) := by
  have he := (physical_orbit_hasDerivAt_zero m (physicalEvolvedDomain m t f)).unique
    (physical_shifted_orbit_hasDerivAt_zero m f t)
  have hx := congrArg (fun v : Relativistic3DTorusFourierEvolution.TorusSpinorL2 => Complex.I • v) he
  simpa [smul_smul] using hx

/-- The orbit satisfies the strong Schrödinger equation on the actual maximal domain. -/
theorem physical_schrodinger_hasDerivAt (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
    HasDerivAt (fun s => continuumTorusUnitary m s f.1)
      ((-Complex.I) • physicalDiracPMap m (physicalEvolvedDomain m t f)) t := by
  rw [physical_hamiltonian_commutes]
  exact physical_orbit_hasDerivAt m f t

/-- Evolution preserves the norm of the unbounded Hamiltonian output. -/
theorem physical_graph_energy_conserved (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
    ‖physicalDiracPMap m (physicalEvolvedDomain m t f)‖ = ‖physicalDiracPMap m f‖ := by
  rw [physical_hamiltonian_commutes, norm_continuumTorusUnitary]

end Relativistic3DGeneratorBridge
end KomorebiPhysics
