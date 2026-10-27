module
public import TorsionEncodingBoundary
@[expose] public section
open Komorebi.Representation.TorsionBoundary
example : pack (firstUnit + firstUnit) = pack firstUnit + pack firstUnit := by decide
