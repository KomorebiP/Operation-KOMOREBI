import KomorebiPhysics.Relativistic3DFourierPropagator
import KomorebiPhysics.Relativistic3DCliffordHilbertRefinement
import Mathlib.Analysis.InnerProductSpace.Adjoint
import Mathlib.Analysis.CStarAlgebra.Basic

/-!
# Hilbert stability of the finite-cutoff Dirac propagators

This module transports the explicit four-component Clifford representation to the
Euclidean four-spinor Hilbert space, proves self-adjointness of both the continuum
and central-difference Fourier-mode Hamiltonians, and deduces exact unitarity of
their bounded exponentials.  It also proves exact norm conservation for fixed
finite Fourier packets.

The results close the stability gap left by the fixed-time propagator-consistency
theorems.  They do not assert compact-time uniform convergence or removal of the
finite Fourier cutoff.
-/

noncomputable section
set_option autoImplicit false

open scoped ComplexConjugate

namespace KomorebiPhysics
namespace Relativistic3DFourierHilbertStability

open Relativistic3DCliffordTransportU1
open Relativistic3DCliffordHilbertRefinement
open Relativistic3DFourierL2Generator

abbrev AlgebraicSpinor := Relativistic3DFourierL2Generator.AlgebraicSpinor
abbrev HilbertSpinor := Relativistic3DFourierL2Generator.HilbertSpinor

/-- Forget the Hilbert wrapper, retaining the four coordinates. -/
def hilbertToSpinor (ψ : HilbertSpinor) : AlgebraicSpinor := fun j => ψ j

@[simp] theorem hilbertToSpinor_apply (ψ : HilbertSpinor) (j : Fin 4) :
    hilbertToSpinor ψ j = ψ j := rfl

@[simp] theorem spinorToHilbert_hilbertToSpinor (ψ : HilbertSpinor) :
    spinorToHilbert (hilbertToSpinor ψ) = ψ := by
  apply PiLp.ext
  intro j
  rfl

@[simp] theorem hilbertToSpinor_spinorToHilbert (ψ : AlgebraicSpinor) :
    hilbertToSpinor (spinorToHilbert ψ) = ψ := by
  rfl

@[simp] theorem hilbertToSpinor_add (ψ φ : HilbertSpinor) :
    hilbertToSpinor (ψ + φ) = hilbertToSpinor ψ + hilbertToSpinor φ := by
  rfl

@[simp] theorem hilbertToSpinor_smul (c : ℂ) (ψ : HilbertSpinor) :
    hilbertToSpinor (c • ψ) = c • hilbertToSpinor ψ := by
  rfl

/-- The Hilbert inner product agrees with the explicit four-spinor pairing. -/
theorem inner_spinorToHilbert (ψ φ : AlgebraicSpinor) :
    inner ℂ (spinorToHilbert ψ) (spinorToHilbert φ) = ip ψ φ := by
  rw [PiLp.inner_apply]
  simp [ip, mul_comm]

/-- Transport a Hermitian Clifford involution to the Euclidean four-spinor Hilbert space. -/
def hilbertCliffordLinear (H : HermitianClifford) : HilbertSpinor →ₗ[ℂ] HilbertSpinor where
  toFun ψ := spinorToHilbert (H.toClifford.act (hilbertToSpinor ψ))
  map_add' := by
    intro ψ φ
    rw [hilbertToSpinor_add, H.toClifford.map_add]
    rfl
  map_smul' := by
    intro c ψ
    rw [hilbertToSpinor_smul, H.toClifford.map_smul]
    rfl

/-- Bounded Hilbert-space Clifford operator. -/
def hilbertCliffordOperator (H : HermitianClifford) : HilbertSpinor →L[ℂ] HilbertSpinor :=
  LinearMap.toContinuousLinearMap (hilbertCliffordLinear H)

@[simp] theorem hilbertCliffordOperator_apply (H : HermitianClifford) (ψ : HilbertSpinor) :
    hilbertCliffordOperator H ψ =
      spinorToHilbert (H.toClifford.act (hilbertToSpinor ψ)) := rfl

/-- The transported Clifford operator is symmetric. -/
theorem hilbertCliffordOperator_symmetric (H : HermitianClifford) :
    (hilbertCliffordOperator H : HilbertSpinor →ₗ[ℂ] HilbertSpinor).IsSymmetric := by
  intro ψ φ
  change inner ℂ
      (spinorToHilbert (H.toClifford.act (hilbertToSpinor ψ))) φ =
    inner ℂ ψ
      (spinorToHilbert (H.toClifford.act (hilbertToSpinor φ)))
  rw [← spinorToHilbert_hilbertToSpinor φ,
    inner_spinorToHilbert,
    ← spinorToHilbert_hilbertToSpinor ψ, inner_spinorToHilbert]
  exact H.hermitian _ _

/-- The transported Clifford operator is self-adjoint. -/
theorem hilbertCliffordOperator_selfAdjoint (H : HermitianClifford) :
    IsSelfAdjoint (hilbertCliffordOperator H) :=
  (hilbertCliffordOperator_symmetric H).isSelfAdjoint


abbrev HilbertSpinorEnd := HilbertSpinor →L[ℂ] HilbertSpinor

local instance : NormedAlgebra ℚ HilbertSpinorEnd :=
  NormedAlgebra.restrictScalars ℚ ℂ HilbertSpinorEnd
abbrev Mode := Relativistic3DFourierGenerator.Mode

abbrev alphaXHilbertOperator : HilbertSpinorEnd :=
  hilbertCliffordOperator hermitianX
abbrev alphaYHilbertOperator : HilbertSpinorEnd :=
  hilbertCliffordOperator hermitianY
abbrev alphaZHilbertOperator : HilbertSpinorEnd :=
  hilbertCliffordOperator hermitianZ
abbrev betaHilbertOperator : HilbertSpinorEnd :=
  hilbertCliffordOperator hermitianBeta

/-- Real complex scalars are self-adjoint. -/
theorem ofReal_selfAdjoint (r : ℝ) : IsSelfAdjoint (r : ℂ) := by
  simp [isSelfAdjoint_iff]

/-- Continuum mode Hamiltonian on the Euclidean four-spinor Hilbert space. -/
def continuumHilbertModeOperator (m : ℝ) (n : Mode) : HilbertSpinorEnd :=
  ((Relativistic3DFourierGenerator.modeMomentum n 0 : ℝ) : ℂ) • alphaXHilbertOperator +
  ((Relativistic3DFourierGenerator.modeMomentum n 1 : ℝ) : ℂ) • alphaYHilbertOperator +
  ((Relativistic3DFourierGenerator.modeMomentum n 2 : ℝ) : ℂ) • alphaZHilbertOperator +
  (m : ℂ) • betaHilbertOperator

/-- Central-difference mode Hamiltonian on the Euclidean four-spinor Hilbert space. -/
def centralHilbertModeOperator (m h : ℝ) (n : Mode) : HilbertSpinorEnd :=
  ((Relativistic3DFourierGenerator.sinQuot
      (Relativistic3DFourierGenerator.modeMomentum n 0) h : ℝ) : ℂ) • alphaXHilbertOperator +
  ((Relativistic3DFourierGenerator.sinQuot
      (Relativistic3DFourierGenerator.modeMomentum n 1) h : ℝ) : ℂ) • alphaYHilbertOperator +
  ((Relativistic3DFourierGenerator.sinQuot
      (Relativistic3DFourierGenerator.modeMomentum n 2) h : ℝ) : ℂ) • alphaZHilbertOperator +
  (m : ℂ) • betaHilbertOperator

/-- Real scalar multiples of transported Hermitian Clifford operators are symmetric. -/
theorem real_smul_hilbertClifford_symmetric (r : ℝ) (H : HermitianClifford) :
    (((r : ℂ) • hilbertCliffordOperator H : HilbertSpinorEnd) :
      HilbertSpinor →ₗ[ℂ] HilbertSpinor).IsSymmetric := by
  change (((r : ℂ) • (hilbertCliffordOperator H :
    HilbertSpinor →ₗ[ℂ] HilbertSpinor))).IsSymmetric
  exact (hilbertCliffordOperator_symmetric H).smul (by simp)

/-- The continuum Fourier-mode Hamiltonian is symmetric. -/
theorem continuumHilbertModeOperator_symmetric (m : ℝ) (n : Mode) :
    (continuumHilbertModeOperator m n :
      HilbertSpinor →ₗ[ℂ] HilbertSpinor).IsSymmetric := by
  unfold continuumHilbertModeOperator
  exact (((real_smul_hilbertClifford_symmetric _ hermitianX).add
    (real_smul_hilbertClifford_symmetric _ hermitianY)).add
    (real_smul_hilbertClifford_symmetric _ hermitianZ)).add
    (real_smul_hilbertClifford_symmetric _ hermitianBeta)

/-- The continuum Fourier-mode Hamiltonian is self-adjoint. -/
theorem continuumHilbertModeOperator_selfAdjoint (m : ℝ) (n : Mode) :
    IsSelfAdjoint (continuumHilbertModeOperator m n) :=
  (continuumHilbertModeOperator_symmetric m n).isSelfAdjoint

/-- The central-difference Fourier-mode Hamiltonian is symmetric at every mesh. -/
theorem centralHilbertModeOperator_symmetric (m h : ℝ) (n : Mode) :
    (centralHilbertModeOperator m h n :
      HilbertSpinor →ₗ[ℂ] HilbertSpinor).IsSymmetric := by
  unfold centralHilbertModeOperator
  exact (((real_smul_hilbertClifford_symmetric _ hermitianX).add
    (real_smul_hilbertClifford_symmetric _ hermitianY)).add
    (real_smul_hilbertClifford_symmetric _ hermitianZ)).add
    (real_smul_hilbertClifford_symmetric _ hermitianBeta)

/-- The central-difference Fourier-mode Hamiltonian is self-adjoint at every mesh. -/
theorem centralHilbertModeOperator_selfAdjoint (m h : ℝ) (n : Mode) :
    IsSelfAdjoint (centralHilbertModeOperator m h n) :=
  (centralHilbertModeOperator_symmetric m h n).isSelfAdjoint

/-- The Schrödinger scalar `-i t` is skew-adjoint. -/
theorem schrodingerScalar_mem_skewAdjoint (t : ℝ) :
    (-(Complex.I * (t : ℂ))) ∈ skewAdjoint ℂ := by
  rw [skewAdjoint.mem_iff]
  simp

/-- Time scaling of a Hilbert-space Hamiltonian. -/
def hilbertTimeScaledOperator (t : ℝ) (A : HilbertSpinorEnd) : HilbertSpinorEnd :=
  (-(Complex.I * (t : ℂ))) • A

/-- A real-time multiple of a self-adjoint Hamiltonian is skew-adjoint. -/
theorem hilbertTimeScaledOperator_mem_skewAdjoint (t : ℝ) {A : HilbertSpinorEnd}
    (hA : IsSelfAdjoint A) :
    hilbertTimeScaledOperator t A ∈ skewAdjoint HilbertSpinorEnd := by
  exact hA.smul_mem_skewAdjoint (schrodingerScalar_mem_skewAdjoint t)

/-- Continuum Hilbert-space propagator on one Fourier mode. -/
def continuumHilbertModePropagator (m : ℝ) (n : Mode) (t : ℝ) : HilbertSpinorEnd :=
  NormedSpace.exp (hilbertTimeScaledOperator t (continuumHilbertModeOperator m n))

/-- Central-difference Hilbert-space propagator on one Fourier mode. -/
def centralHilbertModePropagator (m h : ℝ) (n : Mode) (t : ℝ) : HilbertSpinorEnd :=
  NormedSpace.exp (hilbertTimeScaledOperator t (centralHilbertModeOperator m h n))

/-- Continuum mode evolution is a unitary operator. -/
theorem continuumHilbertModePropagator_mem_unitary (m : ℝ) (n : Mode) (t : ℝ) :
    continuumHilbertModePropagator m n t ∈ unitary HilbertSpinorEnd := by
  exact NormedSpace.exp_mem_unitary_of_mem_skewAdjoint
    (hilbertTimeScaledOperator_mem_skewAdjoint t
      (continuumHilbertModeOperator_selfAdjoint m n))

/-- Lattice mode evolution is a unitary operator at every mesh. -/
theorem centralHilbertModePropagator_mem_unitary (m h : ℝ) (n : Mode) (t : ℝ) :
    centralHilbertModePropagator m h n t ∈ unitary HilbertSpinorEnd := by
  exact NormedSpace.exp_mem_unitary_of_mem_skewAdjoint
    (hilbertTimeScaledOperator_mem_skewAdjoint t
      (centralHilbertModeOperator_selfAdjoint m h n))

/-- Continuum mode propagation preserves the four-spinor Hilbert norm. -/
theorem norm_continuumHilbertModePropagator (m : ℝ) (n : Mode) (t : ℝ)
    (ψ : HilbertSpinor) :
    ‖continuumHilbertModePropagator m n t ψ‖ = ‖ψ‖ :=
  ContinuousLinearMap.norm_map_of_mem_unitary
    (continuumHilbertModePropagator_mem_unitary m n t) ψ

/-- Lattice mode propagation preserves the four-spinor Hilbert norm. -/
theorem norm_centralHilbertModePropagator (m h : ℝ) (n : Mode) (t : ℝ)
    (ψ : HilbertSpinor) :
    ‖centralHilbertModePropagator m h n t ψ‖ = ‖ψ‖ :=
  ContinuousLinearMap.norm_map_of_mem_unitary
    (centralHilbertModePropagator_mem_unitary m h n t) ψ

/-- Continuum mode propagation preserves the inner product. -/
theorem inner_continuumHilbertModePropagator (m : ℝ) (n : Mode) (t : ℝ)
    (ψ φ : HilbertSpinor) :
    inner ℂ (continuumHilbertModePropagator m n t ψ)
      (continuumHilbertModePropagator m n t φ) = inner ℂ ψ φ :=
  ContinuousLinearMap.inner_map_map_of_mem_unitary
    (continuumHilbertModePropagator_mem_unitary m n t) ψ φ

/-- Lattice mode propagation preserves the inner product. -/
theorem inner_centralHilbertModePropagator (m h : ℝ) (n : Mode) (t : ℝ)
    (ψ φ : HilbertSpinor) :
    inner ℂ (centralHilbertModePropagator m h n t ψ)
      (centralHilbertModePropagator m h n t φ) = inner ℂ ψ φ :=
  ContinuousLinearMap.inner_map_map_of_mem_unitary
    (centralHilbertModePropagator_mem_unitary m h n t) ψ φ

/-- A continuum-propagated finite Fourier packet. -/
def continuumHilbertPropagatedPacketL2 (m t : ℝ) (S : Finset Mode)
    (a : Mode → HilbertSpinor) : TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n (continuumHilbertModePropagator m n t (a n))

/-- A lattice-propagated finite Fourier packet. -/
def centralHilbertPropagatedPacketL2 (m h t : ℝ) (S : Finset Mode)
    (a : Mode → HilbertSpinor) : TorusSpinorL2 :=
  ∑ n ∈ S, modeEmbedIsometry n (centralHilbertModePropagator m h n t (a n))

/-- Exact norm conservation for continuum finite Fourier packets. -/
theorem continuumHilbertPropagatedPacketL2_norm_sq (m t : ℝ) (S : Finset Mode)
    (a : Mode → HilbertSpinor) :
    ‖continuumHilbertPropagatedPacketL2 m t S a‖ ^ 2 =
      ∑ n ∈ S, ‖a n‖ ^ 2 := by
  unfold continuumHilbertPropagatedPacketL2
  rw [modeEmbed_orthogonalFamily.norm_sum]
  apply Finset.sum_congr rfl
  intro n hn
  rw [norm_continuumHilbertModePropagator]

/-- Exact norm conservation for lattice finite Fourier packets. -/
theorem centralHilbertPropagatedPacketL2_norm_sq (m h t : ℝ) (S : Finset Mode)
    (a : Mode → HilbertSpinor) :
    ‖centralHilbertPropagatedPacketL2 m h t S a‖ ^ 2 =
      ∑ n ∈ S, ‖a n‖ ^ 2 := by
  unfold centralHilbertPropagatedPacketL2
  rw [modeEmbed_orthogonalFamily.norm_sum]
  apply Finset.sum_congr rfl
  intro n hn
  rw [norm_centralHilbertModePropagator]


end Relativistic3DFourierHilbertStability
end KomorebiPhysics
