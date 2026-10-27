import KomorebiPhysics
import KomorebiPhysics.ExtensionExamples
import KomorebiPhysics.LindbladExamples
import KomorebiPhysics.QuantumInformationExamples
import KomorebiPhysics.RefinementExamples

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

