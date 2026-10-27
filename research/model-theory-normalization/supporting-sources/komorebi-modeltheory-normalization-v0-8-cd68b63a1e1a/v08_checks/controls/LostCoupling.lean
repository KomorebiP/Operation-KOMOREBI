module
import BoundedArithmeticExamples
open Komorebi.Echelon Komorebi.Echelon.Cost Komorebi.BoundedArithmeticExamples
example : entries (boundedNormalizedInsert fourBasis ![3,3])=![![1,0],![0,4]] := by decide +kernel
