module

public import KomorebiPhysics.Relativistic1DContinuumLimit
public import KomorebiPhysics.Relativistic3DCliffordTransportU1
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.Module
public import Mathlib.Tactic.Ring

@[expose] public section
noncomputable section
set_option autoImplicit false

open Filter Asymptotics
open scoped Topology BigOperators

namespace KomorebiPhysics
namespace Relativistic3DFourierGenerator

open Relativistic3DCliffordTransportU1

abbrev Spinor := Relativistic3DCliffordTransportU1.Spinor
abbrev sinQuot := Relativistic1DContinuumLimit.sinQuot

/-- Continuous linear map sending a scalar to its multiple of a fixed spinor. -/
noncomputable def smulVectorCLM (v : Spinor) : ℂ →L[ℂ] Spinor :=
  ContinuousLinearMap.smulRight (ContinuousLinearMap.id ℂ ℂ) v

@[simp] theorem smulVectorCLM_apply (v : Spinor) (z : ℂ) :
    smulVectorCLM v z = z • v := by
  rfl

/-- Multiplying the removable sine-quotient error by a fixed spinor preserves
its quadratic order. -/
theorem sinQuot_residual_smul_isBigO (k : ℝ) (v : Spinor) :
    (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ) • v) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) := by
  have hr := Relativistic1DContinuumLimit.sinQuot_expansion_isBigO k
  have hc0 := Complex.ofRealCLM.isBigO_comp
      (fun h : ℝ => sinQuot k h - k) (𝓝[>] 0)
  have hc : (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) := hc0.trans hr
  have hv0 := (smulVectorCLM v).isBigO_comp
      (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) (𝓝[>] 0)
  simpa only [smulVectorCLM_apply] using hv0.trans hc



/-- Translation eigenphase of a one-dimensional Fourier mode. -/
def modePhase (k h : ℝ) : ℂ :=
  Complex.exp (((k * h : ℝ) : ℂ) * Complex.I)

/-- Central finite-difference multiplier on a Fourier mode, continuously filled
at zero mesh. -/
def centralDifferenceMultiplier (k h : ℝ) : ℂ :=
  if h = 0 then Complex.I * (k : ℂ)
  else (modePhase k h - modePhase k (-h)) / ((2 * h : ℝ) : ℂ)

/-- Exact diagonalization of the central finite difference on a Fourier mode. -/
theorem centralDifferenceMultiplier_eq (k h : ℝ) :
    centralDifferenceMultiplier k h =
      Complex.I * (sinQuot k h : ℂ) := by
  by_cases hh : h = 0
  · subst h
    simp [centralDifferenceMultiplier]
  · simp only [centralDifferenceMultiplier, hh, modePhase]
    rw [Complex.exp_mul_I, Complex.exp_mul_I]
    rw [← Complex.ofReal_cos, ← Complex.ofReal_sin,
      ← Complex.ofReal_cos, ← Complex.ofReal_sin]
    simp only [sinQuot, Relativistic1DContinuumLimit.sinQuot, hh]
    field_simp
    simp [Real.cos_neg, Real.sin_neg]
    ring




@[simp] theorem norm_modePhase (k h : ℝ) : ‖modePhase k h‖ = 1 := by
  simp [modePhase, Complex.norm_exp]

/-- The `-i` prefactor in the Dirac Hamiltonian turns the central-derivative
multiplier into the real lattice momentum. -/
def diracKineticMultiplier (k h : ℝ) : ℂ :=
  -Complex.I * centralDifferenceMultiplier k h

@[simp] theorem diracKineticMultiplier_eq (k h : ℝ) :
    diracKineticMultiplier k h = (sinQuot k h : ℂ) := by
  rw [diracKineticMultiplier, centralDifferenceMultiplier_eq]
  ring_nf
  simp [Complex.I_sq]

/-- The central-derivative multiplier differs quadratically from `i k`. -/
theorem centralDifferenceMultiplier_sub_isBigO (k : ℝ) :
    (fun h : ℝ => centralDifferenceMultiplier k h - Complex.I * (k : ℂ))
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have hs : (fun h : ℝ => Complex.I * ((sinQuot k h - k : ℝ) : ℂ))
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
    have hc0 := Complex.ofRealCLM.isBigO_comp
      (fun h : ℝ => sinQuot k h - k) (𝓝[>] 0)
    have hc : (fun h : ℝ => ((sinQuot k h - k : ℝ) : ℂ)) =O[𝓝[>] 0]
        (fun h : ℝ => h ^ 2) :=
      hc0.trans (Relativistic1DContinuumLimit.sinQuot_expansion_isBigO k)
    exact hc.const_mul_left Complex.I
  exact hs.congr_left (by
    intro h
    rw [centralDifferenceMultiplier_eq]
    push_cast
    ring)

/-- The central-difference derivative multiplier converges to `i k`. -/
theorem tendsto_centralDifferenceMultiplier (k : ℝ) :
    Tendsto (centralDifferenceMultiplier k) (𝓝[>] 0)
      (𝓝 (Complex.I * (k : ℂ))) := by
  have herr := (centralDifferenceMultiplier_sub_isBigO k).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => Complex.I * (k : ℂ))
      (𝓝[>] 0) (𝓝 (Complex.I * (k : ℂ))) := tendsto_const_nhds
  simpa only [sub_add_cancel, zero_add] using herr.add hc


/-- Continuum free Dirac symbol on one momentum mode. -/
def continuumDiracSymbol (m kx ky kz : ℝ) (ψ : Spinor) : Spinor :=
  (kx : ℂ) • alphaX ψ +
    (ky : ℂ) • alphaY ψ +
    (kz : ℂ) • alphaZ ψ +
    (m : ℂ) • beta ψ

/-- Central-difference free Dirac symbol, continuously filled at zero mesh. -/
def centralDiracSymbol (m kx ky kz h : ℝ) (ψ : Spinor) : Spinor :=
  (sinQuot kx h : ℂ) • alphaX ψ +
    (sinQuot ky h : ℂ) • alphaY ψ +
    (sinQuot kz h : ℂ) • alphaZ ψ +
    (m : ℂ) • beta ψ

@[simp] theorem centralDiracSymbol_zero
    (m kx ky kz : ℝ) (ψ : Spinor) :
    centralDiracSymbol m kx ky kz 0 ψ =
      continuumDiracSymbol m kx ky kz ψ := by
  simp [centralDiracSymbol, continuumDiracSymbol]

/-- Exact residual decomposition: the mass term cancels and only the three
central-difference multipliers remain. -/
theorem centralDiracSymbol_sub_continuum
    (m kx ky kz h : ℝ) (ψ : Spinor) :
    centralDiracSymbol m kx ky kz h ψ -
        continuumDiracSymbol m kx ky kz ψ =
      ((sinQuot kx h - kx : ℝ) : ℂ) • alphaX ψ +
      ((sinQuot ky h - ky : ℝ) : ℂ) • alphaY ψ +
      ((sinQuot kz h - kz : ℝ) : ℂ) • alphaZ ψ := by
  simp only [centralDiracSymbol, continuumDiracSymbol, Complex.ofReal_sub]
  module

/-- The full four-spinor central-difference Dirac symbol differs from the
continuum symbol by `O(h²)` on every fixed Fourier mode. -/
theorem centralDiracSymbol_sub_continuum_isBigO
    (m kx ky kz : ℝ) (ψ : Spinor) :
    (fun h : ℝ => centralDiracSymbol m kx ky kz h ψ -
      continuumDiracSymbol m kx ky kz ψ) =O[𝓝[>] 0]
        (fun h : ℝ => h ^ 2) := by
  have hx := sinQuot_residual_smul_isBigO kx (alphaX ψ)
  have hy := sinQuot_residual_smul_isBigO ky (alphaY ψ)
  have hz := sinQuot_residual_smul_isBigO kz (alphaZ ψ)
  exact ((hx.add hy).add hz).congr_left (by
    intro h
    exact centralDiracSymbol_sub_continuum m kx ky kz h ψ |>.symm)

/-- Modewise generator consistency on the positive-mesh side. -/
theorem tendsto_centralDiracSymbol
    (m kx ky kz : ℝ) (ψ : Spinor) :
    Tendsto (fun h : ℝ => centralDiracSymbol m kx ky kz h ψ)
      (𝓝[>] 0) (𝓝 (continuumDiracSymbol m kx ky kz ψ)) := by
  have herr := (centralDiracSymbol_sub_continuum_isBigO m kx ky kz ψ).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumDiracSymbol m kx ky kz ψ)
      (𝓝[>] 0) (𝓝 (continuumDiracSymbol m kx ky kz ψ)) := tendsto_const_nhds
  have hsum := herr.add hc
  simpa only [sub_add_cancel, zero_add] using hsum



/-- Integer momentum label for a three-torus Fourier mode. -/
abbrev Mode := Fin 3 → ℤ

/-- Cartesian point used to evaluate a periodic Fourier packet. -/
abbrev TorusPoint := Fin 3 → ℝ

/-- Physical wave number `2π nᵢ` carried by one integer Fourier label. -/
def modeMomentum (n : Mode) (i : Fin 3) : ℝ :=
  2 * Real.pi * (n i : ℝ)

/-- Scalar plane-wave factor associated with a three-torus mode. -/
def torusPlaneWave (n : Mode) (x : TorusPoint) : ℂ :=
  Complex.exp (Complex.I * ((∑ i : Fin 3, modeMomentum n i * x i : ℝ) : ℂ))

@[simp] theorem norm_torusPlaneWave (n : Mode) (x : TorusPoint) :
    ‖torusPlaneWave n x‖ = 1 := by
  simp [torusPlaneWave, Complex.norm_exp]

/-- Continuum Dirac-symbol action on one integer torus mode. -/
def continuumModeAction (m : ℝ) (n : Mode) (ψ : Spinor) : Spinor :=
  continuumDiracSymbol m (modeMomentum n 0) (modeMomentum n 1)
    (modeMomentum n 2) ψ

/-- Central-difference Dirac-symbol action on one integer torus mode. -/
def centralModeAction (m h : ℝ) (n : Mode) (ψ : Spinor) : Spinor :=
  centralDiracSymbol m (modeMomentum n 0) (modeMomentum n 1)
    (modeMomentum n 2) h ψ

/-- Every fixed torus mode has quadratic central-difference generator error. -/
theorem centralModeAction_sub_continuum_isBigO
    (m : ℝ) (n : Mode) (ψ : Spinor) :
    (fun h : ℝ => centralModeAction m h n ψ - continuumModeAction m n ψ)
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  exact centralDiracSymbol_sub_continuum_isBigO m
    (modeMomentum n 0) (modeMomentum n 1) (modeMomentum n 2) ψ

/-- Modewise central-difference generator convergence. -/
theorem tendsto_centralModeAction
    (m : ℝ) (n : Mode) (ψ : Spinor) :
    Tendsto (fun h : ℝ => centralModeAction m h n ψ)
      (𝓝[>] 0) (𝓝 (continuumModeAction m n ψ)) := by
  exact tendsto_centralDiracSymbol m
    (modeMomentum n 0) (modeMomentum n 1) (modeMomentum n 2) ψ

/-- A finite trigonometric packet after applying the continuum Dirac symbol to
its mode amplitudes. -/
def continuumFourierPacketAction
    (m : ℝ) (S : Finset Mode) (a : Mode → Spinor) (x : TorusPoint) : Spinor :=
  ∑ n ∈ S, torusPlaneWave n x • continuumModeAction m n (a n)

/-- The corresponding finite packet after applying the central-difference
Dirac symbol at mesh `h`. -/
def centralFourierPacketAction
    (m h : ℝ) (S : Finset Mode) (a : Mode → Spinor) (x : TorusPoint) : Spinor :=
  ∑ n ∈ S, torusPlaneWave n x • centralModeAction m h n (a n)

/-- Exact finite-packet residual decomposition into modewise residuals. -/
theorem centralFourierPacketAction_sub_continuum
    (m h : ℝ) (S : Finset Mode) (a : Mode → Spinor) (x : TorusPoint) :
    centralFourierPacketAction m h S a x - continuumFourierPacketAction m S a x =
      ∑ n ∈ S, torusPlaneWave n x •
        (centralModeAction m h n (a n) - continuumModeAction m n (a n)) := by
  simp only [centralFourierPacketAction, continuumFourierPacketAction,
    Finset.sum_sub_distrib, smul_sub]

/-- Every fixed finite Fourier packet has quadratic pointwise generator error. -/
theorem centralFourierPacketAction_sub_continuum_isBigO
    (m : ℝ) (S : Finset Mode) (a : Mode → Spinor) (x : TorusPoint) :
    (fun h : ℝ => centralFourierPacketAction m h S a x -
      continuumFourierPacketAction m S a x) =O[𝓝[>] 0]
        (fun h : ℝ => h ^ 2) := by
  have hterms : ∀ n ∈ S,
      (fun h : ℝ => torusPlaneWave n x •
        (centralModeAction m h n (a n) - continuumModeAction m n (a n)))
        =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
    intro n hn
    exact (centralModeAction_sub_continuum_isBigO m n (a n)).const_smul_left
      (torusPlaneWave n x)
  have hsum := IsBigO.sum hterms
  exact hsum.congr_left (by
    intro h
    simpa only [Finset.sum_apply] using
      (centralFourierPacketAction_sub_continuum m h S a x).symm)

/-- Pointwise generator consistency on every finite Fourier packet. -/
theorem tendsto_centralFourierPacketAction
    (m : ℝ) (S : Finset Mode) (a : Mode → Spinor) (x : TorusPoint) :
    Tendsto (fun h : ℝ => centralFourierPacketAction m h S a x)
      (𝓝[>] 0) (𝓝 (continuumFourierPacketAction m S a x)) := by
  have herr := (centralFourierPacketAction_sub_continuum_isBigO m S a x).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumFourierPacketAction m S a x)
      (𝓝[>] 0) (𝓝 (continuumFourierPacketAction m S a x)) := tendsto_const_nhds
  have hsum := herr.add hc
  simpa only [sub_add_cancel, zero_add] using hsum


/-- Squared continuum momentum and mass. -/
def symbolEnergySq (m px py pz : ℝ) : ℝ :=
  m ^ 2 + px ^ 2 + py ^ 2 + pz ^ 2

/-- Exact Clifford mass-shell identity for arbitrary real symbol coefficients. -/
theorem continuumDiracSymbol_sq
    (m px py pz : ℝ) (ψ : Spinor) :
    continuumDiracSymbol m px py pz
        (continuumDiracSymbol m px py pz ψ) =
      (symbolEnergySq m px py pz : ℂ) • ψ := by
  ext j
  fin_cases j <;>
    simp [continuumDiracSymbol, symbolEnergySq, alphaX, alphaY, alphaZ, beta] <;>
    ring_nf
  all_goals simp [Complex.I_sq]

/-- Exact lattice mass shell obtained by substituting the central-difference
multipliers into the Clifford identity. -/
theorem centralDiracSymbol_sq
    (m kx ky kz h : ℝ) (ψ : Spinor) :
    centralDiracSymbol m kx ky kz h
        (centralDiracSymbol m kx ky kz h ψ) =
      (symbolEnergySq m (sinQuot kx h) (sinQuot ky h) (sinQuot kz h) : ℂ) • ψ := by
  change continuumDiracSymbol m (sinQuot kx h) (sinQuot ky h) (sinQuot kz h)
      (continuumDiracSymbol m (sinQuot kx h) (sinQuot ky h) (sinQuot kz h) ψ) = _
  exact continuumDiracSymbol_sq m (sinQuot kx h) (sinQuot ky h) (sinQuot kz h) ψ

end Relativistic3DFourierGenerator
end KomorebiPhysics
