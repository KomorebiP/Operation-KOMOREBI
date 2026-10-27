import EchelonExamples
open Komorebi.Echelon Komorebi.EchelonExamples Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Discovery Komorebi.Representation.Matrix
example : member 64 [(![2,32] : Fin 2 → ZMod 64)] ![0,32] = true := by decide +kernel
