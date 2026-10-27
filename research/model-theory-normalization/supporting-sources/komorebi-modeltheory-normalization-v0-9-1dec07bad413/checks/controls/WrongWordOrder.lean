module
import CostedExamples
open Komorebi.Costed Komorebi.CostedExamples Komorebi.Echelon
example : (testEval actions observation ([0,1],0)).1=![1,1] := by decide +kernel
