import PowerDivisibility

/-! A split target reflects the ambient power filtration. Membership in a
submodule alone does not imply this statement, especially over nilpotent rings. -/

namespace Komorebi.StrongArtin.SplitTargetFiltration

open Komorebi.StrongArtin.PowerDivisibility

variable {R W : Type*} [CommRing R] [AddCommGroup W] [Module R W]

/-- A declared integral splitting, not just a residual vector-space complement. -/
structure Retraction (C : Submodule R W) where
  project : W →ₗ[R] C
  left_inverse : project.comp C.subtype = LinearMap.id

variable {C : Submodule R W}

@[simp] theorem Retraction.project_coe (r : Retraction C) (w : C) :
    r.project (w : W) = w := by
  exact LinearMap.congr_fun r.left_inverse w

/-- Internal and ambient divisibility agree when a genuine retraction exists. -/
theorem Retraction.powDivisible_iff (r : Retraction C)
    (pi : R) (n : ℕ) (w : C) :
    PowDivisible pi n w ↔ PowDivisible pi n (w : W) := by
  constructor
  · exact fun h => h.map C.subtype
  · intro h
    have h' := h.map r.project
    simpa only [r.project_coe] using h'

/-- A zero projected value is an actual zero for a compatible vector. -/
theorem Retraction.project_eq_zero_iff (r : Retraction C)
    (w : W) (hw : w ∈ C) : r.project w = 0 ↔ w = 0 := by
  constructor
  · intro h
    have hcoe : ((r.project w : C) : W) = w := by
      exact congrArg (fun z : C => (z : W)) (r.project_coe ⟨w, hw⟩)
    simpa only [h, Submodule.coe_zero] using hcoe.symm
  · rintro rfl
    exact map_zero _

/-- Ambient errors can be divided within the compatible submodule. -/
theorem Retraction.exists_compatible_divisor (r : Retraction C)
    (pi : R) (n : ℕ) (w : W) (hw : w ∈ C)
    (hdiv : PowDivisible pi n w) :
    ∃ z : C, (pi ^ n) • (z : W) = w := by
  have h := (r.powDivisible_iff pi n ⟨w, hw⟩).mpr hdiv
  obtain ⟨z, hz⟩ := h
  exact ⟨z, congrArg (fun t : C => (t : W)) hz⟩

end Komorebi.StrongArtin.SplitTargetFiltration

#print axioms Komorebi.StrongArtin.SplitTargetFiltration.Retraction.powDivisible_iff
#print axioms Komorebi.StrongArtin.SplitTargetFiltration.Retraction.exists_compatible_divisor
