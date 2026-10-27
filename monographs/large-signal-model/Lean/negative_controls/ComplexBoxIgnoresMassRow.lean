import KomorebiLSM.ComplexCoefficientBox
open Komorebi.LSM Komorebi.LSM.ComplexCoefficientBox

/- Spatial output zero does not erase the actual positive output mass. -/
example : LorentzCylinder.probabilityCone.value
    (matrixOperator (1 : RealMatrix) (1,(0 : ℂ)))≤0 := by
  rw [LorentzCylinder.value_eq]
  norm_num [matrixOperator,row,RationalBernsteinMargin.coordinate,Fin.sum_univ_three,Matrix.one_apply]
