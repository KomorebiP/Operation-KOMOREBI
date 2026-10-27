import EchelonExamples
open Komorebi.Echelon Komorebi.EchelonExamples Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Discovery Komorebi.Representation.Matrix
example : fastPrimeDiscover 2 2 2 (fun a => rowRight (shearA a)) shearO = some [([],0)] := by decide +kernel
