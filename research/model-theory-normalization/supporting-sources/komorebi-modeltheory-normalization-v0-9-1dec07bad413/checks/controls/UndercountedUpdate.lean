module
import CostedExamples
open Komorebi.Costed Komorebi.CostedExamples Komorebi.Echelon
example : (updateEval fourBasis ![3,3]).2=57 := by decide +kernel
