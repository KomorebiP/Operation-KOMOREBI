import KomorebiLSM.RationalLorentzMatrix
import KomorebiLSM.InteriorRepair

set_option autoImplicit false
namespace Komorebi.LSM.RationalLorentzMatrix
open scoped BigOperators
open LorentzCylinder RationalBernsteinMargin
noncomputable section

theorem matrixOperator_qadd (M N : RationalMatrix) :
    matrixOperator (qadd M N)=matrixOperator M+matrixOperator N := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp [coordinate_matrixOperator,qadd,add_mul,Finset.sum_add_distrib]

theorem matrixOperator_qscale (q : ℚ) (M : RationalMatrix) :
    matrixOperator (qscale q M)=(q : ℝ) • matrixOperator M := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp [coordinate_matrixOperator,qscale,Finset.mul_sum,mul_assoc]

theorem matrixOperator_sub (M N : RationalMatrix) :
    matrixOperator (M-N)=matrixOperator M-matrixOperator N := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp [coordinate_matrixOperator,sub_mul,Finset.sum_sub_distrib]

@[simp] theorem matrixOperator_zero : matrixOperator (0 : RationalMatrix)=0 := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp [coordinate_matrixOperator]

def centerMatrix : RationalMatrix := ![![1,0,0],![0,0,0],![0,0,0]]

@[simp] theorem matrixOperator_center : matrixOperator centerMatrix=InteriorRepair.centerReset := by
  apply ContinuousLinearMap.ext
  intro z
  apply coordinate_ext
  intro i
  simp only [coordinate_matrixOperator,InteriorRepair.centerReset_apply]
  fin_cases i <;> norm_num [centerMatrix,coordinate,Fin.sum_univ_succ,Matrix.cons_val_two]

end
end Komorebi.LSM.RationalLorentzMatrix
