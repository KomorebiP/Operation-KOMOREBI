import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.MeasureTheory.Measure.Prod
import Mathlib.MeasureTheory.Integral.Lebesgue.Map
import Mathlib.Analysis.SpecialFunctions.Pow.NNReal

noncomputable section
set_option autoImplicit false

namespace Komorebi.QuadraticTransport
open MeasureTheory

variable {E : Type*} [NormedAddCommGroup E] [MeasurableSpace E] [BorelSpace E]

/-- A transport plan has the specified actual marginal measures. -/
def IsTransportPlan (μ ν : Measure E) (γ : Measure (E × E)) : Prop :=
  γ.map Prod.fst = μ ∧ γ.map Prod.snd = ν

/-- Extended nonnegative quadratic transport cost. Nonintegrable plans cost infinity,
not zero as a totalized real Bochner integral would. -/
def quadraticCost (γ : Measure (E × E)) : ℝ≥0∞ :=
  ∫⁻ z, ENNReal.ofReal (‖z.1 - z.2‖ ^ 2) ∂γ

/-- The standard squared 2-Wasserstein infimum over ALL marginal-compatible plans.
This is not restricted to Gaussian plans or to a supplied coupling. -/
def wasserstein2Sq (μ ν : Measure E) : ℝ≥0∞ :=
  ⨅ (γ : Measure (E × E)) (_h : IsTransportPlan μ ν γ), quadraticCost γ

/-- The extended 2-Wasserstein value, with the conventional square root. -/
def wasserstein2 (μ ν : Measure E) : ℝ≥0∞ :=
  wasserstein2Sq μ ν ^ (1 / 2 : ℝ)

theorem wasserstein2Sq_le_cost (μ ν : Measure E) (γ : Measure (E × E))
    (hγ : IsTransportPlan μ ν γ) : wasserstein2Sq μ ν ≤ quadraticCost γ := by
  exact iInf_le_of_le γ (iInf_le _ hγ)

variable {Ω : Type*} [MeasurableSpace Ω]

/-- Common-source sampling gives a genuine transport plan. -/
theorem sharedMap_isTransportPlan (ρ : Measure Ω) (f g : Ω → E)
    (hf : Measurable f) (hg : Measurable g) :
    IsTransportPlan (ρ.map f) (ρ.map g) (ρ.map (fun z => (f z, g z))) := by
  constructor
  · rw [Measure.map_map measurable_fst (hf.prodMk hg)]
    rfl
  · rw [Measure.map_map measurable_snd (hf.prodMk hg)]
    rfl

/-- Cost of the explicit shared-source coupling. -/
theorem quadraticCost_sharedMap (ρ : Measure Ω) (f g : Ω → E)
    (hf : Measurable f) (hg : Measurable g) :
    quadraticCost (ρ.map (fun z => (f z, g z))) =
      ∫⁻ z, ENNReal.ofReal (‖f z - g z‖ ^ 2) ∂ρ := by
  unfold quadraticCost
  rw [lintegral_map (by fun_prop) (hf.prodMk hg)]

/-- Every measurable shared-source coupling bounds the all-plan infimum. -/
theorem wasserstein2Sq_map_le (ρ : Measure Ω) (f g : Ω → E)
    (hf : Measurable f) (hg : Measurable g) :
    wasserstein2Sq (ρ.map f) (ρ.map g) ≤
      ∫⁻ z, ENNReal.ofReal (‖f z - g z‖ ^ 2) ∂ρ := by
  calc
    _ ≤ quadraticCost (ρ.map (fun z => (f z, g z))) :=
      wasserstein2Sq_le_cost _ _ _ (sharedMap_isTransportPlan ρ f g hf hg)
    _ = _ := quadraticCost_sharedMap ρ f g hf hg

/-- Rewrite a finite real quadratic integral without losing the extended-cost semantics. -/
theorem wasserstein2Sq_map_le_integral (ρ : Measure Ω) (f g : Ω → E)
    (hf : Measurable f) (hg : Measurable g)
    (hi : Integrable (fun z => ‖f z - g z‖ ^ 2) ρ) :
    wasserstein2Sq (ρ.map f) (ρ.map g) ≤
      ENNReal.ofReal (∫ z, ‖f z - g z‖ ^ 2 ∂ρ) := by
  rw [ofReal_integral_eq_lintegral_ofReal hi (Filter.Eventually.of_forall (fun _ => sq_nonneg _))]
  exact wasserstein2Sq_map_le ρ f g hf hg

end Komorebi.QuadraticTransport
