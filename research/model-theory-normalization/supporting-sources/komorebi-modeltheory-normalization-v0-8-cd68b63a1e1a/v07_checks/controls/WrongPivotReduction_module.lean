module
import NormalizedExamples
open Komorebi.Echelon Komorebi.NormalizedExamples Komorebi.Discovery Komorebi.Discovery.NormalizedBackend Komorebi.Representation.Matrix
example : entries (normalize coupled)=![![2,0],![0,64]] := by decide +kernel
