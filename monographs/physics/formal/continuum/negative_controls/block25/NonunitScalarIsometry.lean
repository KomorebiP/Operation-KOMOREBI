import KomorebiPhysics.Relativistic3DCliffordHilbertRefinement

open KomorebiPhysics.Relativistic3DCliffordTransportU1
open KomorebiPhysics.Relativistic3DCliffordHilbertRefinement

/-- Deliberately false: scalar multiplication by `2` is not unitary. -/
theorem nonunitScalarIsometry (ψ φ : Spinor) :
    ip ((2 : ℂ) • ψ) ((2 : ℂ) • φ) = ip ψ φ := by
  simp
