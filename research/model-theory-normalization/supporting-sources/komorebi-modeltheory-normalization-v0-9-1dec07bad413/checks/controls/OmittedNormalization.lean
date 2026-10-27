module
import CostedExamples
open Komorebi.Costed Komorebi.CostedExamples Komorebi.Echelon
example : (normalizeEval fourBasis).2=0 := by decide +kernel
