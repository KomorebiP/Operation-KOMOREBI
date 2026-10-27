import KomorebiPhysics
import KomorebiPhysics.CurrentSummationExamples
import KomorebiPhysics.DilationExamples
import KomorebiPhysics.DomainExamples
import KomorebiPhysics.EffectExamples
import KomorebiPhysics.ExtensionExamples
import KomorebiPhysics.InfiniteCoarseExamples
import KomorebiPhysics.LadderExamples
import KomorebiPhysics.LindbladExamples
import KomorebiPhysics.QuantumInformationExamples
import KomorebiPhysics.RefinementExamples
import KomorebiPhysics.ResolventExamples
import KomorebiPhysics.SpectralErrorBounds
import KomorebiPhysics.SpectralEvolutionExamples
import KomorebiPhysics.UnboundedExamples

namespace NegativeBatch_FalseEquality
example : (0 : Nat) = 1 := by rfl
end NegativeBatch_FalseEquality

namespace NegativeBatch_AdmittedProof
example : False := by sorry
end NegativeBatch_AdmittedProof

namespace NegativeBatch_MissingSkew
open KomorebiPhysics
example : pairCurrent (1 : ℂ →L[ℂ] ℂ) 1 1 = 0 := by
  norm_num [pairCurrent]
end NegativeBatch_MissingSkew

namespace NegativeBatch_WrongHamiltonianSign
open KomorebiPhysics
example : pairCurrent ((-Complex.I) • (1 : ℂ →L[ℂ] ℂ)) 1 Complex.I = -2 := by
  norm_num [pairCurrent]
end NegativeBatch_WrongHamiltonianSign

namespace NegativeBatch_OmittedIntrinsic
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (3 : ℝ) • N = comm N P * X * Q + P * X * comm N Q := by
  rw [exact_three_terms.2.1, exact_three_terms.2.2]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [N]
end NegativeBatch_OmittedIntrinsic

namespace NegativeBatch_OmittedLeftFrame
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (3 : ℝ) • N = P * dX * Q + P * X * comm N Q := by
  rw [exact_three_terms.1, exact_three_terms.2.2]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [N]
end NegativeBatch_OmittedLeftFrame

namespace NegativeBatch_OmittedRightFrame
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (3 : ℝ) • N = P * dX * Q + comm N P * X * Q := by
  rw [exact_three_terms.1, exact_three_terms.2.1]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [N]
end NegativeBatch_OmittedRightFrame

namespace NegativeBatch_WrongCommutatorSign
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : comm N P = comm P N := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [KomorebiPhysics.Deformation.comm, N, P, Matrix.mul_apply, Fin.sum_univ_two]
end NegativeBatch_WrongCommutatorSign

namespace NegativeBatch_NonunitaryOrthogonality
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (transport (shear 1) (inverseShear 1) P).transpose =
    transport (shear 1) (inverseShear 1) P := by
  rw [transported_projector]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [P, N, Matrix.transpose_apply]
end NegativeBatch_NonunitaryOrthogonality

namespace NegativeBatch_WrongMixedSign

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.current hamiltonian density 0 1 = (1/2:ℝ) := by
  rw [mixed_current_values.1]
  norm_num
end NegativeBatch_WrongMixedSign

namespace NegativeBatch_MissingTraceConjugation

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.amplitude hamiltonian density 1 0 =
    binaryAtlas.amplitude hamiltonian density 0 1 := by
  apply Complex.ext
  · norm_num [MatrixAtlas.amplitude, binaryAtlas, hamiltonian, density,
      Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
      Complex.mul_re, Complex.mul_im]
  · norm_num [MatrixAtlas.amplitude, binaryAtlas, hamiltonian, density,
      Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
      Complex.mul_re, Complex.mul_im]
end NegativeBatch_MissingTraceConjugation

namespace NegativeBatch_MissingDensityHermiticity

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.current hamiltonian badDensity 0 1 =
    -binaryAtlas.current hamiltonian badDensity 1 0 := by
  norm_num [MatrixAtlas.current, MatrixAtlas.amplitude, binaryAtlas, hamiltonian,
    density, badDensity, badHamiltonian, Matrix.trace, Matrix.diag,
    Matrix.mul_apply, Fin.sum_univ_two, Complex.mul_re, Complex.mul_im]
end NegativeBatch_MissingDensityHermiticity

namespace NegativeBatch_MissingHamiltonianHermiticity

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.current badHamiltonian density 0 1 =
    -binaryAtlas.current badHamiltonian density 1 0 := by
  norm_num [MatrixAtlas.current, MatrixAtlas.amplitude, binaryAtlas, hamiltonian,
    density, badDensity, badHamiltonian, Matrix.trace, Matrix.diag,
    Matrix.mul_apply, Fin.sum_univ_two, Complex.mul_re, Complex.mul_im]
end NegativeBatch_MissingHamiltonianHermiticity

namespace NegativeBatch_BinaryWithoutPartition

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : (overlap * overlap) 0 0 = 0 ∨ (overlap * overlap) 0 0 = 1 := by
  norm_num [overlap, Matrix.mul_apply, Fin.sum_univ_two]
end NegativeBatch_BinaryWithoutPartition

namespace NegativeBatch_OmittedSource

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : deriv (fun u : ℝ => ∑ _i : Fin 2, u) 0 = 0 := by
  rw [(source_total_derivative 0).deriv]
  norm_num
end NegativeBatch_OmittedSource

namespace NegativeBatch_JointProbabilityFactorization

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : (binaryAtlas.tensor binaryAtlas).probability bell (0,0) =
    binaryAtlas.probability (PartialTrace.left bell) 0 *
      binaryAtlas.probability (PartialTrace.right bell) 0 := by
  rw [bell_joint_probability, bell_left, bell_right, halfIdentity_probability]
  norm_num
end NegativeBatch_JointProbabilityFactorization

namespace NegativeBatch_MarginalsDetermineJoint

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : bell = PartialTrace.left bell ⊗ₖ PartialTrace.right bell := by
  have h := bell_not_product_of_marginals
  simp_all
end NegativeBatch_MarginalsDetermineJoint

namespace NegativeBatch_BellProductMixture

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : HasFiniteProductDecomposition bell := by
  have h := bell_not_finite_product_mixture
  simp_all
end NegativeBatch_BellProductMixture

namespace NegativeBatch_OmittedPartialTraceFactor

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : PartialTrace.left ((1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ
    (1 : Matrix (Fin 2) (Fin 2) ℂ)) = (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  rw [partial_trace_identity_factor]
  ext i j
  norm_num
end NegativeBatch_OmittedPartialTraceFactor

namespace NegativeBatch_WrongEntropySign

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : deriv (fun t => entropy (packetCurve 1 t)) 0 = -Real.log 3 := by
  rw [(packet_entropy_rate 1).deriv]
  have h : 0 < Real.log (3:ℝ) := Real.log_pos (by norm_num)
  simp_all
end NegativeBatch_WrongEntropySign

namespace NegativeBatch_UniversalEntropyIncrease

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : 0 ≤ deriv (fun t => entropy (packetCurve (-1) t)) 0 := by
  have h := negative_entropy_rate
  simp_all
end NegativeBatch_UniversalEntropyIncrease

namespace NegativeBatch_WrongRenyiFactor

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : deriv (fun t => renyi (packetCurve 1 t) 2) 0 = (4/5:ℝ) := by
  rw [(packet_renyi_two_rate 1).deriv]
  norm_num
end NegativeBatch_WrongRenyiFactor

namespace NegativeBatch_WeightedBalanceWithoutAntisymmetry

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.InformationTransport KomorebiPhysics.EntanglementWitness
open KomorebiPhysics.QuantumInformationExamples
open KomorebiPhysics.ExtensionExamples (binaryAtlas)
open scoped BigOperators Matrix Kronecker ComplexOrder

-- Deliberately false: rejection must be a proof diagnostic, not an import failure.
example : (∑ i : Fin 1, (1:ℝ) * ∑ _j : Fin 1, (1:ℝ)) =
    (1/2:ℝ) * ∑ _i : Fin 1, ∑ _j : Fin 1, (1:ℝ) * (1-1) := by
  norm_num
end NegativeBatch_WeightedBalanceWithoutAntisymmetry

namespace NegativeBatch_WrongJumpOrientation
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : (jump rates 0 1).conjTranspose * jump rates 0 1 = Matrix.single 0 0 (4:ℂ) := by
  have h := source_support_is_essential
  simp_all
end NegativeBatch_WrongJumpOrientation

namespace NegativeBatch_WrongRateAmplitude
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : (Matrix.single (0:Fin 2) (1:Fin 2) (4:ℂ)).conjTranspose *
    Matrix.single (0:Fin 2) (1:Fin 2) (4:ℂ) = Matrix.single 1 1 (4:ℂ) := by
  have h := square_root_is_essential
  simp_all
end NegativeBatch_WrongRateAmplitude

namespace NegativeBatch_NegativeRateSquareRoot
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : (Real.sqrt (-4:ℝ) : ℂ) * (Real.sqrt (-4:ℝ) : ℂ) = (-4:ℂ) := by
  have h := rate_nonnegativity_is_essential
  simp_all
end NegativeBatch_NegativeRateSquareRoot

namespace NegativeBatch_JumpWithoutLoss
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : Matrix.trace (jump rates 0 1 * density * (jump rates 0 1).conjTranspose) = 0 := by
  rw [loss_terms_are_essential]
  norm_num
end NegativeBatch_JumpWithoutLoss

namespace NegativeBatch_WrongAnticommutatorFactor
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : Matrix.trace (jump rates 0 1 * density * (jump rates 0 1).conjTranspose -
      ((jump rates 0 1).conjTranspose * jump rates 0 1 * density +
        density * ((jump rates 0 1).conjTranspose * jump rates 0 1))) = 0 := by
  rw [half_factor_is_essential]
  norm_num
end NegativeBatch_WrongAnticommutatorFactor

namespace NegativeBatch_SelfJumpNoCoherence
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : dissipator (Matrix.single (0:Fin 2) 0 (2:ℂ)) density 0 1 = 0 := by
  rw [self_jump_is_not_zero]
  norm_num
end NegativeBatch_SelfJumpNoCoherence

namespace NegativeBatch_OmittedCoherentCurrent
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : quantumCurrent hamiltonian rates density 0 1 = current rates (population density) 0 1 := by
  have h := coherent_current_is_essential.2
  simp_all
end NegativeBatch_OmittedCoherentCurrent

namespace NegativeBatch_WrongCoherenceRate
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : generator rates density 0 1 = 0 := by
  rw [generator_value]
  norm_num
end NegativeBatch_WrongCoherenceRate

namespace NegativeBatch_RelativeEntropyWrongSign
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : 0 ≤ deriv (fun t => relativeEntropy (population (localCurve t)) reference) 0 := by
  have h := local_relativeEntropy_strictly_decreases
  simp_all
end NegativeBatch_RelativeEntropyWrongSign

namespace NegativeBatch_RelativeEntropyWithoutBalance
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : deriv (fun t => relativeEntropy (population (biasedCurve t)) (fun _ => (1/2:ℝ))) 0 ≤ 0 := by
  have h := wrong_reference_strictly_increases
  simp_all
end NegativeBatch_RelativeEntropyWithoutBalance

namespace NegativeBatch_ZeroDissipationUnique
open KomorebiPhysics KomorebiPhysics.LindbladJumps KomorebiPhysics.LindbladDynamics
open KomorebiPhysics.LindbladCoherence KomorebiPhysics.DetailedBalance
open KomorebiPhysics.LindbladExamples
open KomorebiPhysics.ExtensionExamples (density hamiltonian)
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
-- Intentionally false; only the designated proof diagnostic counts as rejection.
example : (fun _ : Fin 2 => (1/2:ℝ)) = reference := by
  have h := zero_dissipation_does_not_force_equilibrium.2.2.2
  simp_all
end NegativeBatch_ZeroDissipationUnique

namespace NegativeBatch_WrongRefinementWeight
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : (4*(1/2 : ℝ)-1)/(4-1) = 0 := by
  rw [wrong_first_weight]
  norm_num
end NegativeBatch_WrongRefinementWeight

namespace NegativeBatch_WrongRefinementQuadraticSign
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 2 (fun h : ℝ => h^2) 1 1 = 1/2 := by
  rw [surviving_quadratic]
  norm_num
end NegativeBatch_WrongRefinementQuadraticSign

namespace NegativeBatch_RefinementExtraCancellation
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : coefficient 2 2 3 = 0 := by
  norm_num [coefficient]
end NegativeBatch_RefinementExtraCancellation

namespace NegativeBatch_RefinementExtraOrder
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 2 (fun h : ℝ => h^2) 1 =O[𝓝[≠] 0] (fun h : ℝ => h^3) := by
  simp only [quadratic_not_third_order]
end NegativeBatch_RefinementExtraOrder

namespace NegativeBatch_RefinementUnitRatio
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 1 (fun _ : ℝ => (1 : ℝ)) 1 1 = 1 := by
  rw [unit_ratio_degenerate]
  norm_num
end NegativeBatch_RefinementUnitRatio

namespace NegativeBatch_RefinementNoiseContraction
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : ‖tower 2 sampleNoise 1 1‖ ≤ 1 := by
  rw [sampleNoise_amplified]
  norm_num
end NegativeBatch_RefinementNoiseContraction

namespace NegativeBatch_WrongRefinementThirdDenominator
open scoped Topology
open Asymptotics
open KomorebiPhysics.RefinementCancellation KomorebiPhysics.RefinementExamples
-- Intentionally false. An import failure or timeout is not a successful rejection.
example : tower 2 (fun _ : ℝ => (1 : ℝ)) 3 1 = (64-56+14-1)/7 := by
  norm_num [tower]
end NegativeBatch_WrongRefinementThirdDenominator

namespace NegativeBatch_EffectBornSquaredNorm
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.probability softState 0 = ‖softAtlas.effect 0 softState‖ ^ 2 := by
  rw [soft_probabilities.1, soft_squared_effect_norm]
  norm_num
end NegativeBatch_EffectBornSquaredNorm

namespace NegativeBatch_EffectIdempotence
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.effect 0 * softAtlas.effect 0 = softAtlas.effect 0 := by
  simp only [soft_not_idempotent]
end NegativeBatch_EffectIdempotence

namespace NegativeBatch_EffectOrthogonality
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.effect 0 * softAtlas.effect 1 = 0 := by
  simp only [soft_not_orthogonal]
end NegativeBatch_EffectOrthogonality

namespace NegativeBatch_EffectWrongCurrentSign
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : softAtlas.current Examples.rotation2 softState 0 1 = 12/25 := by
  rw [soft_current_nonzero.1]
  norm_num
end NegativeBatch_EffectWrongCurrentSign

namespace NegativeBatch_MovingEffectNoSource
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : deriv (fun t => (oscillatingAtlas t).probability 1 0) 0 = 0 := by
  rw [oscillating_probability_hasDerivAt.deriv]
  norm_num
end NegativeBatch_MovingEffectNoSource

namespace NegativeBatch_MovingEffectWrongSourceSign
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : deriv (fun t => (oscillatingAtlas t).probability 1 0) 0 = -1/2 := by
  rw [oscillating_probability_hasDerivAt.deriv]
  norm_num
end NegativeBatch_MovingEffectWrongSourceSign

namespace NegativeBatch_EffectWithoutSkew
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : deriv (fun t : ℝ => (oscillatingAtlas 0).probability (1 + (t : ℂ)) 0) 0 =
    ∑ j : Fin 2, (oscillatingAtlas 0).current (1 : ℂ →L[ℂ] ℂ) 1 0 j := by
  rw [identity_probability_derivative.deriv]
  simp only [identity_effect_current_zero, Finset.sum_const_zero]
  norm_num
end NegativeBatch_EffectWithoutSkew

namespace NegativeBatch_DuplicateEffectsComplete
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : (∑ _i : Fin 2, (1 : ℂ →L[ℂ] ℂ)) = 1 := by
  simp only [duplicated_identity_not_complete]
end NegativeBatch_DuplicateEffectsComplete

namespace NegativeBatch_SignedPositiveEffect
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.EffectExamples
-- Intentionally false. Timeouts or import errors are not successful rejection tests.
example : 0 ≤ effectExpectation ((-1 : ℂ) • (1 : ℂ →L[ℂ] ℂ)) 1 := by
  rw [signed_effect_negative]
  norm_num
end NegativeBatch_SignedPositiveEffect

namespace NegativeBatch_DilationAmbientIdentity
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.rangeProjection = 1 := by
  simp only [rangeProjection_not_identity]
end NegativeBatch_DilationAmbientIdentity

namespace NegativeBatch_DilationCompressedSharp
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.effectAtlas.effect 0 * scalarFamily.effectAtlas.effect 0 = scalarFamily.effectAtlas.effect 0 := by
  simp only [compressed_effect_not_idempotent]
end NegativeBatch_DilationCompressedSharp

namespace NegativeBatch_DilationCompressionMultiplicative
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.compressOperator
      (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0 *
       ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) =
    scalarFamily.compressOperator (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) *
    scalarFamily.compressOperator (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) := by
  simp only [compression_not_multiplicative]
end NegativeBatch_DilationCompressionMultiplicative

namespace NegativeBatch_DilationOmittedCrossChannels
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : diagonalOnly = 1 := by
  simp only [diagonalOnly_not_identity]
end NegativeBatch_DilationOmittedCrossChannels

namespace NegativeBatch_DilationMissingNormalization
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : (∑ _i : Fin 2, (1:ℂ→L[ℂ]ℂ).adjoint.comp (1:ℂ→L[ℂ]ℂ)) = 1 := by
  simp only [missing_normalization]
end NegativeBatch_DilationMissingNormalization

namespace NegativeBatch_DilationWrongProbability
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : scalarFamily.effectAtlas.probability 1 0 = 3/5 := by
  rw [scalar_probabilities.1]
  norm_num
end NegativeBatch_DilationWrongProbability

namespace NegativeBatch_CycleCurrentUnique
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : CycleGauge.triangle = 0 := by
  simp only [CycleGauge.triangle_nonzero]
end NegativeBatch_CycleCurrentUnique

namespace NegativeBatch_DilationWrongCurrentSign
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example :
    (ChannelDilation.coordinateAtlas (fun _ : Fin 2 => EuclideanSpace ℂ (Fin 2))).current
      (EffectExamples.softAtlas.sqrtFamily.liftOperator Examples.rotation2)
      (EffectExamples.softAtlas.dilation EffectExamples.softState) 0 1 = 12/25 := by
  rw [soft_dilated_current]
  norm_num
end NegativeBatch_DilationWrongCurrentSign

namespace NegativeBatch_DilationSurjective
open scoped BigOperators
open KomorebiPhysics KomorebiPhysics.DilationExamples
-- Deliberately false. Require its own intended diagnostic, not an import failure or timeout.
example : Function.Surjective scalarFamily.analysis := by
  simp only [analysis_not_surjective]
end NegativeBatch_DilationSurjective

namespace NegativeBatch_UnboundedIsBounded
open scoped lp
open KomorebiPhysics.UnboundedExamples
-- False: boundedness cannot be inferred from unbounded self-adjointness.
example : ∃ C : ℝ, ∀ x : harmonic.domain,
    ‖harmonic x‖ ≤ C * ‖(x : ℓ²(ℕ, ℂ))‖ := by
  simp only [harmonic_unbounded]
end NegativeBatch_UnboundedIsBounded

namespace NegativeBatch_StrongImpliesActionLimit
open Filter
open scoped Topology
open KomorebiPhysics.UnboundedExamples
-- The input sequence really tends to zero, but its generator images do not.
example : Tendsto (fun n => harmonic (shrinking n)) atTop (𝓝 0) := by
  simp only [shrinking_action_not_zero]
end NegativeBatch_StrongImpliesActionLimit

namespace NegativeBatch_GraphNormOmitsAction
open scoped lp
open KomorebiPhysics KomorebiPhysics.UnboundedExamples
example : GraphDomain.graphNorm harmonic (basisState 0) =
    ‖(basisState 0 : ℓ²(ℕ, ℂ))‖ := by
  simp only [graph_norm_not_ambient]
end NegativeBatch_GraphNormOmitsAction

namespace NegativeBatch_WrongDomainCurrentSign
open KomorebiPhysics.DomainExamples
example : atlas.current state 0 1 = 2 := by
  rw [exact_current.1]
  norm_num
end NegativeBatch_WrongDomainCurrentSign

namespace NegativeBatch_DomainMissingConjugation
open KomorebiPhysics.DomainExamples
example : atlas.amplitude state 1 0 = atlas.amplitude state 0 1 := by
  simp only [reverse_without_conjugation_false]
end NegativeBatch_DomainMissingConjugation

namespace NegativeBatch_DomainWrongDerivative
open KomorebiPhysics.DomainExamples
example : HasDerivAt (fun s => atlas.atlas.energy (localCurve s) 0) 0 0 := by
  have h := actual_packet_derivative
  apply h.congr_deriv
  norm_num
end NegativeBatch_DomainWrongDerivative

namespace NegativeBatch_StrongMeansNorm
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example : ‖ContinuousLinearMap.id ℂ Space - cutoff 7‖ = 0 := by
  rw [identity_cutoff_norm_error]
end
end NegativeBatch_StrongMeansNorm

namespace NegativeBatch_HeatZeroDecay
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example (M : ℕ) : ‖diagonal (heatSymbol 0 le_rfl) - diagonal (truncate (heatSymbol 0 le_rfl) M)‖ = 0 := by
  rw [heat_zero_error]
end
end NegativeBatch_HeatZeroDecay

namespace NegativeBatch_BoundedZeroAnchor
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example (M : ℕ) : ‖diagonal boundedSymbol - diagonal (truncate boundedSymbol M)‖ = 0 := by
  rw [bounded_zero_padded_exact]
end
end NegativeBatch_BoundedZeroAnchor

namespace NegativeBatch_CayleyZeroAnchor
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example (M : ℕ) : ‖diagonal cayleySymbol - diagonal (truncate cayleySymbol M)‖ = 0 := by
  rw [cayley_zero_padded_exact]
end
end NegativeBatch_CayleyZeroAnchor

namespace NegativeBatch_ResolventWrongEndpoint
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example : ‖diagonal (resolventSymbol 0) - diagonal (truncate (resolventSymbol 0) 10)‖ = 1/10 := by
  rw [resolvent_error_at_ten]
end
end NegativeBatch_ResolventWrongEndpoint

namespace NegativeBatch_CayleyWrongFactor
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example (M : ℕ) : ‖diagonal cayleySymbol - diagonal (anchored cayleySymbol 1 M)‖ = 1 / root M := by
  rw [cayley_error_endpoint]
end
end NegativeBatch_CayleyWrongFactor

namespace NegativeBatch_WrongConstantTail
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example : Tendsto (fun M => ‖diagonal boundedSymbol - diagonal (anchored boundedSymbol (-1) M)‖) atTop (𝓝 0) := by
  rw [anchored_norm_iff]
end
end NegativeBatch_WrongConstantTail

namespace NegativeBatch_BackwardHeatBounded
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.SpectralTruncation
open KomorebiPhysics.HarmonicSurrogates KomorebiPhysics.AnchoredSurrogates
open KomorebiPhysics.SpectralErrorBounds KomorebiPhysics.UnboundedExamples Filter
open scoped Topology lp
noncomputable section
example : ∃ C : ℝ, ∀ n, Real.exp (-(-1) * harmonicEigenvalue n) ≤ C := by
  simp only [neg_neg, one_mul]
end
end NegativeBatch_BackwardHeatBounded

namespace NegativeBatch_RoughStateInDomain
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : roughState ∈ DiagonalDomain.domain harmonicEigenvalue := by
  simp only [roughState_not_domain]
end
end NegativeBatch_RoughStateInDomain

namespace NegativeBatch_CoordinateDerivativeSuffices
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : DifferentiableAt ℝ (fun s => evolution harmonicEigenvalue s roughState) 0 := by
  have coordinates := rough_coordinates_differentiable 0
  simp only [rough_orbit_not_differentiable]
end
end NegativeBatch_CoordinateDerivativeSuffices

namespace NegativeBatch_PhaseSmoothsOutsideDomain
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : evolution harmonicEigenvalue 1 roughState ∈ DiagonalDomain.domain harmonicEigenvalue := by
  rw [domain_iff]
  simp only [roughState_not_domain]
end
end NegativeBatch_PhaseSmoothsOutsideDomain

namespace NegativeBatch_PhaseOperatorNormContinuous
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : ContinuousAt (fun t => evolution harmonicEigenvalue t) 0 := by
  simp only [not_operator_norm_continuous]
end
end NegativeBatch_PhaseOperatorNormContinuous

namespace NegativeBatch_HalfTurnNormDistanceZero
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : ‖evolution harmonicEigenvalue (halfTurnTime 100) -
    ContinuousLinearMap.id ℂ Space‖ = 0 := by
  rw [halfTurn_operator_distance]
end
end NegativeBatch_HalfTurnNormDistanceZero

namespace NegativeBatch_SmoothCutoffVelocityBounded
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : ‖deriv (fun s => SpectralTruncation.cutoff 4
    (evolution harmonicEigenvalue s roughState)) 0‖ ^ 2 ≤ 1 := by
  rw [rough_cutoff_velocity_norm_sq]
  norm_num
end
end NegativeBatch_SmoothCutoffVelocityBounded

namespace NegativeBatch_CoherentObservableStationary
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : HasDerivAt (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) 0 0 := by
  apply coherent_observable_hasDerivAt.congr_deriv
  norm_num
end
end NegativeBatch_CoherentObservableStationary

namespace NegativeBatch_CoherentObservableWrongSign
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : HasDerivAt (fun t => ‖coherentAmplitude t‖ ^ 2 / 2) (-12/25) 0 := by
  apply coherent_observable_hasDerivAt.congr_deriv
  norm_num
end
end NegativeBatch_CoherentObservableWrongSign

namespace NegativeBatch_InfiniteCellWrongEnergy
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (coarse harmonicEigenvalue).atlas.energy (coherentState : Space) 0 = 9/25 := by
  rw [even_probability]
  norm_num
end
end NegativeBatch_InfiniteCellWrongEnergy

namespace NegativeBatch_InfiniteCellWrongDerivative
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : HasDerivAt (fun t => (coarse harmonicEigenvalue).atlas.energy
    (evolution harmonicEigenvalue t (coherentState : Space)) 0) (-288/625) 0 := by
  apply even_probability_hasDerivAt.congr_deriv
  norm_num
end
end NegativeBatch_InfiniteCellWrongDerivative

namespace NegativeBatch_InfiniteCoarseCurrentsZero
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (coarse harmonicEigenvalue).current coherentState 0 1 = 0 := by
  rw [current_even_from_odd]
  norm_num
end
end NegativeBatch_InfiniteCoarseCurrentsZero

namespace NegativeBatch_InfiniteParityCellFinite
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (parity ⁻¹' {(0 : Fin 2)}).Finite := by
  have hn : ¬ (parity ⁻¹' {(0 : Fin 2)}).Finite := even_fiber_infinite
  simp only [hn]
end
end NegativeBatch_InfiniteParityCellFinite

namespace NegativeBatch_RowwiseSummabilityIsJoint
open KomorebiPhysics.CurrentSummationExamples
noncomputable section
example : (∀ i : Label, Summable (cycles i)) →
    Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro _
  simp only [not_joint_summable]
end
end NegativeBatch_RowwiseSummabilityIsJoint

namespace NegativeBatch_IteratedSumsAreJoint
open KomorebiPhysics.CurrentSummationExamples
open scoped BigOperators
noncomputable section
example : (HasSum (fun i : Label => ∑' j, cycles i j) 0 ∧
    HasSum (fun j : Label => ∑' i, cycles i j) 0) →
    Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro _
  simp only [not_joint_summable]
end
end NegativeBatch_IteratedSumsAreJoint

namespace NegativeBatch_ResidueWrongCharacterSign
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : (3 : ℂ)⁻¹ * ∑ k : ZMod 3,
    ZMod.stdAddChar ((1 : ZMod 3)*k) * ZMod.stdAddChar (k*(1 : ZMod 3)) = 1 := by
  rw [ResidueCharacters.wrong_sign_three]
  norm_num
end
end NegativeBatch_ResidueWrongCharacterSign

namespace NegativeBatch_ResidueMissingNormalization
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∑ k : ZMod 3,
    ZMod.stdAddChar (-((1 : ZMod 3)*k)) * ZMod.stdAddChar (k*(1 : ZMod 3)) = (1 : ℂ) := by
  rw [unnormalized_character_sum]
  norm_num
end
end NegativeBatch_ResidueMissingNormalization

namespace NegativeBatch_LadderWrongAmplitude
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : lower (single 9 1) = lp.single 2 8 (9 : ℂ) := by
  simp only [wrong_square_root_amplitude]
end
end NegativeBatch_LadderWrongAmplitude

namespace NegativeBatch_LadderLowerWrongLane
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : projector 3 0 (lower (packet 3 0 (single 9 1))) ≠ 0 := by
  simp only [lowering_wrong_lane, ne_eq, not_true_eq_false]
end
end NegativeBatch_LadderLowerWrongLane

namespace NegativeBatch_LadderRaiseWrongLane
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : projector 3 1 (raise (packet 3 2 (single 8 1))) ≠ 0 := by
  simp only [raising_wrong_lane, ne_eq, not_true_eq_false]
end
end NegativeBatch_LadderRaiseWrongLane

namespace NegativeBatch_LadderVacuumSurvives
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : lower (single 0 1) ≠ 0 := by
  simp only [vacuum_lowering, ne_eq, not_true_eq_false]
end
end NegativeBatch_LadderVacuumSurvives

namespace NegativeBatch_LadderLowerBounded
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∃ A : Space →L[ℂ] Space, ∀ x : domain, lower x = A x := by
  simp only [no_bounded_lower_extension]
end
end NegativeBatch_LadderLowerBounded

namespace NegativeBatch_LadderRaiseBounded
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∃ A : Space →L[ℂ] Space, ∀ x : domain, raise x = A x := by
  simp only [no_bounded_raise_extension]
end
end NegativeBatch_LadderRaiseBounded

namespace NegativeBatch_ResolventMissingMinus
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : commutator (R 0) P = R 0 * B * R 0 := by
  simp only [wrong_sign_rejected]
end
end NegativeBatch_ResolventMissingMinus

namespace NegativeBatch_ResolventOmittedFactor
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : commutator (R 0) P = -(R 0 * B) := by
  simp only [omitted_factor_rejected]
end
end NegativeBatch_ResolventOmittedFactor

namespace NegativeBatch_ResolventZeroEtaBound
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : ‖commutator (R 0) P‖ ≤ ‖B‖ / (0 : ℝ)^2 := by
  simp only [zero_parameter_bound_rejected]
end
end NegativeBatch_ResolventZeroEtaBound

namespace NegativeBatch_ResolventAllPacketsReduce
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : ∀ x : harmonic.domain, harmonic (restrict harmonic P P_domain x) = P (harmonic x) := by
  simp only [packet_does_not_reduce]
end
end NegativeBatch_ResolventAllPacketsReduce

namespace NegativeBatch_ResolventLeakageZero
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : commutator (R 1) P = 0 := by
  simp only [resolvent_commutator_nonzero]
end
end NegativeBatch_ResolventLeakageZero

namespace NegativeBatch_ResolventWrongNormSquare
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.ResolventDomain
open KomorebiPhysics.ResolventExamples KomorebiPhysics.UnboundedExamples
open scoped lp
noncomputable section
example : ‖commutator (R 1) P‖ ^ 2 = 0 := by
  rw [unit_parameter_norm_sq]
  norm_num
end
end NegativeBatch_ResolventWrongNormSquare

