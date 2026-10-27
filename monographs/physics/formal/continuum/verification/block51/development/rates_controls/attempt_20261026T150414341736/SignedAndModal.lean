import KomorebiPhysics.Relativistic3DCenteredRates

noncomputable section
open KomorebiPhysics
open Relativistic3DCenteredRates
open Relativistic3DFullFourierEvolution
open Relativistic3DFourierHilbertStability
open Relativistic3DModalPerturbation

example (m h : ℝ) (f : Relativistic3DFullFourierEvolution.CoeffL2)
    (hf : HasThirdOrderMoment f) :
    ‖centralCoeffPropagator m h 0 f - continuumCoeffPropagator m 0 f‖ ≤ 0 := by
  have hb := centered_propagator_compactTime_bound m h 0 (by norm_num) f hf 0 (by simp)
  simpa using hb

example (m t : ℝ) (f : Relativistic3DFullFourierEvolution.CoeffL2)
    (hf : HasThirdOrderMoment f) :
    ‖centralCoeffPropagator m 0 t f - continuumCoeffPropagator m t f‖ ≤ 0 := by
  simpa using centered_propagator_quadratic_bound m 0 t f hf

example (A : HilbertSpinorEnd) (hA : IsSelfAdjoint A) (t : ℝ)
    (ψ : Relativistic3DFourierHilbertStability.HilbertSpinor) :
    ‖modalEvolution A t ψ - modalEvolution A t ψ‖ ≤ 0 := by
  simpa using modal_perturbation_bound A A hA hA 0 (by norm_num)
    (by intro φ; simp) t ψ
