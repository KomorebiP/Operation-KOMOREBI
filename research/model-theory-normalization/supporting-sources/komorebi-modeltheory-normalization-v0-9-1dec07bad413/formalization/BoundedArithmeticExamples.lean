module
public import BoundedDiscovery
public import EuclidCost

@[expose] public section
namespace Komorebi.BoundedArithmeticExamples
open Komorebi.Echelon Komorebi.Echelon.Cost

def fourBasis : Basis 2 := diagonal 4 (by decide) 2

theorem bezout_signed : smallBezout 6 (-4)=(1,1) := by decide +kernel

theorem euclid_anchor : euclidCoeff 240 46=(-9,47) := by decide +kernel

theorem euclid_steps_anchor : euclidSteps 240 46=5 := by decide +kernel

theorem update_peak_exceeds_modulus : updatePeak fourBasis ![3,3]=12 := by decide +kernel

theorem reduced_result : entries (boundedNormalizedInsert fourBasis ![3,3])=![![1,1],![0,4]] := by
  decide +kernel

theorem no_extra_growth_at_zero_dimension : updatePeak Basis.nil (fun i => Fin.elim0 i)=0 := rfl

end Komorebi.BoundedArithmeticExamples
