import EchelonExamples
open Komorebi.Echelon Komorebi.EchelonExamples Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Discovery Komorebi.Representation.Matrix
example : fastWorklist 4 (fun a => rowRight (shearA a)) shearO 0 (initial 4 2) [] (roots 1 1) = some [] := by decide +kernel
