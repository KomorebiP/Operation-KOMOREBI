import EchelonExamples
open Komorebi.Echelon Komorebi.EchelonExamples Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Discovery Komorebi.Representation.Matrix
example : member 4 [(![2] : Fin 1 → ZMod 4)] ![1] = true := by decide +kernel
