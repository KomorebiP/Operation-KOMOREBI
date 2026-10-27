module
import NormalizedExamples
open Komorebi.Echelon Komorebi.NormalizedExamples Komorebi.Discovery Komorebi.Discovery.NormalizedBackend Komorebi.Representation.Matrix
example : normalizedRun 4 (fun a => rowRight (shearA a)) shearO 0 (diagonal 4 (by decide) 2) [] []=some (diagonal 4 (by decide) 2,[]) := by simp [normalizedRun]
