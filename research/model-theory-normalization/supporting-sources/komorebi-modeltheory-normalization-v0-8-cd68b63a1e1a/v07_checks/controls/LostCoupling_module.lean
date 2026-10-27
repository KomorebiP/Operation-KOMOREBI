module
import NormalizedExamples
open Komorebi.Echelon Komorebi.NormalizedExamples Komorebi.Discovery Komorebi.Discovery.NormalizedBackend Komorebi.Representation.Matrix
example : (coordinates (normalize coupled) ![2,0]).isSome=true := by decide +kernel
