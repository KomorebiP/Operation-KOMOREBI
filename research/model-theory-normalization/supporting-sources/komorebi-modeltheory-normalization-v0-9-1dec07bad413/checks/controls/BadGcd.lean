module
import CostedExamples
open Komorebi.Costed Komorebi.CostedExamples Komorebi.Echelon
example : (gcdEval 240 46).1=1 := by decide +kernel
