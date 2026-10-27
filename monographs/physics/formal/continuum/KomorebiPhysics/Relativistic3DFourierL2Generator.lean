module

public import KomorebiPhysics.Relativistic3DFourierGenerator
public import Mathlib.Analysis.Fourier.AddCircleMulti
public import Mathlib.Analysis.InnerProductSpace.PiL2

@[expose] public section
noncomputable section
set_option autoImplicit false

/-!
# Torus `L²` consistency of the central-difference Dirac generator

This module upgrades the modewise and pointwise finite-packet estimates from
`Relativistic3DFourierGenerator` to the genuine Hilbert space of four-spinor
fields on the flat three-torus.  The multivariate Fourier basis gives an exact
orthogonal decomposition, so the finite-packet residual obeys Parseval exactly
and remains `O(h²)` in the torus `L²` norm.

The support is fixed and finite.  No self-adjointness, strong-resolvent
convergence, or propagator convergence is claimed here.
-/

open Filter Asymptotics
open scoped ENNReal BigOperators ComplexConjugate Topology
open MeasureTheory WithLp

namespace KomorebiPhysics
namespace Relativistic3DFourierL2Generator

local instance : MeasureSpace UnitAddCircle := ⟨AddCircle.haarAddCircle⟩
local instance : Measure.IsAddHaarMeasure (volume : Measure UnitAddCircle) :=
  inferInstanceAs (Measure.IsAddHaarMeasure AddCircle.haarAddCircle)
local instance : IsProbabilityMeasure (volume : Measure UnitAddCircle) :=
  inferInstanceAs (IsProbabilityMeasure AddCircle.haarAddCircle)

abbrev FourierMode := Relativistic3DFourierGenerator.Mode
abbrev AlgebraicSpinor := Relativistic3DFourierGenerator.Spinor
abbrev ScalarTorusL2 := Lp ℂ 2 (volume : Measure (UnitAddTorus (Fin 3)))
abbrev HilbertSpinor := EuclideanSpace ℂ (Fin 4)
abbrev TorusSpinorL2 := PiLp 2 (fun _ : Fin 4 => ScalarTorusL2)

/-- Identify the algebraic four-spinor with its Euclidean Hilbert realization. -/
def spinorToHilbert : AlgebraicSpinor →L[ℂ] HilbertSpinor :=
  (PiLp.continuousLinearEquiv 2 ℂ (fun _ : Fin 4 => ℂ)).symm.toContinuousLinearMap

@[simp] theorem spinorToHilbert_apply (ψ : AlgebraicSpinor) (j : Fin 4) :
    spinorToHilbert ψ j = ψ j := rfl

/-- Embed one four-spinor amplitude into the corresponding torus Fourier mode. -/
def modeEmbed (n : FourierMode) (ψ : HilbertSpinor) : TorusSpinorL2 :=
  toLp 2 (fun j => (ψ j) • UnitAddTorus.mFourierLp 2 n)

@[simp] theorem modeEmbed_apply (n : FourierMode) (ψ : HilbertSpinor) (j : Fin 4) :
    modeEmbed n ψ j = (ψ j) • UnitAddTorus.mFourierLp 2 n := rfl

theorem modeEmbed_add (n : FourierMode) (ψ φ : HilbertSpinor) :
    modeEmbed n (ψ + φ) = modeEmbed n ψ + modeEmbed n φ := by
  apply PiLp.ext
  intro j
  simp [modeEmbed_apply, add_smul]

theorem modeEmbed_smul (n : FourierMode) (c : ℂ) (ψ : HilbertSpinor) :
    modeEmbed n (c • ψ) = c • modeEmbed n ψ := by
  apply PiLp.ext
  intro j
  simp [modeEmbed_apply, mul_smul]

/-- Linear embedding of one mode amplitude. -/
def modeEmbedLinear (n : FourierMode) : HilbertSpinor →ₗ[ℂ] TorusSpinorL2 where
  toFun := modeEmbed n
  map_add' := modeEmbed_add n
  map_smul' := modeEmbed_smul n

/-- The torus Fourier mode embedding preserves the four-spinor norm exactly. -/
theorem norm_modeEmbed (n : FourierMode) (ψ : HilbertSpinor) :
    ‖modeEmbed n ψ‖ = ‖ψ‖ := by
  apply (sq_eq_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  rw [PiLp.norm_sq_eq_of_L2, PiLp.norm_sq_eq_of_L2]
  apply Finset.sum_congr rfl
  intro j hj
  rw [modeEmbed_apply, norm_smul,
    UnitAddTorus.orthonormal_mFourier.norm_eq_one]
  simp

/-- Linear isometry embedding a four-spinor into one torus Fourier mode. -/
def modeEmbedIsometry (n : FourierMode) : HilbertSpinor →ₗᵢ[ℂ] TorusSpinorL2 where
  toLinearMap := modeEmbedLinear n
  norm_map' := norm_modeEmbed n

@[simp] theorem modeEmbedIsometry_apply (n : FourierMode) (ψ : HilbertSpinor) :
    modeEmbedIsometry n ψ = modeEmbed n ψ := rfl

/-- Exact inner product of two embedded spinor Fourier modes. -/
theorem inner_modeEmbed (m n : FourierMode) (ψ φ : HilbertSpinor) :
    inner ℂ (modeEmbed m ψ) (modeEmbed n φ) =
      if m = n then inner ℂ ψ φ else 0 := by
  rw [PiLp.inner_apply, PiLp.inner_apply]
  simp only [modeEmbed_apply, inner_smul_left, inner_smul_right]
  rw [show inner ℂ (UnitAddTorus.mFourierLp 2 m)
      (UnitAddTorus.mFourierLp 2 n) = if m = n then 1 else 0 by
    exact (orthonormal_iff_ite.mp UnitAddTorus.orthonormal_mFourier) m n]
  split_ifs with h
  · subst n
    simp
  · simp

/-- Distinct mode embeddings form an orthogonal family of four-spinor subspaces. -/
theorem modeEmbed_orthogonalFamily :
    OrthogonalFamily ℂ (fun _ : FourierMode => HilbertSpinor) modeEmbedIsometry := by
  intro m n hmn ψ φ
  rw [modeEmbedIsometry_apply, modeEmbedIsometry_apply, inner_modeEmbed]
  simp [hmn]

/-- A finite four-spinor Fourier packet in torus `L²`. -/
def fourierPacketL2 (S : Finset FourierMode) (a : FourierMode → HilbertSpinor) :
    TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n (a n)

/-- Exact Parseval identity for a finite four-spinor Fourier packet. -/
theorem fourierPacketL2_norm_sq (S : Finset FourierMode)
    (a : FourierMode → HilbertSpinor) :
    ‖fourierPacketL2 S a‖ ^ 2 = ∑ n ∈ S, ‖a n‖ ^ 2 := by
  exact modeEmbed_orthogonalFamily.norm_sum a S

/-- Continuum Dirac generator applied modewise to a finite torus packet. -/
def continuumPacketL2 (m : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) : TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n
    (spinorToHilbert (Relativistic3DFourierGenerator.continuumModeAction m n (a n)))

/-- Central-difference Dirac generator applied modewise to a finite torus packet. -/
def centralPacketL2 (m h : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) : TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n
    (spinorToHilbert (Relativistic3DFourierGenerator.centralModeAction m h n (a n)))

/-- Embedded `L²` residual on one fixed Fourier mode. -/
def modeResidualL2 (m : ℝ) (n : FourierMode)
    (ψ : AlgebraicSpinor) (h : ℝ) : TorusSpinorL2 :=
  modeEmbedIsometry n
    (spinorToHilbert
      (Relativistic3DFourierGenerator.centralModeAction m h n ψ -
       Relativistic3DFourierGenerator.continuumModeAction m n ψ))

/-- Full finite-packet generator residual in torus `L²`. -/
def packetResidualL2 (m : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) (h : ℝ) : TorusSpinorL2 :=
  centralPacketL2 m h S a - continuumPacketL2 m S a

/-- Exact decomposition of the packet residual into orthogonal mode residuals. -/
theorem packetResidualL2_eq_sum (m h : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) :
    packetResidualL2 m S a h =
      ∑ n ∈ S, modeResidualL2 m n (a n) h := by
  rw [packetResidualL2, centralPacketL2, continuumPacketL2]
  rw [← Finset.sum_sub_distrib]
  apply Finset.sum_congr rfl
  intro n hn
  simp only [modeResidualL2]
  rw [map_sub, map_sub]

/-- Exact Parseval identity for the finite-packet generator residual. -/
theorem packetResidualL2_norm_sq (m h : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) :
    ‖packetResidualL2 m S a h‖ ^ 2 =
      ∑ n ∈ S,
        ‖spinorToHilbert
          (Relativistic3DFourierGenerator.centralModeAction m h n (a n) -
           Relativistic3DFourierGenerator.continuumModeAction m n (a n))‖ ^ 2 := by
  rw [packetResidualL2_eq_sum]
  exact modeEmbed_orthogonalFamily.norm_sum
    (fun n => spinorToHilbert
      (Relativistic3DFourierGenerator.centralModeAction m h n (a n) -
       Relativistic3DFourierGenerator.continuumModeAction m n (a n))) S

/-- The algebraic mode residual remains `O(h²)` in the four-spinor Hilbert norm. -/
theorem hilbertModeResidual_isBigO (m : ℝ) (n : FourierMode)
    (ψ : AlgebraicSpinor) :
    (fun h : ℝ => spinorToHilbert
      (Relativistic3DFourierGenerator.centralModeAction m h n ψ -
       Relativistic3DFourierGenerator.continuumModeAction m n ψ))
      =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have hc := spinorToHilbert.isBigO_comp
    (fun h : ℝ =>
      Relativistic3DFourierGenerator.centralModeAction m h n ψ -
      Relativistic3DFourierGenerator.continuumModeAction m n ψ)
    (𝓝[>] 0)
  exact hc.trans
    (Relativistic3DFourierGenerator.centralModeAction_sub_continuum_isBigO m n ψ)

/-- One embedded torus mode has quadratic generator residual in `L²`. -/
theorem modeResidualL2_isBigO (m : ℝ) (n : FourierMode)
    (ψ : AlgebraicSpinor) :
    modeResidualL2 m n ψ =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have he := (modeEmbedIsometry n).toContinuousLinearMap.isBigO_comp
    (fun h : ℝ => spinorToHilbert
      (Relativistic3DFourierGenerator.centralModeAction m h n ψ -
       Relativistic3DFourierGenerator.continuumModeAction m n ψ))
    (𝓝[>] 0)
  exact he.trans (hilbertModeResidual_isBigO m n ψ)

/-- Every fixed finite Fourier packet has quadratic generator residual in torus `L²`. -/
theorem packetResidualL2_isBigO (m : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) :
    packetResidualL2 m S a =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
  have hterms : ∀ n ∈ S,
      modeResidualL2 m n (a n) =O[𝓝[>] 0] (fun h : ℝ => h ^ 2) := by
    intro n hn
    exact modeResidualL2_isBigO m n (a n)
  have hsum := IsBigO.sum hterms
  exact hsum.congr_left (by
    intro h
    simpa only [Finset.sum_apply] using
      (packetResidualL2_eq_sum m h S a).symm)

/-- The `L²` norm of every fixed finite-packet residual is `O(h²)`. -/
theorem norm_packetResidualL2_isBigO (m : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) :
    (fun h : ℝ => ‖packetResidualL2 m S a h‖) =O[𝓝[>] 0]
      (fun h : ℝ => h ^ 2) :=
  (packetResidualL2_isBigO m S a).norm_left

/-- Central-difference generator action converges in torus `L²` on every fixed
finite four-spinor Fourier packet. -/
theorem tendsto_centralPacketL2 (m : ℝ) (S : Finset FourierMode)
    (a : FourierMode → AlgebraicSpinor) :
    Tendsto (fun h : ℝ => centralPacketL2 m h S a)
      (𝓝[>] 0) (𝓝 (continuumPacketL2 m S a)) := by
  have herr := (packetResidualL2_isBigO m S a).trans_tendsto (by
    have hid : Tendsto (fun h : ℝ => h) (𝓝[>] 0) (𝓝 0) :=
      tendsto_id.mono_left nhdsWithin_le_nhds
    simpa using hid.pow 2)
  have hc : Tendsto (fun _ : ℝ => continuumPacketL2 m S a)
      (𝓝[>] 0) (𝓝 (continuumPacketL2 m S a)) := tendsto_const_nhds
  simpa only [packetResidualL2, sub_add_cancel, zero_add] using herr.add hc

end Relativistic3DFourierL2Generator
end KomorebiPhysics
