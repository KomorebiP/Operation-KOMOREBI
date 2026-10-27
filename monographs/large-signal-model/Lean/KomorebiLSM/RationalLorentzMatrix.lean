import KomorebiLSM.RationalBernsteinMargin
import Mathlib.Algebra.MvPolynomial.Funext

set_option autoImplicit false
namespace Komorebi.LSM.RationalLorentzMatrix
open scoped BigOperators
open LorentzCylinder RationalBernsteinMargin TensorBernsteinCertificate
noncomputable section

theorem coordinate_ext {z w : State ℂ} (h : ∀ i,coordinate i z=coordinate i w) : z=w := by
  apply Prod.ext
  · simpa [coordinate] using h 0
  · apply Complex.ext
    · simpa [coordinate] using h 1
    · simpa [coordinate] using h 2

def qadd (M N : RationalMatrix) : RationalMatrix := fun i j => M i j+N i j

def qscale (q : ℚ) (M : RationalMatrix) : RationalMatrix := fun i j => q*M i j

def qmul (M N : RationalMatrix) : RationalMatrix := fun i j => ∑ k,M i k*N k j

theorem matrixOperator_qmul (M N : RationalMatrix) :
    matrixOperator (qmul M N)=(matrixOperator M).comp (matrixOperator N) := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp only [coordinate_matrixOperator,ContinuousLinearMap.comp_apply,qmul,
    Rat.cast_sum,Rat.cast_mul,Finset.sum_mul,Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro k _
  ring

theorem matrixOperator_add (M N : RationalMatrix) :
    matrixOperator (M+N)=matrixOperator M+matrixOperator N := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp [coordinate_matrixOperator,add_mul,Finset.sum_add_distrib]

theorem matrixOperator_smul (q : ℚ) (M : RationalMatrix) :
    matrixOperator (q • M)=(q : ℝ) • matrixOperator M := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp [coordinate_matrixOperator,Finset.mul_sum,mul_assoc]

theorem matrixOperator_mul (M N : RationalMatrix) :
    matrixOperator (M*N)=(matrixOperator M).comp (matrixOperator N) := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp only [coordinate_matrixOperator,ContinuousLinearMap.comp_apply,Matrix.mul_apply,
    Rat.cast_sum,Rat.cast_mul,Finset.sum_mul,Finset.mul_sum]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro j _
  apply Finset.sum_congr rfl
  intro k _
  ring

theorem matrixOperator_one : matrixOperator (1 : RationalMatrix)=ContinuousLinearMap.id ℝ (State ℂ) := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp only [coordinate_matrixOperator,Matrix.one_apply,apply_ite]
  simp

/-- Equality of the finite rational polynomials can be proved through exact real identities. -/
theorem polynomial_eq_of_value_eq (p q : Polynomial₂) (h : ∀ x,value p x=value q x) : p=q := by
  apply MvPolynomial.map_injective (algebraMap ℚ ℝ) (FaithfulSMul.algebraMap_injective ℚ ℝ)
  apply MvPolynomial.funext
  intro x
  simpa only [value,MvPolynomial.eval_map] using h x

end
end Komorebi.LSM.RationalLorentzMatrix
