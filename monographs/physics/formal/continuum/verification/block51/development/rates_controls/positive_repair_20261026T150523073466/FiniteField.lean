import KomorebiPhysics.Relativistic3DCenteredRates

noncomputable section
open scoped ENNReal BigOperators lp
open KomorebiPhysics
open Relativistic3DCenteredRates
open Relativistic3DCenteredConvergence
open Relativistic3DFullFourierEvolution
open Relativistic3DFourierL2Generator
open Relativistic3DTorusFourierEvolution
open Relativistic3DUnboundedDirac

namespace RatesFiniteControl

abbrev C := Relativistic3DFullFourierEvolution.CoeffL2
abbrev N := Relativistic3DFullFourierEvolution.Mode

def mode : N := fun _ => 1
def spinor : Relativistic3DFourierHilbertStability.HilbertSpinor :=
  spinorToHilbert (fun j => if j = 0 then 1 else 0)
def field : C := lp.single 2 mode spinor

theorem field_coordinate : field mode 0 = 1 := by
  simp [field, spinor]

theorem field_ne_zero : field ≠ 0 := by
  intro h
  have he := congrArg (fun f : C => f mode 0) h
  rw [field_coordinate] at he
  change (1 : ℂ) = 0 at he
  exact one_ne_zero he

theorem field_moment : HasThirdOrderMoment field := by
  classical
  apply summable_of_ne_finset_zero (s := {mode})
  intro n hn
  have hne : n ≠ mode := by simpa only [Finset.mem_singleton] using hn
  simp [thirdOrderModeTerm, field, hne]

example :
    ‖Relativistic3DCenteredConvergence.centeredCoeffOperator 1 (-(1/10 : ℝ)) field -
      continuumDiracOutput 1 ⟨field, field_moment.mem_continuumDiracDomain 1⟩‖ ≤
      (-(1/10 : ℝ)) ^ 2 / 6 * thirdOrderMoment field :=
  centered_generator_quadratic_bound 1 (-(1/10 : ℝ)) (by norm_num) field field_moment

example :
    ‖centralCoeffPropagator 1 (-(1/10 : ℝ)) (-2) field -
      continuumCoeffPropagator 1 (-2) field‖ ≤
      (|(-2 : ℝ)| * (-(1/10 : ℝ)) ^ 2 / 6) * thirdOrderMoment field :=
  centered_propagator_quadratic_bound 1 (-(1/10 : ℝ)) (-2) field field_moment

example :
    ‖centralTorusUnitary 1 (-(1/10 : ℝ)) (-2) (torusFourierEquiv.symm field) -
      continuumTorusUnitary 1 (-2) (torusFourierEquiv.symm field)‖ ≤
      (|(-2 : ℝ)| * (-(1/10 : ℝ)) ^ 2 / 6) *
        thirdOrderMoment (torusFourierEquiv (torusFourierEquiv.symm field)) := by
  apply physical_propagator_quadratic_bound
  simpa only [LinearIsometryEquiv.apply_symm_apply] using field_moment

end RatesFiniteControl
