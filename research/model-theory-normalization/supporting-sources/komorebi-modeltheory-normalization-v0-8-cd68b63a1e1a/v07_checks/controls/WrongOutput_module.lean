module
import NormalizedExamples
open Komorebi.Echelon Komorebi.NormalizedExamples Komorebi.Discovery Komorebi.Discovery.NormalizedBackend Komorebi.Representation.Matrix
example : normalizedPrimeDiscover 2 2 2 (fun a => rowRight (shearA a)) shearO=some [([],0)] := by decide +kernel
