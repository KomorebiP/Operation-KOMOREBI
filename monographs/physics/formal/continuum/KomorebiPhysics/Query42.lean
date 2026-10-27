module
public import KomorebiPhysics.Relativistic3DFourierGenerator
public import Mathlib.Analysis.Fourier.AddCircleMulti
public import Mathlib.Analysis.InnerProductSpace.PiL2
@[expose] public section
open scoped ENNReal BigOperators ComplexConjugate
open MeasureTheory WithLp
local instance : MeasureSpace UnitAddCircle := ⟨AddCircle.haarAddCircle⟩
local instance : Measure.IsAddHaarMeasure (volume : Measure UnitAddCircle) := inferInstanceAs (Measure.IsAddHaarMeasure AddCircle.haarAddCircle)
local instance : IsProbabilityMeasure (volume : Measure UnitAddCircle) := inferInstanceAs (IsProbabilityMeasure AddCircle.haarAddCircle)
#check Orthonormal.norm_eq_one
#check UnitAddTorus.orthonormal_mFourier.norm_eq_one
#check norm_smul
#check PiLp.norm_sq_eq_of_L2
#check WithLp.toLp_apply
#check Finset.sum_congr
