module

public import KomorebiPhysics.Relativistic3DFourierL2Generator
public import Mathlib.Analysis.Normed.Algebra.Exponential
public import Mathlib.Tactic.Module

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Asymptotics
open NormedSpace
open scoped Topology BigOperators

/-!
# Fixed-cutoff Fourier propagator convergence

This module upgrades the Block 42 generator-consistency theorem to bounded
finite-dimensional exponential evolution on each Fourier mode.  The mode
generators are packaged as continuous linear endomorphisms, their difference is
`O(h²)` in operator norm, and analyticity of the Banach-algebra exponential
transfers that rate to the mode propagators.

For every fixed finite Fourier support and fixed physical time, the propagated
packet converges strongly in torus `L²`, again with `O(h²)` mesh error.  Exact
zero-time, one-parameter group, inverse-time, residual decomposition, and
Parseval identities are included.

The block does not yet prove that these exponential operators are unitary in
the Hilbert norm, does not give a time-uniform estimate on compact intervals,
and does not remove the fixed Fourier cutoff.
-/

namespace KomorebiPhysics
namespace Relativistic3DFourierPropagator

open Relativistic3DCliffordTransportU1
open Relativistic3DFourierGenerator
open Relativistic3DFourierL2Generator

abbrev Spinor := Relativistic3DFourierGenerator.Spinor
abbrev Mode := Relativistic3DFourierGenerator.Mode
abbrev SpinorEnd := Spinor →L[ℂ] Spinor

local instance : NormedAlgebra ℚ SpinorEnd :=
  NormedAlgebra.restrictScalars ℚ ℂ SpinorEnd

/-- The linear endomorphism attached to a concrete Clifford involution. -/
def cliffordLinear (A : CliffordInvolution) : Spinor →ₗ[ℂ] Spinor where
  toFun := A.act
  map_add' := A.map_add
  map_smul' := A.map_smul

/-- Every four-spinor linear map is continuous because the source is finite-dimensional. -/
def cliffordOperator (A : CliffordInvolution) : SpinorEnd :=
  LinearMap.toContinuousLinearMap (cliffordLinear A)

@[simp] theorem cliffordOperator_apply (A : CliffordInvolution) (ψ : Spinor) :
    cliffordOperator A ψ = A.act ψ := rfl

/-- The Dirac beta action as a complex-linear endomorphism. -/
def betaLinear : Spinor →ₗ[ℂ] Spinor where
  toFun := beta
  map_add' := by
    intro ψ φ
    ext j
    fin_cases j <;> simp [beta] <;> abel
  map_smul' := by
    intro c ψ
    ext j
    fin_cases j <;> simp [beta]

/-- Continuous beta operator on algebraic four-spinors. -/
def betaOperator : SpinorEnd :=
  LinearMap.toContinuousLinearMap betaLinear

@[simp] theorem betaOperator_apply (ψ : Spinor) :
    betaOperator ψ = beta ψ := rfl

abbrev alphaXOperator : SpinorEnd := cliffordOperator cliffordX
abbrev alphaYOperator : SpinorEnd := cliffordOperator cliffordY
abbrev alphaZOperator : SpinorEnd := cliffordOperator cliffordZ

/-- Continuum free Dirac generator on one Fourier mode as a bounded endomorphism. -/
def continuumModeOperator (m : ℝ) (n : Mode) : SpinorEnd :=
  ((modeMomentum n 0 : ℝ) : ℂ) • alphaXOperator +
  ((modeMomentum n 1 : ℝ) : ℂ) • alphaYOperator +
  ((modeMomentum n 2 : ℝ) : ℂ) • alphaZOperator +
  (m : ℂ) • betaOperator

/-- Central-difference free Dirac generator on one Fourier mode. -/
def centralModeOperator (m h : ℝ) (n : Mode) : SpinorEnd :=
  ((sinQuot (modeMomentum n 0) h : ℝ) : ℂ) • alphaXOperator +
  ((sinQuot (modeMomentum n 1) h : ℝ) : ℂ) • alphaYOperator +
  ((sinQuot (modeMomentum n 2) h : ℝ) : ℂ) • alphaZOperator +
  (m : ℂ) • betaOperator

@[simp] theorem continuumModeOperator_apply (m : ℝ) (n : Mode) (ψ : Spinor) :
    continuumModeOperator m n ψ = continuumModeAction m n ψ := by
  rfl

@[simp] theorem centralModeOperator_apply (m h : ℝ) (n : Mode) (ψ : Spinor) :
    centralModeOperator m h n ψ = centralModeAction m h n ψ := by
  rfl

/-- Exact operator residual: the mass contribution cancels. -/
theorem centralModeOperator_sub_continuum (m h : ℝ) (n : Mode) :
    centralModeOperator m h n - continuumModeOperator m n =
      (((sinQuot (modeMomentum n 0) h - modeMomentum n 0 : ℝ) : ℂ) • alphaXOperator +
       ((sinQuot (modeMomentum n 1) h - modeMomentum n 1 : ℝ) : ℂ) • alphaYOperator +
       ((sinQuot (modeMomentum n 2) h - modeMomentum n 2 : ℝ) : ℂ) • alphaZOperator) := by
  simp only [centralModeOperator, continuumModeOperator, Complex.ofReal_sub]
  module

/-- Scalar multiplication of a fixed endomorphism as a continuous linear map. -/
def smulOperatorCLM (A : SpinorEnd) : ℂ →L[ℂ] SpinorEnd :=
  ContinuousLinearMap.smulRight (ContinuousLinearMap.id ℂ ℂ) A

@[simp] theorem smulOperatorCLM_apply (A : SpinorEnd) (z : ℂ) :
    smulOperatorCLM A z = z • A := rfl

/-- A sine-quotient residual times a fixed endomorphism remains quadratic. -/
theorem sinQuot_residual_operator_isBigO (k : ℝ) (A : SpinorEnd) :
    (fun h : ℝ => (((sinQuot k h - k : ℝ) : ℂ) • A)) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) := by
  have hc0 := Complex.ofRealCLM.isBigO_comp
    (fun h : ℝ => sinQuot k h - k) (𝓝[>] 0)
  have hc : (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) :=
    hc0.trans (Relativistic1DContinuumLimit.sinQuot_expansion_isBigO k)
  have hop := (smulOperatorCLM A).isBigO_comp
    (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) (𝓝[>] 0)
  simpa only [smulOperatorCLM_apply] using hop.trans hc

/-- The complete mode generator converges in operator norm with quadratic order. -/
theorem centralModeOperator_sub_continuum_isBigO (m : ℝ) (n : Mode) :
    (fun h : ℝ => centralModeOperator m h n - continuumModeOperator m n)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have hx := sinQuot_residual_operator_isBigO (modeMomentum n 0) alphaXOperator
  have hy := sinQuot_residual_operator_isBigO (modeMomentum n 1) alphaYOperator
  have hz := sinQuot_residual_operator_isBigO (modeMomentum n 2) alphaZOperator
  exact ((hx.add hy).add hz).congr_left (by
    intro h
    exact (centralModeOperator_sub_continuum m h n).symm)

/-- Operator-norm convergence of the central-difference mode generator. -/
theorem tendsto_centralModeOperator (m : ℝ) (n : Mode) :
    Tendsto (fun h : ℝ => centralModeOperator m h n)
      (𝓝[>] 0) (𝓝 (continuumModeOperator m n)) := by
  have herr := (centralModeOperator_sub_continuum_isBigO m n).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumModeOperator m n)
      (𝓝[>] 0) (𝓝 (continuumModeOperator m n)) := tendsto_const_nhds
  simpa only [sub_add_cancel, zero_add] using herr.add hc


/-- Multiply a bounded mode generator by the Schrödinger time coefficient `-i t`. -/
def timeScaledOperator (t : ℝ) (A : SpinorEnd) : SpinorEnd :=
  (-(Complex.I * (t : ℂ))) • A

@[simp] theorem timeScaledOperator_zero (A : SpinorEnd) :
    timeScaledOperator 0 A = 0 := by
  ext ψ
  simp [timeScaledOperator]

/-- Exact time-scaled generator residual. -/
theorem timeScaledOperator_sub (m t h : ℝ) (n : Mode) :
    timeScaledOperator t (centralModeOperator m h n) -
        timeScaledOperator t (continuumModeOperator m n) =
      (-(Complex.I * (t : ℂ))) •
        (centralModeOperator m h n - continuumModeOperator m n) := by
  simp only [timeScaledOperator]
  module

/-- The time-scaled generator residual retains quadratic mesh order. -/
theorem timeScaledOperator_sub_isBigO (m t : ℝ) (n : Mode) :
    (fun h : ℝ => timeScaledOperator t (centralModeOperator m h n) -
      timeScaledOperator t (continuumModeOperator m n))
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  exact ((centralModeOperator_sub_continuum_isBigO m n).const_smul_left
    (-(Complex.I * (t : ℂ)))).congr_left (by
      intro h
      exact (timeScaledOperator_sub m t h n).symm)

/-- Time-scaled mode generators converge in operator norm. -/
theorem tendsto_timeScaledOperator (m t : ℝ) (n : Mode) :
    Tendsto (fun h : ℝ => timeScaledOperator t (centralModeOperator m h n))
      (𝓝[>] 0) (𝓝 (timeScaledOperator t (continuumModeOperator m n))) := by
  exact (tendsto_centralModeOperator m n).const_smul
    (-(Complex.I * (t : ℂ)))

/-- Continuum finite-dimensional propagator on one Fourier mode. -/
def continuumModePropagator (m : ℝ) (n : Mode) (t : ℝ) : SpinorEnd :=
  NormedSpace.exp (timeScaledOperator t (continuumModeOperator m n))

/-- Central-difference finite-dimensional propagator on one Fourier mode. -/
def centralModePropagator (m h : ℝ) (n : Mode) (t : ℝ) : SpinorEnd :=
  NormedSpace.exp (timeScaledOperator t (centralModeOperator m h n))

@[simp] theorem continuumModePropagator_zero_time (m : ℝ) (n : Mode) :
    continuumModePropagator m n 0 = 1 := by
  simp [continuumModePropagator]

@[simp] theorem centralModePropagator_zero_time (m h : ℝ) (n : Mode) :
    centralModePropagator m h n 0 = 1 := by
  simp [centralModePropagator]


/-- Time scaling is additive for a fixed bounded generator. -/
theorem timeScaledOperator_add (s t : ℝ) (A : SpinorEnd) :
    timeScaledOperator (s + t) A =
      timeScaledOperator s A + timeScaledOperator t A := by
  simp only [timeScaledOperator, Complex.ofReal_add]
  module

/-- Scalar multiples of one fixed generator commute. -/
theorem timeScaledOperator_commute (s t : ℝ) (A : SpinorEnd) :
    Commute (timeScaledOperator s A) (timeScaledOperator t A) := by
  rw [commute_iff_eq]
  ext ψ
  simp [timeScaledOperator, mul_left_comm, mul_assoc]

/-- The continuum mode exponential forms a one-parameter group. -/
theorem continuumModePropagator_add_time (m s t : ℝ) (n : Mode) :
    continuumModePropagator m n (s + t) =
      continuumModePropagator m n s * continuumModePropagator m n t := by
  rw [continuumModePropagator, timeScaledOperator_add]
  exact NormedSpace.exp_add_of_commute
    (timeScaledOperator_commute s t (continuumModeOperator m n))

/-- The lattice mode exponential forms a one-parameter group at every mesh. -/
theorem centralModePropagator_add_time (m h s t : ℝ) (n : Mode) :
    centralModePropagator m h n (s + t) =
      centralModePropagator m h n s * centralModePropagator m h n t := by
  rw [centralModePropagator, timeScaledOperator_add]
  exact NormedSpace.exp_add_of_commute
    (timeScaledOperator_commute s t (centralModeOperator m h n))

/-- Opposite continuum times compose to the identity. -/
theorem continuumModePropagator_neg_mul (m t : ℝ) (n : Mode) :
    continuumModePropagator m n (-t) * continuumModePropagator m n t = 1 := by
  rw [← continuumModePropagator_add_time]
  simp

/-- Opposite lattice times compose to the identity. -/
theorem centralModePropagator_neg_mul (m h t : ℝ) (n : Mode) :
    centralModePropagator m h n (-t) * centralModePropagator m h n t = 1 := by
  rw [← centralModePropagator_add_time]
  simp

/-- Mode propagators converge in operator norm for every fixed physical time. -/
theorem tendsto_centralModePropagator (m t : ℝ) (n : Mode) :
    Tendsto (fun h : ℝ => centralModePropagator m h n t)
      (𝓝[>] 0) (𝓝 (continuumModePropagator m n t)) := by
  exact (tendsto_timeScaledOperator m t n).exp

/-- The exponential map is locally Lipschitz, so the propagator residual inherits
quadratic mesh order from the generator residual. -/
theorem centralModePropagator_sub_isBigO (m t : ℝ) (n : Mode) :
    (fun h : ℝ => centralModePropagator m h n t -
      continuumModePropagator m n t)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  let A : SpinorEnd := timeScaledOperator t (continuumModeOperator m n)
  have hlocal : (fun X : SpinorEnd => NormedSpace.exp X - NormedSpace.exp A)
      =O[𝓝 A] (fun X : SpinorEnd => X - A) :=
    (NormedSpace.exp_analytic (𝕂 := ℂ) A).differentiableAt.isBigO_sub
  have hcomp := hlocal.comp_tendsto (tendsto_timeScaledOperator m t n)
  have htime : (fun h : ℝ => timeScaledOperator t (centralModeOperator m h n) - A)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
    simpa only [A] using timeScaledOperator_sub_isBigO m t n
  exact (hcomp.trans htime).congr_left (by
    intro h
    rfl)

/-- Evaluation of an endomorphism at a fixed four-spinor. -/
def evalAtCLM (ψ : Spinor) : SpinorEnd →L[ℂ] Spinor :=
  (ContinuousLinearMap.apply ℂ Spinor) ψ

@[simp] theorem evalAtCLM_apply (ψ : Spinor) (A : SpinorEnd) :
    evalAtCLM ψ A = A ψ := rfl

/-- One mode's propagated spinor residual has quadratic mesh order. -/
theorem modePropagatorAction_sub_isBigO (m t : ℝ) (n : Mode) (ψ : Spinor) :
    (fun h : ℝ => centralModePropagator m h n t ψ -
      continuumModePropagator m n t ψ)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have heval := (evalAtCLM ψ).isBigO_comp
    (fun h : ℝ => centralModePropagator m h n t -
      continuumModePropagator m n t) (𝓝[>] 0)
  exact (heval.trans (centralModePropagator_sub_isBigO m t n)).congr_left (by
    intro h
    rfl)

/-- One mode's propagated spinor converges for every fixed time. -/
theorem tendsto_centralModePropagator_apply (m t : ℝ) (n : Mode) (ψ : Spinor) :
    Tendsto (fun h : ℝ => centralModePropagator m h n t ψ)
      (𝓝[>] 0) (𝓝 (continuumModePropagator m n t ψ)) := by
  have herr := (modePropagatorAction_sub_isBigO m t n ψ).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumModePropagator m n t ψ)
      (𝓝[>] 0) (𝓝 (continuumModePropagator m n t ψ)) := tendsto_const_nhds
  simpa only [sub_add_cancel, zero_add] using herr.add hc

/-- Continuum time evolution of a fixed finite Fourier packet. -/
def continuumPropagatedPacketL2 (m t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) : TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n
    (spinorToHilbert (continuumModePropagator m n t (a n)))

/-- Central-difference time evolution of the same finite Fourier packet. -/
def centralPropagatedPacketL2 (m h t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) : TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n
    (spinorToHilbert (centralModePropagator m h n t (a n)))


@[simp] theorem continuumPropagatedPacketL2_zero_time (m : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    continuumPropagatedPacketL2 m 0 S a =
      fourierPacketL2 S (fun n => spinorToHilbert (a n)) := by
  simp [continuumPropagatedPacketL2, fourierPacketL2]

@[simp] theorem centralPropagatedPacketL2_zero_time (m h : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    centralPropagatedPacketL2 m h 0 S a =
      fourierPacketL2 S (fun n => spinorToHilbert (a n)) := by
  simp [centralPropagatedPacketL2, fourierPacketL2]

/-- Full finite-cutoff propagator residual. -/
def packetPropagatorResidualL2 (m t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) (h : ℝ) : TorusSpinorL2 :=
  centralPropagatedPacketL2 m h t S a - continuumPropagatedPacketL2 m t S a

/-- Exact decomposition of the finite-cutoff propagator residual by Fourier mode. -/
theorem packetPropagatorResidualL2_eq_sum (m h t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    packetPropagatorResidualL2 m t S a h =
      ∑ n ∈ S, modeEmbedIsometry n
        (spinorToHilbert
          (centralModePropagator m h n t (a n) -
           continuumModePropagator m n t (a n))) := by
  rw [packetPropagatorResidualL2, centralPropagatedPacketL2,
    continuumPropagatedPacketL2, ← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro n hn
  rw [map_sub, map_sub]

/-- Exact Parseval identity for the finite-cutoff propagator residual. -/
theorem packetPropagatorResidualL2_norm_sq (m h t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    ‖packetPropagatorResidualL2 m t S a h‖ ^ 2 =
      ∑ n ∈ S,
        ‖spinorToHilbert
          (centralModePropagator m h n t (a n) -
           continuumModePropagator m n t (a n))‖ ^ 2 := by
  rw [packetPropagatorResidualL2_eq_sum]
  exact modeEmbed_orthogonalFamily.norm_sum
    (fun n => spinorToHilbert
      (centralModePropagator m h n t (a n) -
       continuumModePropagator m n t (a n))) S

/-- One embedded Fourier-mode propagator residual has quadratic mesh order. -/
theorem modePropagatorResidualL2_isBigO (m t : ℝ) (n : Mode) (ψ : Spinor) :
    (fun h : ℝ => modeEmbedIsometry n
      (spinorToHilbert
        (centralModePropagator m h n t ψ -
         continuumModePropagator m n t ψ)))
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have hh := spinorToHilbert.isBigO_comp
    (fun h : ℝ => centralModePropagator m h n t ψ -
      continuumModePropagator m n t ψ) (𝓝[>] 0)
  have he := (modeEmbedIsometry n).toContinuousLinearMap.isBigO_comp
    (fun h : ℝ => spinorToHilbert
      (centralModePropagator m h n t ψ -
       continuumModePropagator m n t ψ)) (𝓝[>] 0)
  exact he.trans (hh.trans (modePropagatorAction_sub_isBigO m t n ψ))

/-- Every fixed finite Fourier cutoff has quadratic propagator error in torus `L²`. -/
theorem packetPropagatorResidualL2_isBigO (m t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    packetPropagatorResidualL2 m t S a =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) := by
  have hterms : ∀ n ∈ S,
      (fun h : ℝ => modeEmbedIsometry n
        (spinorToHilbert
          (centralModePropagator m h n t (a n) -
           continuumModePropagator m n t (a n))))
        =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
    intro n hn
    exact modePropagatorResidualL2_isBigO m t n (a n)
  have hsum := IsBigO.sum hterms
  exact hsum.congr_left (by
    intro h
    simpa only [Finset.sum_apply] using
      (packetPropagatorResidualL2_eq_sum m h t S a).symm)

/-- The norm of the finite-cutoff propagator residual is `O(h²)`. -/
theorem norm_packetPropagatorResidualL2_isBigO (m t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    (fun h : ℝ => ‖packetPropagatorResidualL2 m t S a h‖)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) :=
  (packetPropagatorResidualL2_isBigO m t S a).norm_left

/-- Strong torus-`L²` convergence of the finite-cutoff central-difference
propagator at every fixed physical time. -/
theorem tendsto_centralPropagatedPacketL2 (m t : ℝ) (S : Finset Mode)
    (a : Mode → Spinor) :
    Tendsto (fun h : ℝ => centralPropagatedPacketL2 m h t S a)
      (𝓝[>] 0) (𝓝 (continuumPropagatedPacketL2 m t S a)) := by
  have herr := (packetPropagatorResidualL2_isBigO m t S a).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumPropagatedPacketL2 m t S a)
      (𝓝[>] 0) (𝓝 (continuumPropagatedPacketL2 m t S a)) := tendsto_const_nhds
  simpa only [packetPropagatorResidualL2, sub_add_cancel, zero_add] using herr.add hc

end Relativistic3DFourierPropagator
end KomorebiPhysics
