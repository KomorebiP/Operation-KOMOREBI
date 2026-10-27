module
import CostedExamples
open Komorebi.Costed Komorebi.CostedExamples Komorebi.Echelon
example : (coordinatesEval fourBasis ![3,3]).2=0 := by decide +kernel
