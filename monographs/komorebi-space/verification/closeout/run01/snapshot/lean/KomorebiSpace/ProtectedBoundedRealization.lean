import KomorebiSpace.BoundedApproximateRealization
import KomorebiSpace.ProtectedHilbertRepair

/-!
# Bounded protected approximate realization

WR01 is applied to the actual protected kernel with its inherited Hilbert norm.
The conclusion constructs an exact repaired candidate and retains the very same
correction budget. No closed-range hypothesis is introduced.
-/

set_option autoImplicit false
noncomputable section

open Filter Topology

namespace KomorebiSpace.ProtectedBoundedRealization

variable {E Y Z : Type*}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable [NormedAddCommGroup Z] [NormedSpace ℝ Z]

/-- An exact repair with the original protected data and the same norm budget. -/
theorem exists_exact_repair_of_bounded_approximation
    (D : E →L[ℝ] Y) (p : E →L[ℝ] Z) (f : E)
    (u : ℕ → p.ker) (M : ℝ)
    (hbound : ∀ n, ‖u n‖ ≤ M)
    (hresidual : Tendsto (fun n => ‖D (u n) - D f‖) atTop (𝓝 0)) :
    ∃ y : E, D y = 0 ∧ p y = p f ∧ ‖f - y‖ ≤ M := by
  obtain ⟨a, ha, hnorm⟩ :=
    BoundedApproximateRealization.exists_solution_of_bounded_residual_tendsto_zero
      (ProtectedHilbertRepair.restricted D p) u (D f) M hbound hresidual
  refine ⟨f - (a : E), ?_, ?_, ?_⟩
  · rw [map_sub]
    exact sub_eq_zero.mpr ha.symm
  · rw [map_sub]
    have hp : p (a : E) = 0 := a.property
    rw [hp, sub_zero]
  · rw [sub_sub_cancel]
    exact hnorm

end KomorebiSpace.ProtectedBoundedRealization
