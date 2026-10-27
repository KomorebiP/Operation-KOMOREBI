module
import BoundedArithmeticExamples
open Komorebi.Echelon Komorebi.Echelon.Cost Komorebi.BoundedArithmeticExamples
example : updatePeak fourBasis ![3,3]≤4 := by decide +kernel
