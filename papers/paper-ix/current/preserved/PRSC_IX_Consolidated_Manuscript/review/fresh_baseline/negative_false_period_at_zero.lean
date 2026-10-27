module
public import PeriodExamples
open KomorebiPaperIX WindowIndependence PeriodExamples
example : reduced 3 2 1=reduced 3 2 0 := by
 norm_num [reduced_one]
