module
public import DyadicIsometryControls

open KomorebiPaperIX

example : Function.Surjective (DyadicFourIsometry.originalExtension 0 (by decide)) := by
  exact DyadicFourIsometry.isometry_surjective 0 (by decide)
