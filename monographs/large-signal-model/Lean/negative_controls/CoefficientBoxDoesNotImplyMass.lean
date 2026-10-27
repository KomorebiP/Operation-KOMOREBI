import KomorebiLSM.CoefficientBox3
open MeasureTheory Komorebi.LSM Komorebi.LSM.CoefficientBox3
open scoped BigOperators

/- The identity error has entries bounded by one, but its integrated mass row
is not zero. A coefficient box cannot replace the affine mass constraint. -/
example : LorentzCylinder.probabilityCone.mass
    ((∫ u,PolynomialGram.operatorPolynomial (fun _ : Fin 1 => operator (1 : Coefficient)) u
      ∂UniformIntervalMoments.measure) (1,(0 : Spatial)))=0 := by
  rw [PolynomialGram.operatorPolynomial_integral]
  norm_num [Fin.sum_univ_one]
