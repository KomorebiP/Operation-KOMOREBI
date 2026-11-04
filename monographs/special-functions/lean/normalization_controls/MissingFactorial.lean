import CoupledNormalization
noncomputable section
open Komorebi.SpecialFunctions.Coupled.Scales

example (p : RationalScales) (i : Fin 2) (n : ℕ) :
    p.derivativeComponent i n = p.componentCoefficient i n := by
  exact derivative_component_normalized p i n
