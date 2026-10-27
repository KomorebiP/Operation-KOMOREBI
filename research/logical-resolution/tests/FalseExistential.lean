module
public import SemanticBoundaries
open Komorebi.LogicalResolution
-- Expected mathematical rejection: the only state has observed value false.
example : existsTrue.Holds pointSystem (fun _ => ()) := by
  exact ⟨(), rfl⟩
