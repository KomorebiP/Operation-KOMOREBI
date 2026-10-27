import Mathlib.Analysis.SumIntegralComparisons
import Mathlib.Analysis.SpecialFunctions.ImproperIntegrals
import Mathlib.Analysis.SpecialFunctions.Integrals.Basic

set_option autoImplicit false
noncomputable section
open Filter Set MeasureTheory
open scoped Topology
namespace KomorebiSpace.DiagonalRegularization

#check integral_Ioi_of_hasDerivAt_of_tendsto'
#check integral_Ioi_of_hasDerivAt_of_tendsto
#check Measure.integral_comp_mul_left
#check Measure.integral_comp_div
#check Integrable.comp_mul_left'
#check Integrable.mono'
#check tendsto_div_pow_atTop
#check tendsto_pow_div_pow_atTop
#check Real.tendsto_arctan_atTop
#check Real.hasDerivAt_arctan'
#check Filter.Tendsto.div_atTop
#check tendsto_one_div_add_atTop_nhds_zero_nat
#check tendsto_natCast_atTop_atTop
#check MeasureTheory.integral_comp_mul_left_Ioi
#check integral_comp_mul_left_Ioi

end KomorebiSpace.DiagonalRegularization
