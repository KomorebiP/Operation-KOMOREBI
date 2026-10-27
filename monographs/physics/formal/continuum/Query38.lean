import KomorebiPhysics.Relativistic3DOctreeEuclideanCoding
import Mathlib.Probability.CDF
import Mathlib.MeasureTheory.Constructions.Pi
import Mathlib.MeasureTheory.Constructions.UnitInterval

open scoped ENNReal NNReal MeasureTheory unitInterval
open MeasureTheory Set ProbabilityTheory

#check Measure.ext_of_Iic
#check unitInterval.volume_Iic
#check Measure.map_apply
#check Measure.infinitePi_cylinder
#check Measure.infinitePi_map_pi
#check Measure.map_map
#check MeasurePreserving.comp
#check MeasurePreserving.map_eq
#check MeasureTheory.Measure.measure_iUnion
#check MeasureTheory.Measure.measure_iUnion_null
#check MeasureTheory.Measure.tsum_meas_le_meas_iUnion
#check Real.ofDigits_eq_sum_add_ofDigits
#check Real.abs_ofDigits_sub_ofDigits_le
#check Real.ofDigitsTerm
#check Real.ofDigits_nonneg
#check Real.ofDigits_le_one
#check MeasureTheory.Measure.eq_of_cdf
#check ProbabilityTheory.cdf_eq_real
#check unitInterval.cdf_eq_real
#check MeasureTheory.measureReal_def
#check ENNReal.toReal_eq_toReal
#check Measure.real
#check Measure.map_apply_of_aemeasurable
#check MeasureTheory.MeasurePreserving.map_eq
#check MeasureTheory.MeasurePreserving.comp
#check MeasureTheory.measurePreserving_pi
#check MeasureTheory.Measure.infinitePi_map_pi
#check MeasureTheory.Measure.pi_map_pi
#check MeasurableEquiv.piCongrLeft
#check MeasureTheory.measurePreserving_piCongrLeft
#check MeasurableEquiv.arrowCongr'
#check MeasureTheory.measurePreserving_arrowCongr'
#check Lp.compMeasurePreservingₗᵢ
