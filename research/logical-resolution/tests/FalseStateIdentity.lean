module
public import SemanticBoundaries
open Komorebi.LogicalResolution
-- Expected mathematical rejection: f(true) is false, not true.
example : constantSystem.step () true = true := by decide
